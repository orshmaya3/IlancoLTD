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
    rows = db.execute("SELECT * FROM ProductionPlans").fetchall()
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
