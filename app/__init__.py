"""Application Factory."""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_migrate import Migrate

db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()
migrate = Migrate()


def create_app(config_name='development'):
    """Create and configure the application."""
    app = Flask(__name__)
    
    from config import config_by_name
    app.config.from_object(config_by_name[config_name])
    
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    migrate.init_app(app, db)
    
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    
    @login_manager.user_loader
    def load_user(user_id):
        from app.models.admin import Admin
        return Admin.query.get(int(user_id))
    
    from app.routes.main import main_bp
    from app.routes.auth import auth_bp
    from app.routes.admin import admin_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    
    with app.app_context():
        # Import all models BEFORE creating tables
        from app.models.admin import Admin
        from app.models.team import Team
        from app.models.participant import Participant
        from app.models.game import Game
        from app.models.score import Score
        
        # Now create tables
        db.create_all()
        initialize_admins(app)
    
    return app


def initialize_admins(app):
    """Initialize admin accounts."""
    from app.models.admin import Admin
    
    admin = Admin.query.filter_by(username=app.config['ADMIN_USERNAME']).first()
    if not admin:
        admin = Admin(username=app.config['ADMIN_USERNAME'])
        admin.setPassword(app.config['ADMIN_DEFAULT_PASSWORD'])
        db.session.add(admin)
        db.session.commit()
    
    dev_admin = Admin.query.filter_by(username=app.config['DEVADMIN_USERNAME']).first()
    if not dev_admin:
        dev_admin = Admin(username=app.config['DEVADMIN_USERNAME'])
        dev_admin.setPassword(app.config['DEVADMIN_PASSWORD'])
        db.session.add(dev_admin)
        db.session.commit()
