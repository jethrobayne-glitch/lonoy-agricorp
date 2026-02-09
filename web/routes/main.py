from flask import Blueprint, render_template, request, jsonify, flash, send_from_directory, current_app, session
from web.routes.auth import login_required, role_required
from web.models import db, User, ActivityLog, Student, Certificate, Employee, EmployeeDocument, LPAFInventoryFolder, LPAFProduction, LPAFStatus, LPAFInventoryMaterial, TVETInventoryFolder, TVETCoreCompetency, TVETCategory, TVETInspectionRemark, TVETInventoryMaterial, StudyFolder, StudyVideo, FinanceTransaction
from web.models.lpaf_inventory import LPAFInventoryMaterial
from sqlalchemy import desc
import os
from werkzeug.utils import secure_filename
import uuid
from PIL import Image
import io
from datetime import datetime
import mimetypes
import cv2
import numpy as np

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return render_template('login.html')

# Admin Routes
@main_bp.route('/admin/logs')
@role_required('admin')
def admin_logs():
    # Get filter parameters
    department_filter = request.args.get('department', 'all')
    
    # Build query
    query = ActivityLog.query
    if department_filter and department_filter != 'all':
        query = query.filter(ActivityLog.department == department_filter.upper())
    
    # Get logs ordered by most recent first
    logs = query.order_by(desc(ActivityLog.timestamp)).limit(100).all()
    
    return render_template('admin/logs.html', logs=logs, current_filter=department_filter)

@main_bp.route('/admin/users')
@role_required('admin')
def admin_users():
    users = User.query.all()
    return render_template('admin/user.html', users=users)

@main_bp.route('/api/users', methods=['GET'])
@role_required('admin')
def get_users():
    """Get all users as JSON"""
    users = User.query.all()
    users_data = []
    for user in users:
        users_data.append({
            'id': user.id,
            'name': user.name,
            'username': user.username,
            'user_type': user.user_type,
            'position': user.position or ''
        })
    return jsonify({'users': users_data})

@main_bp.route('/api/users', methods=['POST'])
@role_required('admin')
def create_user():
    """Create a new user"""
    try:
        data = request.get_json()
        
        # Validate input
        name = data.get('name', '').strip()
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()
        user_type = data.get('user_type', '').strip()
        position = data.get('position', '').strip()
        
        if not name or not username or not password or not user_type:
            return jsonify({'success': False, 'message': 'Name, username, password, and user type are required'})
        
        if user_type not in ['admin', 'user']:
            return jsonify({'success': False, 'message': 'Invalid user type'})
        
        # Check if username already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return jsonify({'success': False, 'message': 'Username already exists'})
        
        # Create new user
        new_user = User(name=name, username=username, user_type=user_type, position=position)
        new_user.set_password(password)
        
        db.session.add(new_user)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'User created successfully'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'An error occurred while creating the user'})

@main_bp.route('/api/users/<int:user_id>', methods=['PUT'])
@role_required('admin')
def update_user(user_id):
    """Update an existing user"""
    try:
        user = User.query.get_or_404(user_id)
        data = request.get_json()
        
        # Validate input
        name = data.get('name', '').strip()
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()
        user_type = data.get('user_type', '').strip()
        position = data.get('position', '').strip()
        
        if not name or not username or not user_type:
            return jsonify({'success': False, 'message': 'Name, username and user type are required'})
        
        if user_type not in ['admin', 'user']:
            return jsonify({'success': False, 'message': 'Invalid user type'})
        
        # Check if username already exists (excluding current user)
        existing_user = User.query.filter(User.username == username, User.id != user_id).first()
        if existing_user:
            return jsonify({'success': False, 'message': 'Username already exists'})
        
        # Update user
        user.name = name
        user.username = username
        user.user_type = user_type
        user.position = position
        
        # Only update password if provided
        if password:
            user.set_password(password)
        
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'User updated successfully'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'An error occurred while updating the user'})

@main_bp.route('/api/users/<int:user_id>', methods=['DELETE'])
@role_required('admin')
def delete_user(user_id):
    """Delete a user"""
    try:
        user = User.query.get_or_404(user_id)
        
        # Prevent deletion of the last admin user
        if user.user_type == 'admin':
            admin_count = User.query.filter_by(user_type='admin').count()
            if admin_count <= 1:
                return jsonify({'success': False, 'message': 'Cannot delete the last admin user'})
        
        db.session.delete(user)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'User deleted successfully'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'An error occurred while deleting the user'})

@main_bp.route('/api/logs', methods=['GET'])
@role_required('admin')
def get_logs():
    """Get activity logs with optional filtering"""
    try:
        department_filter = request.args.get('department', 'all')
        
        # Build query
        query = ActivityLog.query
        if department_filter and department_filter != 'all':
            query = query.filter(ActivityLog.department == department_filter.upper())
        
        # Get logs ordered by most recent first
        logs = query.order_by(desc(ActivityLog.timestamp)).limit(100).all()
        
        logs_data = []
        for log in logs:
            logs_data.append({
                'id': log.id,
                'name': log.name,
                'username': log.username,
                'position': log.position or '',
                'action': log.action,
                'timestamp': log.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                'department': log.department or ''
            })
        
        return jsonify({'success': True, 'logs': logs_data})
        
    except Exception as e:
        return jsonify({'success': False, 'message': 'An error occurred while fetching logs'})

# TVET Routes
@main_bp.route('/tvet/inventory')
@role_required('tvet')
def tvet_inventory():
    # Get folders for the dropdown using new TVET models
    folders = TVETInventoryFolder.query.all()
    materials = TVETInventoryMaterial.query.order_by(TVETInventoryMaterial.created_at.desc()).all()
    user_type = session.get('user_type', 'user')
    return render_template('tvet/inventory.html', folders=folders, materials=materials, user_type=user_type)

@main_bp.route('/tvet/students')
@role_required('tvet')
def tvet_students():
    return render_template('tvet/students.html')

@main_bp.route('/tvet/employees')
@role_required('tvet')
def tvet_employees():
    return render_template('tvet/employees.html')

@main_bp.route('/tvet/finance')
@role_required('tvet')
def tvet_finance():
    return render_template('tvet/finance.html')

# LPAF Routes
@main_bp.route('/lpaf/inventory')
@role_required('lpaf')
def lpaf_inventory():
    user_type = session.get('user_type', 'user')
    return render_template('lpaf/inventory.html', user_type=user_type)

@main_bp.route('/lpaf/employees')
@role_required('lpaf')
def lpaf_employees():
    return render_template('lpaf/employees.html')

@main_bp.route('/lpaf/finance')
@role_required('lpaf')
def lpaf_finance():
    return render_template('lpaf/finance.html')

@main_bp.route('/lpaf/study')
@role_required('lpaf')
def lpaf_study():
    user_type = session.get('user_type', 'user')
    return render_template('lpaf/study.html', user_type=user_type)

# Student Management API Routes

@main_bp.route('/api/students', methods=['GET'])
@role_required('tvet')
def get_students():
    """Get all students"""
    try:
        search = request.args.get('search', '').strip()
        
        query = Student.query
        if search:
            # Search in name, batch, or certificate fields
            search_term = f'%{search}%'
            query = query.filter(
                db.or_(
                    Student.name.ilike(search_term),
                    Student.batch.ilike(search_term)
                )
            )
        
        students = query.order_by(Student.batch, Student.name).all()
        students_data = [student.to_dict() for student in students]
        
        return jsonify({'success': True, 'students': students_data})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@main_bp.route('/api/students', methods=['POST'])
@role_required('tvet')
def create_student():
    """Create a new student"""
    try:
        data = request.get_json()
        
        # Validate required fields
        batch = data.get('batch', '').strip()
        name = data.get('name', '').strip()
        age = data.get('age')
        address = data.get('address', '').strip()
        contact_no = data.get('contact_no', '').strip()
        
        if not all([batch, name, age, address, contact_no]):
            return jsonify({'success': False, 'message': 'All fields are required'})
        
        try:
            age = int(age)
            if age <= 0 or age > 150:
                raise ValueError()
        except (ValueError, TypeError):
            return jsonify({'success': False, 'message': 'Age must be a valid number between 1 and 150'})
        
        # Create new student
        student = Student(
            batch=batch,
            name=name,
            age=age,
            address=address,
            contact_no=contact_no
        )
        
        db.session.add(student)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Student created successfully', 'student': student.to_dict()})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'An error occurred while creating the student: {str(e)}'})

