from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from extensions import db
from models.db_models import Room, Student, User, Allocation, Warden

warden = Blueprint('warden', __name__, url_prefix='/warden')

@warden.route('/dashboard')
@login_required
def dashboard():
    if current_user.role != 'Warden':
        flash('Access denied.', 'danger')
        return redirect(url_for('auth.login'))
    return render_template('dashboard_warden.html')

@warden.route('/rooms')
@login_required
def manage_rooms():
    if current_user.role not in ['Warden', 'Admin']:
        flash('Access denied.', 'danger')
        return redirect(url_for('auth.login'))
        
    warden_profile = None
    if current_user.role == 'Warden':
        warden_profile = Warden.query.filter_by(user_id=current_user.id).first()
        if not warden_profile or not warden_profile.hostel_id:
            flash('You are not assigned to manage any hostel.', 'danger')
            return redirect(url_for('warden.dashboard'))
            
    if current_user.role == 'Admin':
        from models.db_models import Hostel
        rooms = Room.query.all()
        hostels = Hostel.query.all()
        return render_template('manage_rooms.html', rooms=rooms, hostels=hostels)
    else:
        rooms = Room.query.filter_by(hostel_id=warden_profile.hostel_id).all()
        return render_template('manage_rooms.html', rooms=rooms)

@warden.route('/rooms/add', methods=['GET', 'POST'])
@login_required
def add_room():
    if current_user.role not in ['Warden', 'Admin']:
        flash('Access denied.', 'danger')
        return redirect(url_for('auth.login'))
        
    warden_profile = None
    if current_user.role == 'Warden':
        warden_profile = Warden.query.filter_by(user_id=current_user.id).first()
        if not warden_profile or not warden_profile.hostel_id:
            flash('You are not assigned to manage any hostel.', 'danger')
            return redirect(url_for('warden.dashboard'))

    if request.method == 'POST':
        room_number = request.form.get('room_number')
        capacity = request.form.get('capacity', type=int)
        hostel_id = request.form.get('hostel_id', type=int) if current_user.role == 'Admin' else warden_profile.hostel_id
        
        if not hostel_id:
            flash('Hostel must be selected.', 'danger')
        else:
            existing = Room.query.filter_by(room_number=room_number, hostel_id=hostel_id).first()
            if existing:
                flash(f'Room {room_number} already exists in this hostel.', 'danger')
            else:
                new_room = Room(room_number=room_number, capacity=capacity, hostel_id=hostel_id)
                db.session.add(new_room)
                db.session.commit()
                flash(f'Room {room_number} created successfully.', 'success')
                return redirect(url_for('warden.manage_rooms'))
                
    if current_user.role == 'Admin':
        from models.db_models import Hostel
        hostels = Hostel.query.all()
        return render_template('add_room.html', hostels=hostels)
    else:
        return render_template('add_room.html')

@warden.route('/rooms/allocate/<int:room_id>', methods=['GET', 'POST'])
@login_required
def allocate_room(room_id):
    if current_user.role not in ['Warden', 'Admin']:
        flash('Access denied.', 'danger')
        return redirect(url_for('auth.login'))
        
    room = Room.query.get_or_404(room_id)
    
    if current_user.role == 'Warden':
        warden_profile = Warden.query.filter_by(user_id=current_user.id).first()
        if room.hostel_id != warden_profile.hostel_id:
            flash('You do not have permission to manage this room.', 'danger')
            return redirect(url_for('warden.manage_rooms'))
    
    if request.method == 'POST':
        student_id = request.form.get('student_id', type=int)
        student = Student.query.get_or_404(student_id)
        
        # Check active allocation
        active_allocation = Allocation.query.filter_by(student_id=student.student_id, status='Active').first()
        
        if room.current_occupancy >= room.capacity:
            flash(f'Room {room.room_number} is full.', 'danger')
        elif active_allocation and active_allocation.room_id == room.room_id:
            flash('Student is already in this room.', 'info')
        else:
            # If moving from another room, decrement that room's occupancy
            if active_allocation:
                active_allocation.status = 'Inactive'
                old_room = Room.query.get(active_allocation.room_id)
                if old_room:
                    old_room.current_occupancy -= 1
                    
            # Create new Allocation
            new_allocation = Allocation(student_id=student.student_id, room_id=room.room_id)
            db.session.add(new_allocation)
            room.current_occupancy += 1
            db.session.commit()
            flash(f'Student allocated to Room {room.room_number}.', 'success')
            
        return redirect(url_for('warden.allocate_room', room_id=room.room_id))
        
    # Get students not active in this room
    all_students = Student.query.all()
    # Find list of students already allocated here
    current_allocations = Allocation.query.filter_by(room_id=room.room_id, status='Active').all()
    current_student_ids = [a.student_id for a in current_allocations]
    
    available_students = [s for s in all_students if s.student_id not in current_student_ids]
    current_students = [Student.query.get(sid) for sid in current_student_ids]
    
    return render_template('allocate_room.html', room=room, available_students=available_students, current_students=current_students)

@warden.route('/attendance')
@login_required
def view_attendance():
    if current_user.role not in ['Warden', 'Admin']:
        flash('Access denied.', 'danger')
        return redirect(url_for('auth.login'))
        
    from models.db_models import Student, Attendance, Allocation, Room
    from datetime import datetime
    
    today = datetime.utcnow().date()
    
    if current_user.role == 'Admin':
        active_allocations = Allocation.query.filter(Allocation.status=='Active').all()
    else:
        warden_profile = Warden.query.filter_by(user_id=current_user.id).first()
        rooms_in_hostel = Room.query.filter_by(hostel_id=warden_profile.hostel_id).all()
        room_ids = [r.room_id for r in rooms_in_hostel]
        active_allocations = Allocation.query.filter(Allocation.room_id.in_(room_ids), Allocation.status=='Active').all()
        
    student_ids = [a.student_id for a in active_allocations]
    total_students = len(student_ids) if student_ids else 0
    
    if student_ids:
        today_records = Attendance.query.filter(Attendance.date==today, Attendance.student_id.in_(student_ids)).all()
    else:
        today_records = []
    
    present_count = sum(1 for r in today_records if r.status in ['Present', 'Late'])
    absent_count = total_students - present_count
    
    return render_template('warden_attendance.html',
                           today=today,
                           total_students=total_students,
                           present_count=present_count,
                           absent_count=absent_count,
                           today_records=today_records)
