Hospital Management System (HMS)

🏥 Project Overview

This is a simple web-based Hospital Management System (HMS) built using the Flask framework. The application manages user authentication across three distinct roles (Admin, Doctor, Patient) and handles core functionalities like doctor registration, patient registration, and appointment scheduling.

The project uses SQLAlchemy for database management, ensuring a robust and well-structured data layer.

✨ Key Features

Role-Based Authentication: Secure login and access control for Admin, Doctors, and Patients.

Admin Dashboard:

Add and manage new Doctor profiles.

View all registered Patients and Appointments.

Secure Deletion: Deleting a Doctor correctly handles cascade deletion of the associated User account and all linked Appointment records.

Doctor Dashboard:

View all scheduled appointments.

Update appointment status (Completed, Cancelled).

Record diagnosis and prescriptions for completed appointments.

Patient Dashboard:

Register and create a Patient profile.

Book new appointments with available Doctors.

View history of all booked appointments.

Database: Persistent storage using SQLite and SQLAlchemy.

🚀 Technologies Used

Technology

Purpose

Python

Primary development language.

Flask

Core web framework for routing and backend logic.

Flask-SQLAlchemy

ORM (Object-Relational Mapper) for database interaction (SQLite).

Flask-Login

Manages user sessions and authentication.

Werkzeug

Used for secure password hashing.

Jinja2

Templating engine for dynamic HTML rendering.

⚙️ Setup and Installation

Follow these steps to set up and run the project locally.

1. Prerequisites

You must have Python installed on your system.

2. Clone the Repository (Simulated)

Assuming your project files are in a directory named hms_app.

cd D:\hms_app


3. Create a Virtual Environment (Recommended)

python -m venv venv
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate


4. Install Dependencies

Install all necessary libraries using pip:

pip install Flask Flask-SQLAlchemy Flask-Login Werkzeug


5. Running the Application

Ensure you have the following two files in your project root:

app.py

models.py (with the latest, corrected SQLAlchemy relationships)

Run the main application file:

python app.py


The application will start the Flask development server, and the database file (hospital.db) will be created automatically upon the first run, along with the default Admin user.

🔑 Default Credentials

The system initializes a default administrative user:

Role

Username

Password

Admin

admin

admin123

You can register new Patient accounts via the /register route or add Doctor accounts through the Admin Dashboard.
