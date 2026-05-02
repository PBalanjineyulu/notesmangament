from flask import Flask, render_template, request, redirect, session, flash, send_from_directory
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask_mail import Mail, Message
import os
import random
import config

app = Flask(__name__)
app.secret_key = config.SECRET_KEY

# ---------------- EMAIL CONFIG ----------------

app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = config.MAIL_USERNAME
app.config["MAIL_PASSWORD"] = config.MAIL_PASSWORD

mail = Mail(app)

# ---------------- FILE UPLOAD ----------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# ---------------- DATABASE ----------------

db = mysql.connector.connect(
    host=config.DB_HOST,
    user=config.DB_USER,
    password=config.DB_PASSWORD,
    database=config.DB_NAME
)

cursor = db.cursor(dictionary=True)
# ---------------- HOME ----------------
@app.route("/")
def home():
    if session.get("user_id"):
        return redirect("/dashboard")
    return render_template("home.html")

# ---------------- ABOUT ----------------

@app.route("/about")
def about():
    return render_template("about.html")

# ---------------- CONTACT ----------------

@app.route("/contact", methods=["GET","POST"])
def contact():

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        message = request.form["message"]

        msg = Message(
            subject="Contact Message",
            sender=app.config["MAIL_USERNAME"],
            recipients=["balanjineyulu03@gmail.com"]
        )

        msg.body = f"""
Name: {name}
Email: {email}

Message:
{message}
        """

        mail.send(msg)

        flash("Message sent successfully", "success")

        return redirect("/contact")

    return render_template("contact.html")

# ---------------- REGISTER ----------------

from mysql.connector import IntegrityError

from flask import session
from flask_mail import Message

@app.route("/register", methods=["GET","POST"])
def register():

    if request.method == "POST":

        username = request.form["username"]
        email = request.form["email"]
        password = generate_password_hash(request.form["password"])

        # check already exists
        cursor.execute("SELECT * FROM users WHERE username=%s OR email=%s", (username, email))
        existing = cursor.fetchone()

        if existing:
            flash("Username or Email already exists!", "danger")
            return redirect("/register")

        # store temporarily
        session["temp_user"] = {
            "username": username,
            "email": email,
            "password": password
        }

        # generate OTP
        otp = str(random.randint(100000, 999999))
        session["otp"] = otp

        # send email
        msg = Message(
            "OTP Verification - Notes App",
            sender=app.config["MAIL_USERNAME"],
            recipients=[email]
        )
        msg.body = f"Your OTP is: {otp}"

        mail.send(msg)

        flash("OTP sent to your email", "info")
        return redirect("/verify")

    return render_template("register.html")



# ---------------- LOGIN ----------------

@app.route("/login", methods=["GET","POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        query = "SELECT * FROM users WHERE email=%s"

        cursor.execute(query,(email,))
        user = cursor.fetchone()

        if user and check_password_hash(user["password"], password):

            session["user_id"] = user["id"]

            flash("Login successful", "success")

            return redirect("/dashboard")

        else:

            flash("Invalid email or password", "danger")

    return render_template("login.html")
# ---------------- SEARCH NOTES ----------------

@app.route("/search")
def search():

    if "user_id" not in session:
        return redirect("/login")

    query_text = request.args.get("query")

    query = """
    SELECT * FROM notes
    WHERE user_id=%s
    AND (title LIKE %s OR content LIKE %s)
    """

    search_pattern = f"%{query_text}%"

    cursor.execute(query,(session["user_id"], search_pattern, search_pattern))

    notes = cursor.fetchall()

    return render_template("viewall.html", notes=notes)

# ---------------- LOGOUT ----------------

@app.route("/logout")
def logout():

    session.clear()

    flash("Logout successful", "warning")

    return redirect("/login")

# ---------------- DASHBOARD ----------------

@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:
        return redirect("/login")

    return render_template("dashboard.html")

# ---------------- ADD NOTE ----------------

@app.route("/addnote", methods=["GET","POST"])
def addnote():

    if "user_id" not in session:
        return redirect("/login")

    if request.method == "POST":

        title = request.form["title"]
        content = request.form["content"].strip()
        user_id = session["user_id"]

        file = request.files["file"]
        filename = None

        if file and file.filename != "":

            filename = secure_filename(file.filename)

            file.save(
                os.path.join(app.config["UPLOAD_FOLDER"], filename)
            )

        query = """
        INSERT INTO notes(title,content,file_name,user_id)
        VALUES(%s,%s,%s,%s)
        """

        cursor.execute(query,(title,content,filename,user_id))
        db.commit()

        flash("Note created successfully", "success")

        return redirect("/viewall")

    return render_template("addnote.html")

# ---------------- VIEW ALL NOTES ----------------

@app.route("/viewall")
def viewall():

    if "user_id" not in session:
        return redirect("/login")

    query = "SELECT * FROM notes WHERE user_id=%s"

    cursor.execute(query,(session["user_id"],))
    notes = cursor.fetchall()

    return render_template("viewall.html", notes=notes)

# ---------------- VIEW NOTE ----------------

# ---------------- VIEW NOTE ----------------
@app.route("/viewnotes/<int:id>")
def viewnotes(id):

    if "user_id" not in session:
        return redirect("/login")

    query = """
    SELECT notes.*, users.username AS updated_username
    FROM notes
    LEFT JOIN users ON notes.updated_by = users.id
    WHERE notes.id=%s AND notes.user_id=%s
    """

    cursor.execute(query, (id, session["user_id"]))
    note = cursor.fetchone()

    if not note:
        flash("Note not found", "danger")
        return redirect("/viewall")

    return render_template("viewnotes.html", note=note)


# ---------------- UPDATE NOTE ----------------
@app.route("/updatenote/<int:id>", methods=["GET", "POST"])
def updatenote(id):

    if "user_id" not in session:
        return redirect("/login")

    if request.method == "POST":

        title = request.form["title"].strip()
        content = request.form["content"].strip()

        cursor.execute(
            "SELECT file_name FROM notes WHERE id=%s AND user_id=%s",
            (id, session["user_id"])
        )
        old_note = cursor.fetchone()

        if not old_note:
            flash("Note not found", "danger")
            return redirect("/viewall")

        filename = old_note["file_name"]

        file = request.files.get("file")

        if file and file.filename != "":
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))

        query = """
        UPDATE notes 
        SET title=%s, content=%s, file_name=%s, updated_at=NOW(), updated_by=%s
        WHERE id=%s AND user_id=%s
        """

        cursor.execute(
            query,
            (title, content, filename, session["user_id"], id, session["user_id"])
        )
        db.commit()

        flash("Note updated successfully", "success")
        return redirect("/viewall")

    cursor.execute(
        "SELECT * FROM notes WHERE id=%s AND user_id=%s",
        (id, session["user_id"])
    )
    note = cursor.fetchone()

    if not note:
        flash("Note not found", "danger")
        return redirect("/viewall")

    return render_template("updatenote.html", note=note)
