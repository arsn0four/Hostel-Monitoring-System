from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from datetime import datetime
from extensions import db
from models.db_models import Student, Attendance, Allocation
from utils.qr_generator import generate_qr_code

student = Blueprint('student', __name__, url_prefix='/student')

@student.route('/dashboard')
@login_required
def dashboard():
    if current_user.role != 'Student':
        flash('Access denied.', 'danger')
        return redirect(url_for('auth.login'))
        
    student_profile = Student.query.filter_by(user_id=current_user.id).first()
    if not student_profile:
        flash('Student profile not found. Please contact Admin.', 'danger')
        return redirect(url_for('auth.login'))
        
    # Generate QR if it doesn't exist
    if not student_profile.qrcode:
        student_profile.qrcode = generate_qr_code(student_profile.roll_no)
        db.session.commit()
        
    # Get recent attendance
    recent_attendance = Attendance.query.filter_by(student_id=student_profile.student_id).order_by(Attendance.date.desc()).limit(5).all()
    
    # Check if checked in today
    today = datetime.utcnow().date()
    today_record = Attendance.query.filter_by(student_id=student_profile.student_id, date=today).first()
    
    # Get current room allocation
    active_allocation = Allocation.query.filter_by(student_id=student_profile.student_id, status='Active').first()
    
    return render_template('dashboard_student.html', 
                         student=student_profile, 
                         recent_attendance=recent_attendance,
                         today_record=today_record,
                         allocation=active_allocation)

@student.route('/checkin_scanner')
@login_required
def checkin_scanner():
    """Renders the webcam scanner page for checking in."""
    return render_template('attendance_scanner.html')

@student.route('/api/mark_attendance', methods=['POST'])
def mark_attendance():
    """API endpoint to receive scanned QR code data."""
    data = request.json
    if not data or 'qr_data' not in data:
        return jsonify({'status': 'error', 'message': 'No QR data provided'})
        
    roll_no = data.get('qr_data')
    student_record = Student.query.filter_by(roll_no=roll_no).first()
    
    if not student_record:
        return jsonify({'status': 'error', 'message': 'Invalid QR Code / Student not found'})
        
    today = datetime.utcnow().date()
    now_time = datetime.utcnow()
    
    existing_record = Attendance.query.filter_by(student_id=student_record.student_id, date=today).first()
    
    if existing_record:
        if existing_record.status == 'Present' or existing_record.status == 'Late':
            return jsonify({'status': 'info', 'message': f'{student_record.name} is already checked in today.'})
        else:
            existing_record.status = 'Present'
            existing_record.checkin_time = now_time
            db.session.commit()
            return jsonify({'status': 'success', 'message': f'{student_record.name} marked Present.'})
            
    # Time window checks (6:00 PM to 7:00 PM)
    # Using local time for hostel operations
    now = datetime.now()
    current_hour = now.hour
    
    if current_hour < 18:
        return jsonify({'status': 'error', 'message': 'Attendance window has not opened yet. (Starts at 6:00 PM)'})
        
    status = 'Present'
    if current_hour >= 19:
        status = 'Late'
        
    new_attendance = Attendance(
        student_id=student_record.student_id,
        date=now.date(),
        status=status,
        checkin_time=now
    )
    db.session.add(new_attendance)
    db.session.commit()
    
    return jsonify({'status': 'success', 'message': f'Attendance marked for {student_record.name} ({status}).'})
