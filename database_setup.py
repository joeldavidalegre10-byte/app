# database_setup.py
import sqlite3
import os
import hashlib

DB_FILE = "supermarket.db"

CASHIERS_DATA = [
    {"id": 1, "name": "Caja 01", "status": "open", "operator": "María González", "sales": 156},
    {"id": 2, "name": "Caja 02", "status": "open", "operator": "Juan Pérez", "sales": 143},
    {"id": 3, "name": "Caja 03", "status": "closed", "operator": None, "sales": 0},
    {"id": 4, "name": "Caja 04", "status": "open", "operator": "Ana Silva", "sales": 98},
    {"id": 5, "name": "Caja 05", "status": "closed", "operator": None, "sales": 0},
    {"id": 6, "name": "Caja 06", "status": "open", "operator": "Carlos Ruiz", "sales": 167},
    {"id": 7, "name": "Caja 07", "status": "maintenance", "operator": None, "sales": 0},
    {"id": 8, "name": "Caja 08", "status": "open", "operator": "Laura Díaz", "sales": 89},
    {"id": 9, "name": "Caja 09", "status": "open", "operator": "Roberto Sánchez", "sales": 134},
    {"id": 10, "name": "Caja 10", "status": "closed", "operator": None, "sales": 0},
    {"id": 11, "name": "Caja 11", "status": "open", "operator": "Patricia López", "sales": 112},
    {"id": 12, "name": "Caja 12", "status": "maintenance", "operator": None, "sales": 0},
    {"id": 13, "name": "Caja 13", "status": "open", "operator": "Diego Fernández", "sales": 78},
    {"id": 14, "name": "Caja 14", "status": "closed", "operator": None, "sales": 0},
    {"id": 15, "name": "Caja 15", "status": "maintenance", "operator": None, "sales": 0},
    {"id": 16, "name": "Caja 16", "status": "open", "operator": "Sofía Ramírez", "sales": 145},
    {"id": 17, "name": "Caja 17", "status": "open", "operator": "Miguel Torres", "sales": 91},
    {"id": 18, "name": "Caja 18", "status": "closed", "operator": None, "sales": 0},
    {"id": 19, "name": "Caja 19", "status": "maintenance", "operator": None, "sales": 0},
    {"id": 20, "name": "Caja 20", "status": "open", "operator": "Carmen Vargas", "sales": 156},
    {"id": 21, "name": "Caja 21", "status": "maintenance", "operator": None, "sales": 0},
    {"id": 22, "name": "Caja 22", "status": "closed", "operator": None, "sales": 0},
    {"id": 23, "name": "Caja 23", "status": "maintenance", "operator": None, "sales": 0},
    {"id": 24, "name": "Caja 24", "status": "open", "operator": "Fernando Castro", "sales": 102},
]

MAINTENANCE_DATA = [
    {"cashier_id": 7, "issue": "Impresora de tickets no funciona", "details": "La impresora térmica no responde. Revisar cable de alimentación y conectividad USB.", "reported_by": "Ana Silva", "reported_date": "08/10/2025", "estimated_days": 2, "priority": "high"},
    {"cashier_id": 12, "issue": "Lector de código de barras intermitente", "details": "El escáner funciona de forma intermitente. Posible problema de cable o necesita reemplazo.", "reported_by": "Carlos Ruiz", "reported_date": "07/10/2025", "estimated_days": 1, "priority": "medium"},
    {"cashier_id": 15, "issue": "Cajón de dinero atascado", "details": "El mecanismo del cajón está trabado. Requiere limpieza y lubricación.", "reported_by": "María González", "reported_date": "06/10/2025", "estimated_days": 1, "priority": "high"},
    {"cashier_id": 19, "issue": "Pantalla táctil descalibrada", "details": "La pantalla no responde correctamente al tacto. Necesita recalibración o reemplazo.", "reported_by": "Juan Pérez", "reported_date": "09/10/2025", "estimated_days": 3, "priority": "medium"},
    {"cashier_id": 21, "issue": "Teclado numérico no funciona", "details": "Algunas teclas del teclado numérico no registran. Probablemente requiere reemplazo.", "reported_by": "Laura Díaz", "reported_date": "05/10/2025", "estimated_days": 2, "priority": "low"},
    {"cashier_id": 23, "issue": "Sistema operativo lento", "details": "El sistema tarda mucho en iniciar y procesar operaciones. Requiere optimización o actualización.", "reported_by": "Pedro Martínez", "reported_date": "04/10/2025", "estimated_days": 4, "priority": "low"},
]

