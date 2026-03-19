from app import create_app
from extensions import db, bcrypt
from models.db_models import User, Hostel, Warden, Room, Student, Allocation, Attendance
from datetime import datetime

app = create_app()

def init_db():
    with app.app_context():
        # Drop all tables since the schema has drastically changed
        db.drop_all()
        db.create_all()
        
        # Create default Admin
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            hashed_pw = bcrypt.generate_password_hash('admin123').decode('utf-8')
            default_admin = User(
                username='admin',
                password_hash=hashed_pw,
                role='Admin'
            )
            db.session.add(default_admin)
            db.session.commit()
            print("Database initialized and default Admin 'admin'/'admin123' created.")

        print("Seeding sample data...")

        # Insert Hostels
        h1 = Hostel(hostel_id=101, hostel_name='Boys Hostel', location='Block A')
        h2 = Hostel(hostel_id=102, hostel_name='Girls Hostel', location='Block B')
        h3 = Hostel(hostel_id=103, hostel_name='International Hostel', location='Block C')
        db.session.add_all([h1, h2, h3])
        db.session.commit()

        # Insert Rooms
        r1 = Room(room_id=201, room_number='101', capacity=3, hostel_id=101)
        r2 = Room(room_id=202, room_number='102', capacity=2, hostel_id=101)
        r3 = Room(room_id=203, room_number='201', capacity=3, hostel_id=102)
        r4 = Room(room_id=204, room_number='202', capacity=2, hostel_id=103)
        db.session.add_all([r1, r2, r3, r4])
        db.session.commit()

        # Helper method to create linked users
        def create_user(username, role):
            hashed_pw = bcrypt.generate_password_hash('password123').decode('utf-8')
            u = User(username=username, password_hash=hashed_pw, role=role)
            db.session.add(u)
            db.session.commit()
            return u

        # Insert Wardens (with User profiles)
        uw1 = create_user('warden1', 'Warden')
        uw2 = create_user('warden2', 'Warden')
        uw3 = create_user('warden3', 'Warden')

        w1 = Warden(warden_id=301, name='Mr.Ramesh', phone='9876543210', hostel_id=101, user_id=uw1.id)
        w2 = Warden(warden_id=302, name='Mrs.Kavitha', phone='9876501234', hostel_id=102, user_id=uw2.id)
        w3 = Warden(warden_id=303, name='Mr.Suresh', phone='9123456780', hostel_id=103, user_id=uw3.id)
        db.session.add_all([w1, w2, w3])
        db.session.commit()

        # Insert Students (with User profiles)
        us1 = create_user('rahul', 'Student')
        us2 = create_user('anjali', 'Student')
        us3 = create_user('karthik', 'Student')
        us4 = create_user('priya', 'Student')
        us5 = create_user('arjun', 'Student')

        s1 = Student(student_id=1, name='Rahul Sharma', roll_no='RA101', department='CSE', user_id=us1.id)
        s2 = Student(student_id=2, name='Anjali Verma', roll_no='RA102', department='IT', user_id=us2.id)
        s3 = Student(student_id=3, name='Karthik R', roll_no='RA103', department='ECE', user_id=us3.id)
        s4 = Student(student_id=4, name='Priya Nair', roll_no='RA104', department='AI&ML', user_id=us4.id)
        s5 = Student(student_id=5, name='Arjun Singh', roll_no='RA105', department='CSE', user_id=us5.id)
        db.session.add_all([s1, s2, s3, s4, s5])
        db.session.commit()

        # Insert Allocations
        a1 = Allocation(allocation_id=401, allocation_date=datetime.strptime('2026-01-10', '%Y-%m-%d').date(), status='Active', student_id=1, room_id=201)
        a2 = Allocation(allocation_id=402, allocation_date=datetime.strptime('2026-01-12', '%Y-%m-%d').date(), status='Active', student_id=2, room_id=202)
        a3 = Allocation(allocation_id=403, allocation_date=datetime.strptime('2026-01-15', '%Y-%m-%d').date(), status='Active', student_id=3, room_id=203)
        a4 = Allocation(allocation_id=404, allocation_date=datetime.strptime('2026-01-18', '%Y-%m-%d').date(), status='Active', student_id=4, room_id=204)
        db.session.add_all([a1, a2, a3, a4])
        
        # Update Room occupancies
        r1.current_occupancy = 1
        r2.current_occupancy = 1
        r3.current_occupancy = 1
        r4.current_occupancy = 1
        db.session.commit()

        # Insert Attendance
        date_att = datetime.strptime('2026-02-01', '%Y-%m-%d').date()
        att1 = Attendance(attendance_id=501, date=date_att, status='Present', student_id=1)
        att2 = Attendance(attendance_id=502, date=date_att, status='Absent', student_id=2)
        att3 = Attendance(attendance_id=503, date=date_att, status='Present', student_id=3)
        att4 = Attendance(attendance_id=504, date=date_att, status='Present', student_id=4)
        att5 = Attendance(attendance_id=505, date=date_att, status='Absent', student_id=5)
        db.session.add_all([att1, att2, att3, att4, att5])
        db.session.commit()

        print("Data seeded successfully!")

if __name__ == '__main__':
    init_db()
