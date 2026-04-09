from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import mysql.connector
import os

# ================= FLASK APP =================

app = Flask(__name__, template_folder='templates', static_folder='static')
CORS(app)

# ================= DATABASE CONNECTION =================

def get_db_connection():
    return mysql.connector.connect(
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
    employee_id = data.get('employee_id')
    password = data.get('password')

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT role FROM employees 
        WHERE employee_id=%s AND password=%s
    """, (employee_id, password))

    result = cursor.fetchone()

    cursor.close()
    conn.close()

    if result:
        return jsonify({
            "status": "success",
            "role": result['role']
        })
    else:
        return jsonify({"status": "failed"})

# ================= CREATE BRIEF =================

@app.route('/createBrief', methods=['POST'])
def create_brief():
    data = request.json

    conn = get_db_connection()
    cursor = conn.cursor()

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

    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({"status": "success"})

# ================= LATEST BRIEF =================

@app.route('/latestBrief')
def latest_brief():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT * FROM briefings 
        ORDER BY brief_id DESC 
        LIMIT 1
    """)

    result = cursor.fetchone()

    cursor.close()
    conn.close()

    return jsonify(result)

# ================= ACKNOWLEDGE =================

@app.route('/acknowledge', methods=['POST'])
def acknowledge():
    data = request.json
    employee_id = data['employee_id']
    brief_id = data['brief_id']

    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if already acknowledged
    cursor.execute("""
        SELECT * FROM acknowledgements
        WHERE employee_id=%s AND brief_id=%s
    """, (employee_id, brief_id))

    if cursor.fetchone():
        cursor.close()
        conn.close()
        return jsonify({"status": "already"})

    # Insert acknowledgement
    cursor.execute("""
        INSERT INTO acknowledgements
        (employee_id, brief_id, status)
        VALUES (%s,%s,'Read')
    """, (employee_id, brief_id))

    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({"status": "success"})

# ================= HISTORY =================

@app.route('/historyData')
def history_data():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT * FROM briefings 
        ORDER BY brief_id DESC
    """)

    result = cursor.fetchall()

    cursor.close()
    conn.close()

    return jsonify(result)

# ================= ADMIN STATS =================

@app.route('/stats')
def stats():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT COUNT(*) AS total FROM employees")
    total = cursor.fetchone()['total']

    cursor.execute("""
        SELECT COUNT(*) AS read_count 
        FROM acknowledgements 
        WHERE status='Read'
    """)
    read = cursor.fetchone()['read_count']

    pending = total - read

    cursor.close()
    conn.close()

    return jsonify({
        "total_employees": total,
        "read": read,
        "pending": pending
    })

# ================= ACKNOWLEDGEMENT LIST (ADMIN) =================

@app.route('/acknowledgementList')
def acknowledgement_list():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT e.name, e.employee_id, a.status
        FROM employees e
        LEFT JOIN acknowledgements a
        ON e.employee_id = a.employee_id
    """)

    result = cursor.fetchall()

    cursor.close()
    conn.close()

    return jsonify(result)

# ================= RUN =================

if __name__ == '__main__':
    app.run(debug=True)