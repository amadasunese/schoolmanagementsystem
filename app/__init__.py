from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bootstrap import Bootstrap
from config import Config
from flask_login import LoginManager
from flask import g
from flask_login import current_user



db = SQLAlchemy()
migrate = Migrate()
bootstrap = Bootstrap()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    

    @app.before_request
    def before_request():
        g.current_user = current_user

    
    db.init_app(app)
    migrate.init_app(app, db)
    bootstrap.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'main.login'

    

    # static files
    app.static_folder ='static'
    app.static_url_path = '/static'




    with app.app_context():
        from . import models
        from .routes import main
        app.register_blueprint(main)

        db.create_all()
    
    return app


