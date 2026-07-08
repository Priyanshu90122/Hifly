import sqlite3
import datetime
import os
import traceback
from flask import Flask, render_template_string, request, redirect, session, url_for, flash

app = Flask(__name__)
app.secret_key = "erp_high_fly_ultra_secure_2026"

# Pure Wasm Context In-Memory Engine State Initialization
GLOBAL_CONN = sqlite3.connect(":memory:", check_same_thread=False)

def init_db():
    cursor = GLOBAL_CONN.cursor()
    
    # 1. Base Users Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL, 
            name TEXT NOT NULL,
            phone TEXT DEFAULT '',
            dob TEXT DEFAULT ''
        )''')
        
    # 2. Student Profiles
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS student_profiles (
            student_id INTEGER PRIMARY KEY,
            class_section TEXT,
            batch_time TEXT DEFAULT '04:00 PM',
            fee_total INTEGER DEFAULT 0,
            fee_paid INTEGER DEFAULT 0,
            fee_remaining INTEGER DEFAULT 0,
            assigned_teacher_id INTEGER DEFAULT 0
        )''')
        
    # 3. Attendance Table (Explicit Constraints Setup)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            date TEXT,
            status TEXT,
            UNIQUE(student_id, date)
        )''')

    # 4. Quizzes Matrix Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS examinations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            exam_title TEXT,
            marks_obtained INTEGER,
            max_marks INTEGER,
            quiz_file_name TEXT,
            teacher_remarks TEXT
        )''')

    # Core Admin Initializer Account
    cursor.execute("SELECT * FROM users WHERE username='admin'")
    if not cursor.fetchone():
        cursor.execute("INSERT INTO users (username, password, role, name, phone) VALUES ('admin', 'admin123', 'admin', 'Head Director', '919999999999')")
        GLOBAL_CONN.commit()

init_db()

def get_db_connection():
    GLOBAL_CONN.row_factory = sqlite3.Row
    return GLOBAL_CONN

# Live Traceback Error Handler Matrix to expose inside Wasmer instance
@app.errorhandler(Exception)
def handle_exception(e):
    # Renders the exact error sequence on screen instead of an obscure 500 block page
    return f"<div style='padding:20px; background:#fff1f2; color:#9f1239; border-radius:12px; font-family:monospace; margin:40px;'><h2 style='margin-top:0;'>💥 Application Exception Traceback Caught</h2><pre>{traceback.format_exc()}</pre></div>", 500

