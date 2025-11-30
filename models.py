from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

# User Model (Handles Auth for Admin, Doctor, Patient)
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=True)
    password = db.Column(db.String(150), nullable=True)
    role = db.Column(db.String(50), nullable=True)
    
    # Relationships
    doctor_profile = db.relationship('Doctor', backref='user', uselist=False, cascade="all, delete-orphan")
    patient_profile = db.relationship('Patient', backref='user', uselist=False, cascade="all, delete-orphan")

class Department(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

class Doctor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    specialization = db.Column(db.String(100), nullable=False)
    availability = db.Column(db.String(200), default="Mon-Fri, 9:00 AM - 5:00 PM")

    appointments = db.relationship('Appointment', backref='doctor', cascade="all, delete-orphan")

class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer)
    contact = db.Column(db.String(50))

    appointments = db.relationship('Appointment', backref='patient', cascade="all, delete-orphan")

class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'), nullable=False)
    date_time = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(50), default='Booked')  # Booked, Completed, Cancelled
    diagnosis = db.Column(db.Text, nullable=True)
    prescription = db.Column(db.Text, nullable=True)