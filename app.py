import datetime
import os
import traceback
from flask import Flask, render_template_string, request, redirect, session, url_for, flash

app = Flask(__name__)
app.secret_key = "erp_high_fly_ultra_secure_2026_isolated_cloud"

# ------------------ MEMORY PERSISTENCE MATRIX ------------------
GLOBAL_DB = {
    "users": {
        1: {"id": 1, "username": "admin", "password": "admin123", "role": "admin", "name": "Head Director", "phone": "919999999999"}
    },
    "student_profiles": {},
    "attendance": {}, # Key: "student_id:date" -> status
    "examinations": [],
    "user_id_counter": 2,
    "exam_id_counter": 1
}

# Live Traceback Error Handler for Cloud Server Diagnostics
@app.errorhandler(Exception)
def handle_exception(e):
    return f"<div style='padding:20px; background:#fff1f2; color:#9f1239; border-radius:12px; font-family:monospace; margin:40px;'><h2 style='margin-top:0;'>💥 Application Exception Traceback Caught</h2><pre>{traceback.format_exc()}</pre></div>", 500

# ------------------ MASTER LAYOUT TEMPLATE ------------------
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

                <label>Quiz Document Code / Reference Name</label>
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
        username = request.form["username"]
        password = request.form["password"]
        
        target_user = None
        for u in GLOBAL_DB["users"].values():
            if u["username"] == username and u["password"] == password:
                target_user = u
                break
                
        if target_user:
            session["user_id"] = target_user["id"]
            session["role"] = target_user["role"]
            session["name"] = target_user["name"]
            session["username"] = target_user["username"]
            return redirect(url_for("dashboard"))
        else:
            flash("Authentication Denied: Invalid Credentials")
    return render_template_string(BASE_LAYOUT, content=LOGIN_HTML)

@app.route("/dashboard")
def dashboard():
    if "user_id" not in session: return redirect(url_for("login"))
    
    if session["role"] == "admin":
        students = []
        for u in GLOBAL_DB["users"].values():
            if u["role"] == "student":
                prof = GLOBAL_DB["student_profiles"].get(u["id"], {"class_section": "", "fee_total": 0, "fee_paid": 0, "fee_remaining": 0, "assigned_teacher_id": 0})
                students.append({
                    "id": u["id"], "username": u["username"], "name": u["name"], "phone": u["phone"],
                    "class_section": prof["class_section"], "fee_total": prof["fee_total"],
                    "fee_paid": prof["fee_paid"], "fee_remaining": prof["fee_remaining"],
                    "assigned_teacher_id": prof["assigned_teacher_id"]
                })
        
        teachers = [u for u in GLOBAL_DB["users"].values() if u["role"] == "teacher"]
        return render_template_string(BASE_LAYOUT, content=render_template_string(ADMIN_HTML, students=students, teachers=teachers, today=datetime.date.today().isoformat()))
        
    elif session["role"] == "teacher":
        students = []
        for u in GLOBAL_DB["users"].values():
            if u["role"] == "student":
                prof = GLOBAL_DB["student_profiles"].get(u["id"], {"assigned_teacher_id": 0, "class_section": ""})
                if prof["assigned_teacher_id"] == session["user_id"]:
                    students.append({"id": u["id"], "name": u["name"], "class_section": prof["class_section"]})
        return render_template_string(BASE_LAYOUT, content=render_template_string(TEACHER_HTML, students=students))
        
    else: # Student Role
        target_id = session["user_id"]
        user_meta = GLOBAL_DB["users"][target_id]
        prof = GLOBAL_DB["student_profiles"].get(target_id, {"class_section": "", "batch_time": "04:00 PM", "fee_total": 0, "fee_paid": 0, "fee_remaining": 0})
        
        profile = {
            "name": user_meta["name"], "username": user_meta["username"], "phone": user_meta["phone"],
            "class_section": prof["class_section"], "batch_time": prof["batch_time"],
            "fee_total": prof["fee_total"], "fee_paid": prof["fee_paid"], "fee_remaining": prof["fee_remaining"]
        }
        
        exams = [e for e in GLOBAL_DB["examinations"] if e["student_id"] == target_id]
        return render_template_string(BASE_LAYOUT, content=render_template_string(STUDENT_HTML, profile=profile, exams=exams, today_stamp=datetime.datetime.now().strftime("%Y-%m-%d %H:%M")))

