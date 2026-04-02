from flask import Flask, render_template, request, jsonify
import mysql.connector
from flask_cors import CORS
import os

# Flask App
app = Flask(__name__, template_folder='templates', static_folder='static')
CORS(app)

# Database Connection (Railway Environment Variables)
db = mysql.connector.connect(
    host=os.environ.get("MYSQLHOST"),
    user=os.environ.get("MYSQLUSER"),
    password=os.environ.get("MYSQLPASSWORD"),
    database=os.environ.get("MYSQLDATABASE"),
    port=int(os.environ.get("MYSQLPORT"))
)

# ================= PAGE ROUTES =================

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/admin')
def admin():
    return render_template("admin-dashboard.html")

@app.route('/employee')
def employee():
    return render_template("employee-dashboard.html")

@app.route('/create')
def create():
    return render_template("create-brief.html")

@app.route('/admin/history')
def admin_history():
    return render_template("admin-history.html")

@app.route('/employee/history')
def employee_history():
    return render_template("employee-history.html")

# ================= LOGIN =================

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    employee_id = data['employee_id']
    password = data['password']

    cursor = db.cursor()
    cursor.execute(
        "SELECT * FROM employees WHERE employee_id=%s AND password=%s",
        (employee_id, password)
    )

    if cursor.fetchone():
        return jsonify({"status": "success"})
    else:
        return jsonify({"status": "failed"})

# ================= CREATE BRIEF =================

@app.route('/createBrief', methods=['POST'])
def create_brief():
    data = request.json
    cursor = db.cursor()

    query = """
    INSERT INTO briefings
    (week_number, airline, incident, circular_link, ops_comment, conclusion)
    VALUES (%s,%s,%s,%s,%s,%s)
    """

    cursor.execute(query, (
        data['week_number'],
        data['airline'],
        data['incident'],
        data['circular_link'],
        data['ops_comment'],
        data['conclusion']
    ))

    db.commit()
    return jsonify({"status": "success"})

# ================= LATEST BRIEF =================

@app.route('/latestBrief')
def latest_brief():
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM briefings ORDER BY brief_id DESC LIMIT 1")
    return jsonify(cursor.fetchone())

# ================= ACKNOWLEDGE =================

@app.route('/acknowledge', methods=['POST'])
def acknowledge():
    data = request.json
    employee_id = data['employee_id']
    brief_id = data['brief_id']

    cursor = db.cursor()

    cursor.execute("""
        SELECT * FROM acknowledgements
        WHERE employee_id=%s AND brief_id=%s
    """, (employee_id, brief_id))

    if cursor.fetchone():
        return jsonify({"status": "already"})

    cursor.execute("""
        INSERT INTO acknowledgements
        (employee_id, brief_id, status)
        VALUES (%s,%s,'Read')
    """, (employee_id, brief_id))

    db.commit()
    return jsonify({"status": "success"})

# ================= HISTORY DATA =================

@app.route('/historyData')
def history_data():
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM briefings ORDER BY brief_id DESC")
    return jsonify(cursor.fetchall())

# ================= ADMIN STATS =================

@app.route('/stats')
def stats():
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT COUNT(*) AS total FROM employees")
    total = cursor.fetchone()['total']

    cursor.execute("SELECT COUNT(*) AS read_count FROM acknowledgements WHERE status='Read'")
    read = cursor.fetchone()['read_count']

    pending = total - read

    return jsonify({
        "total_employees": total,
        "read": read,
        "pending": pending
    })

# ================= RUN SERVER =================

if __name__ == '__main__':
    app.run()