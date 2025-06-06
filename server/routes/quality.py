from flask import Blueprint, render_template, request, redirect, session, url_for , send_file
from db import get_db
from io import BytesIO
import openpyxl

quality_bp = Blueprint('quality', __name__)

# 🧾 הצגת טופס בקרת איכות
@quality_bp.route('/quality-check/<int:plan_id>', methods=['GET'])
def quality_check(plan_id):
    if session.get('role') not in ['operator', 'admin']:
        return redirect(url_for('dashboard'))

    db = get_db()
    plan = db.execute('SELECT * FROM ProductionPlans WHERE id=?', (plan_id,)).fetchone()

    return render_template('quality_check.html', plan=plan)


@quality_bp.route('/quality-dashboard')
def quality_dashboard():
    if session.get('role') not in ['admin', 'operator']:
        return redirect(url_for('dashboard'))

    db = get_db()

    # קבלת פרמטרים מהטופס
    customer = request.args.get('customer')
    from_date = request.args.get('from_date')
    to_date = request.args.get('to_date')
    quality_status = request.args.get('quality_status')

    # בניית שאילתה דינמית
    query = '''
        SELECT id, date, customer, quality_status, quality_notes, status
        FROM ProductionPlans
        WHERE (quality_status IS NOT NULL OR status = 'ממתין לבקרת איכות')
    '''
    params = []

    if customer:
        query += ' AND customer LIKE ?'
        params.append(f'%{customer}%')

    if from_date:
        query += ' AND date >= ?'
        params.append(from_date)

    if to_date:
        query += ' AND date <= ?'
        params.append(to_date)

    if quality_status == 'pending':
        query += ' AND quality_status IS NULL'
    elif quality_status:
        query += ' AND quality_status = ?'
        params.append(quality_status)


    query += ' ORDER BY date DESC'

    checks = db.execute(query, params).fetchall()

    return render_template('quality_dashboard.html', checks=checks)


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



@quality_bp.route('/export-quality-excel')
def export_quality_excel():
    db = get_db()
    checks = db.execute('''
        SELECT id, date, customer, status, quality_status, quality_notes
        FROM ProductionPlans
        WHERE quality_status IS NOT NULL OR status = 'ממתין לבקרת איכות'
        ORDER BY date DESC
    ''').fetchall()

    # יצירת קובץ Excel חדש
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "בקרת איכות"

    # כותרות
    headers = ['ID', 'תאריך', 'לקוח', 'סטטוס תוכנית', 'מצב בקרה', 'הערות']
    ws.append(headers)

    for row in checks:
        ws.append([
            row['id'],
            row['date'],
            row['customer'],
            row['status'],
            row['quality_status'],
            row['quality_notes'] or ''
        ])

    output = BytesIO()
    wb.save(output)
    output.seek(0)

    return send_file(output, as_attachment=True,
                     download_name="quality_checks.xlsx",
                     mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")