@main_bp.route('/api/students/<int:student_id>', methods=['PUT'])
@role_required('tvet')
def update_student(student_id):
    """Update an existing student"""
    try:
        student = Student.query.get_or_404(student_id)
        data = request.get_json()
        
        # Validate required fields
        batch = data.get('batch', '').strip()
        name = data.get('name', '').strip()
        age = data.get('age')
        address = data.get('address', '').strip()
        contact_no = data.get('contact_no', '').strip()
        
        if not all([batch, name, age, address, contact_no]):
            return jsonify({'success': False, 'message': 'All fields are required'})
        
        try:
            age = int(age)
            if age <= 0 or age > 150:
                raise ValueError()
        except (ValueError, TypeError):
            return jsonify({'success': False, 'message': 'Age must be a valid number between 1 and 150'})
        
        # Update student
        student.batch = batch
        student.name = name
        student.age = age
        student.address = address
        student.contact_no = contact_no
        
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Student updated successfully', 'student': student.to_dict()})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'An error occurred while updating the student: {str(e)}'})

@main_bp.route('/api/students/<int:student_id>', methods=['DELETE'])
@role_required('tvet')
def delete_student(student_id):
    """Delete a student"""
    try:
        student = Student.query.get_or_404(student_id)
        
        db.session.delete(student)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Student deleted successfully'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'An error occurred while deleting the student: {str(e)}'})

# Certificate Management Routes
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx'}
UPLOAD_FOLDER = 'web/static/uploads/certificates'
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_thumbnail(file_path, mime_type):
    """Generate thumbnail for image files"""
    try:
        if mime_type.startswith('image/'):
            with Image.open(file_path) as img:
                img.thumbnail((200, 200))
                thumb_filename = f"thumb_{os.path.basename(file_path)}"
                thumb_path = os.path.join(os.path.dirname(file_path), thumb_filename)
                img.save(thumb_path)
                return thumb_filename
    except Exception as e:
        print(f"Error generating thumbnail: {e}")
    return None

@main_bp.route('/api/students/<int:student_id>/certificates', methods=['GET'])
@role_required(['tvet'])
def get_student_certificates(student_id):
    """Get all certificates for a student"""
    try:
        student = Student.query.get(student_id)
        if not student:
            return jsonify({'success': False, 'message': 'Student not found'})
        
        certificates = Certificate.query.filter_by(student_id=student_id).all()
        certificates_data = []
        
        for cert in certificates:
            cert_dict = cert.to_dict()
            # Add thumbnail path for images
            if cert.mime_type and cert.mime_type.startswith('image/'):
                thumb_filename = f"thumb_{cert.filename}"
                thumb_path = f"/static/uploads/certificates/{thumb_filename}"
                if os.path.exists(f"web{thumb_path}"):
                    cert_dict['thumbnail'] = thumb_path
            certificates_data.append(cert_dict)
        
        return jsonify({'success': True, 'certificates': certificates_data})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@main_bp.route('/api/students/<int:student_id>/certificates', methods=['POST'])
@role_required(['tvet'])
def upload_certificate(student_id):
    """Upload certificate for a student"""
    try:
        student = Student.query.get(student_id)
        if not student:
            return jsonify({'success': False, 'message': 'Student not found'})
        
        if 'file' not in request.files:
            return jsonify({'success': False, 'message': 'No file selected'})
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'message': 'No file selected'})
        
        if not allowed_file(file.filename):
            return jsonify({'success': False, 'message': 'File type not allowed'})
        
        # Check file size
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)
        
        if file_size > MAX_FILE_SIZE:
            return jsonify({'success': False, 'message': 'File size exceeds 16MB limit'})
        
        # Generate unique filename
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4()}_{filename}"
        file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
        
        # Ensure upload directory exists
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        
        # Save file
        file.save(file_path)
        
        # Get MIME type
        mime_type = file.content_type
        
        # Generate thumbnail for images
        generate_thumbnail(file_path, mime_type)
        
        # Save to database
        certificate = Certificate(
            student_id=student_id,
            filename=unique_filename,
            original_name=filename,
            file_path=file_path,
            file_size=file_size,
            mime_type=mime_type
        )
        
        db.session.add(certificate)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Certificate uploaded successfully'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@main_bp.route('/api/certificates/<int:certificate_id>', methods=['DELETE'])
@role_required(['tvet'])
def delete_certificate(certificate_id):
    """Delete a certificate"""
    try:
        certificate = Certificate.query.get(certificate_id)
        if not certificate:
            return jsonify({'success': False, 'message': 'Certificate not found'})
        
        # Delete file from filesystem
        if os.path.exists(certificate.file_path):
            os.remove(certificate.file_path)
        
        # Delete thumbnail if it exists
        thumb_filename = f"thumb_{certificate.filename}"
        thumb_path = os.path.join(os.path.dirname(certificate.file_path), thumb_filename)
        if os.path.exists(thumb_path):
            os.remove(thumb_path)
        
        # Delete from database
        db.session.delete(certificate)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Certificate deleted successfully'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

@main_bp.route('/uploads/certificates/<filename>')
def uploaded_file(filename):
    """Serve uploaded files"""
    return send_from_directory('../static/uploads/certificates', filename)

# Employee Management Routes
EMPLOYEE_UPLOAD_FOLDER = 'web/static/uploads/employee_documents'

@main_bp.route('/api/employees', methods=['GET'])
@role_required(['tvet', 'lpaf'])
def get_employees():
    """Get all employees with optional search"""
    try:
        from flask import session
        department = session.get('selected_role', '').upper()
        search = request.args.get('search', '').strip()
        
        query = Employee.query.filter_by(department=department)
        if search:
            query = query.filter(
                Employee.name.contains(search) | 
                Employee.position.contains(search) |
                Employee.job_description.contains(search)
            )
        
        employees = query.order_by(Employee.name).all()
        employees_data = [employee.to_dict() for employee in employees]
        
        return jsonify({'success': True, 'employees': employees_data})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@main_bp.route('/api/employees', methods=['POST'])
@role_required(['tvet', 'lpaf'])
def create_employee():
    """Create a new employee"""
    try:
        from flask import session
        department = session.get('selected_role', '').upper()
        data = request.get_json()
        
        # Validate required fields
        name = data.get('name', '').strip()
        position = data.get('position', '').strip()
        job_description = data.get('job_description', '').strip()
        
        if not all([name, position, job_description]):
            return jsonify({'success': False, 'message': 'All fields are required'})
        
        # Create new employee
        employee = Employee(
            name=name,
            position=position,
            job_description=job_description,
            department=department
        )
        
        db.session.add(employee)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Employee created successfully', 'employee': employee.to_dict()})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'An error occurred while creating the employee: {str(e)}'})

@main_bp.route('/api/employees/<int:employee_id>', methods=['PUT'])
@role_required(['tvet', 'lpaf'])
def update_employee(employee_id):
    """Update an existing employee"""
    try:
        from flask import session
        department = session.get('selected_role', '').upper()
        
        employee = Employee.query.filter_by(id=employee_id, department=department).first()
        if not employee:
            return jsonify({'success': False, 'message': 'Employee not found'})
        
        data = request.get_json()
        
        # Validate required fields
        name = data.get('name', '').strip()
        position = data.get('position', '').strip()
        job_description = data.get('job_description', '').strip()
        
        if not all([name, position, job_description]):
            return jsonify({'success': False, 'message': 'All fields are required'})
        
        # Update employee
        employee.name = name
        employee.position = position
        employee.job_description = job_description
        
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Employee updated successfully', 'employee': employee.to_dict()})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'An error occurred while updating the employee: {str(e)}'})

@main_bp.route('/api/employees/<int:employee_id>', methods=['DELETE'])
@role_required(['tvet', 'lpaf'])
def delete_employee(employee_id):
    """Delete an employee"""
    try:
        from flask import session
        department = session.get('selected_role', '').upper()
        
        employee = Employee.query.filter_by(id=employee_id, department=department).first()
        if not employee:
            return jsonify({'success': False, 'message': 'Employee not found'})
        
        # Delete all associated documents first
        for document in employee.documents:
            if os.path.exists(document.file_path):
                os.remove(document.file_path)
            # Delete thumbnail if it exists
            thumb_filename = f"thumb_{document.filename}"
            thumb_path = os.path.join(os.path.dirname(document.file_path), thumb_filename)
            if os.path.exists(thumb_path):
                os.remove(thumb_path)
        
        db.session.delete(employee)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Employee deleted successfully'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'An error occurred while deleting the employee: {str(e)}'})

