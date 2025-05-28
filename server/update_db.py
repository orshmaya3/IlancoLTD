import sqlite3

# התחברות למסד הנתונים
conn = sqlite3.connect('../database/people.db')
cur = conn.cursor()

# הוספת העמודות אם לא קיימות
try:
    cur.execute("ALTER TABLE ProductionPlans ADD COLUMN quality_status TEXT;")
except sqlite3.OperationalError:
    print("עמודה quality_status כבר קיימת.")

try:
    cur.execute("ALTER TABLE ProductionPlans ADD COLUMN quality_notes TEXT;")
except sqlite3.OperationalError:
    print("עמודה quality_notes כבר קיימת.")

conn.commit()
conn.close()
print("✅ סיום עדכון מבנה הטבלה.")