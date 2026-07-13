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
            invoice_number TEXT,
            created_at TEXT NOT NULL,
            ip_address TEXT
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS company (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            address TEXT,
            phone TEXT,
            email TEXT,
            tax_number TEXT,
            iban TEXT,
            bic TEXT,
            updated_at TEXT
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS pro_users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ip_address TEXT,
            stripe_session_id TEXT,
            created_at TEXT
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
            ai_content, invoice_number, created_at, ip_address
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
        data['invoice_number'],
        datetime.now().isoformat(),
        data.get('ip_address', '')
    ))

    doc_id = c.lastrowid
    conn.commit()
    conn.close()
    return doc_id

def get_next_invoice_number():
    conn = sqlite3.connect('handwerker.db')
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM documents WHERE type = 'rechnung'")
    count = c.fetchone()[0]
    conn.close()
    year = datetime.now().year
    return f"RE-{year}-{(count + 1):04d}"

def get_next_offer_number():
    conn = sqlite3.connect('handwerker.db')
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM documents WHERE type = 'angebot'")
    count = c.fetchone()[0]
    conn.close()
    year = datetime.now().year
    return f"AN-{year}-{(count + 1):04d}"

def save_company(data):
    conn = sqlite3.connect('handwerker.db')
    c = conn.cursor()
    c.execute('DELETE FROM company')
    c.execute('''
        INSERT INTO company (name, address, phone, email, tax_number, iban, bic, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        data['name'],
        data['address'],
        data['phone'],
        data['email'],
        data['tax_number'],
        data['iban'],
        data['bic'],
        datetime.now().isoformat()
    ))
    conn.commit()
    conn.close()

def get_company():
    conn = sqlite3.connect('handwerker.db')
    c = conn.cursor()
    c.execute('SELECT * FROM company LIMIT 1')
    row = c.fetchone()
    conn.close()
    if row:
        return {
            'name': row[1],
            'address': row[2],
            'phone': row[3],
            'email': row[4],
            'tax_number': row[5],
            'iban': row[6],
            'bic': row[7]
        }
    return {}

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

def get_monthly_usage(ip_address):
    conn = sqlite3.connect('handwerker.db')
    c = conn.cursor()
    month = datetime.now().strftime('%Y-%m')
    c.execute('''
        SELECT COUNT(*) FROM documents
        WHERE ip_address = ? AND created_at LIKE ?
    ''', (ip_address, f'{month}%'))
    count = c.fetchone()[0]
    conn.close()
    return count

def save_pro_user(ip_address, session_id):
    conn = sqlite3.connect('handwerker.db')
    c = conn.cursor()
    c.execute('''
        INSERT INTO pro_users (ip_address, stripe_session_id, created_at)
        VALUES (?, ?, ?)
    ''', (ip_address, session_id, datetime.now().isoformat()))
    conn.commit()
    conn.close()

def check_is_pro(ip_address):
    conn = sqlite3.connect('handwerker.db')
    c = conn.cursor()
    c.execute('SELECT * FROM pro_users WHERE ip_address = ?', (ip_address,))
    row = c.fetchone()
    conn.close()
    return row is not None