# Employee Document Management Routes
@main_bp.route('/api/employees/<int:employee_id>/documents', methods=['GET'])
@role_required(['tvet', 'lpaf'])
def get_employee_documents(employee_id):
    """Get all documents for an employee"""
    try:
        from flask import session
        department = session.get('selected_role', '').upper()
        
        employee = Employee.query.filter_by(id=employee_id, department=department).first()
        if not employee:
            return jsonify({'success': False, 'message': 'Employee not found'})
        
        documents = EmployeeDocument.query.filter_by(employee_id=employee_id).all()
        documents_data = []
        
        for doc in documents:
            doc_dict = doc.to_dict()
            # Add thumbnail path for images
            if doc.mime_type and doc.mime_type.startswith('image/'):
                thumb_filename = f"thumb_{doc.filename}"
                thumb_path = f"/static/uploads/employee_documents/{department.lower()}/{thumb_filename}"
                if os.path.exists(f"web{thumb_path}"):
                    doc_dict['thumbnail'] = thumb_path
            documents_data.append(doc_dict)
        
        return jsonify({'success': True, 'documents': documents_data})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@main_bp.route('/api/employees/<int:employee_id>/documents', methods=['POST'])
@role_required(['tvet', 'lpaf'])
def upload_employee_document(employee_id):
    """Upload document for an employee"""
    try:
        from flask import session
        department = session.get('selected_role', '').upper()
        
        employee = Employee.query.filter_by(id=employee_id, department=department).first()
        if not employee:
            return jsonify({'success': False, 'message': 'Employee not found'})
        
        if 'file' not in request.files:
            return jsonify({'success': False, 'message': 'No file selected'})
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'message': 'No file selected'})
        
        if not allowed_file(file.filename):
            return jsonify({'success': False, 'message': 'File type not allowed'})
        
        # Check file size
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)
        
        if file_size > MAX_FILE_SIZE:
            return jsonify({'success': False, 'message': 'File size exceeds 16MB limit'})
        
        # Generate unique filename
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4()}_{filename}"
        file_path = os.path.join(EMPLOYEE_UPLOAD_FOLDER, unique_filename)
        
        # Ensure upload directory exists
        os.makedirs(EMPLOYEE_UPLOAD_FOLDER, exist_ok=True)
        
        # Save file
        file.save(file_path)
        
        # Get MIME type
        mime_type = file.content_type
        
        # Generate thumbnail for images
        generate_thumbnail(file_path, mime_type)
        
        # Save to database
        document = EmployeeDocument(
            employee_id=employee_id,
            filename=unique_filename,
            original_name=filename,
            file_path=file_path,
            file_size=file_size,
            mime_type=mime_type
        )
        
        db.session.add(document)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Document uploaded successfully'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@main_bp.route('/api/employee_documents/<int:document_id>', methods=['DELETE'])
@role_required(['tvet', 'lpaf'])
def delete_employee_document(document_id):
    """Delete an employee document"""
    try:
        from flask import session
        department = session.get('selected_role', '').upper()
        
        document = EmployeeDocument.query.join(Employee).filter(
            EmployeeDocument.id == document_id,
            Employee.department == department
        ).first()
        if not document:
            return jsonify({'success': False, 'message': 'Document not found'})
        
        # Delete file from filesystem
        if os.path.exists(document.file_path):
            os.remove(document.file_path)
        
        # Delete thumbnail if it exists
        thumb_filename = f"thumb_{document.filename}"
        thumb_path = os.path.join(os.path.dirname(document.file_path), thumb_filename)
        if os.path.exists(thumb_path):
            os.remove(thumb_path)
        
        # Delete from database
        db.session.delete(document)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Document deleted successfully'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

# LPAF Inventory API Routes

# LPAF Folder Management
@main_bp.route('/api/lpaf/inventory/folders', methods=['GET'])
@role_required('lpaf')
def get_lpaf_folders():
    """Get LPAF folders"""
    try:
        folders = LPAFInventoryFolder.query.all()
        folders_data = []
        for folder in folders:
            folders_data.append({
                'id': folder.id,
                'name': folder.name,
                'description': folder.description or '',
                'created_at': folder.created_at.strftime('%Y-%m-%d %H:%M:%S')
            })
        
        return jsonify({'success': True, 'folders': folders_data})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@main_bp.route('/api/lpaf/inventory/folders', methods=['POST'])
@role_required('lpaf')
def create_lpaf_folder():
    """Create a new LPAF folder"""
    try:
        data = request.get_json()
        
        name = data.get('name', '').strip()
        description = data.get('description', '').strip()
        
        if not name:
            return jsonify({'success': False, 'message': 'Folder name is required'})
        
        # Check if folder exists
        existing = LPAFInventoryFolder.query.filter_by(name=name).first()
        if existing:
            return jsonify({'success': False, 'message': 'Folder name already exists'})
        
        folder = LPAFInventoryFolder(name=name, description=description)
        db.session.add(folder)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Folder created successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

@main_bp.route('/api/lpaf/inventory/folders/<int:folder_id>', methods=['PUT'])
@role_required('lpaf')
def update_lpaf_folder(folder_id):
    """Update a LPAF folder"""
    try:
        data = request.get_json()
        
        folder = LPAFInventoryFolder.query.get(folder_id)
        if not folder:
            return jsonify({'success': False, 'message': 'Folder not found'})
        
        name = data.get('name', '').strip()
        description = data.get('description', '').strip()
        
        if not name:
            return jsonify({'success': False, 'message': 'Folder name is required'})
        
        # Check if new name conflicts
        existing = LPAFInventoryFolder.query.filter(
            LPAFInventoryFolder.name == name, 
            LPAFInventoryFolder.id != folder_id
        ).first()
        if existing:
            return jsonify({'success': False, 'message': 'Folder name already exists'})
        
        folder.name = name
        folder.description = description
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Folder updated successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

@main_bp.route('/api/lpaf/inventory/folders/<int:folder_id>', methods=['DELETE'])
@role_required('lpaf')
def delete_lpaf_folder(folder_id):
    """Delete a LPAF folder"""
    try:
        folder = LPAFInventoryFolder.query.get(folder_id)
        if not folder:
            return jsonify({'success': False, 'message': 'Folder not found'})
        
        # Check if folder has materials
        if folder.materials:
            return jsonify({'success': False, 'message': 'Cannot delete folder that contains materials'})
        
        db.session.delete(folder)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Folder deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

# LPAF Production Management
@main_bp.route('/api/lpaf/inventory/productions', methods=['GET'])
@role_required('lpaf')
def get_lpaf_productions():
    """Get LPAF productions"""
    try:
        productions = LPAFProduction.query.all()
        prod_data = []
        for prod in productions:
            prod_data.append({
                'id': prod.id,
                'name': prod.name,
                'description': prod.description or '',
                'created_at': prod.created_at.strftime('%Y-%m-%d %H:%M:%S')
            })
        
        return jsonify({'success': True, 'productions': prod_data})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@main_bp.route('/api/lpaf/inventory/productions', methods=['POST'])
@role_required('lpaf')
def create_lpaf_production():
    """Create a new LPAF production"""
    try:
        data = request.get_json()
        
        name = data.get('name', '').strip()
        description = data.get('description', '').strip()
        
        if not name:
            return jsonify({'success': False, 'message': 'Production name is required'})
        
        # Check if production exists
        existing = LPAFProduction.query.filter_by(name=name).first()
        if existing:
            return jsonify({'success': False, 'message': 'Production name already exists'})
        
        production = LPAFProduction(name=name, description=description)
        db.session.add(production)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Production created successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

@main_bp.route('/api/lpaf/inventory/productions/<int:production_id>', methods=['PUT'])
@role_required('lpaf')
def update_lpaf_production(production_id):
    """Update a LPAF production"""
    try:
        data = request.get_json()
        
        production = LPAFProduction.query.get(production_id)
        if not production:
            return jsonify({'success': False, 'message': 'Production not found'})
        
        name = data.get('name', '').strip()
        description = data.get('description', '').strip()
        
        if not name:
            return jsonify({'success': False, 'message': 'Production name is required'})
        
        # Check if new name conflicts
        existing = LPAFProduction.query.filter(
            LPAFProduction.name == name, 
            LPAFProduction.id != production_id
        ).first()
        if existing:
            return jsonify({'success': False, 'message': 'Production name already exists'})
        
        production.name = name
        production.description = description
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Production updated successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

@main_bp.route('/api/lpaf/inventory/productions/<int:production_id>', methods=['DELETE'])
@role_required('lpaf')
def delete_lpaf_production(production_id):
    """Delete a LPAF production"""
    try:
        production = LPAFProduction.query.get(production_id)
        if not production:
            return jsonify({'success': False, 'message': 'Production not found'})
        
        # Check if production has materials
        if production.materials:
            return jsonify({'success': False, 'message': 'Cannot delete production that has associated materials'})
        
        db.session.delete(production)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Production deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

