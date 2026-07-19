import sqlite3
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

def init_db():
    conn = sqlite3.connect('handwerker.db')
    c = conn.cursor()

    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
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
            ip_address TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS company (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
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
            user_id INTEGER,
            ip_address TEXT,
            stripe_session_id TEXT,
            created_at TEXT
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            address TEXT,
            email TEXT,
            phone TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    conn.commit()
    conn.close()

# ── USER FUNCTIONS ───────────────────────────────────
def create_user(email, password):
    conn = sqlite3.connect('handwerker.db')
    c = conn.cursor()
    try:
        c.execute('''
            INSERT INTO users (email, password_hash, created_at)
            VALUES (?, ?, ?)
        ''', (email, generate_password_hash(password), datetime.now().isoformat()))
        conn.commit()
        user_id = c.lastrowid
        conn.close()
        return user_id
    except sqlite3.IntegrityError:
        conn.close()
        return None

def get_user_by_email(email):
    conn = sqlite3.connect('handwerker.db')
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE email = ?', (email,))
    row = c.fetchone()
    conn.close()
    return row

def get_user_by_id(user_id):
    conn = sqlite3.connect('handwerker.db')
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    row = c.fetchone()
    conn.close()
    return row

def verify_password(email, password):
    user = get_user_by_email(email)
    if user and check_password_hash(user[2], password):
        return user
    return None

# ── DOCUMENT FUNCTIONS ───────────────────────────────
def save_document(data):
    conn = sqlite3.connect('handwerker.db')
    c = conn.cursor()
    c.execute('''
        INSERT INTO documents (
            user_id, type, customer_name, customer_address,
            job_description, materials, hours,
            hourly_rate, total_net, vat, total_gross,
            ai_content, invoice_number, created_at, ip_address
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        data['user_id'],
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

def get_next_invoice_number(user_id):
    conn = sqlite3.connect('handwerker.db')
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM documents WHERE user_id = ? AND type = 'rechnung'", (user_id,))
    count = c.fetchone()[0]
    conn.close()
    year = datetime.now().year
    return f"RE-{year}-{(count + 1):04d}"

def get_next_offer_number(user_id):
    conn = sqlite3.connect('handwerker.db')
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM documents WHERE user_id = ? AND type = 'angebot'", (user_id,))
    count = c.fetchone()[0]
    conn.close()
    year = datetime.now().year
    return f"AN-{year}-{(count + 1):04d}"

def get_all_documents(user_id):
    conn = sqlite3.connect('handwerker.db')
    c = conn.cursor()
    c.execute('SELECT * FROM documents WHERE user_id = ? ORDER BY created_at DESC', (user_id,))
    rows = c.fetchall()
    conn.close()
    return rows

def get_document(doc_id, user_id):
    conn = sqlite3.connect('handwerker.db')
    c = conn.cursor()
    c.execute('SELECT * FROM documents WHERE id = ? AND user_id = ?', (doc_id, user_id))
    row = c.fetchone()
    conn.close()
    return row

# ── COMPANY FUNCTIONS ────────────────────────────────
def save_company(data, user_id):
    conn = sqlite3.connect('handwerker.db')
    c = conn.cursor()
    c.execute('DELETE FROM company WHERE user_id = ?', (user_id,))
    c.execute('''
        INSERT INTO company (user_id, name, address, phone, email, tax_number, iban, bic, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        user_id,
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

def get_company(user_id):
    conn = sqlite3.connect('handwerker.db')
    c = conn.cursor()
    c.execute('SELECT * FROM company WHERE user_id = ? LIMIT 1', (user_id,))
    row = c.fetchone()
    conn.close()
    if row:
        return {
            'name': row[2],
            'address': row[3],
            'phone': row[4],
            'email': row[5],
            'tax_number': row[6],
            'iban': row[7],
            'bic': row[8]
        }
    return {}

# ── PRO USER FUNCTIONS ───────────────────────────────
def save_pro_user(user_id, session_id):
    conn = sqlite3.connect('handwerker.db')
    c = conn.cursor()
    c.execute('''
        INSERT INTO pro_users (user_id, stripe_session_id, created_at)
        VALUES (?, ?, ?)
    ''', (user_id, session_id, datetime.now().isoformat()))
    conn.commit()
    conn.close()

def check_is_pro(user_id):
    conn = sqlite3.connect('handwerker.db')
    c = conn.cursor()
    c.execute('SELECT * FROM pro_users WHERE user_id = ?', (user_id,))
    row = c.fetchone()
    conn.close()
    return row is not None

def get_monthly_usage(user_id):
    conn = sqlite3.connect('handwerker.db')
    c = conn.cursor()
    month = datetime.now().strftime('%Y-%m')
    c.execute('''
        SELECT COUNT(*) FROM documents
        WHERE user_id = ? AND created_at LIKE ?
    ''', (user_id, f'{month}%'))
    count = c.fetchone()[0]
    conn.close()
    return count

# ── CUSTOMER FUNCTIONS ───────────────────────────────
def save_customer(data, user_id):
    conn = sqlite3.connect('handwerker.db')
    c = conn.cursor()
    c.execute('''
        INSERT INTO customers (user_id, name, address, email, phone, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        user_id,
        data['name'],
        data['address'],
        data['email'],
        data['phone'],
        datetime.now().isoformat()
    ))
    customer_id = c.lastrowid
    conn.commit()
    conn.close()
    return customer_id

def get_customers(user_id):
    conn = sqlite3.connect('handwerker.db')
    c = conn.cursor()
    c.execute('SELECT * FROM customers WHERE user_id = ? ORDER BY name', (user_id,))
    rows = c.fetchall()
    conn.close()
    return rows

def get_customer(customer_id, user_id):
    conn = sqlite3.connect('handwerker.db')
    c = conn.cursor()
    c.execute('SELECT * FROM customers WHERE id = ? AND user_id = ?', (customer_id, user_id))
    row = c.fetchone()
    conn.close()
    return row