@app.route("/admin/add_student", methods=["POST"])
def admin_add_student():
    if session.get("role") != "admin": return "Forbidden", 403
    
    uid = GLOBAL_DB["user_id_counter"]
    GLOBAL_DB["users"][uid] = {
        "id": uid, "username": request.form["username"], "password": request.form["password"],
        "role": "student", "name": request.form["name"], "phone": request.form["phone"]
    }
    
    total = int(request.form["fee_total"])
    GLOBAL_DB["student_profiles"][uid] = {
        "student_id": uid, "class_section": request.form["class_section"], "batch_time": "04:00 PM",
        "fee_total": total, "fee_paid": 0, "fee_remaining": total, "assigned_teacher_id": 0
    }
    
    GLOBAL_DB["user_id_counter"] += 1
    flash("Student Record Added Successfully")
    return redirect(url_for("dashboard"))

@app.route("/admin/add_teacher", methods=["POST"])
def admin_add_teacher():
    if session.get("role") != "admin": return "Forbidden", 403
    
    uid = GLOBAL_DB["user_id_counter"]
    GLOBAL_DB["users"][uid] = {
        "id": uid, "username": request.form["username"], "password": request.form["password"],
        "role": "teacher", "name": request.form["name"], "phone": request.form["phone"]
    }
    GLOBAL_DB["user_id_counter"] += 1
    flash("Teacher Profile Provisioned Into System Roster")
    return redirect(url_for("dashboard"))

@app.route("/admin/update_student/<int:sid>", methods=["POST"])
def admin_update_student(sid):
    if session.get("role") != "admin": return "Forbidden", 403
    
    total = int(request.form.get("fee_total", 0))
    paid = int(request.form.get("fee_paid", 0))
    remaining = total - paid
    t_id = int(request.form.get("assigned_teacher_id", 0))
    
    if sid in GLOBAL_DB["student_profiles"]:
        GLOBAL_DB["student_profiles"][sid]["fee_total"] = total
        GLOBAL_DB["student_profiles"][sid]["fee_paid"] = paid
        GLOBAL_DB["student_profiles"][sid]["fee_remaining"] = remaining
        GLOBAL_DB["student_profiles"][sid]["assigned_teacher_id"] = t_id
        
    flash("Student Parameters and Fee Balances Synced Successfully")
    return redirect(url_for("dashboard"))

@app.route("/admin/attendance/save", methods=["POST"])
def admin_save_attendance():
    if session.get("role") != "admin": return "Forbidden", 403
    date = request.form["date"]
    p_ids = [int(i) for i in request.form.getlist("present_students")]
    
    for sid, prof in GLOBAL_DB["student_profiles"].items():
        status = "Present" if sid in p_ids else "Absent"
        GLOBAL_DB["attendance"][f"{sid}:{date}"] = status
            
    flash("Daily Attendance Log Synchronized by Admin Console")
    return redirect(url_for("dashboard"))

@app.route("/teacher/exams/save", methods=["POST"])
def save_exams():
    if session.get("role") != "teacher": return "Forbidden", 403
    
    st_id = int(request.form.get("selected_student_id"))
    
    GLOBAL_DB["examinations"].append({
        "id": GLOBAL_DB["exam_id_counter"],
        "student_id": st_id,
        "exam_title": request.form["exam_title"],
        "marks_obtained": int(request.form["marks_obtained"]),
        "max_marks": int(request.form["max_marks"]),
        "quiz_file_name": request.form.get("quiz_file_ref", ""),
        "teacher_remarks": request.form["remarks"]
    })
    GLOBAL_DB["exam_id_counter"] += 1
    
    flash("Quiz Meta Vector Evaluated & Metrics Logged")
    return redirect(url_for("dashboard"))

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# Wasmer Edge ke standard WSGI layers is wrapper variable ko directly look up karte hain
wsgi_app = app.wsgi_app

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=False)