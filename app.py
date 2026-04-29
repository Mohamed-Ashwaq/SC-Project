from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL

app = Flask(__name__)

# ── Secret key for sessions ──
app.secret_key = "my_super_secret_key_123"

# ── MySQL config ──
app.config["MYSQL_HOST"]     = "localhost"
app.config["MYSQL_USER"]     = "root"
app.config["MYSQL_PASSWORD"] = "Ash@2007"        # ← your MySQL password here
app.config["MYSQL_DB"]       = "myapp_db"

mysql = MySQL(app)


@app.route("/")
def home():
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        email    = request.form["email"].strip().lower()
        password = request.form["password"]

        cur = mysql.connection.cursor()
        cur.execute(
            "SELECT id, first_name, last_name FROM users WHERE email=%s AND password=%s",
            (email, password)
        )
        user = cur.fetchone()
        cur.close()

        if user:
            session["user_id"]    = user[0]
            session["first_name"] = user[1]
            session["last_name"]  = user[2]
            session["email"]      = email
            return redirect(url_for("dashboard"))
        else:
            error = "Invalid email or password. Please try again."

    return render_template("login.html", error=error)


@app.route("/register", methods=["GET", "POST"])
def register():
    error   = None
    success = None
    if request.method == "POST":
        first_name = request.form["firstName"].strip()
        last_name  = request.form["lastName"].strip()
        email      = request.form["email"].strip().lower()
        password   = request.form["password"]

        cur = mysql.connection.cursor()
        cur.execute("SELECT id FROM users WHERE email=%s", (email,))
        existing = cur.fetchone()

        if existing:
            error = "An account with this email already exists."
        else:
            cur.execute(
                "INSERT INTO users (first_name, last_name, email, password) VALUES (%s, %s, %s, %s)",
                (first_name, last_name, email, password)
            )
            mysql.connection.commit()
            success = "Account created! You can now log in."
        cur.close()

    return render_template("register.html", error=error, success=success)


@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))

    # Pass variables explicitly into the template
    return render_template(
        "dashboard.html",
        first_name = session.get("first_name"),
        last_name  = session.get("last_name"),
        email      = session.get("email")
    )


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)