# LPAF Status Management
@main_bp.route('/api/lpaf/inventory/statuses', methods=['GET'])
@role_required('lpaf')
def get_lpaf_statuses():
    """Get LPAF statuses"""
    try:
        statuses = LPAFStatus.query.all()
        status_data = []
        for status in statuses:
            status_data.append({
                'id': status.id,
                'name': status.name,
                'description': status.description or '',
                'created_at': status.created_at.strftime('%Y-%m-%d %H:%M:%S')
            })
        
        return jsonify({'success': True, 'statuses': status_data})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@main_bp.route('/api/lpaf/inventory/statuses', methods=['POST'])
@role_required('lpaf')
def create_lpaf_status():
    """Create a new LPAF status"""
    try:
        data = request.get_json()
        
        name = data.get('name', '').strip()
        description = data.get('description', '').strip()
        
        if not name:
            return jsonify({'success': False, 'message': 'Status name is required'})
        
        # Check if status exists
        existing = LPAFStatus.query.filter_by(name=name).first()
        if existing:
            return jsonify({'success': False, 'message': 'Status name already exists'})
        
        status = LPAFStatus(name=name, description=description)
        db.session.add(status)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Status created successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

@main_bp.route('/api/lpaf/inventory/statuses/<int:status_id>', methods=['PUT'])
@role_required('lpaf')
def update_lpaf_status(status_id):
    """Update a LPAF status"""
    try:
        data = request.get_json()
        
        status = LPAFStatus.query.get(status_id)
        if not status:
            return jsonify({'success': False, 'message': 'Status not found'})
        
        name = data.get('name', '').strip()
        description = data.get('description', '').strip()
        
        if not name:
            return jsonify({'success': False, 'message': 'Status name is required'})
        
        # Check if new name conflicts
        existing = LPAFStatus.query.filter(
            LPAFStatus.name == name, 
            LPAFStatus.id != status_id
        ).first()
        if existing:
            return jsonify({'success': False, 'message': 'Status name already exists'})
        
        status.name = name
        status.description = description
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Status updated successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

@main_bp.route('/api/lpaf/inventory/statuses/<int:status_id>', methods=['DELETE'])
@role_required('lpaf')
def delete_lpaf_status(status_id):
    """Delete a LPAF status"""
    try:
        status = LPAFStatus.query.get(status_id)
        if not status:
            return jsonify({'success': False, 'message': 'Status not found'})
        
        # Check if status has materials
        if status.materials:
            return jsonify({'success': False, 'message': 'Cannot delete status that has associated materials'})
        
        db.session.delete(status)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Status deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

# LPAF Material Management
@main_bp.route('/api/lpaf/inventory/materials', methods=['GET'])
@role_required('lpaf')
def get_lpaf_materials():
    """Get LPAF materials"""
    try:
        folder_id = request.args.get('folder_id', type=int)
        
        query = LPAFInventoryMaterial.query
        if folder_id:
            query = query.filter_by(folder_id=folder_id)
        
        materials = query.all()
        materials_data = [material.to_dict() for material in materials]
        
        return jsonify({'success': True, 'materials': materials_data})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@main_bp.route('/api/lpaf/inventory/materials', methods=['POST'])
@role_required('lpaf')
def create_lpaf_material():
    """Create a new LPAF material"""
    try:
        data = request.get_json()
        
        # Required fields
        item_name = data.get('item_name', '').strip()
        if not item_name:
            return jsonify({'success': False, 'message': 'Item name is required'})
        
        # Optional fields
        item_code = LPAFInventoryMaterial.generate_item_code()
        description = data.get('description', '').strip()
        folder_id = data.get('folder_id') or None
        production_id = data.get('production_id') or None
        status_id = data.get('status_id') or None
        
        # Validate foreign keys exist
        if folder_id:
            folder = LPAFInventoryFolder.query.get(folder_id)
            if not folder:
                return jsonify({'success': False, 'message': 'Selected folder not found'})
        
        if production_id:
            production = LPAFProduction.query.get(production_id)
            if not production:
                return jsonify({'success': False, 'message': 'Selected production not found'})
        
        if status_id:
            status = LPAFStatus.query.get(status_id)
            if not status:
                return jsonify({'success': False, 'message': 'Selected status not found'})
        
        material = LPAFInventoryMaterial(
            item_name=item_name,
            item_code=item_code,
            description=description,
            folder_id=folder_id,
            production_id=production_id,
            status_id=status_id
        )
        
        db.session.add(material)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Material created successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

@main_bp.route('/api/lpaf/inventory/materials/<int:material_id>', methods=['PUT'])
@role_required('lpaf')
def update_lpaf_material(material_id):
    """Update a LPAF material"""
    try:
        data = request.get_json()
        
        material = LPAFInventoryMaterial.query.get(material_id)
        if not material:
            return jsonify({'success': False, 'message': 'Material not found'})
        
        # Required fields
        item_name = data.get('item_name', '').strip()
        if not item_name:
            return jsonify({'success': False, 'message': 'Item name is required'})
        
        # Optional fields
        description = data.get('description', '').strip()
        folder_id = data.get('folder_id') or None
        production_id = data.get('production_id') or None
        status_id = data.get('status_id') or None
        
        # Validate foreign keys exist
        if folder_id:
            folder = LPAFInventoryFolder.query.get(folder_id)
            if not folder:
                return jsonify({'success': False, 'message': 'Selected folder not found'})
        
        if production_id:
            production = LPAFProduction.query.get(production_id)
            if not production:
                return jsonify({'success': False, 'message': 'Selected production not found'})
        
        if status_id:
            status = LPAFStatus.query.get(status_id)
            if not status:
                return jsonify({'success': False, 'message': 'Selected status not found'})
        
        # Update material
        material.item_name = item_name
        material.description = description
        material.folder_id = folder_id
        material.production_id = production_id
        material.status_id = status_id
        
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Material updated successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

@main_bp.route('/api/lpaf/inventory/materials/<int:material_id>', methods=['DELETE'])
@role_required('lpaf')
def delete_lpaf_material(material_id):
    """Delete a LPAF material"""
    try:
        material = LPAFInventoryMaterial.query.get(material_id)
        if not material:
            return jsonify({'success': False, 'message': 'Material not found'})
        
        db.session.delete(material)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Material deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

# TVET Inventory API Routes

# TVET Folder Management
@main_bp.route('/api/tvet/inventory/folders', methods=['GET'])
@role_required('tvet')
def get_tvet_folders():
    """Get TVET folders"""
    try:
        folders = TVETInventoryFolder.query.all()
        folders_data = []
        for folder in folders:
            folders_data.append({
                'id': folder.id,
                'name': folder.name,
                'description': folder.description or '',
                'created_at': folder.created_at.strftime('%Y-%m-%d %H:%M:%S')
            })
        
        return jsonify({'success': True, 'folders': folders_data})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@main_bp.route('/api/tvet/inventory/folders', methods=['POST'])
@role_required('tvet')
def create_tvet_folder():
    """Create a new TVET folder"""
    try:
        data = request.get_json()
        
        name = data.get('name', '').strip()
        description = data.get('description', '').strip()
        
        if not name:
            return jsonify({'success': False, 'message': 'Folder name is required'})
        
        # Check if folder exists
        existing = TVETInventoryFolder.query.filter_by(name=name).first()
        if existing:
            return jsonify({'success': False, 'message': 'Folder name already exists'})
        
        folder = TVETInventoryFolder(name=name, description=description)
        db.session.add(folder)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Folder created successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

@main_bp.route('/api/tvet/inventory/folders/<int:folder_id>', methods=['PUT'])
@role_required('tvet')
def update_tvet_folder(folder_id):
    """Update a TVET folder"""
    try:
        data = request.get_json()
        
        folder = TVETInventoryFolder.query.get(folder_id)
        if not folder:
            return jsonify({'success': False, 'message': 'Folder not found'})
        
        name = data.get('name', '').strip()
        description = data.get('description', '').strip()
        
        if not name:
            return jsonify({'success': False, 'message': 'Folder name is required'})
        
        # Check if new name conflicts
        existing = TVETInventoryFolder.query.filter(
            TVETInventoryFolder.name == name, 
            TVETInventoryFolder.id != folder_id
        ).first()
        if existing:
            return jsonify({'success': False, 'message': 'Folder name already exists'})
        
        folder.name = name
        folder.description = description
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Folder updated successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

@main_bp.route('/api/tvet/inventory/folders/<int:folder_id>', methods=['DELETE'])
@role_required('tvet')
def delete_tvet_folder(folder_id):
    """Delete a TVET folder"""
    try:
        folder = TVETInventoryFolder.query.get(folder_id)
        if not folder:
            return jsonify({'success': False, 'message': 'Folder not found'})
        
        # Check if folder has materials
        if folder.materials:
            return jsonify({'success': False, 'message': 'Cannot delete folder that contains materials'})
        
        db.session.delete(folder)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Folder deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

