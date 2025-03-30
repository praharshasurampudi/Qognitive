# Qognitive

## Getting Started
To run CollabSphere locally on your machine, follow these steps:

1. Create a virtual environment to isolate project dependencies:
   ```
   python -m venv venv
   ```
   
2. Activate the virtual environment (on Windows):
   ```
   venv/Scripts/activate
   ```
   Activate the virtual environment (on IOS)
   ```
   source venv/bin/activate
   ```

4. Install the project dependencies using pip:
   ```
   pip install -r requirement.txt
   ```
5. Update environemt variables (.env file):
    ```
    FLASK_DEBUG=true
    FLASK_APP=app.py
    SECRET_KEY=your_secret_key_here
    SQL_ALCHEMY_DATABASE_URI=sqlite:///db_name.sqlite3
    SQLALCHEMY_TRACK_MODIFICATIONS=true
    ```

6. Start the Flask development server:
   ```
   flask run
   ```
7. Access the CollabSphere web application by opening a web browser and navigating to `http://localhost:5000`.