EARNINGS_DATA = {
    "today": {"total": 45230, "transactions": 152, "avg": 297},
    "week": [
        {"day": "Lun", "amount": 38420, "profit": 11526, "transactions": 145},
        {"day": "Mar", "amount": 42150, "profit": 12645, "transactions": 162},
        {"day": "Mié", "amount": 39870, "profit": 11961, "transactions": 138},
        {"day": "Jue", "amount": 44200, "profit": 13260, "transactions": 178},
        {"day": "Vie", "amount": 51340, "profit": 15402, "transactions": 195},
        {"day": "Sáb", "amount": 62580, "profit": 18774, "transactions": 234},
        {"day": "Dom", "amount": 35120, "profit": 10536, "transactions": 126},
    ],
    "month": {
        "total": 1250430,
        "profit": 375129,
        "growth": 18,
        "weeks": [
            {"week": "Semana 1", "amount": 298450, "profit": 89535, "transactions": 1234},
            {"week": "Semana 2", "amount": 315680, "profit": 94704, "transactions": 1301},
            {"week": "Semana 3", "amount": 287920, "profit": 86376, "transactions": 1189},
            {"week": "Semana 4", "amount": 348380, "profit": 104514, "transactions": 1432},
        ]
    },
}

INVENTORY_DATA = [
    {"id": 1, "name": "Laptop Dell XPS 15", "sku": "LAP-001", "stock": 45, "min_stock": 10, "price": 1299.99, "category": "Electrónica"},
    {"id": 2, "name": "Mouse Logitech MX Master", "sku": "ACC-002", "stock": 8, "min_stock": 15, "price": 99.99, "category": "Accesorios"},
    {"id": 3, "name": "Teclado Mecánico RGB", "sku": "ACC-003", "stock": 120, "min_stock": 20, "price": 149.99, "category": "Accesorios"},
    {"id": 4, "name": "Monitor LG 27 UHD", "sku": "MON-004", "stock": 67, "min_stock": 15, "price": 449.99, "category": "Monitores"},
    {"id": 5, "name": "Webcam Logitech C920", "sku": "ACC-005", "stock": 5, "min_stock": 10, "price": 79.99, "category": "Accesorios"},
]

SALES_DATA = [
    {"id": 1, "cashier": "Caja 01", "amount": 1250.50, "items": 8, "time": "14:32", "payment": "Tarjeta", "customer": "Cliente Regular", "status": "completed"},
    {"id": 2, "cashier": "Caja 02", "amount": 856.00, "items": 5, "time": "14:28", "payment": "Efectivo", "customer": "Nuevo Cliente", "status": "completed"},
    {"id": 3, "cashier": "Caja 04", "amount": 2340.75, "items": 12, "time": "14:15", "payment": "Tarjeta", "customer": "Cliente VIP", "status": "completed"},
    {"id": 4, "cashier": "Caja 01", "amount": 456.20, "items": 3, "time": "14:05", "payment": "Efectivo", "customer": "Cliente Regular", "status": "completed"},
    {"id": 5, "cashier": "Caja 06", "amount": 1890.00, "items": 7, "time": "13:58", "payment": "Tarjeta", "customer": "Cliente Regular", "status": "pending"},
    {"id": 6, "cashier": "Caja 08", "amount": 345.75, "items": 4, "time": "13:45", "payment": "Efectivo", "customer": "Cliente Regular", "status": "refunded"},
    {"id": 7, "cashier": "Caja 02", "amount": 678.90, "items": 6, "time": "13:30", "payment": "Tarjeta", "customer": "Cliente VIP", "status": "completed"},
    {"id": 8, "cashier": "Caja 04", "amount": 234.50, "items": 2, "time": "13:20", "payment": "Efectivo", "customer": "Nuevo Cliente", "status": "pending"},
]

# --- FUNCIÓN DE HASHING ---
def hash_password(password):
    """Genera un hash SHA-256 seguro para la contraseña."""
    return hashlib.sha256(password.encode()).hexdigest()


