from flask import Flask
from web.models import db, User, ActivityLog
import logging

def create_app():
    web = Flask(__name__)

    # Configuration
    web.config.from_object('config.Config')
    
    # Initialize extensions
    db.init_app(web)

    # Import and register blueprints
    from web.routes.main import main_bp
    from web.routes.auth import auth_bp
    web.register_blueprint(main_bp)
    web.register_blueprint(auth_bp, url_prefix='/auth')
    
    # Create tables and default admin user
    with web.app_context():
        db.create_all()
        logging.info("Database tables created.")
        
        try:
            # Create default admin user if it doesn't exist
            admin_user = User.query.filter_by(username='admin').first()
            if not admin_user:
                admin_user = User(name='System Administrator', username='admin', user_type='admin', position='System Administrator')
                admin_user.set_password('admin')
                db.session.add(admin_user)
                db.session.commit()
            logging.info("Default admin user created.")
        except Exception as e:
            db.session.rollback()
            logging.error(f"Failed to create default admin user: {e}")

    return web
