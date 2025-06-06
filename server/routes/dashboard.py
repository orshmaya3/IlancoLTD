from flask import Blueprint, render_template, session, redirect, url_for
from db import get_db
dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/main-dashboard')
def main_dashboard():
    if session.get('role') not in ['admin', 'operator']:
        return redirect(url_for('login'))

    db = get_db()

    # סך הכול הזמנות ייצור
    total_orders = db.execute('SELECT COUNT(*) FROM ProductionPlans').fetchone()[0]

    # הזמנות פעילות (נניח שהן בסטטוס "בייצור")
    active_orders = db.execute('''
        SELECT COUNT(*) FROM ProductionPlans
        WHERE status = 'בייצור'
    ''').fetchone()[0]

    # בדיקות איכות שבוצעו בפועל
    quality_checks = db.execute('''
        SELECT COUNT(*) FROM ProductionPlans
        WHERE quality_status IS NOT NULL
    ''').fetchone()[0]

     # חדש: כמות תוכניות שממתינות לבקרת איכות
    pending_quality = db.execute("SELECT COUNT(*) FROM ProductionPlans" 
    " WHERE status = 'ממתין לבקרת איכות'").fetchone()[0]

    # אחוז כשל
    failed_checks = db.execute('''
        SELECT COUNT(*) FROM ProductionPlans
        WHERE quality_status = 'failed'
    ''').fetchone()[0]
    fail_rate = (failed_checks / quality_checks * 100) if quality_checks else 0

    # נתוני עוגה - התפלגות בקרת איכות
    dist_results = db.execute('''
        SELECT quality_status, COUNT(*) FROM ProductionPlans
        WHERE quality_status IS NOT NULL
        GROUP BY quality_status
    ''').fetchall()
    quality_labels = [row[0] for row in dist_results if row[0] is not None]
    quality_values = [row[1] for row in dist_results if row[1] is not None]

    # נתוני עמודות - כמות ייצור לפי תאריך
    bar_results = db.execute('''
        SELECT date, COUNT(*) as total FROM ProductionPlans
        GROUP BY date
        ORDER BY date DESC
        LIMIT 7
    ''').fetchall()
    bar_labels = [row[0] for row in reversed(bar_results) if row[0] is not None]
    bar_values = [row[1] for row in reversed(bar_results) if row[1] is not None]

    return render_template("main_dashboard.html",
                           total_orders=total_orders,
                           active_orders=active_orders,
                           quality_checks=quality_checks,
                            pending_quality=pending_quality  ,
                           fail_rate=round(fail_rate, 1),
                           quality_labels=quality_labels or [],
                           quality_values=quality_values or [],
                           bar_labels=bar_labels or [],
                           bar_values=bar_values or [])
