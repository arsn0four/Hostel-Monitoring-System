# 🏨 Hostel Monitoring System (HMS)

![Project](https://img.shields.io/badge/Project-HMS-cyan?style=for-the-badge)  
![Database](https://img.shields.io/badge/Database-MySQL-blue?style=for-the-badge)  
![AI](https://img.shields.io/badge/AI-Local_NLP-success?style=for-the-badge)  
![Status](https://img.shields.io/badge/Status-Production--Ready-success?style=for-the-badge)

> 💡 A modern, intelligent, and fully-featured **Hostel Monitoring & Attendence System** built using **Python, Flask, and MySQL** — designed for real-world deployment.

---

## 🌟 Overview

**HMS** is a powerful web-based system that streamlines hostel operations with:

- Smart role-based dashboards  
- Automated QR attendance system  
- Real-time database insights  
- A built-in **local AI assistant (no API required)**  

---

## 🚀 Key Features

### 🏢 Role-Based Management
- Admin, Warden, and Student dashboards
- Full control over hostel operations

### 📸 QR-Based Attendance
- Time-based attendance (6 PM – 7 PM)
- Late detection after 7 PM
- Secure scan system

### 🤖 Local AI Chatbot
- No API required
- Reads live data
- Answers system-related queries

---

## 🛠️ Tech Stack

- Python (Flask)
- MySQL
- SQLAlchemy
- HTML, CSS, JavaScript
- html5-qrcode

---

## ⚙️ Setup

```bash
git clone <your-repo-url>
```
Go to root Dictonary
```bash
cd HMS
```
Making Virtual Envirnoment
```bash
python -m venv venv
```
Activating Virtual Envirnoment
```bash
venv\Scripts\activate
```
Installing Requirements 
```bash
pip install -r requirements.txt
```

### Database
Creating DataBase
Run in MySQL Server
```sql
CREATE DATABASE hms_db;
```

### Run
Initializing DataBase Details
```bash
python init_db.py
```
Running Application
```bash
python app.py
```

---

## 🔐 Default Login

Username: admin  
Password: admin123  

---

## 📄 License

Developed by **Arslan Sajjad**
