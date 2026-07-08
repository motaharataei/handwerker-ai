import sqlite3
from datetime import datetime

def init_db():
    conn = sqlite3.connect('handwerker.db')
    c = conn.cursor()
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT NOT NULL,
            customer_name TEXT NOT NULL,
            customer_address TEXT NOT NULL,
            job_description TEXT NOT NULL,
            materials TEXT,
            hours REAL,
            hourly_rate REAL,
            total_net REAL,
            vat REAL,
            total_gross REAL,
            ai_content TEXT,
            created_at TEXT NOT NULL
        )
    ''')
    
    conn.commit()
    conn.close()

def save_document(data):
    conn = sqlite3.connect('handwerker.db')
    c = conn.cursor()
    
    c.execute('''
        INSERT INTO documents (
            type, customer_name, customer_address,
            job_description, materials, hours,
            hourly_rate, total_net, vat, total_gross,
            ai_content, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        data['type'],
        data['customer_name'],
        data['customer_address'],
        data['job_description'],
        data['materials'],
        data['hours'],
        data['hourly_rate'],
        data['total_net'],
        data['vat'],
        data['total_gross'],
        data['ai_content'],
        datetime.now().isoformat()
    ))
    
    doc_id = c.lastrowid
    conn.commit()
    conn.close()
    return doc_id

def get_all_documents():
    conn = sqlite3.connect('handwerker.db')
    c = conn.cursor()
    c.execute('SELECT * FROM documents ORDER BY created_at DESC')
    rows = c.fetchall()
    conn.close()
    return rows

def get_document(doc_id):
    conn = sqlite3.connect('handwerker.db')
    c = conn.cursor()
    c.execute('SELECT * FROM documents WHERE id = ?', (doc_id,))
    row = c.fetchone()
    conn.close()
    return row