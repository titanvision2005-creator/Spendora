import sqlite3
from datetime import datetime


DB_NAME = "expenses.db"


def connect_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def create_tables():
    conn = connect_db()
    cur = conn.cursor()

    # USERS
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
    """)

    # INCOME
    cur.execute("""
    CREATE TABLE IF NOT EXISTS income(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        amount REAL NOT NULL,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    """)

    # EXPENSES
    cur.execute("""
    CREATE TABLE IF NOT EXISTS expenses(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        category TEXT NOT NULL,
        amount REAL NOT NULL,
        date TEXT NOT NULL,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    """)

    # BUDGETS
    cur.execute("""
    CREATE TABLE IF NOT EXISTS budgets(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        category TEXT NOT NULL,
        amount REAL NOT NULL,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    """)

    # NOTIFICATIONS
    cur.execute("""
    CREATE TABLE IF NOT EXISTS notifications(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        message TEXT NOT NULL,
        created_at TEXT NOT NULL,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    """)

    # RECURRING
    cur.execute("""
    CREATE TABLE IF NOT EXISTS recurring(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        category TEXT NOT NULL,
        amount REAL NOT NULL,
        day_no INTEGER NOT NULL,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    """)

    conn.commit()
    conn.close()


# ---------------- USERS ----------------

def register_user(name, email, hashed_password):
    conn = connect_db()
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO users(name,email,password)
    VALUES(?,?,?)
    """, (name, email, hashed_password))

    conn.commit()
    conn.close()


def get_user_by_email(email):
    conn = connect_db()
    cur = conn.cursor()

    cur.execute("""
    SELECT * FROM users WHERE email=?
    """, (email,))

    user = cur.fetchone()

    conn.close()
    return user


# ---------------- INCOME ----------------

def save_income(user_id, amount):
    conn = connect_db()
    cur = conn.cursor()

    cur.execute("DELETE FROM income WHERE user_id=?", (user_id,))
    cur.execute("""
    INSERT INTO income(user_id,amount)
    VALUES(?,?)
    """, (user_id, amount))

    conn.commit()
    conn.close()


def get_income(user_id):
    conn = connect_db()
    cur = conn.cursor()

    cur.execute("""
    SELECT amount FROM income WHERE user_id=?
    """, (user_id,))

    row = cur.fetchone()

    conn.close()

    if row:
        return row["amount"]
    return 0


# ---------------- EXPENSES ----------------

def add_expense(user_id, category, amount, date):
    conn = connect_db()
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO expenses(user_id,category,amount,date)
    VALUES(?,?,?,?)
    """, (user_id, category, amount, date))

    conn.commit()
    conn.close()


def get_total_expense(user_id):
    conn = connect_db()
    cur = conn.cursor()

    cur.execute("""
    SELECT SUM(amount) AS total
    FROM expenses
    WHERE user_id=?
    """, (user_id,))

    row = cur.fetchone()

    conn.close()

    if row["total"]:
        return row["total"]
    return 0


def get_recent_expenses(user_id):
    conn = connect_db()
    cur = conn.cursor()

    cur.execute("""
    SELECT id, category, amount, date
    FROM expenses
    WHERE user_id=?
    ORDER BY id DESC
    LIMIT 5
    """, (user_id,))

    rows = cur.fetchall()

    conn.close()
    return rows


def search_expenses(user_id, keyword):
    conn = connect_db()
    cur = conn.cursor()

    cur.execute("""
    SELECT id, category, amount, date
    FROM expenses
    WHERE user_id=?
    AND category LIKE ?
    ORDER BY id DESC
    """, (user_id, f"%{keyword}%"))

    rows = cur.fetchall()

    conn.close()
    return rows


def delete_expense(user_id, expense_id):
    conn = connect_db()
    cur = conn.cursor()

    cur.execute("""
    DELETE FROM expenses
    WHERE id=? AND user_id=?
    """, (expense_id, user_id))

    conn.commit()
    conn.close()


# ---------------- CHARTS ----------------

def get_chart_data(user_id):
    conn = connect_db()
    cur = conn.cursor()

    cur.execute("""
    SELECT category, SUM(amount) AS total
    FROM expenses
    WHERE user_id=?
    GROUP BY category
    """, (user_id,))

    rows = cur.fetchall()

    conn.close()
    return rows


# ---------------- BUDGETS ----------------

def save_budget(user_id, category, amount):
    conn = connect_db()
    cur = conn.cursor()

    cur.execute("""
    DELETE FROM budgets
    WHERE user_id=? AND category=?
    """, (user_id, category))

    cur.execute("""
    INSERT INTO budgets(user_id,category,amount)
    VALUES(?,?,?)
    """, (user_id, category, amount))

    conn.commit()
    conn.close()


def get_budgets(user_id):
    conn = connect_db()
    cur = conn.cursor()

    cur.execute("""
    SELECT category, amount
    FROM budgets
    WHERE user_id=?
    """, (user_id,))

    rows = cur.fetchall()

    conn.close()
    return rows


# ---------------- NOTIFICATIONS ----------------

def add_notification(user_id, message):
    conn = connect_db()
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO notifications(user_id,message,created_at)
    VALUES(?,?,?)
    """, (
        user_id,
        message,
        datetime.now().strftime("%Y-%m-%d %H:%M")
    ))

    conn.commit()
    conn.close()


def get_notifications(user_id):
    conn = connect_db()
    cur = conn.cursor()

    cur.execute("""
    SELECT message, created_at
    FROM notifications
    WHERE user_id=?
    ORDER BY id DESC
    LIMIT 5
    """, (user_id,))

    rows = cur.fetchall()

    conn.close()
    return rows


# ---------------- RECURRING ----------------

def add_recurring(user_id, category, amount, day_no):
    conn = connect_db()
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO recurring(user_id,category,amount,day_no)
    VALUES(?,?,?,?)
    """, (user_id, category, amount, day_no))

    conn.commit()
    conn.close()


def get_recurring(user_id):
    conn = connect_db()
    cur = conn.cursor()

    cur.execute("""
    SELECT category, amount, day_no
    FROM recurring
    WHERE user_id=?
    """, (user_id,))

    rows = cur.fetchall()

    conn.close()
    return rows