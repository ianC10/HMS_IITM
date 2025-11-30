from flask import Flask, render_template, redirect, url_for, request, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from models import db, User, Doctor, Patient, Appointment, Department
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hospital.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- Database Initialization (Runs once) ---
def init_db():
    with app.app_context():
        # Ensure tables are created with the latest model definitions
        db.create_all()
        
        # Create Admin if not exists
        if not User.query.filter_by(role='admin').first():
            admin = User(username='admin', password=generate_password_hash('admin123'), role='admin')
            db.session.add(admin)
            
            # Add sample departments
            for dept in ['Cardiology', 'Neurology', 'Orthopedics', 'General']:
                db.session.add(Department(name=dept))
            
            db.session.commit()
            print("Database initialized with Admin user and departments.")

# --- Authentication Routes ---
@app.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.role == 'admin': return redirect(url_for('admin_dashboard'))
        elif current_user.role == 'doctor': return redirect(url_for('doctor_dashboard'))
        else: return redirect(url_for('patient_dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('index'))
        flash('Invalid credentials')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        name = request.form.get('name')
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return redirect(url_for('register'))
            
        hashed_pw = generate_password_hash(password)
        new_user = User(username=username, password=hashed_pw, role='patient')
        db.session.add(new_user)
        db.session.commit()
        
        # Create Patient Profile
        new_patient = Patient(user_id=new_user.id, name=name)
        db.session.add(new_patient)
        db.session.commit()
        
        login_user(new_user)
        return redirect(url_for('patient_dashboard'))
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# --- Admin Routes ---
@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin_dashboard():
    if current_user.role != 'admin': return redirect(url_for('index'))
    
    doctors = Doctor.query.all()
    patients = Patient.query.all()
    appointments = Appointment.query.all()
    departments = Department.query.all()
    
    # Add Doctor Logic
    if request.method == 'POST':
        if 'add_doctor' in request.form:
            name = request.form.get('name')
            username = request.form.get('username')
            password = request.form.get('password')
            specialization = request.form.get('specialization')
            
            if not User.query.filter_by(username=username).first():
                user = User(username=username, password=generate_password_hash(password), role='doctor')
                db.session.add(user)
                db.session.commit()
                
                doc = Doctor(user_id=user.id, name=name, specialization=specialization)
                db.session.add(doc)
                db.session.commit()
                flash('Doctor added successfully')
            else:
                flash('Username exists')
                
    return render_template('admin_dashboard.html', doctors=doctors, patients=patients, appointments=appointments, departments=departments)

@app.route('/delete_doctor/<int:id>')
@login_required
def delete_doctor(id):
    if current_user.role != 'admin': 
        flash('Access denied.')
        return redirect(url_for('index'))
    
    doc = Doctor.query.get(id)
    
    if doc:
        # Deleting the User will trigger cascade deletion for Doctor and all related Appointments.
        user = User.query.get(doc.user_id)
        if user:
            db.session.delete(user)
            db.session.commit()
            flash('Doctor and all related appointments deleted successfully.', 'success')
        else:
            flash('Error: Associated user not found.', 'error')
    else:
        flash('Doctor not found.', 'error')
        
    return redirect(url_for('admin_dashboard'))

# --- Doctor Routes ---
@app.route('/doctor', methods=['GET', 'POST'])
@login_required
def doctor_dashboard():
    if current_user.role != 'doctor': return redirect(url_for('index'))
    doctor = Doctor.query.filter_by(user_id=current_user.id).first()
    appointments = Appointment.query.filter_by(doctor_id=doctor.id).order_by(Appointment.date_time).all()
    
    if request.method == 'POST':
        appt_id = request.form.get('appt_id')
        status = request.form.get('status') # Completed or Cancelled
        diagnosis = request.form.get('diagnosis')
        prescription = request.form.get('prescription')
        
        appt = Appointment.query.get(appt_id)
        if appt:
            appt.status = status
            if diagnosis: appt.diagnosis = diagnosis
            if prescription: appt.prescription = prescription
            db.session.commit()
            
    return render_template('doctor_dashboard.html', doctor=doctor, appointments=appointments)

# --- Patient Routes ---
@app.route('/patient', methods=['GET', 'POST'])
@login_required
def patient_dashboard():
    if current_user.role != 'patient': return redirect(url_for('index'))
    patient = Patient.query.filter_by(user_id=current_user.id).first()
    my_appointments = Appointment.query.filter_by(patient_id=patient.id).all()
    doctors = Doctor.query.all()
    
    if request.method == 'POST':
        doc_id = request.form.get('doctor_id')
        date_str = request.form.get('date')
        time_str = request.form.get('time')
        
        try:
            appt_dt = datetime.strptime(f"{date_str} {time_str}", '%Y-%m-%d %H:%M')
            
            # Prevent double booking
            existing = Appointment.query.filter_by(doctor_id=doc_id, date_time=appt_dt, status='Booked').first()
            if existing:
                flash('Doctor is already booked at this time.')
            else:
                new_appt = Appointment(patient_id=patient.id, doctor_id=doc_id, date_time=appt_dt)
                db.session.add(new_appt)
                db.session.commit()
                flash('Appointment booked successfully')
        except ValueError:
            flash('Invalid date/time format')

    return render_template('patient_dashboard.html', patient=patient, appointments=my_appointments, doctors=doctors)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)