from flask import Blueprint, request, jsonify
from db import get_db

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