# TVET Core Competency Management
@main_bp.route('/api/tvet/inventory/competencies', methods=['GET'])
@role_required('tvet')
def get_tvet_competencies():
    """Get TVET core competencies"""
    try:
        competencies = TVETCoreCompetency.query.all()
        competencies_data = []
        for competency in competencies:
            competencies_data.append({
                'id': competency.id,
                'name': competency.name,
                'description': competency.description or '',
                'created_at': competency.created_at.strftime('%Y-%m-%d %H:%M:%S')
            })
        
        return jsonify({'success': True, 'competencies': competencies_data})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@main_bp.route('/api/tvet/inventory/competencies', methods=['POST'])
@role_required('tvet')
def create_tvet_competency():
    """Create a new TVET core competency"""
    try:
        data = request.get_json()
        
        name = data.get('name', '').strip()
        description = data.get('description', '').strip()
        
        if not name:
            return jsonify({'success': False, 'message': 'Competency name is required'})
        
        # Check if competency exists
        existing = TVETCoreCompetency.query.filter_by(name=name).first()
        if existing:
            return jsonify({'success': False, 'message': 'Competency name already exists'})
        
        competency = TVETCoreCompetency(name=name, description=description)
        db.session.add(competency)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Competency created successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

@main_bp.route('/api/tvet/inventory/competencies/<int:comp_id>', methods=['PUT'])
@role_required('tvet')
def update_tvet_competency(comp_id):
    """Update a TVET core competency"""
    try:
        data = request.get_json()
        
        competency = TVETCoreCompetency.query.get(comp_id)
        if not competency:
            return jsonify({'success': False, 'message': 'Competency not found'})
        
        name = data.get('name', '').strip()
        description = data.get('description', '').strip()
        
        if not name:
            return jsonify({'success': False, 'message': 'Competency name is required'})
        
        # Check if new name conflicts
        existing = TVETCoreCompetency.query.filter(
            TVETCoreCompetency.name == name,
            TVETCoreCompetency.id != comp_id
        ).first()
        if existing:
            return jsonify({'success': False, 'message': 'Competency name already exists'})
        
        competency.name = name
        competency.description = description
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Competency updated successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

@main_bp.route('/api/tvet/inventory/competencies/<int:comp_id>', methods=['DELETE'])
@role_required('tvet')
def delete_tvet_competency(comp_id):
    """Delete a TVET core competency"""
    try:
        competency = TVETCoreCompetency.query.get(comp_id)
        if not competency:
            return jsonify({'success': False, 'message': 'Competency not found'})
        
        # Check if competency has materials
        if competency.materials:
            return jsonify({'success': False, 'message': 'Cannot delete competency that is used by materials'})
        
        db.session.delete(competency)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Competency deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

# TVET Category Management
@main_bp.route('/api/tvet/inventory/categories', methods=['GET'])
@role_required('tvet')
def get_tvet_categories():
    """Get TVET categories"""
    try:
        categories = TVETCategory.query.all()
        categories_data = []
        for category in categories:
            categories_data.append({
                'id': category.id,
                'name': category.name,
                'description': category.description or '',
                'created_at': category.created_at.strftime('%Y-%m-%d %H:%M:%S')
            })
        
        return jsonify({'success': True, 'categories': categories_data})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@main_bp.route('/api/tvet/inventory/categories', methods=['POST'])
@role_required('tvet')
def create_tvet_category():
    """Create a new TVET category"""
    try:
        data = request.get_json()
        
        name = data.get('name', '').strip()
        description = data.get('description', '').strip()
        
        if not name:
            return jsonify({'success': False, 'message': 'Category name is required'})
        
        # Check if category exists
        existing = TVETCategory.query.filter_by(name=name).first()
        if existing:
            return jsonify({'success': False, 'message': 'Category name already exists'})
        
        category = TVETCategory(name=name, description=description)
        db.session.add(category)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Category created successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

@main_bp.route('/api/tvet/inventory/categories/<int:cat_id>', methods=['PUT'])
@role_required('tvet')
def update_tvet_category(cat_id):
    """Update a TVET category"""
    try:
        data = request.get_json()
        
        category = TVETCategory.query.get(cat_id)
        if not category:
            return jsonify({'success': False, 'message': 'Category not found'})
        
        name = data.get('name', '').strip()
        description = data.get('description', '').strip()
        
        if not name:
            return jsonify({'success': False, 'message': 'Category name is required'})
        
        # Check if new name conflicts
        existing = TVETCategory.query.filter(
            TVETCategory.name == name,
            TVETCategory.id != cat_id
        ).first()
        if existing:
            return jsonify({'success': False, 'message': 'Category name already exists'})
        
        category.name = name
        category.description = description
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Category updated successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

@main_bp.route('/api/tvet/inventory/categories/<int:cat_id>', methods=['DELETE'])
@role_required('tvet')
def delete_tvet_category(cat_id):
    """Delete a TVET category"""
    try:
        category = TVETCategory.query.get(cat_id)
        if not category:
            return jsonify({'success': False, 'message': 'Category not found'})
        
        # Check if category has materials
        if category.materials:
            return jsonify({'success': False, 'message': 'Cannot delete category that is used by materials'})
        
        db.session.delete(category)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Category deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

# TVET Inspection Remark Management
@main_bp.route('/api/tvet/inventory/remarks', methods=['GET'])
@role_required('tvet')
def get_tvet_remarks():
    """Get TVET inspection remarks"""
    try:
        remarks = TVETInspectionRemark.query.all()
        remarks_data = []
        for remark in remarks:
            remarks_data.append({
                'id': remark.id,
                'name': remark.name,
                'description': remark.description or '',
                'created_at': remark.created_at.strftime('%Y-%m-%d %H:%M:%S')
            })
        
        return jsonify({'success': True, 'remarks': remarks_data})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@main_bp.route('/api/tvet/inventory/remarks', methods=['POST'])
@role_required('tvet')
def create_tvet_remark():
    """Create a new TVET inspection remark"""
    try:
        data = request.get_json()
        
        name = data.get('name', '').strip()
        description = data.get('description', '').strip()
        
        if not name:
            return jsonify({'success': False, 'message': 'Remark name is required'})
        
        # Check if remark exists
        existing = TVETInspectionRemark.query.filter_by(name=name).first()
        if existing:
            return jsonify({'success': False, 'message': 'Remark name already exists'})
        
        remark = TVETInspectionRemark(name=name, description=description)
        db.session.add(remark)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Remark created successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

@main_bp.route('/api/tvet/inventory/remarks/<int:remark_id>', methods=['PUT'])
@role_required('tvet')
def update_tvet_remark(remark_id):
    """Update a TVET inspection remark"""
    try:
        data = request.get_json()
        
        remark = TVETInspectionRemark.query.get(remark_id)
        if not remark:
            return jsonify({'success': False, 'message': 'Remark not found'})
        
        name = data.get('name', '').strip()
        description = data.get('description', '').strip()
        
        if not name:
            return jsonify({'success': False, 'message': 'Remark name is required'})
        
        # Check if new name conflicts
        existing = TVETInspectionRemark.query.filter(
            TVETInspectionRemark.name == name,
            TVETInspectionRemark.id != remark_id
        ).first()
        if existing:
            return jsonify({'success': False, 'message': 'Remark name already exists'})
        
        remark.name = name
        remark.description = description
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Remark updated successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

@main_bp.route('/api/tvet/inventory/remarks/<int:remark_id>', methods=['DELETE'])
@role_required('tvet')
def delete_tvet_remark(remark_id):
    """Delete a TVET inspection remark"""
    try:
        remark = TVETInspectionRemark.query.get(remark_id)
        if not remark:
            return jsonify({'success': False, 'message': 'Remark not found'})
        
        # Check if remark has materials
        if remark.materials:
            return jsonify({'success': False, 'message': 'Cannot delete remark that is used by materials'})
        
        db.session.delete(remark)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Remark deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

# TVET Material Management
@main_bp.route('/api/tvet/inventory/materials', methods=['GET'])
@role_required('tvet')
def get_tvet_materials():
    """Get TVET materials"""
    try:
        folder_id = request.args.get('folder_id')
        
        query = TVETInventoryMaterial.query
        if folder_id:
            query = query.filter_by(folder_id=folder_id)
        
        materials = query.all()
        materials_data = []
        for material in materials:
            materials_data.append(material.to_dict())
        
        return jsonify({'success': True, 'materials': materials_data})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@main_bp.route('/api/tvet/inventory/materials', methods=['POST'])
