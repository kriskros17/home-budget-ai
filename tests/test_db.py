import pytest
import db


@pytest.fixture(autouse=True)
def fresh_db(tmp_path, monkeypatch):
    monkeypatch.setattr(db, "DB_NAME", str(tmp_path / "test.db"))
    db.init_db()


def test_init_db_twice_does_not_fail():
    db.init_db()
    db.init_db()


def test_expense_is_saved_as_negative():
    db.add_expense("2024-06-01", "Pizza", 40, "Food")
    assert db.get_transactions()[0][3] == -40


def test_expense_entered_as_negative_stays_negative():
    db.add_expense("2024-06-01", "Coffee", -12, "Food")
    assert db.get_transactions()[0][3] == -12


def test_income_is_saved_as_positive():
    db.add_income("2024-06-01", "Salary", 5000, "Income")
    assert db.get_transactions()[0][3] == 5000


def test_get_transactions_returns_rows_with_id():
    db.add_expense("2023-01-01", "Test Expense", 100.0, "Test Category")
    db.add_income("2023-01-02", "Test Income", 200.0, "Test Category")
    assert db.get_transactions() == [
        (1, "2023-01-01", "Test Expense", -100.0, "Test Category"),
        (2, "2023-01-02", "Test Income", 200.0, "Test Category"),
    ]


def test_totals_by_category():
    db.add_expense("2024-06-03", "Groceries", 50, "Food")
    db.add_expense("2024-06-04", "Coffee", 5, "Food")
    db.add_expense("2024-06-05", "Tram ticket", 10, "Transport")
    assert dict(db.get_totals_by_category()) == {"Food": -55, "Transport": -10}

def test_cancel_existing_subscription():
    db.add_subscription("Netflix", 15, "monthly", "2024-06-01", 1)
    db.cancel_subscription(1)
    assert db.get_subscriptions()[0][5] == 0


def test_cancel_nonexistent_subscription():
    result = db.cancel_subscription(999)
    assert result is False

def test_delete_subscription():
    db.add_subscription("Spotify", 10, "monthly", "2024-06-01", 1)
    db.delete_subscription(1)
    assert db.get_subscriptions() == []


def test_add_to_goal_increases_saved_amount():
    db.add_goal("Vacation", 1000, 200, 1)
    db.add_to_goal(1, 200)
    assert db.get_goals()[0][3] == 400


def test_add_to_goal_nonexistent_returns_false():
    result = db.add_to_goal(999, 100)
    assert result is False

def test_delete_goal():
    db.add_goal("New Car", 5000, 1000, 1)
    db.delete_goal(1)
    assert db.get_goals() == []


def test_set_budget_adds_new_limit():
    db.set_budget("Food", 300)
    assert db.get_budgets()[0][1] == "Food"
    assert db.get_budgets()[0][2] == 300


def test_set_budget_updates_existing_limit():
    db.set_budget("Food", 300)
    db.set_budget("Food", 400)
    db.set_budget("Food", 500)
    assert len(db.get_budgets()) == 1
    assert db.get_budgets()[0][2] == 500

def test_set_budget_keeps_id():
    db.set_budget("Food", 300)
    db.set_budget("Food", 400)
    assert db.get_budgets()[0][0] == 1