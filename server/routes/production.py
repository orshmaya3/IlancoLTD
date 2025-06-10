from flask import Blueprint, request, jsonify ,render_template, make_response, session, redirect, url_for , send_file
from db import get_db
from datetime import datetime
from io import BytesIO
import openpyxl


production_bp = Blueprint('production', __name__, url_prefix='/api/production')

#  שליפה של כל תוכניות הייצור
@production_bp.route('/', methods=['GET'])
def get_all_plans():
    db = get_db()
    rows = db.execute("SELECT * FROM ProductionPlans ORDER BY id DESC").fetchall()
    return jsonify([dict(row) for row in rows])
 
#  יצירת תוכנית ייצור חדשה
@production_bp.route('/', methods=['POST'])
def create_plan():

    data = request.get_json()

    # בדיקת שדות חובה
    required_fields = ['date', 'quantity', 'status', 'notes', 'customer', 'priority']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing one or more required fields'}), 400
    
    #  בדיקת תקינות ערכים
    try:
        datetime.strptime(data['date'], '%Y-%m-%d')
        quantity = int(data['quantity'])
        if quantity <= 0:
            raise ValueError
    except:
        return jsonify({'error': 'Invalid date or quantity'}), 400


    db = get_db()
    db.execute('''
    INSERT INTO ProductionPlans (date, quantity, status, notes, customer, priority)
    VALUES (?, ?, ?, ?, ?, ?)
''', (
    data['date'],
    data['quantity'],
    data['status'],
    data['notes'],
    data['customer'],
    data['priority']
    ))
    
    db.commit()
    return jsonify({'message': 'Production plan created successfully'}), 201


@production_bp.route('/export-excel')
def export_excel():
    db = get_db()
    plans = db.execute('SELECT * FROM ProductionPlans').fetchall()

    # יצירת קובץ Excel חדש
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "תוכניות ייצור"

    # כותרות
    headers = ['ID', 'Date', 'Customer', 'Status', 'Quality Status', 'Quality Notes']
    ws.append(headers)

    # נתונים
    for row in plans:
        ws.append([
            row['id'],
            row['date'],
            row['customer'],
            row['status'],
            row['quality_status'],
            row['quality_notes']
        ])

    # שליחה כקובץ להורדה
    output = BytesIO()
    wb.save(output)
    output.seek(0)

    return send_file(output, as_attachment=True,
                     download_name="production_plans.xlsx",
                     mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")


@production_bp.route('/<int:plan_id>/update-status', methods=['POST'])
def update_status(plan_id):
    db = get_db()

    # שלב ראשון: בדוק את הסטטוס הנוכחי
    current = db.execute('SELECT status FROM ProductionPlans WHERE id = ?', (plan_id,)).fetchone()
    if not current:
        return jsonify({'error': 'תוכנית לא נמצאה'}), 404

    if current['status'] in ['עבר בקרת איכות', 'נכשל בקרת איכות']:
        return jsonify({'error': 'לא ניתן לעדכן תוכנית שעברה בקרת איכות'}), 403

    # המשך עדכון
    data = request.get_json()
    new_status = data.get('status')

    db.execute('UPDATE ProductionPlans SET status = ? WHERE id = ?', (new_status, plan_id))
    db.commit()

    return jsonify({'success': True, 'id': plan_id, 'new_status': new_status})

@production_bp.route('/priority-distribution', methods=['GET'])
def get_priority_distribution():
    db = get_db()
    rows = db.execute('''
        SELECT priority, COUNT(*) as count
        FROM ProductionPlans
        GROUP BY priority
    ''').fetchall()

    distribution = {row['priority']: row['count'] for row in rows}
    return jsonify(distribution)

@production_bp.route('/edit/<int:plan_id>', methods=['GET', 'POST'])
def edit_plan(plan_id):
    db = get_db()

    # בדיקת סטטוס לפני עדכון
    current = db.execute('SELECT status FROM ProductionPlans WHERE id = ?', (plan_id,)).fetchone()
    if not current:
        return "תוכנית לא נמצאה", 404

    if request.method == 'POST':
        if current['status'] in ['עבר בקרת איכות', 'נכשל בקרת איכות']:
            return "⛔ לא ניתן לערוך תוכנית שעברה בקרת איכות", 403

        date = request.form['date']
        quantity = request.form['quantity']
        status = request.form['status']
        priority = request.form['priority']
        customer = request.form['customer']
        notes = request.form['notes']

        db.execute('''
            UPDATE ProductionPlans
            SET date = ?, quantity = ?, status = ?, priority = ?, customer = ?, notes = ?
            WHERE id = ?
        ''', (date, quantity, status, priority, customer, notes, plan_id))
        db.commit()

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify(success=True)

        return redirect(url_for('dashboard'))

    # GET – שליפה להצגת התוכנית בטופס
    plan = db.execute('SELECT * FROM ProductionPlans WHERE id = ?', (plan_id,)).fetchone()
    return render_template('edit_plan.html', plan=plan)

@production_bp.route('/delete/<int:plan_id>', methods=['POST'])
def delete_plan(plan_id):
    db = get_db()
    db.execute('DELETE FROM ProductionPlans WHERE id = ?', (plan_id,))
    db.commit()
    return redirect(url_for('dashboard'))