@role_required('tvet')
def create_tvet_material():
    """Create a new TVET material"""
    try:
        data = request.get_json()
        
        item = data.get('item', '').strip()
        if not item:
            return jsonify({'success': False, 'message': 'Item name is required'})
        
        quantity_required = data.get('quantity_required')
        quantity_on_site = data.get('quantity_on_site')
        
        if quantity_required is None or quantity_on_site is None:
            return jsonify({'success': False, 'message': 'Quantity required and quantity on site are required'})
        
        try:
            quantity_required = int(quantity_required)
            quantity_on_site = int(quantity_on_site)
            quantity_y1 = int(data.get('quantity_y1', 0))
            quantity_y2 = int(data.get('quantity_y2', 0))
        except (ValueError, TypeError):
            return jsonify({'success': False, 'message': 'Quantities must be valid numbers'})
        
        if quantity_required < 0 or quantity_on_site < 0 or quantity_y1 < 0 or quantity_y2 < 0:
            return jsonify({'success': False, 'message': 'Quantities cannot be negative'})
        
        # Validate foreign keys
        folder_id = data.get('folder_id') or None
        competency_id = data.get('competency_id') or None
        category_id = data.get('category_id') or None
        inspection_remark_id = data.get('inspection_remark_id') or None
        
        if folder_id and not TVETInventoryFolder.query.get(folder_id):
            return jsonify({'success': False, 'message': 'Selected folder not found'})
        
        if competency_id and not TVETCoreCompetency.query.get(competency_id):
            return jsonify({'success': False, 'message': 'Selected competency not found'})
        
        if category_id and not TVETCategory.query.get(category_id):
            return jsonify({'success': False, 'message': 'Selected category not found'})
        
        if inspection_remark_id and not TVETInspectionRemark.query.get(inspection_remark_id):
            return jsonify({'success': False, 'message': 'Selected remark not found'})
        
        material = TVETInventoryMaterial(
            folder_id=folder_id,
            competency_id=competency_id,
            category_id=category_id,
            inspection_remark_id=inspection_remark_id,
            item=item,
            specification=data.get('specification', '').strip(),
            quantity_required=quantity_required,
            quantity_on_site=quantity_on_site,
            quantity_y1=quantity_y1,
            quantity_y2=quantity_y2
        )
        
        db.session.add(material)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Material created successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

@main_bp.route('/api/tvet/inventory/materials/<int:material_id>', methods=['PUT'])
@role_required('tvet')
def update_tvet_material(material_id):
    """Update a TVET material"""
    try:
        data = request.get_json()
        
        material = TVETInventoryMaterial.query.get(material_id)
        if not material:
            return jsonify({'success': False, 'message': 'Material not found'})
        
        item = data.get('item', '').strip()
        if not item:
            return jsonify({'success': False, 'message': 'Item name is required'})
        
        quantity_required = data.get('quantity_required')
        quantity_on_site = data.get('quantity_on_site')
        
        if quantity_required is None or quantity_on_site is None:
            return jsonify({'success': False, 'message': 'Quantity required and quantity on site are required'})
        
        try:
            quantity_required = int(quantity_required)
            quantity_on_site = int(quantity_on_site)
            quantity_y1 = int(data.get('quantity_y1', 0))
            quantity_y2 = int(data.get('quantity_y2', 0))
        except (ValueError, TypeError):
            return jsonify({'success': False, 'message': 'Quantities must be valid numbers'})
        
        if quantity_required < 0 or quantity_on_site < 0 or quantity_y1 < 0 or quantity_y2 < 0:
            return jsonify({'success': False, 'message': 'Quantities cannot be negative'})
        
        # Validate foreign keys
        folder_id = data.get('folder_id') or None
        competency_id = data.get('competency_id') or None
        category_id = data.get('category_id') or None
        inspection_remark_id = data.get('inspection_remark_id') or None
        
        if folder_id and not TVETInventoryFolder.query.get(folder_id):
            return jsonify({'success': False, 'message': 'Selected folder not found'})
        
        if competency_id and not TVETCoreCompetency.query.get(competency_id):
            return jsonify({'success': False, 'message': 'Selected competency not found'})
        
        if category_id and not TVETCategory.query.get(category_id):
            return jsonify({'success': False, 'message': 'Selected category not found'})
        
        if inspection_remark_id and not TVETInspectionRemark.query.get(inspection_remark_id):
            return jsonify({'success': False, 'message': 'Selected remark not found'})
        
        # Update material
        material.folder_id = folder_id
        material.competency_id = competency_id
        material.category_id = category_id
        material.inspection_remark_id = inspection_remark_id
        material.item = item
        material.specification = data.get('specification', '').strip()
        material.quantity_required = quantity_required
        material.quantity_on_site = quantity_on_site
        material.quantity_y1 = quantity_y1
        material.quantity_y2 = quantity_y2
        
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Material updated successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

@main_bp.route('/api/tvet/inventory/materials/<int:material_id>', methods=['DELETE'])
@role_required('tvet')
def delete_tvet_material(material_id):
    """Delete a TVET material"""
    try:
        material = TVETInventoryMaterial.query.get(material_id)
        if not material:
            return jsonify({'success': False, 'message': 'Material not found'})
        
        db.session.delete(material)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Material deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

@main_bp.route('/uploads/employee_documents/<filename>')
def uploaded_employee_document(filename):
    """Serve uploaded employee document files"""
    return send_from_directory('../static/uploads/employee_documents', filename)

# Study Folder and Video Management Routes
ALLOWED_VIDEO_EXTENSIONS = {'mp4', 'avi', 'mov', 'wmv', 'flv', 'mkv', 'webm', 'mpeg', 'mpg'}
STUDY_VIDEO_FOLDER = 'web/static/uploads/study_videos'
STUDY_THUMBNAIL_FOLDER = 'web/static/uploads/study_videos/thumbnails'
MAX_VIDEO_SIZE = 500 * 1024 * 1024  # 500MB

def allowed_video_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_VIDEO_EXTENSIONS