# ------------------ MASTER SYSTEM LAYOUT ------------------
BASE_LAYOUT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>HIGH FLY ERP</title>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --primary: #4f46e5; --primary-hover: #4338ca;
            --success: #10b981; --warning: #f59e0b; --danger: #ef4444;
            --bg: #f8fafc; --card-bg: #ffffff; --text: #0f172a;
        }
        body { font-family: 'Plus Jakarta Sans', sans-serif; background: var(--bg); color: var(--text); margin: 0; padding: 20px; line-height: 1.5; }
        .nav-bar { display: flex; justify-content: space-between; align-items: center; background: linear-gradient(135deg, #1e1b4b, #311042); padding: 15px 30px; border-radius: 16px; margin-bottom: 30px; color: white; }
        .nav-bar a { color: #f472b6; text-decoration: none; font-weight: 600; padding: 8px 16px; border-radius: 8px; transition: 0.2s; }
        .nav-bar a:hover { background: rgba(255,255,255,0.1); color: white; }
        .card { background: var(--card-bg); border: none; padding: 25px; border-radius: 16px; margin-bottom: 25px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); border: 1px solid #e2e8f0; }
        .grid-2 { display: grid; grid-template-columns: repeat(auto-fit, minmax(350px, 1fr)); gap: 25px; }
        input, select, textarea { width: 100%; padding: 10px 14px; border: 1px solid #cbd5e1; border-radius: 10px; margin-bottom: 12px; box-sizing: border-box; font-family: inherit; font-size: 14px; }
        button { background: var(--primary); color: white; border: none; padding: 12px 20px; font-weight: 600; border-radius: 10px; cursor: pointer; width: 100%; font-size: 14px; }
        button:hover { background: var(--primary-hover); }
        table { width: 100%; border-collapse: collapse; margin-top: 10px; font-size: 14px; }
        th { background: #f1f5f9; padding: 12px; text-align: left; font-weight: 600; color: #475569; border-bottom: 2px solid #e2e8f0; }
        td { padding: 12px; border-bottom: 1px solid #e2e8f0; }
        .badge { padding: 4px 10px; border-radius: 9999px; font-size: 11px; font-weight: 700; color: white; display: inline-block; text-decoration: none; }
        .alert-flash { padding: 14px; border-radius: 12px; margin-bottom: 20px; font-weight: 600; font-size: 14px; background: #dcfce7; color: #166534; }
    </style>
</head>
<body>
    <div class="nav-bar">
        <span style="font-size: 20px; font-weight: 800;">✨ HIGH FLY ERP</span>
        <div>
            {% if session.get('user_id') %}
                <span style="margin-right: 15px;">Welcome, <strong>{{ session['name'] }}</strong> <span class="badge" style="background:#f472b6;">{{ session['role'].upper() }}</span></span>
                <a href="/dashboard">🏠 Dashboard</a>
                <a href="/logout" style="color:#ef4444;">🚪 Logout</a>
            {% endif %}
        </div>
    </div>

    {% with messages = get_flashed_messages() %}
      {% if messages %}
        {% for m in messages %}
            <div class="alert-flash">{{ m }}</div>
        {% endfor %}
      {% endif %}
    {% endwith %}

    {{ content | safe }}
</body>
</html>
"""

LOGIN_HTML = """
<div class="card" style="max-width: 450px; margin: 80px auto; border-top: 5px solid #4f46e5;">
    <h2 style="text-align: center; margin-top:0; font-weight:800;">🔐 Account Login</h2>
    <form method="POST">
        <label>Username</label>
        <input type="text" name="username" required placeholder="Enter UID or Roll ID">
        <label>Password</label>
        <input type="password" name="password" required placeholder="••••••••">
        <button type="submit">Verify & Enter</button>
    </form>
</div>
"""

ADMIN_HTML = """
<div class="grid-2">
    <div>
        <div class="card" style="border-left: 4px solid #10b981;">
            <h3>🎓 Register New Student</h3>
            <form action="/admin/add_student" method="POST">
                <input type="text" name="name" placeholder="Student Name" required>
                <input type="text" name="username" placeholder="Roll Number ID" required>
                <input type="text" name="password" placeholder="Account Password" required>
                <input type="text" name="phone" placeholder="WhatsApp Phone" required>
                <input type="text" name="class_section" placeholder="Class Stream" required>
                <input type="number" name="fee_total" placeholder="Total Fees Amount (₹)" required>
                <button type="submit" style="background:#10b981;">Create Student Profile</button>
            </form>
        </div>

        <div class="card" style="border-left: 4px solid #7c3aed;">
            <h3>👩‍🏫 Register New Teacher</h3>
            <form action="/admin/add_teacher" method="POST">
                <input type="text" name="name" placeholder="Teacher Name" required>
                <input type="text" name="username" placeholder="Teacher Username" required>
                <input type="text" name="password" placeholder="Teacher Password" required>
                <input type="text" name="phone" placeholder="Contact Number" required>
                <button type="submit" style="background:#7c3aed;">Onboard Faculty Account</button>
            </form>
        </div>

        <div class="card" style="border-left: 4px solid #f59e0b;">
            <h3>📅 Admin Controlled Attendance Matrix</h3>
            <form action="/admin/attendance/save" method="POST">
                <input type="date" name="date" value="{{ today }}" required>
                <table>
                    <thead><tr><th>Student Name</th><th>Mark Present</th></tr></thead>
                    <tbody>
                        {% for s in students %}
                        <tr>
                            <td><strong>{{ s.name }}</strong> ({{ s.class_section }})</td>
                            <td><input type="checkbox" name="present_students" value="{{ s.id }}" checked style="width:20px; height:20px;"></td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
                <button type="submit" style="background:#f59e0b; margin-top:10px;">Commit Daily Registry State</button>
            </form>
        </div>
    </div>

    <div>
        <div class="card">
            <h3>📋 Roster Directory & Fee / Teacher Assignment</h3>
            <div style="overflow-x: auto;">
                <table>
                    <tr><th>Student Details</th><th>Fees Management</th><th>Assign Teacher Node</th></tr>
                    {% for s in students %}
                    <tr>
                        <form action="/admin/update_student/{{ s.id }}" method="POST">
                        <td>
                            <strong>{{ s.name }}</strong><br>
                            <small>Roll ID: {{ s.username }}</small><br>
                            <span class="badge" style="background:#3b82f6; margin-top:4px;">{{ s.class_section }}</span>
                        </td>
                        <td>
                            <label style="font-size:11px;">Total Structure:</label>
                            <input type="number" name="fee_total" value="{{ s.fee_total }}" style="padding:4px; font-size:12px; margin-bottom:4px;">
                            <label style="font-size:11px;">Paid Amount:</label>
                            <input type="number" name="fee_paid" value="{{ s.fee_paid }}" style="padding:4px; font-size:12px; margin-bottom:4px;">
                            <label style="font-size:11px; color:#ef4444;">Dues Left: ₹{{ s.fee_remaining }}</label>
                        </td>
                        <td>
                            <select name="assigned_teacher_id" style="font-size:12px; padding:4px; margin-bottom:6px;">
                                <option value="0">Not Assigned</option>
                                {% for t in teachers %}
                                <option value="{{ t.id }}" {% if s.assigned_teacher_id == t.id %}selected{% endif %}>{{ t.name }}</option>
                                {% endfor %}
                            </select>
                            <button type="submit" style="padding:6px; font-size:11px; background:#475569; margin-bottom:4px;">Save Updates</button>
                            
                            {% set wa_msg = "Hello, this is an update from High Fly Classes. Your computed outstanding due structure balance left is Rs. " ~ s.fee_remaining %}
                            <a href="https://wa.me/{{ s.phone }}?text={{ wa_msg | urlencode }}" target="_blank" class="badge" style="background:#25D366; display:block; text-align:center;">💬 WhatsApp Fee Alert</a>
                        </td>
                        </form>
                    </tr>
                    {% endfor %}
                </table>
            </div>
        </div>
    </div>
</div>
"""

TEACHER_HTML = """
<div class="card" style="background: linear-gradient(135deg, #7c3aed, #4f46e5); color:white;">
    <h2 style="margin:0;">Instructor Matrix Dashboard</h2>
</div>

<div class="grid-2">
    <div style="grid-column: span 2;">
        <div class="card" style="border-top: 4px solid #3b82f6;">
            <h3>🏆 Log Quiz Performance & Grade Student</h3>
            <!-- Removed dynamic file encoding stream mapping to preserve Wasm stability -->
            <form action="/teacher/exams/save" method="POST">
                <label>Select Target Student</label>
                <select name="selected_student_id" required>
                    <option value="">-- Choose Student from Assigned List --</option>
                    {% for s in students %}
                    <option value="{{ s.id }}">{{ s.name }} ({{ s.class_section }})</option>
                    {% endfor %}
                </select>

                <label>Quiz Title</label>
                <input type="text" name="exam_title" placeholder="e.g. Science Mock Quiz 1" required>
                
                <label>Marks Obtained</label>
                <input type="number" name="marks_obtained" placeholder="Obtained Score" required>

                <label>Maximum Marks Ceiling</label>
                <input type="number" name="max_marks" value="100" required>

                <label>Quiz Document Code / Reference Name (Plain Text Input)</label>
                <input type="text" name="quiz_file_ref" placeholder="e.g. Quiz-Paper-Set-A.pdf" required>

                <label>Instructor Evaluation Remarks</label>
                <input type="text" name="remarks" placeholder="Enter feedback commentary">

                <button type="submit" style="background:#3b82f6; margin-top:10px;">Dispatch Metrics Logs</button>
            </form>
        </div>
    </div>
</div>
"""

STUDENT_HTML = """
<div class="grid-2">
    <div>
        <div class="card" style="border-left:4px solid #4f46e5;">
            <h3>📋 Student Details</h3>
            <p><strong>NAME:</strong> {{ profile.name }}</p>
            <p><strong>ROLL IDENTIFIER:</strong> {{ profile.username }}</p>
            <p><strong>CLASS TRACK:</strong> {{ profile.class_section }}</p>
            <p><strong>TIMETABLE BATCH:</strong> {{ profile.batch_time }}</p>
        </div>
        
        <div class="card">
            <h3>💳 Auto-Generated Digital Receipt</h3>
            <div style="border: 2px dashed #cbd5e1; padding: 20px; border-radius:12px; background:#fafafa; color:black; font-family:monospace;" id="print-area">
                <h3 style="text-align:center; margin:0;">HIGH FLY LEARNING CLASSES</h3>
                <p style="text-align:center; font-size:11px; margin:2px 0 15px 0;">Official Statement Transaction Voucher</p>
                <hr style="border:1px dashed #222;">
                <p><strong>TIMESTAMP TRACE :</strong> {{ today_stamp }}</p>
                <p><strong>STUDENT IDENTITY :</strong> {{ profile.name }}</p>
                <p><strong>ROLL IDENTIFIER  :</strong> {{ profile.username }}</p>
                <p><strong>CLASS WORKSTREAM  :</strong> {{ profile.class_section }}</p>
                <hr style="border:1px dashed #222;">
                <p><strong>TOTAL COURSE FEE  :</strong> ₹{{ profile.fee_total }}</p>
                <p><strong>TOTAL CAPITAL PAID :</strong> ₹{{ profile.fee_paid }}</p>
                <p style="color: #b91c1c;"><strong>OUTSTANDING ARREARS:</strong> ₹{{ profile.fee_remaining }}</p>
                <hr style="border:1px dashed #222;">
                <p style="text-align:center; font-weight:bold; color:green; margin-bottom:0;">✓ SYSTEM SEALED & SIGNED</p>
            </div>
            <button onclick="window.print()" style="margin-top:15px; background:#10b981;">🖨️ Print Receipt Document</button>
        </div>
    </div>

    <div>
        <div class="card">
            <h3>🏆 Quiz Score Performance Metrics Reports</h3>
            <table>
                <thead><tr style="background:#f8fafc;"><th>Quiz Assessment Module</th><th>Score Matrix</th><th>Attached Quiz Reference</th><th>Instructor Comments</th></tr></thead>
                <tbody>
                    {% for ex in exams %}
                    <tr>
                        <td><strong>{{ ex.exam_title }}</strong></td>
                        <td><span style="color:#4f46e5; font-weight:700;">{{ ex.marks_obtained }}</span> / {{ ex.max_marks }}</td>
                        <td><small>{{ ex.quiz_file_name if ex.quiz_file_name else "No Ref" }}</small></td>
                        <td><small>"{{ ex.teacher_remarks }}"</small></td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
</div>
"""

# ------------------ ENGINE CONTROLLERS ------------------
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username, password = request.form["username"], request.form["password"]
        conn = get_db_connection()
        user = conn.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password)).fetchone()
        if user:
            session["user_id"] = user["id"]
            session["role"] = user["role"]
            session["name"] = user["name"]
            session["username"] = user["username"]
            return redirect(url_for("dashboard"))
        else:
            flash("Authentication Denied: Invalid Username or Password")
    return render_template_string(BASE_LAYOUT, content=LOGIN_HTML)

@app.route("/dashboard")
def dashboard():
    if "user_id" not in session: return redirect(url_for("login"))
    conn = get_db_connection()
    
    if session["role"] == "admin":
        students = conn.execute('SELECT users.id, users.username, users.name, users.phone, student_profiles.class_section, student_profiles.fee_total, student_profiles.fee_paid, student_profiles.fee_remaining, student_profiles.assigned_teacher_id FROM users JOIN student_profiles ON users.id = student_profiles.student_id WHERE users.role="student"').fetchall()
        teachers = conn.execute("SELECT id, name FROM users WHERE role='teacher'").fetchall()
        return render_template_string(BASE_LAYOUT, content=render_template_string(ADMIN_HTML, students=students, teachers=teachers, today=datetime.date.today().isoformat()))
        
    elif session["role"] == "teacher":
        students = conn.execute('SELECT users.id, users.name, student_profiles.class_section FROM users JOIN student_profiles ON users.id = student_profiles.student_id WHERE student_profiles.assigned_teacher_id = ?', (session["user_id"],)).fetchall()
        return render_template_string(BASE_LAYOUT, content=render_template_string(TEACHER_HTML, students=students))
        
    else: # Student Role
        target_id = session["user_id"]
        profile = conn.execute('SELECT users.name, users.username, users.phone, student_profiles.class_section, student_profiles.batch_time, student_profiles.fee_total, student_profiles.fee_paid, student_profiles.fee_remaining FROM users JOIN student_profiles ON users.id = student_profiles.student_id WHERE users.id = ?', (target_id,)).fetchone()
        exams = conn.execute("SELECT * FROM examinations WHERE student_id = ?", (target_id,)).fetchall()
        return render_template_string(BASE_LAYOUT, content=render_template_string(STUDENT_HTML, profile=profile, exams=exams, today_stamp=datetime.datetime.now().strftime("%Y-%m-%d %H:%M")))

@app.route("/admin/add_student", methods=["POST"])
def admin_add_student():
    if session.get("role") != "admin": return "Forbidden", 403
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (username, password, role, name, phone) VALUES (?, ?, 'student', ?, ?)", (request.form["username"], request.form["password"], request.form["name"], request.form["phone"]))
        s_id = cursor.lastrowid
        
        total = int(request.form["fee_total"])
        cursor.execute("INSERT INTO student_profiles (student_id, class_section, fee_total, fee_remaining) VALUES (?, ?, ?, ?)", (s_id, request.form["class_section"], total, total))
        conn.commit()
        flash("Student Record Added Successfully")
    except Exception: flash("Error: Username duplication conflict.")
    return redirect(url_for("dashboard"))

@app.route("/admin/add_teacher", methods=["POST"])
def admin_add_teacher():
    if session.get("role") != "admin": return "Forbidden", 403
    conn = get_db_connection()
    try:
        conn.execute("INSERT INTO users (username, password, role, name, phone) VALUES (?, ?, 'teacher', ?, ?)", (request.form["username"], request.form["password"], request.form["name"], request.form["phone"]))
        conn.commit()
        flash("Teacher Profile Provisioned Into System Roster")
    except Exception: flash("Error: Unique Teacher Username conflict.")
    return redirect(url_for("dashboard"))

@app.route("/admin/update_student/<int:sid>", methods=["POST"])
def admin_update_student(sid):
    if session.get("role") != "admin": return "Forbidden", 403
    conn = get_db_connection()
    
    total = int(request.form.get("fee_total", 0))
    paid = int(request.form.get("fee_paid", 0))
    remaining = total - paid
    
    t_id = int(request.form.get("assigned_teacher_id", 0))
    
    conn.execute("UPDATE student_profiles SET fee_total = ?, fee_paid = ?, fee_remaining = ?, assigned_teacher_id = ? WHERE student_id = ?", (total, paid, remaining, t_id, sid))
    conn.commit()
    flash("Student Parameters and Fee Balances Synced Successfully")
    return redirect(url_for("dashboard"))

@app.route("/admin/attendance/save", methods=["POST"])
def admin_save_attendance():
    if session.get("role") != "admin": return "Forbidden", 403
    date = request.form["date"]
    p_ids = [int(i) for i in request.form.getlist("present_students")]
    conn = get_db_connection()
    
    students = conn.execute("SELECT student_id FROM student_profiles").fetchall()
    for s in students:
        status = "Present" if s["student_id"] in p_ids else "Absent"
        
        # Wasm-safe SQLite compatible execution rewrite block
        try:
            conn.execute("INSERT INTO attendance (student_id, date, status) VALUES (?, ?, ?)", (s["student_id"], date, status))
        except sqlite3.IntegrityError:
            conn.execute("UPDATE attendance SET status = ? WHERE student_id = ? AND date = ?", (status, s["student_id"], date))
            
    conn.commit()
    flash("Daily Attendance Log Synchronized by Admin Console")
    return redirect(url_for("dashboard"))

@app.route("/teacher/exams/save", methods=["POST"])
def save_exams():
    if session.get("role") != "teacher": return "Forbidden", 403
    
    st_id = request.form.get("selected_student_id")
    file_name = request.form.get("quiz_file_ref", "")
        
    conn = get_db_connection()
    conn.execute("INSERT INTO examinations (student_id, exam_title, marks_obtained, max_marks, quiz_file_name, teacher_remarks) VALUES (?, ?, ?, ?, ?, ?)", 
                 (st_id, request.form["exam_title"], request.form["marks_obtained"], request.form["max_marks"], file_name, request.form["remarks"]))
    conn.commit()
    
    flash("Quiz Meta Vector Evaluated & Metrics Logged")
    return redirect(url_for("dashboard"))

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=True)