def setup_database():

    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)
        print(f"Archivo '{DB_FILE}' anterior eliminado.")

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE cashiers (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        status TEXT NOT NULL,
        operator TEXT,
        sales INTEGER DEFAULT 0
    )
    ''')
    cashiers_to_insert = [(c['id'], c['name'], c['status'], c['operator'], c['sales']) for c in CASHIERS_DATA]
    cursor.executemany("INSERT INTO cashiers VALUES (?, ?, ?, ?, ?)", cashiers_to_insert)
    print(f"Tabla 'cashiers' creada y {len(cashiers_to_insert)} registros insertados.")

    cursor.execute('''
    CREATE TABLE maintenance_tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cashier_id INTEGER NOT NULL,
        issue TEXT NOT NULL,
        details TEXT,
        reported_by TEXT,
        reported_date TEXT,
        estimated_days INTEGER,
        priority TEXT,
        FOREIGN KEY(cashier_id) REFERENCES cashiers(id)
    )
    ''')
    tasks_to_insert = [(mt['cashier_id'], mt['issue'], mt['details'], mt['reported_by'], mt['reported_date'], mt['estimated_days'], mt['priority']) for mt in MAINTENANCE_DATA]
    cursor.executemany("INSERT INTO maintenance_tasks (cashier_id, issue, details, reported_by, reported_date, estimated_days, priority) VALUES (?, ?, ?, ?, ?, ?, ?)", tasks_to_insert)
    print(f"Tabla 'maintenance_tasks' creada y {len(tasks_to_insert)} registros insertados.")


    cursor.execute('''
    CREATE TABLE inventory (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        sku TEXT NOT NULL UNIQUE,
        stock INTEGER DEFAULT 0,
        min_stock INTEGER DEFAULT 0,
        price REAL DEFAULT 0.0,
        category TEXT
    )
    ''')
    inventory_to_insert = [(p['id'], p['name'], p['sku'], p['stock'], p['min_stock'], p['price'], p['category']) for p in INVENTORY_DATA]
    cursor.executemany("INSERT INTO inventory VALUES (?, ?, ?, ?, ?, ?, ?)", inventory_to_insert)
    print(f"Tabla 'inventory' creada y {len(inventory_to_insert)} registros insertados.")

    cursor.execute('''
    CREATE TABLE sales (
        id INTEGER PRIMARY KEY,
        cashier TEXT NOT NULL,
        amount REAL NOT NULL,
        items INTEGER,
        time TEXT,
        payment TEXT,
        customer TEXT,
        status TEXT
    )
    ''')
    sales_to_insert = [(s['id'], s['cashier'], s['amount'], s['items'], s['time'], s['payment'], s['customer'], s['status']) for s in SALES_DATA]
    cursor.executemany("INSERT INTO sales VALUES (?, ?, ?, ?, ?, ?, ?, ?)", sales_to_insert)
    print(f"Tabla 'sales' creada y {len(sales_to_insert)} registros insertados.")

    cursor.execute("CREATE TABLE today_earnings (total REAL, transactions INTEGER, avg REAL)")
    today = EARNINGS_DATA['today']
    cursor.execute("INSERT INTO today_earnings VALUES (?, ?, ?)", (today['total'], today['transactions'], today['avg']))
    print("Tabla 'today_earnings' creada.")

    cursor.execute("CREATE TABLE daily_earnings (day TEXT PRIMARY KEY, amount REAL, profit REAL, transactions INTEGER)")
    week_data = [(d['day'], d['amount'], d['profit'], d['transactions']) for d in EARNINGS_DATA['week']]
    cursor.executemany("INSERT INTO daily_earnings VALUES (?, ?, ?, ?)", week_data)
    print(f"Tabla 'daily_earnings' creada y {len(week_data)} registros insertados.")
    
    cursor.execute("CREATE TABLE weekly_earnings (week TEXT PRIMARY KEY, amount REAL, profit REAL, transactions INTEGER)")
    month_week_data = [(w['week'], w['amount'], w['profit'], w['transactions']) for w in EARNINGS_DATA['month']['weeks']]
    cursor.executemany("INSERT INTO weekly_earnings VALUES (?, ?, ?, ?)", month_week_data)
    print(f"Tabla 'weekly_earnings' creada y {len(month_week_data)} registros insertados.")

    cursor.execute("CREATE TABLE month_stats (total REAL, profit REAL, growth INTEGER)")
    month = EARNINGS_DATA['month']
    cursor.execute("INSERT INTO month_stats VALUES (?, ?, ?)", (month['total'], month['profit'], month['growth']))
    print("Tabla 'month_stats' creada.")
    

    cursor.execute('''
    CREATE TABLE users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL CHECK(role IN ('admin', 'user'))
    )
    ''')
    
    users_to_create = [
        ("1", "1", "admin"),
        ("joel", "joel", "admin"),
        ("joela", "joela", "user"),
        ("admin_jp", "AdminPass@1", "admin"),
        ("admin_mg", "AdminPass@2", "admin"),
        ("admin_as", "AdminPass@3", "admin"),
        ("admin_cr", "AdminPass@4", "admin"),
        ("admin_root", "SuperPass@25", "admin"),
        ("user_ld", "UserPass#10", "user"),
        ("user_rs", "UserPass#20", "user"),
        ("user_pl", "UserPass#30", "user"),
        ("user_df", "UserPass#40", "user"),
        ("user_caja", "CajaPass#50", "user"),
    ]
    
    users_to_insert = []
    for username, plain_password, role in users_to_create:
        hashed_pass = hash_password(plain_password)
        users_to_insert.append((username, hashed_pass, role))
        
    cursor.executemany("INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)", users_to_insert)
    print(f"Tabla 'users' creada y {len(users_to_insert)} usuarios insertados.")


    conn.commit()
    conn.close()
    print(f"\n¡Base de datos '{DB_FILE}' creada y poblada con éxito!")

if __name__ == "__main__":
    setup_database()