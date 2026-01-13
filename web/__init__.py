from flask import Flask
from web.models import db, User, ActivityLog
import logging
from sqlalchemy import inspect
from sqlalchemy import text

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
        # Ensure finance_transactions has required columns (migrations for first-deploy)
        try:
            inspector = inspect(db.engine)
            if 'finance_transactions' in inspector.get_table_names():
                existing_cols = [c['name'] for c in inspector.get_columns('finance_transactions')]
                alter_queries = []
                if 'units' not in existing_cols:
                    alter_queries.append("ALTER TABLE finance_transactions ADD COLUMN units INTEGER NOT NULL DEFAULT 1;")
                if 'receipt' not in existing_cols:
                    alter_queries.append("ALTER TABLE finance_transactions ADD COLUMN receipt TEXT;")

                if alter_queries:
                    for q in alter_queries:
                        try:
                            db.session.execute(text(q))
                        except Exception as e:
                            logging.error(f"Failed to run alter query '{q}': {e}")
                    db.session.commit()
                    logging.info('Applied missing finance_transactions column fixes.')
        except Exception as e:
            logging.error(f'Error while ensuring finance_transactions columns: {e}')
        
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
