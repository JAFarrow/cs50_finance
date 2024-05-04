import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    holdings = db.execute("SELECT * FROM holdings WHERE user_id = ?", session["user_id"])
    summed_value = 0
    for holding in holdings:
        price = lookup(holding["symbol"])["price"]
        holding["price"] = usd(price)
        value = price * holding["amount"]
        holding["value"] = usd(value)
        summed_value += value
    cash = db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"])[0]["cash"]
    total_value = summed_value + cash
    return render_template("portfolio.html", holdings=holdings, cash=usd(cash), totalValue = usd(total_value))


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    if request.method == "POST":
        stock_info = ""
        symbol = (request.form.get("symbol")).upper()
        amount = int(request.form.get("amount"))
        if symbol:
            stock_info = lookup(symbol)
            if stock_info and amount:
                if amount > 0:
                    if not update_balance(session["user_id"], stock_info["price"], amount):
                        return apology("insufficient funds", 403)
                    append_transaction(session["user_id"], symbol, amount, "BUY")
                    update_holdings(session["user_id"], symbol, amount)
                    return redirect("/")
                else:
                    return apology("shares missing", 403)
            else:
                return apology("invalid symbol", 403)
    else:
        return render_template("buy.html")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    return apology("TODO")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    if request.method == "POST":
        stock_info = ""
        symbol = request.form.get("symbol")
        if symbol:
            stock_info = lookup(symbol)
        if stock_info:
            stock = stock_info["symbol"]
            price = usd(stock_info["price"])
            return render_template("quoted.html", stock=stock, price=price)
        else:
            return apology("invalid symbol", 403)
    else:
        return render_template("quote.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if not username:
            return apology("must provide username", 403)
        elif not password:
            return apology("must provide password", 403)
        elif not password == request.form.get("confirmation"):
            return apology("passwords must match", 403)
        
        db.execute("INSERT INTO users (username, hash) VALUES(?, ?)", username, generate_password_hash(password))

        return redirect("/")
        
    else:
        return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    if request.method == "POST":
        symbol = request.form.get("symbol")
        negative_amount = -int(request.form.get("shares"))
        if not update_holdings(session["user_id"], symbol, negative_amount):
            return apology("not enough shares owned", 403)
        update_balance(session["user_id"], lookup(symbol)["price"], negative_amount)
        append_transaction(session["user_id"], symbol, abs(negative_amount), "SELL")
        return redirect("/")
    else:
        holdings = db.execute("SELECT symbol FROM holdings WHERE user_id = ?", session["user_id"])
        return render_template("sell.html", holdings=holdings)


def update_balance(user_id, price, amount):
    balance = db.execute("SELECT cash FROM users WHERE id = ?", user_id)[0]["cash"]
    if (balance - (price * amount)) > -1:
        balance -= (price * amount)
        db.execute("UPDATE users SET cash = ? WHERE id = ?", balance, user_id)
        return True
    return False

def update_holdings(user_id, symbol, add_amount):
    current_holdings = db.execute("SELECT * FROM holdings WHERE user_id = ? AND symbol = ?", user_id, symbol)
    if current_holdings:
        new_amount = current_holdings[0]["amount"] + add_amount
        if new_amount > 0:
            db.execute("UPDATE holdings SET amount = ? WHERE user_id = ? AND symbol = ?", new_amount, user_id, symbol)
        elif new_amount == 0:
            db.execute("DELETE FROM holdings WHERE user_id = ? AND symbol = ?", user_id, symbol)
        else:
            return False
    else:
        db.execute("INSERT INTO holdings (user_id, symbol, amount) VALUES (?, ?, ?)", user_id, symbol, add_amount)
    return True

def append_transaction(user_id, symbol, amount, transaction_type):
        db.execute("INSERT INTO transactions (user_id, symbol, shares, transaction_type)\
                    VALUES (?, ?, ?, ?)", user_id, symbol, amount, transaction_type)