# ---------------- DELETE NOTE ----------------

@app.route("/deletenote/<int:id>")
def deletenote(id):

    # 🔒 Check login
    if "user_id" not in session:
        return redirect("/login")

    # ❌ Delete only user's own note
    query = "DELETE FROM notes WHERE id=%s AND user_id=%s"

    cursor.execute(query, (id, session["user_id"]))
    db.commit()

    # ⚠️ Check if anything was deleted
    if cursor.rowcount == 0:
        flash("Note not found or not allowed", "danger")
    else:
        flash("Note deleted successfully", "success")

    return redirect("/viewall")

# ---------------- OPEN FILE ----------------

@app.route("/uploads/<path:filename>")
def uploaded_file(filename):
    return send_from_directory(
        app.config["UPLOAD_FOLDER"],
        filename
    )

# ---------------- FORGOT PASSWORD (OTP VIA EMAIL ONLY) ----------------

@app.route("/forgot", methods=["GET","POST"])
def forgot():

    if request.method == "POST":

        email = request.form["email"]

        query = "SELECT * FROM users WHERE email=%s"
        cursor.execute(query,(email,))
        user = cursor.fetchone()

        if user:

            otp = str(random.randint(100000,999999))

            # store otp in session (not database)
            session["reset_otp"] = otp
            session["reset_email"] = email

            msg = Message(
                "Password Reset OTP",
                sender=app.config["MAIL_USERNAME"],
                recipients=[email]
            )

            msg.body = f"Your OTP is: {otp}"

            mail.send(msg)

            flash("OTP sent to email", "success")

            return redirect("/reset")

        else:

            flash("Email not found", "danger")

    return render_template("forgot.html")

# ---------------- RESET PASSWORD ----------------

@app.route("/reset", methods=["GET","POST"])
def reset():

    if request.method == "POST":

        otp = request.form["otp"]
        password = generate_password_hash(request.form["password"])

        # verify otp from session
        if otp == session.get("reset_otp"):

            email = session.get("reset_email")

            query = "UPDATE users SET password=%s WHERE email=%s"
            cursor.execute(query,(password,email))
            db.commit()

            # clear session
            session.pop("reset_otp", None)
            session.pop("reset_email", None)

            flash("Password updated successfully", "success")

            return redirect("/login")

        else:

            flash("Invalid OTP", "danger")

    return render_template("reset.html")


@app.route("/verify", methods=["GET", "POST"])
def verify():

    # If user directly opens /verify without registering
    if "temp_user" not in session or "otp" not in session:
        flash("Session expired. Please register again.", "danger")
        return redirect("/register")

    if request.method == "POST":

        user_otp = request.form["otp"].strip()

        if user_otp == session.get("otp"):

            data = session.get("temp_user")

            cursor.execute(
                "INSERT INTO users(username,email,password) VALUES(%s,%s,%s)",
                (data["username"], data["email"], data["password"])
            )
            db.commit()

            session.pop("otp", None)
            session.pop("temp_user", None)

            flash("Registration successful! Please login.", "success")
            return redirect("/login")

        flash("Invalid OTP", "danger")
        return redirect("/verify")

    return render_template("verify.html")












# ---------------- RUN ----------------

if __name__ == "__main__":
    app.run(debug=True)