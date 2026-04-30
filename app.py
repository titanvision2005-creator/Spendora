import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, session

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

from database import (
    create_tables,
    register_user,
    get_user_by_email,
    save_income,
    get_income,
    add_expense,
    get_total_expense,
    get_recent_expenses,
    search_expenses,
    delete_expense,
    get_chart_data,
    save_budget,
    get_budgets,
    add_notification,
    get_notifications
)

from analysis import generate_analysis

app = Flask(__name__)

app.secret_key = os.environ.get(
    "SECRET_KEY",
    "spendora_local_key"
)

app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

create_tables()


# ---------------- HOME ----------------
@app.route("/")
def home():
    return render_template("splash.html")


# ---------------- LOGIN ----------------
@app.route("/login_page")
def login_page():
    return render_template("login.html")


@app.route("/login", methods=["POST"])
def login():

    email = request.form["email"].strip()
    password = request.form["password"]

    user = get_user_by_email(email)

    if user and check_password_hash(
        user["password"], password
    ):
        session["user_id"] = user["id"]
        session["user_name"] = user["name"]
        return redirect("/dashboard")

    return render_template(
        "login.html",
        message="Invalid credentials"
    )


# ---------------- REGISTER ----------------
@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form["name"].strip()
        email = request.form["email"].strip()
        password = request.form["password"]

        if len(name) < 2:
            return render_template(
                "register.html",
                message="Enter valid name"
            )

        if "@" not in email:
            return render_template(
                "register.html",
                message="Enter valid email"
            )

        if len(password) < 6:
            return render_template(
                "register.html",
                message="Password minimum 6 characters"
            )

        if get_user_by_email(email):
            return render_template(
                "register.html",
                message="Email already registered"
            )

        hashed = generate_password_hash(password)

        register_user(name, email, hashed)

        return redirect("/login_page")

    return render_template("register.html")


# ---------------- DASHBOARD ----------------
@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:
        return redirect("/login_page")

    user_id = session["user_id"]

    income = get_income(user_id)
    expense = get_total_expense(user_id)

    result = generate_analysis(income, expense)

    chart = get_chart_data(user_id)
    budgets = get_budgets(user_id)
    notes = get_notifications(user_id)

    keyword = request.args.get("search", "").strip()

    if keyword:
        recent = search_expenses(user_id, keyword)
    else:
        recent = get_recent_expenses(user_id)

    today = max(datetime.now().day, 1)
    avg = round(expense / today, 2)

    return render_template(
        "dashboard.html",
        name=session["user_name"],
        income=income,
        expense=expense,
        savings=result["savings"],
        score=result["score"],
        alert=result["alert"],
        recommendations=result["recommendations"],
        chart=chart,
        budgets=budgets,
        notes=notes,
        recent=recent,
        avg=avg
    )


# ---------------- SAVE INCOME ----------------
@app.route("/save_income", methods=["POST"])
def save_user_income():

    if "user_id" not in session:
        return redirect("/login_page")

    amount = request.form["income"]

    try:
        amount = float(amount)
        if amount < 0:
            raise ValueError
    except:
        return redirect("/dashboard")

    save_income(session["user_id"], amount)

    add_notification(
        session["user_id"],
        "Income updated"
    )

    return redirect("/dashboard")


# ---------------- SAVE BUDGET ----------------
@app.route("/save_budget", methods=["POST"])
def save_user_budget():

    if "user_id" not in session:
        return redirect("/login_page")

    category = request.form["category"]
    amount = request.form["amount"]

    try:
        amount = float(amount)
        if amount <= 0:
            raise ValueError
    except:
        return redirect("/dashboard")

    save_budget(
        session["user_id"],
        category,
        amount
    )

    add_notification(
        session["user_id"],
        "Budget saved"
    )

    return redirect("/dashboard")


# ---------------- ADD EXPENSE ----------------
@app.route("/add_expense", methods=["GET", "POST"])
def expense_page():

    if "user_id" not in session:
        return redirect("/login_page")

    if request.method == "POST":

        category = request.form["category"]
        amount = request.form["amount"]
        date = request.form["date"]

        try:
            amount = float(amount)
            if amount <= 0:
                raise ValueError
        except:
            return redirect("/add_expense")

        add_expense(
            session["user_id"],
            category,
            amount,
            date
        )

        add_notification(
            session["user_id"],
            "Expense added"
        )

        return redirect("/dashboard")

    return render_template("add_expense.html")


# ---------------- DELETE ----------------
@app.route("/delete/<int:id>")
def remove_expense(id):

    if "user_id" not in session:
        return redirect("/login_page")

    delete_expense(
        session["user_id"],
        id
    )

    add_notification(
        session["user_id"],
        "Expense deleted"
    )

    return redirect("/dashboard")


# ---------------- REPORT ----------------
@app.route("/report")
def report():

    if "user_id" not in session:
        return redirect("/login_page")

    user_id = session["user_id"]

    income = get_income(user_id)
    expense = get_total_expense(user_id)

    result = generate_analysis(
        income,
        expense
    )

    chart = get_chart_data(user_id)

    return render_template(
        "report.html",
        income=income,
        expense=expense,
        savings=result["savings"],
        score=result["score"],
        recommendations=result["recommendations"],
        chart=chart
    )


# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


if __name__ == "__main__":
    app.run()