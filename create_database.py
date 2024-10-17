from app import create_app, db  # Replace 'yourapp' with your actual app's package name

# Create the app
app = create_app()

# Use the app context to access the database
with app.app_context():
    db.create_all()
