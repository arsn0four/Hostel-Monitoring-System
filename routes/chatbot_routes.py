import os
from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from extensions import db
from models.db_models import ChatbotLog, Student, Room, Attendance, Hostel, Allocation
from datetime import datetime

chatbot = Blueprint('chatbot', __name__, url_prefix='/chatbot')

def get_smart_response(query):
    """Local Smart NLP Engine for HMS Assistant."""
    q = query.lower().strip()
    role = current_user.role
    user_id = current_user.id
    today = datetime.utcnow().date()
    
    # 1. Define Knowledge Base (Categories and Patterns)
    kb = {
        'greeting': {
            'patterns': ['hi', 'hello', 'hey', 'good morning', 'good evening', 'how are you', 'sup'],
            'response': lambda: f"Hello, **{current_user.username}**! I'm your HMS Local AI Assistant. How can I help you with the hostel today?"
        },
        'status': {
            'patterns': ['status', 'my data', 'info about me', 'details'],
            'response': lambda: get_user_status(role, user_id, today)
        },
        'attendance': {
            'patterns': ['attendance', 'present', 'absent', 'checkin', 'check in', 'mark', 'scanned'],
            'response': lambda: get_attendance_status(role, user_id, today)
        },
        'rooms': {
            'patterns': ['room', 'bed', 'available', 'occupancy', 'capacity', 'stay', 'where'],
            'response': lambda: get_room_info(role, user_id)
        },
        'mess': {
            'patterns': ['mess', 'food', 'breakfast', 'lunch', 'dinner', 'meal', 'eat', 'menu'],
            'response': lambda: "**Mess Schedule:**\n- 🍕 **Breakfast:** 7:30 AM - 9:00 AM\n- 🍱 **Lunch:** 12:30 PM - 2:00 PM\n- ☕ **Tea/Snacks:** 4:30 PM - 5:30 PM\n- 🍽️ **Dinner:** 7:30 PM - 9:00 PM"
        },
        'wifi': {
            'patterns': ['wifi', 'wi-fi', 'internet', 'password', 'connection', 'network'],
            'response': lambda: "🌐 **Hostel Wi-Fi Info:**\n- **SSID:** HMS_Student_Common\n- **Password:** `hostel_guest_2024` (Case Sensitive)"
        },
        'rules': {
            'patterns': ['rule', 'policy', 'timings', 'curfew', 'restriction', 'allowed', 'gate'],
            'response': lambda: "📜 **HMS Guidelines:**\n- **Attendance Window:** 6:00 PM - 7:00 PM (Late after 7 PM)\n- **Gate Curfew:** 10:00 PM Sharp\n- **Quiet Hours:** 10 PM - 6 AM\n- **Visitors:** Strictly in the lounge area only."
        },
        'emergency': {
            'patterns': ['emergency', 'help', 'doctor', 'urgent', 'police', 'contact', 'security'],
            'response': lambda: "🚨 **Emergency Contacts:**\n- **Warden (24/7):** +1 (234) 567-8901\n- **Clinic:** EXT 800\n- **Security:** EXT 100"
        }
    }

    # 2. Match Query against Patterns
    best_match = None
    for category, content in kb.items():
        if any(pattern in q for pattern in content['patterns']):
            best_match = category
            break

    if best_match:
        return kb[best_match]['response']()
    
    return "I'm not exactly sure about that. I can provide details on **Rooms, Attendance, Mess timings, Wi-Fi, Rules, or Emergency contacts**. Try asking about one of those!"

def get_user_status(role, user_id, today):
    msg = f"You are logged in as a **{role}**."
    if role == 'Student':
        student = Student.query.filter_by(user_id=user_id).first()
        if student:
            msg += f"\n- **Name:** {student.name}\n- **Roll No:** {student.roll_no}\n- **Dept:** {student.department}"
    return msg

def get_attendance_status(role, user_id, today):
    if role == 'Student':
        student = Student.query.filter_by(user_id=user_id).first()
        record = Attendance.query.filter_by(student_id=student.student_id, date=today).first()
        if record:
            return f"✅ You are marked as **{record.status}** for today ({today})."
        return "❌ You haven't checked in today yet. Please scan your QR code between **6:00 PM and 7:00 PM**!"
    else:
        present = Attendance.query.filter_by(date=today, status='Present').count()
        late = Attendance.query.filter_by(date=today, status='Late').count()
        return f"📊 **Today's Stats:** {present} Present, {late} Late students recorded."

def get_room_info(role, user_id):
    if role == 'Student':
        student = Student.query.filter_by(user_id=user_id).first()
        alloc = Allocation.query.filter_by(student_id=student.student_id, status='Active').first()
        if alloc:
            room = Room.query.get(alloc.room_id)
            return f"🏠 You are assigned to **Room {room.room_number}** in **{room.hostel.hostel_name}**."
        return "⚠️ You haven't been allocated a room yet. Please contact your Warden."
    else:
        rooms = Room.query.all()
        total = sum(r.capacity for r in rooms)
        occ = sum(r.current_occupancy for r in rooms)
        return f"🏨 **Hostel Load:** {occ}/{total} beds are currently occupied (**{total - occ}** free)."

@chatbot.route('/')
@login_required
def interface():
    """Renders the Chatbot UI."""
    return render_template('chatbot.html')

@chatbot.route('/api/query', methods=['POST'])
@login_required
def handle_query():
    data = request.json
    user_query = data.get('query', '').strip()
    
    if not user_query:
        return jsonify({'response': 'Please ask a question.'})

    # Execute Local Smart Engine
    response_text = get_smart_response(user_query)

    # Log to DB
    log = ChatbotLog(user_id=current_user.id, query_text=user_query, response_text=response_text)
    db.session.add(log)
    db.session.commit()
    
    return jsonify({'response': response_text})
