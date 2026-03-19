from datetime import datetime
from extensions import db
from flask_login import UserMixin

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), nullable=False) # 'Admin', 'Warden', 'Student'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    student_profile = db.relationship('Student', backref='user_profile', uselist=False, lazy=True, cascade='all, delete-orphan')
    warden_profile = db.relationship('Warden', backref='user_profile', uselist=False, lazy=True, cascade='all, delete-orphan')
    chatbot_logs = db.relationship('ChatbotLog', backref='user', lazy=True)

    def get_id(self):
        return str(self.id)


class Hostel(db.Model):
    __tablename__ = 'hostel'
    hostel_id = db.Column(db.Integer, primary_key=True)
    hostel_name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(200), nullable=False)

    rooms = db.relationship('Room', backref='hostel', lazy=True, cascade='all, delete-orphan')
    wardens = db.relationship('Warden', backref='managed_hostel', lazy=True)


class Warden(db.Model):
    __tablename__ = 'warden'
    warden_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    hostel_id = db.Column(db.Integer, db.ForeignKey('hostel.hostel_id'), nullable=True)


class Room(db.Model):
    __tablename__ = 'room'
    room_id = db.Column(db.Integer, primary_key=True)
    room_number = db.Column(db.String(20), nullable=False)
    capacity = db.Column(db.Integer, nullable=False, default=2)
    current_occupancy = db.Column(db.Integer, nullable=False, default=0)
    hostel_id = db.Column(db.Integer, db.ForeignKey('hostel.hostel_id'), nullable=False)

    allocations = db.relationship('Allocation', backref='room', lazy=True, cascade='all, delete-orphan')


class Student(db.Model):
    __tablename__ = 'student'
    student_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    roll_no = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    department = db.Column(db.String(100), nullable=True)
    qrcode = db.Column(db.Text, nullable=True)

    allocations = db.relationship('Allocation', backref='student', lazy=True, cascade='all, delete-orphan')
    attendances = db.relationship('Attendance', backref='student', lazy=True, cascade='all, delete-orphan')


class Allocation(db.Model):
    __tablename__ = 'allocation'
    allocation_id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.student_id'), nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey('room.room_id'), nullable=False)
    allocation_date = db.Column(db.Date, nullable=False, default=datetime.utcnow().date)
    status = db.Column(db.String(20), nullable=False, default='Active')


class Attendance(db.Model):
    __tablename__ = 'attendance'
    attendance_id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.student_id'), nullable=False)
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow().date)
    status = db.Column(db.String(20), nullable=False, default='Absent') # 'Present', 'Absent', 'Late'
    checkin_time = db.Column(db.DateTime, nullable=True)


class ChatbotLog(db.Model):
    __tablename__ = 'chatbot_logs'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    query_text = db.Column(db.Text, nullable=False)
    response_text = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
