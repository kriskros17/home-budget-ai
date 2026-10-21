import sqlite3

DB_NAME = 'budget.db'

def get_connection():
    return sqlite3.connect(DB_NAME)

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS transactions(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT NOT NULL,
        description TEXT NOT NULL,
        amount REAL NOT NULL,
        category TEXT NOT NULL  
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS subscriptions(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        amount REAL NOT NULL CHECK(amount > 0),
        cycle TEXT NOT NULL CHECK(cycle IN ('monthly', 'yearly')),
        next_payment TEXT NOT NULL,
        active INTEGER NOT NULL CHECK(active IN (0, 1))
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS budgets(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category TEXT NOT NULL UNIQUE,
        monthly_limit REAL NOT NULL 
    )
    """)


    cursor.execute("""
    CREATE TABLE IF NOT EXISTS goals(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        target_amount REAL NOT NULL,
        saved_amount REAL NOT NULL DEFAULT 0,
        priority INTEGER NOT NULL
    )
    """)

    conn.commit()
    conn.close()

def add_transaction(date, description, amount, category):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO transactions (date, description, amount, category) VALUES (?, ?, ?, ?)",
            (date, description, amount, category)
        )
        conn.commit()
    finally:
        conn.close()
    

def add_subscription(name, amount, cycle, next_payment, active):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "INSERT INTO subscriptions (name, amount, cycle, next_payment, active) VALUES (?, ?, ?, ?, ?)",
            (name, amount, cycle, next_payment, active)
        )
        conn.commit()
    finally:
        conn.close()
   


def add_budget(category, monthly_limit):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "INSERT INTO budgets (category, monthly_limit) VALUES (?, ?)",
            (category, monthly_limit)
        )
        conn.commit()
    finally:
        conn.close()

def add_goal(name, target_amount, saved_amount, priority):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "INSERT INTO goals (name, target_amount, saved_amount, priority) VALUES (?, ?, ?, ?)",
            (name, target_amount, saved_amount, priority)
        )
        conn.commit()
    finally:
        conn.close()

    


def get_subscriptions():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM subscriptions")
    subscriptions = cursor.fetchall()
    conn.close()
    return subscriptions

def get_budgets():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM budgets")
    budgets = cursor.fetchall()
    conn.close()
    return budgets

def get_goals():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM goals")
    goals = cursor.fetchall()
    conn.close()
    return goals



def get_transactions():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM transactions")
    transactions = cursor.fetchall()
    conn.close()
    return transactions


def delete_subscription(subscription_id):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("DELETE FROM subscriptions WHERE id = ?", (subscription_id,))
        conn.commit()
    finally:
        conn.close()


def delete_goal(goal_id):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("DELETE FROM goals WHERE id = ?", (goal_id,))
        conn.commit()
    finally:
        conn.close()


def add_expense(date, description, amount, category):
    amount = -abs(amount)  
    add_transaction(date, description, amount, category)


def add_income(date, description, amount, category):
    amount = abs(amount)  
    add_transaction(date, description, amount, category)


def get_totals_by_category():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT category, SUM(amount) as total
    FROM transactions
    GROUP BY category
    """)
    totals = cursor.fetchall()
    conn.close()
    return totals

def cancel_subscription(subscription_id):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("UPDATE subscriptions SET active = 0 WHERE id = ?", (subscription_id,))
        conn.commit()
        return cursor.rowcount > 0 
    finally:
        conn.close()


def add_to_goal(goal_id, amount):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("UPDATE goals SET saved_amount = saved_amount + ? WHERE id = ?", (amount, goal_id))
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()

def set_budget(category, monthly_limit):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("INSERT INTO budgets (category, monthly_limit) VALUES (?, ?) ON CONFLICT(category) DO UPDATE SET monthly_limit = excluded.monthly_limit", (category, monthly_limit))
        conn.commit()
    finally:
        conn.close()

if __name__ == "__main__":
    init_db()


    add_income("2024-06-01", "Salary", 5000, "Income")
    add_expense("2024-06-02", "Groceries", 100, "Food")
    add_expense("2026-06-03", "Tram ticket", 2.5, "Transport")
    add_expense("2024-06-04", "Coffee", -12, "Food")


    for transaction in get_transactions():
        print(transaction)

    for total in get_totals_by_category():
        print(total)


    add_subscription("Netflix", 15.99, "monthly", "2024-07-01", 1)
    add_subscription("Spotify", 9.99, "monthly", "2024-07-01", 1)

    for subscription in get_subscriptions():
        print(subscription)

    print("Cancelling Netflix subscription...")
    print(cancel_subscription(1))

    print("Subscription which never exist:")
    print(cancel_subscription(999)) 

    for subscription in get_subscriptions():
        print(subscription)

    delete_subscription(2)

    for subscription in get_subscriptions():
        print(subscription)


    add_goal("Vacation", 2000, 500, 1)
    add_goal("New Laptop", 1500, 300, 2)
    add_to_goal(1, 200)
    for goal in get_goals():
        print(goal)
    print(add_to_goal(999, 300))
    delete_goal(1)
    for goal in get_goals():
        print(goal)

    set_budget("Food", 300)
    set_budget("Food", 400)
    set_budget("Food", 500)
    for budget in get_budgets():
        print(budget)
    set_budget("Transport", 150)
    for budget in get_budgets():
        print(budget)


    