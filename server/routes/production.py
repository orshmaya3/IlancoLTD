from flask import Blueprint, request, jsonify ,render_template, make_response, session, redirect, url_for
from db import get_db
from xhtml2pdf import pisa
from io import BytesIO

production_bp = Blueprint('production', __name__, url_prefix='/api/production')

@production_bp.route('/', methods=['GET'])
def get_all_plans():
    db = get_db()
    rows = db.execute("SELECT * FROM ProductionPlans").fetchall()
    return jsonify([dict(row) for row in rows])

@production_bp.route('/', methods=['POST'])
def create_plan():
    data = request.get_json()

    # בדיקת שדות חובה
    required_fields = ['date', 'quantity', 'status', 'notes', 'customer', 'priority']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing one or more required fields'}), 400

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

@production_bp.route('/export/pdf', methods=['GET'])
def export_production_pdf():
    if session.get('role') not in ['admin', 'operator']:
        return redirect(url_for('login'))

    db = get_db()
    rows = db.execute('SELECT * FROM ProductionPlans').fetchall()

    html = render_template("pdf_template.html", plans=rows)
    pdf = BytesIO()
    pisa_status = pisa.CreatePDF(html, dest=pdf)

    if pisa_status.err:
        return "<h2>שגיאה ביצירת PDF</h2>"

    response = make_response(pdf.getvalue())
    response.headers["Content-Type"] = "application/pdf"
    response.headers["Content-Disposition"] = "attachment; filename=production_report.pdf"
    return response
