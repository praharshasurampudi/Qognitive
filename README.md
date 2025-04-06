# Qognitive

Qognitive is a Flask-based quiz master project that helps to organize learning and testing. It allows Administrators to handle study material, prepare and schedule quizzes, and monitor user activity, while Students can take quizzes and monitor their progress.

### [Demo Video](https://drive.google.com/file/d/1dkpa2FuTD2Ad0M_NgaxBD5-c92_sjBLd/view?usp=sharing)

### Features

- [x] 🔧 Admin Panel 
- [x] 🧠 Smart Quiz System
- [x] 📊 Student Dashboard
- [x] 💻 Tech Stack & Extensibility
      
## Getting Started
To run Qognitive locally on your machine, follow these steps:

## 1. Create a virtual environment to isolate project dependencies:
   ```
   python -m venv venv
   ```
   
## 2. Activate the virtual environment (on Windows):
   ```
   venv/Scripts/activate
   ```
 ## 3. Activate the virtual environment (on IOS)
   ```
   source venv/bin/activate
   ```

## 4. Install the project dependencies using pip:
   ```
   pip install -r requirement.txt
   ```
## 5. Update environemt variables (.env file):
    ```
    FLASK_DEBUG=true
    FLASK_APP=app.py
    SECRET_KEY=your_secret_key_here
    SQL_ALCHEMY_DATABASE_URI=sqlite:///db_name.sqlite3
    SQLALCHEMY_TRACK_MODIFICATIONS=true
    ```

## 6. Start the Flask development server:
   ```
   flask run
   ```
### 7. Access the Qognitive web application by opening a web browser and navigating to `http://localhost:5000`.


## 📝 License © [Praharsha Surampudi](https://www.linkedin.com/in/praharsha-surampudi/)
