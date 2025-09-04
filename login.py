from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import check_password_hash
from db_config import get_db

login_bp = Blueprint("login", __name__)

@login_bp.route("/", methods=["GET", "POST"])
@login_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        db = get_db()
        user = db["users"].find_one({"username": username})

        if user and check_password_hash(user["password"], password):
            session["user"] = username
            return redirect(url_for("chat.chat_page"))
            # return redirect(url_for("chat_page"))

        else:
            flash("Invalid credentials", "danger")
            return redirect(url_for("login.login"))

    return render_template("login.html")
