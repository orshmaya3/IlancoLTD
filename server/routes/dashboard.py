from flask import Blueprint, render_template, session, redirect, url_for
from db import get_db

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/main-dashboard')
def main_dashboard():
    if session.get('role') not in ['admin', 'operator']:
        return redirect(url_for('login'))

    db = get_db()

    # כמות הזמנות פעילות
    production_orders = db.execute('''
        SELECT COUNT(*) FROM ProductionPlans
        WHERE status NOT IN ('בוצע', 'מבוטל')
    ''').fetchone()[0]

    # כמות בקרות איכות
    quality_checks = db.execute('''
        SELECT COUNT(*) FROM ProductionPlans
        WHERE quality_status IS NOT NULL
    ''').fetchone()[0]

    # התפלגות בקרת איכות (Pass / Fail וכו׳)
    dist_results = db.execute('''
        SELECT quality_status, COUNT(*) FROM ProductionPlans
        WHERE quality_status IS NOT NULL
        GROUP BY quality_status
    ''').fetchall()
    quality_labels = [row[0] for row in dist_results if row[0] is not None]
    quality_values = [row[1] for row in dist_results if row[1] is not None]

    # גרף עמודות: כמות תוכניות לפי תאריך
    bar_results = db.execute('''
        SELECT date, COUNT(*) as total FROM ProductionPlans
        GROUP BY date
        ORDER BY date DESC
        LIMIT 7
    ''').fetchall()
    bar_labels = [row[0] for row in reversed(bar_results) if row[0] is not None]
    bar_values = [row[1] for row in reversed(bar_results) if row[1] is not None]

    # בדיקות סופיות (למניעת TypeError)
    quality_labels = quality_labels or []
    quality_values = quality_values or []
    bar_labels = bar_labels or []
    bar_values = bar_values or []

    return render_template("main_dashboard.html",
                           production_orders=production_orders,
                           quality_checks=quality_checks,
                           quality_labels=quality_labels,
                           quality_values=quality_values,
                           bar_labels=bar_labels,
                           bar_values=bar_values)