def generate_video_thumbnail(video_path, thumbnail_path, timestamp=1.0):
    """
    Generate a thumbnail from a video file at a specific timestamp.
    
    Args:
        video_path: Path to the video file
        thumbnail_path: Path where thumbnail should be saved
        timestamp: Time in seconds to capture the frame (default: 1 second)
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Open the video file
        video = cv2.VideoCapture(video_path)
        
        if not video.isOpened():
            return False
        
        # Get video properties
        fps = video.get(cv2.CAP_PROP_FPS)
        total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
        
        # Calculate frame number to capture
        frame_number = min(int(fps * timestamp), total_frames - 1)
        
        # Set video position to the desired frame
        video.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
        
        # Read the frame
        success, frame = video.read()
        
        if success:
            # Resize thumbnail to a reasonable size (maintaining aspect ratio)
            height, width = frame.shape[:2]
            max_width = 400
            if width > max_width:
                ratio = max_width / width
                new_width = max_width
                new_height = int(height * ratio)
                frame = cv2.resize(frame, (new_width, new_height), interpolation=cv2.INTER_AREA)
            
            # Convert BGR to RGB (OpenCV uses BGR by default)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Convert to PIL Image and save as JPEG
            img = Image.fromarray(frame)
            img.save(thumbnail_path, 'JPEG', quality=85, optimize=True)
            
            video.release()
            return True
        
        video.release()
        return False
        
    except Exception as e:
        print(f"Error generating thumbnail: {str(e)}")
        return False

# Folder Management
@main_bp.route('/api/study/folders', methods=['GET'])
@role_required('lpaf')
def get_study_folders():
    """Get all study folders with optional parent filter"""
    try:
        parent_id = request.args.get('parent_id', type=int)
        
        if parent_id is not None:
            # Get folders in specific parent
            folders = StudyFolder.query.filter_by(parent_folder_id=parent_id).all()
        elif request.args.get('root_only') == 'true':
            # Get only root folders (no parent)
            folders = StudyFolder.query.filter_by(parent_folder_id=None).all()
        else:
            # Get all folders
            folders = StudyFolder.query.all()
        
        folders_data = [folder.to_dict() for folder in folders]
        return jsonify({'success': True, 'folders': folders_data})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@main_bp.route('/api/study/folders', methods=['POST'])
@role_required('lpaf')
def create_study_folder():
    """Create a new study folder"""
    try:
        data = request.get_json()
        
        name = data.get('name', '').strip()
        description = data.get('description', '').strip()
        parent_folder_id = data.get('parent_folder_id')
        
        if not name:
            return jsonify({'success': False, 'message': 'Folder name is required'})
        
        # Validate parent folder exists if provided
        if parent_folder_id:
            parent = StudyFolder.query.get(parent_folder_id)
            if not parent:
                return jsonify({'success': False, 'message': 'Parent folder not found'})
        
        folder = StudyFolder(
            name=name,
            description=description,
            parent_folder_id=parent_folder_id
        )
        
        db.session.add(folder)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Folder created successfully', 'folder': folder.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

@main_bp.route('/api/study/folders/<int:folder_id>', methods=['PUT'])
@role_required('lpaf')
def update_study_folder(folder_id):
    """Update a study folder"""
    try:
        folder = StudyFolder.query.get(folder_id)
        if not folder:
            return jsonify({'success': False, 'message': 'Folder not found'})
        
        data = request.get_json()
        name = data.get('name', '').strip()
        description = data.get('description', '').strip()
        
        if not name:
            return jsonify({'success': False, 'message': 'Folder name is required'})
        
        folder.name = name
        folder.description = description
        
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Folder updated successfully', 'folder': folder.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

@main_bp.route('/api/study/folders/<int:folder_id>', methods=['DELETE'])
@role_required('lpaf')
def delete_study_folder(folder_id):
    """Delete a study folder"""
    try:
        folder = StudyFolder.query.get(folder_id)
        if not folder:
            return jsonify({'success': False, 'message': 'Folder not found'})
        
        # Check if folder has subfolders or videos
        if folder.subfolders:
            return jsonify({'success': False, 'message': 'Cannot delete folder that contains subfolders. Delete subfolders first.'})
        
        if folder.videos:
            return jsonify({'success': False, 'message': f'Cannot delete folder that contains {len(folder.videos)} video(s). Delete or move videos first.'})
        
        db.session.delete(folder)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Folder deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

# Video Management
@main_bp.route('/api/study/videos', methods=['GET'])
@role_required('lpaf')
def get_study_videos():
    """Get all study videos with optional folder filter"""
    try:
        folder_id = request.args.get('folder_id')
        
        if folder_id == 'null' or folder_id == 'root':
            # Get videos in root (no folder)
            videos = StudyVideo.query.filter_by(folder_id=None).all()
        elif folder_id:
            # Get videos in specific folder
            videos = StudyVideo.query.filter_by(folder_id=int(folder_id)).all()
        else:
            # Get all videos
            videos = StudyVideo.query.all()
        
        videos_data = [video.to_dict() for video in videos]
        return jsonify({'success': True, 'videos': videos_data})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@main_bp.route('/api/study/videos', methods=['POST'])
@role_required('lpaf')
def upload_study_video():
    """Upload a new study video"""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'message': 'No file selected'})
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'message': 'No file selected'})
        
        if not allowed_video_file(file.filename):
            return jsonify({'success': False, 'message': f'File type not allowed. Allowed types: {", ".join(ALLOWED_VIDEO_EXTENSIONS)}'})
        
        # Get form data
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        folder_id = request.form.get('folder_id')
        
        if not title:
            return jsonify({'success': False, 'message': 'Video title is required'})
        
        # Validate folder if provided
        if folder_id and folder_id != 'null':
            folder_id = int(folder_id)
            folder = StudyFolder.query.get(folder_id)
            if not folder:
                return jsonify({'success': False, 'message': 'Folder not found'})
        else:
            folder_id = None
        
        # Check file size
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)
        
        if file_size > MAX_VIDEO_SIZE:
            return jsonify({'success': False, 'message': 'File size exceeds 500MB limit'})
        
        # Generate unique filename
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4()}_{filename}"
        file_path = os.path.join(STUDY_VIDEO_FOLDER, unique_filename)
        
        # Ensure upload directories exist
        os.makedirs(STUDY_VIDEO_FOLDER, exist_ok=True)
        os.makedirs(STUDY_THUMBNAIL_FOLDER, exist_ok=True)
        
        # Save file
        file.save(file_path)
        
        # Generate thumbnail
        thumbnail_filename = f"thumb_{unique_filename.rsplit('.', 1)[0]}.jpg"
        thumbnail_path = os.path.join(STUDY_THUMBNAIL_FOLDER, thumbnail_filename)
        thumbnail_generated = generate_video_thumbnail(file_path, thumbnail_path)
        
        # Store relative path for database
        db_thumbnail_path = f"/static/uploads/study_videos/thumbnails/{thumbnail_filename}" if thumbnail_generated else None
        
        # Get MIME type - prefer file extension detection for better compatibility
        mime_type = file.content_type
        
        # If content_type is generic or missing, detect from file extension
        if not mime_type or mime_type in ['application/octet-stream', 'binary/octet-stream']:
            # Detect MIME type from filename
            detected_mime, _ = mimetypes.guess_type(filename)
            if detected_mime:
                mime_type = detected_mime
            else:
                # Manual mapping for common video formats
                extension = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
                mime_mapping = {
                    'mp4': 'video/mp4',
                    'webm': 'video/webm',
                    'ogg': 'video/ogg',
                    'avi': 'video/x-msvideo',
                    'mov': 'video/quicktime',
                    'wmv': 'video/x-ms-wmv',
                    'flv': 'video/x-flv',
                    'mkv': 'video/x-matroska',
                    'mpeg': 'video/mpeg',
                    'mpg': 'video/mpeg',
                    '3gp': 'video/3gpp'
                }
                mime_type = mime_mapping.get(extension, 'video/mp4')
        
        # Save to database
        video = StudyVideo(
            title=title,
            description=description,
            filename=unique_filename,
            original_name=filename,
            file_path=file_path,
            file_size=file_size,
            mime_type=mime_type,
            thumbnail_path=db_thumbnail_path,
            folder_id=folder_id
        )
        
        db.session.add(video)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Video uploaded successfully', 'video': video.to_dict()})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

@main_bp.route('/api/study/videos/<int:video_id>', methods=['PUT'])
@role_required('lpaf')
def update_study_video(video_id):
    """Update a study video metadata"""
    try:
        video = StudyVideo.query.get(video_id)
        if not video:
            return jsonify({'success': False, 'message': 'Video not found'})
        
        data = request.get_json()
        title = data.get('title', '').strip()
        description = data.get('description', '').strip()
        
        if not title:
            return jsonify({'success': False, 'message': 'Video title is required'})
        
        video.title = title
        video.description = description
        
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Video updated successfully', 'video': video.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

@main_bp.route('/api/study/videos/<int:video_id>', methods=['DELETE'])
@role_required('lpaf')
def delete_study_video(video_id):
    """Delete a study video"""
    try:
        video = StudyVideo.query.get(video_id)
        if not video:
            return jsonify({'success': False, 'message': 'Video not found'})
        
        # Delete file from filesystem
        if os.path.exists(video.file_path):
            os.remove(video.file_path)
        
        # Delete thumbnail if it exists
        if video.thumbnail_path and os.path.exists(video.thumbnail_path):
            os.remove(video.thumbnail_path)
        
        # Delete from database
        db.session.delete(video)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Video deleted successfully'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

@main_bp.route('/uploads/study_videos/<filename>')
def uploaded_study_video(filename):
    """Serve uploaded video files with proper MIME type"""
    # Get the video from database to retrieve stored MIME type
    video = StudyVideo.query.filter_by(filename=filename).first()
    
    # Use absolute path from Flask's static folder
    upload_dir = os.path.join(current_app.root_path, 'static', 'uploads', 'study_videos')
    response = send_from_directory(upload_dir, filename)
    
    # Set proper MIME type if we have it in database
    if video and video.mime_type:
        response.headers['Content-Type'] = video.mime_type
    else:
        # Fallback to detecting from filename
        mime_type, _ = mimetypes.guess_type(filename)
        if mime_type:
            response.headers['Content-Type'] = mime_type
    
    # Enable range requests for video seeking
    response.headers['Accept-Ranges'] = 'bytes'
    
    return response

# Finance Transaction API Routes
@main_bp.route('/api/finance/transactions', methods=['GET'])
@role_required(['tvet', 'lpaf'])
def get_finance_transactions():
    """Get finance transactions with optional filters"""
    try:
        department = session.get('selected_role', '').upper()
        transaction_type = request.args.get('transaction_type')  # 'income' or 'expenses'
        search = request.args.get('search', '').strip()
        
        query = FinanceTransaction.query.filter_by(department=department)
        
        if transaction_type:
            query = query.filter_by(transaction_type=transaction_type)
        
        if search:
            search_term = f'%{search}%'
            query = query.filter(
                db.or_(
                    FinanceTransaction.source.ilike(search_term),
                    FinanceTransaction.description.ilike(search_term),
                    FinanceTransaction.receipt.ilike(search_term)
                )
            )
        
        transactions = query.order_by(desc(FinanceTransaction.date)).all()
        transactions_data = [t.to_dict() for t in transactions]
        
        # Calculate totals from ALL transactions (not just filtered ones)
        all_transactions = FinanceTransaction.query.filter_by(department=department).all()
        total_income = sum(float(t.amount) for t in all_transactions if t.transaction_type == 'income')
        total_expenses = sum(float(t.amount) for t in all_transactions if t.transaction_type == 'expenses')
        net_income = total_income - total_expenses
        
        return jsonify({
            'success': True,
            'transactions': transactions_data,
            'total_income': total_income,
            'total_expenses': total_expenses,
            'net_income': net_income
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@main_bp.route('/api/finance/transactions', methods=['POST'])
@role_required(['tvet', 'lpaf'])
def create_finance_transaction():
    """Create a new finance transaction"""
    try:
        department = session.get('selected_role', '').upper()

        # Check if it's a FormData request (multipart/form-data)
        if request.content_type and 'multipart/form-data' in request.content_type:
            # Handle FormData with file upload
            date_str = request.form.get('date', '').strip()
            transaction_type = request.form.get('transaction_type', '').strip()
            source = request.form.get('source', '').strip()
            amount = request.form.get('amount')
            description = request.form.get('description', '').strip()
            units = request.form.get('units', 1)
            receipt_file = request.files.get('receipt')

            if not all([date_str, transaction_type, source, amount, description]):
                return jsonify({'success': False, 'message': 'Date, type, source, items, and amount are required'})

            if transaction_type not in ['income', 'expenses']:
                return jsonify({'success': False, 'message': 'Invalid transaction type'})

            # Parse date
            try:
                transaction_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'success': False, 'message': 'Invalid date format. Use YYYY-MM-DD'})

            # Validate amount
            try:
                amount = float(amount)
                if amount <= 0:
                    raise ValueError()
            except (ValueError, TypeError):
                return jsonify({'success': False, 'message': 'Amount must be a positive number'})

            # Validate units
            try:
                units = int(units)
                if units < 0:
                    raise ValueError()
            except (ValueError, TypeError):
                return jsonify({'success': False, 'message': 'Units must be a non-negative integer'})

            receipt_path = None
            if receipt_file and receipt_file.filename:
                filename = secure_filename(f"{uuid.uuid4()}_{receipt_file.filename}")
                upload_dir = os.path.join(current_app.root_path, 'static', 'uploads', 'finance_receipts')
                os.makedirs(upload_dir, exist_ok=True)
                receipt_path = os.path.join('static', 'uploads', 'finance_receipts', filename)
                receipt_file.save(os.path.join(upload_dir, filename))

            transaction = FinanceTransaction(
                date=transaction_date,
                transaction_type=transaction_type,
                source=source,
                description=description,
                units=units,
                amount=amount,
                receipt=receipt_path,
                department=department
            )

            db.session.add(transaction)
            db.session.commit()

            return jsonify({'success': True, 'message': 'Transaction created successfully', 'transaction': transaction.to_dict()})
        else:
            # Handle JSON request (without file upload)
            data = request.get_json()

            # Validate required fields
            date_str = data.get('date', '').strip()
            transaction_type = data.get('transaction_type', '').strip()
            source = data.get('source', '').strip()
            amount = data.get('amount')
            description = data.get('description', '').strip()
            units = data.get('units', 1)
            receipt = data.get('receipt', '').strip()

            if not all([date_str, transaction_type, source, amount, description]):
                return jsonify({'success': False, 'message': 'Date, type, source, items, and amount are required'})

            if transaction_type not in ['income', 'expenses']:
                return jsonify({'success': False, 'message': 'Invalid transaction type'})

            # Parse date
            try:
                transaction_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'success': False, 'message': 'Invalid date format. Use YYYY-MM-DD'})

            # Validate amount
            try:
                amount = float(amount)
                if amount <= 0:
                    raise ValueError()
            except (ValueError, TypeError):
                return jsonify({'success': False, 'message': 'Amount must be a positive number'})

            # Validate units
            try:
                units = int(units)
                if units < 0:
                    raise ValueError()
            except (ValueError, TypeError):
                return jsonify({'success': False, 'message': 'Units must be a non-negative integer'})

            transaction = FinanceTransaction(
                date=transaction_date,
                transaction_type=transaction_type,
                source=source,
                description=description,
                units=units,
                amount=amount,
                receipt=receipt,
                department=department
            )

            db.session.add(transaction)
            db.session.commit()

            return jsonify({'success': True, 'message': 'Transaction created successfully', 'transaction': transaction.to_dict()})

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'An error occurred: {str(e)}'})

@main_bp.route('/api/finance/transactions/<int:transaction_id>', methods=['PUT'])
@role_required(['tvet', 'lpaf'])
def update_finance_transaction(transaction_id):
    """Update a finance transaction"""
    try:
        department = session.get('selected_role', '').upper()
        transaction = FinanceTransaction.query.filter_by(id=transaction_id, department=department).first()
        if not transaction:
            return jsonify({'success': False, 'message': 'Transaction not found'})

        # Check if it's a FormData request (multipart/form-data)
        if request.content_type and 'multipart/form-data' in request.content_type:
            # Handle FormData with file upload
            date_str = request.form.get('date', '').strip()
            transaction_type = request.form.get('transaction_type', '').strip()
            source = request.form.get('source', '').strip()
            amount = request.form.get('amount')
            description = request.form.get('description', '').strip()
            units = request.form.get('units', 1)
            receipt_file = request.files.get('receipt')

            if not all([date_str, transaction_type, source, amount, description]):
                return jsonify({'success': False, 'message': 'Date, type, source, items, and amount are required'})

            if transaction_type not in ['income', 'expenses']:
                return jsonify({'success': False, 'message': 'Invalid transaction type'})

            try:
                transaction_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'success': False, 'message': 'Invalid date format. Use YYYY-MM-DD'})

            try:
                amount = float(amount)
                if amount <= 0:
                    raise ValueError()
            except (ValueError, TypeError):
                return jsonify({'success': False, 'message': 'Amount must be a positive number'})

            try:
                units = int(units)
                if units < 0:
                    raise ValueError()
            except (ValueError, TypeError):
                return jsonify({'success': False, 'message': 'Units must be a non-negative integer'})

            if receipt_file and receipt_file.filename:
                filename = secure_filename(f"{uuid.uuid4()}_{receipt_file.filename}")
                upload_dir = os.path.join(current_app.root_path, 'static', 'uploads', 'finance_receipts')
                os.makedirs(upload_dir, exist_ok=True)
                receipt_path = os.path.join('static', 'uploads', 'finance_receipts', filename)
                receipt_file.save(os.path.join(upload_dir, filename))

                # Delete old receipt file if exists
                if transaction.receipt and os.path.exists(transaction.receipt):
                    try:
                        os.remove(transaction.receipt)
                    except:
                        pass

                transaction.receipt = receipt_path

            transaction.date = transaction_date
            transaction.transaction_type = transaction_type
            transaction.source = source
            transaction.description = description
            transaction.units = units
            transaction.amount = amount

            db.session.commit()

            return jsonify({'success': True, 'message': 'Transaction updated successfully', 'transaction': transaction.to_dict()})
        else:
            # Handle JSON request (without file upload)
            data = request.get_json()

            date_str = data.get('date', '').strip()
            transaction_type = data.get('transaction_type', '').strip()
            source = data.get('source', '').strip()
            amount = data.get('amount')
            description = data.get('description', '').strip()
            units = data.get('units', 1)
            receipt = data.get('receipt', '').strip()

            if not all([date_str, transaction_type, source, amount, description]):
                return jsonify({'success': False, 'message': 'Date, type, source, items, and amount are required'})

            if transaction_type not in ['income', 'expenses']:
                return jsonify({'success': False, 'message': 'Invalid transaction type'})

            try:
                transaction_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'success': False, 'message': 'Invalid date format. Use YYYY-MM-DD'})

            try:
                amount = float(amount)
                if amount <= 0:
                    raise ValueError()
            except (ValueError, TypeError):
                return jsonify({'success': False, 'message': 'Amount must be a positive number'})

            try:
                units = int(units)
                if units < 0:
                    raise ValueError()
            except (ValueError, TypeError):
                return jsonify({'success': False, 'message': 'Units must be a non-negative integer'})

            transaction.date = transaction_date
            transaction.transaction_type = transaction_type
            transaction.source = source
            transaction.description = description
            transaction.units = units
            transaction.amount = amount
            transaction.receipt = receipt

            db.session.commit()

            return jsonify({'success': True, 'message': 'Transaction updated successfully', 'transaction': transaction.to_dict()})

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'An error occurred: {str(e)}'})

@main_bp.route('/api/finance/transactions/<int:transaction_id>', methods=['DELETE'])
@role_required(['tvet', 'lpaf'])
def delete_finance_transaction(transaction_id):
    """Delete a finance transaction"""
    try:
        department = session.get('selected_role', '').upper()
        
        transaction = FinanceTransaction.query.filter_by(id=transaction_id, department=department).first()
        if not transaction:
            return jsonify({'success': False, 'message': 'Transaction not found'})
        
        db.session.delete(transaction)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Transaction deleted successfully'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'An error occurred: {str(e)}'})











