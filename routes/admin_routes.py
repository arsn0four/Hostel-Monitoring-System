from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from extensions import db, bcrypt
from models.db_models import User, Student, Warden, Hostel, Room, Attendance
import uuid
from datetime import datetime

admin = Blueprint('admin', __name__, url_prefix='/admin')

@admin.route('/dashboard')
@login_required
def dashboard():
    if current_user.role != 'Admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('auth.login'))
    return render_template('dashboard_admin.html')

@admin.route('/users')
@login_required
def manage_users():
    if current_user.role != 'Admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('auth.login'))
    
    users = User.query.all()
    # To pass name and contact, we'll build a dictionary or fetch inline in template
    return render_template('manage_users.html', users=users)

@admin.route('/users/add', methods=['GET', 'POST'])
@login_required
def add_user():
    if current_user.role != 'Admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        name = request.form.get('name')
        role = request.form.get('role')
        contact_or_dept = request.form.get('contact') # using same field for phone or department

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists.', 'danger')
        else:
            hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')
            new_user = User(
                username=username,
                password_hash=hashed_pw,
                role=role
            )
            db.session.add(new_user)
            db.session.flush()
            
            if role == 'Student':
                student_count = Student.query.count()
                new_roll = f"RA{student_count + 101}"
                new_student = Student(
                    user_id=new_user.id,
                    roll_no=new_roll,
                    name=name,
                    department=contact_or_dept
                )
                db.session.add(new_student)
            elif role == 'Warden':
                new_warden = Warden(
                    user_id=new_user.id,
                    name=name,
                    phone=contact_or_dept
                )
                db.session.add(new_warden)
                
            db.session.commit()
            flash(f'{role} account created successfully!', 'success')
            return redirect(url_for('admin.manage_users'))

    return render_template('add_user.html')

@admin.route('/users/delete/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    if current_user.role != 'Admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('auth.login'))
        
    user = User.query.get_or_404(user_id)
    if user.username == 'admin':
        flash('Cannot delete the default admin account.', 'danger')
    else:
        db.session.delete(user)
        db.session.commit()
        flash('User deleted successfully.', 'success')
        
    return redirect(url_for('admin.manage_users'))

@admin.route('/hostels')
@login_required
def manage_hostels():
    if current_user.role != 'Admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('auth.login'))
        
    hostels = Hostel.query.all()
    wardens = Warden.query.all()
    return render_template('manage_hostels.html', hostels=hostels, wardens=wardens)

@admin.route('/hostels/add', methods=['GET', 'POST'])
@login_required
def add_hostel():
    if current_user.role != 'Admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        hostel_name = request.form.get('hostel_name')
        location = request.form.get('location')
        
        new_hostel = Hostel(hostel_name=hostel_name, location=location)
        db.session.add(new_hostel)
        db.session.commit()
        flash(f'Hostel {hostel_name} added successfully.', 'success')
        return redirect(url_for('admin.manage_hostels'))
        
    return render_template('add_hostel.html')

@admin.route('/hostels/assign_warden/<int:hostel_id>', methods=['POST'])
@login_required
def assign_warden(hostel_id):
    if current_user.role != 'Admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('auth.login'))
        
    warden_id = request.form.get('warden_id', type=int)
    if warden_id:
        warden = Warden.query.get(warden_id)
        if warden:
            warden.hostel_id = hostel_id
            db.session.commit()
            flash('Warden assigned successfully.', 'success')
    return redirect(url_for('admin.manage_hostels'))

@admin.route('/reports')
@login_required
def reports():
    if current_user.role != 'Admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('auth.login'))
        
    rooms = Room.query.all()
    total_capacity = sum(r.capacity for r in rooms)
    total_occupied = sum(r.current_occupancy for r in rooms)
    occupancy_percentage = (total_occupied / total_capacity * 100) if total_capacity > 0 else 0
    
    today = datetime.utcnow().date()
    total_students = Student.query.count()
    today_records = Attendance.query.filter_by(date=today).all()
    
    present_count = sum(1 for r in today_records if r.status in ['Present', 'Late'])
    absent_count = total_students - present_count
    
    return render_template('reports.html',
                           total_capacity=total_capacity,
                           total_occupied=total_occupied,
                           occupancy_percentage=occupancy_percentage,
                           total_students=total_students,
                           present_count=present_count,
                           absent_count=absent_count,
                           today_records=today_records,
                           today=today)
