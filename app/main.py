from flask import Flask, g
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bootstrap import Bootstrap
from flask_login import LoginManager, current_user
from config import Config
import os
from extensions import db, migrate, login_manager, bootstrap



# Create and configure the Flask app
app = Flask(__name__)
app.config.from_object(Config)
app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'static/uploads')

# Initialize extensions with app
db.init_app(app)
migrate.init_app(app, db)
bootstrap.init_app(app)
login_manager.init_app(app)
login_manager.login_view = 'main.login'

# Static files configuration
app.static_folder = 'static'
app.static_url_path = '/static'

# Before request handler
@app.before_request
def before_request():
    g.current_user = current_user

# Import and register blueprints within the app context
with app.app_context():
    # from models import models
    from routes import main
    app.register_blueprint(main)


    # Create all database tables
    db.create_all()

# To run the app directly
if __name__ == '__main__':
    app.run(debug=True)
