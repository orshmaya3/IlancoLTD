from flask import Flask, render_template, request, redirect, session, url_for
import requests
from routes.production import production_bp
from routes.quality import quality_bp
from db import get_db
from routes.dashboard import dashboard_bp
from datetime import datetime, timedelta
import os

login_attempts = {}
LOCKOUT_TIME = timedelta(minutes=10)
BASE_DIR = os.path.abspath(os.path.dirname(__file__))



app = Flask(
    __name__,
    static_folder=os.path.join(BASE_DIR, 'static'),
    template_folder=os.path.join(BASE_DIR, 'templates'))

app.secret_key = 'your_secret_key_here'
app.permanent_session_lifetime = timedelta(minutes=15)  # ⏱️ זמן תפוגה לסשן


# רישום מסלולי Blueprint
app.register_blueprint(production_bp)
app.register_blueprint(quality_bp)
app.register_blueprint(dashboard_bp)

# דף פתיחה
@app.route('/')
def index():
    return redirect(url_for('login'))

# משתמשים קיימים
USERS = {
    "admin": {"password": "admin123", "role": "admin"},
    "operator": {"password": "operator123", "role": "operator"}
}

# התחברות
@app.route('/login', methods=['GET', 'POST'])
def login():
    ip = request.remote_addr
    now = datetime.now()

    # הגדרה כמה ניסיונות מותר
    MAX_ATTEMPTS = 5

    # בדיקת חסימה
    if ip in login_attempts:
        attempts, last_attempt = login_attempts[ip]
        if attempts >= MAX_ATTEMPTS and now - last_attempt < LOCKOUT_TIME:
            return render_template('login.html', error="⛔ נחסמת זמנית עקב ניסיונות מרובים. נסה שוב בעוד כמה דקות.")

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = USERS.get(username)

        if user and user['password'] == password:
            session['username'] = username
            session['role'] = user['role'] 
            session.permanent = True  # 🕒 הפיכת הסשן לקבוע עם תפוגה
            login_attempts.pop(ip, None)  # איפוס לאחר הצלחה
            return redirect(url_for('dashboard.main_dashboard'))
        else:
            # עדכון מונה ניסיונות
            if ip in login_attempts:
                attempts, _ = login_attempts[ip]
                attempts += 1
            else:
                attempts = 1
            login_attempts[ip] = (attempts, now)

            attempts_left = MAX_ATTEMPTS - attempts
            if attempts_left <= 0:
                error_msg = "⛔ הגעת למספר מקסימלי של ניסיונות. נסה שוב בעוד 10 דקות."
            else:
                error_msg = f"שגיאה. נותרו {attempts_left} ניסיונות לפני חסימה."

            return render_template('login.html', error=error_msg)

    return render_template('login.html')


# התנתקות
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

# טופס יצירת תוכנית ייצור
@app.route('/form')
def production_form():
    if session.get('role') != 'admin':
        return redirect(url_for('dashboard'))
    return render_template('production_form.html')

# שליחת טופס תוכנית ייצור
@app.route('/submit-production', methods=['POST'])
def submit_production():
    if session.get('role') != 'admin':
        return redirect(url_for('dashboard'))

    data = {
        "date": request.form['date'],
        "quantity": int(request.form['quantity']),
        "status": request.form['status'],
        "notes": request.form['notes'],
        "customer": request.form['customer'],
        "priority": request.form['priority']
    }

    response = requests.post('http://127.0.0.1:5000/api/production/', json=data)

    if response.status_code == 201:
        return redirect('/dashboard')
    else:
        return f"<h2>❌ שגיאה בשמירה</h2><pre>{response.text}</pre>"

# דשבורד תוכניות ייצור
@app.route('/dashboard')
def dashboard():
    if session.get('role') not in ['admin', 'operator']:
        return redirect(url_for('login'))

    response = requests.get('http://127.0.0.1:5000/api/production/')
    if response.status_code != 200:
        return f"<h2>❌ שגיאה בקבלת הנתונים</h2><pre>{response.text}</pre>"

    plans = response.json()

    # פרמטרים מהסינון
    status = request.args.get('status')
    priority = request.args.get('priority')
    from_date = request.args.get('from_date')
    to_date = request.args.get('to_date')
    customer = request.args.get('customer')

    # סינון נתונים
    if status:
        plans = [p for p in plans if p['status'] == status]
    if priority:
        plans = [p for p in plans if p['priority'] == priority]
    if customer:
        plans = [p for p in plans if customer in p['customer']]
    if from_date:
        plans = [p for p in plans if p['date'] >= from_date]
    if to_date:
        plans = [p for p in plans if p['date'] <= to_date]

    return render_template('production_dashboard.html', plans=plans)


# עריכת תוכנית
@app.route('/edit/<int:plan_id>', methods=['GET', 'POST'])
def edit_plan(plan_id):
    if session.get('role') != 'admin':
        return redirect('/dashboard')

    db = get_db()
    plan = db.execute('SELECT * FROM ProductionPlans WHERE id=?', (plan_id,)).fetchone()

    # 🔒 חסימה עסקית – לא ניתן לערוך תוכניות שעברו או נכשלו בבקרה
    if plan['status'] in ['עבר בקרת איכות', 'נכשל בקרת איכות']:
        return "<h2 style='text-align:center; margin-top:50px;'>🔒 לא ניתן לערוך תוכנית שכבר עברה או נכשלה בבקרת איכות.</h2>", 403


    if request.method == 'POST':
        data = request.form
        db.execute('''
            UPDATE ProductionPlans
            SET date=?, quantity=?, status=?, notes=?, customer=?, priority=?
            WHERE id=?
        ''', (
            data['date'], data['quantity'], data['status'],
            data['notes'], data['customer'], data['priority'], plan_id
        ))
        db.commit()
        return redirect('/dashboard')

    plan = db.execute('SELECT * FROM ProductionPlans WHERE id=?', (plan_id,)).fetchone()
    return render_template('edit_form.html', plan=plan)





# הרצת השרת
if __name__ == '__main__':
    app.run(debug=True)