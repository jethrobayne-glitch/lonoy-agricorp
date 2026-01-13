from flask import Blueprint, render_template, redirect, url_for, request, flash, session, jsonify
from web.models import User, ActivityLog
from functools import wraps

auth_bp = Blueprint('auth', __name__)

def login_required(f):
    """Decorator to require login for routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

def role_required(required_role):
    """Decorator to require specific role for routes"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                return redirect(url_for('main.index'))
            
            current_user = get_current_user()
            selected_role = session.get('selected_role')
            
            # Handle both single role and list of roles
            if isinstance(required_role, list):
                allowed_roles = required_role
                role_check = any(current_user.can_access_role(role) for role in allowed_roles)
                role_selected = selected_role in allowed_roles
                role_name = ' or '.join(allowed_roles)
            else:
                allowed_roles = [required_role]
                role_check = current_user.can_access_role(required_role)
                role_selected = selected_role == required_role
                role_name = required_role
            
            if not current_user or not role_check:
                flash('You do not have permission to access this page.', 'error')
                return redirect(url_for('auth.role_selection'))
            
            if not role_selected:
                flash(f'Please select the {role_name} role to access this page.', 'warning')
                return redirect(url_for('auth.role_selection'))
                
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def get_current_user():
    """Get current user from session"""
    if 'user_id' in session:
        return User.query.get(session['user_id'])
    return None

@auth_bp.route('/login', methods=['POST'])
def login():
    """Handle login form submission"""
    try:
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            return jsonify({'success': False, 'message': 'Username and password are required'})
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['user_type'] = user.user_type
            session['username'] = user.username
            
            # Log login activity
            ActivityLog.log_activity(user, 'login')
            
            return jsonify({
                'success': True, 
                'message': 'Login successful',
                'redirect': url_for('auth.role_selection')
            })
        else:
            return jsonify({'success': False, 'message': 'Invalid username or password'})
            
    except Exception as e:
        return jsonify({'success': False, 'message': 'An error occurred during login'})

@auth_bp.route('/role')
@login_required
def role_selection():
    """Display role selection page"""
    return render_template('role.html', user_type=session.get('user_type'))

@auth_bp.route('/select-role/<role>')
@login_required
def select_role(role):
    """Handle role selection and redirect to appropriate dashboard"""
    current_user = get_current_user()
    if not current_user or not current_user.can_access_role(role):
        flash('You do not have permission to access this role.', 'error')
        return redirect(url_for('auth.role_selection'))
    
    session['selected_role'] = role
    
    # Log role access activity
    department = role.upper()
    ActivityLog.log_activity(current_user, 'access', department)
    
    # Redirect based on role
    if role == 'admin':
        return redirect(url_for('main.admin_logs'))
    elif role == 'tvet':
        return redirect(url_for('main.tvet_inventory'))
    elif role == 'lpaf':
        return redirect(url_for('main.lpaf_inventory'))
    else:
        flash('Invalid role selected.', 'error')
        return redirect(url_for('auth.role_selection'))

@auth_bp.route('/logout')
@login_required
def logout():
    """Handle user logout"""
    # Log logout activity before clearing session
    current_user = get_current_user()
    if current_user:
        department = session.get('selected_role', '').upper()
        ActivityLog.log_activity(current_user, 'logout', department)
    
    session.clear()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('main.index'))

