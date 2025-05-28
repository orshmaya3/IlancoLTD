from flask import Blueprint, render_template, request, redirect, session, url_for
from db import get_db

quality_bp = Blueprint('quality', __name__)

# 🧾 הצגת טופס בקרת איכות
@quality_bp.route('/quality-check/<int:plan_id>', methods=['GET'])
def quality_check(plan_id):
    if session.get('role') not in ['operator', 'admin']:
        return redirect(url_for('dashboard'))

    db = get_db()
    plan = db.execute('SELECT * FROM ProductionPlans WHERE id=?', (plan_id,)).fetchone()

    return render_template('quality_check.html', plan=plan)

# ✅ שליחת תוצאה והעדכון במסד הנתונים
@quality_bp.route('/submit-quality/<int:plan_id>', methods=['POST'])
def submit_quality(plan_id):
    if session.get('role') not in ['admin', 'operator']:
        return redirect(url_for('dashboard'))

    result = request.form['quality_result']
    notes = request.form['notes']

    db = get_db()
    new_status = 'עבר בקרת איכות' if result == 'passed' else 'בשלב ייצור'

    db.execute('''
        UPDATE ProductionPlans
        SET quality_status=?, quality_notes=?, status=?
        WHERE id=?
    ''', (result, notes, new_status, plan_id))

    db.commit()
    return redirect('/dashboard')

# 📊 דאשבורד בקרות איכות
@quality_bp.route('/quality-dashboard')
def quality_dashboard():
    if session.get('role') not in ['admin', 'operator']:
        return redirect(url_for('dashboard'))

    db = get_db()
    checks = db.execute('''
        SELECT id, date, customer, quality_status, quality_notes, status
        FROM ProductionPlans
        WHERE quality_status IS NOT NULL OR status = 'ממתין לבקרת איכות'
        ORDER BY date DESC
    ''').fetchall()

    return render_template('quality_dashboard.html', checks=checks)
