from app import create_app, db
from app.models import User

def create_admin():
    # Initialize the app context
    app = create_app()
    with app.app_context():
        # Check if admin user already exists
        existing_admin = User.query.filter_by(username='admin').first()
        if existing_admin:
            print("Admin user already exists.")
            return

        # Create the admin user
        admin = User(username='admin')
        admin.set_password('1234567')  # Change 'admin_password' to a secure password
        admin.is_admin = True
        
        # Add to the session and commit
        db.session.add(admin)
        db.session.commit()
        
        print("Admin user created successfully.")

if __name__ == "__main__":
    create_admin()
