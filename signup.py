from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename
from db_config import get_db
import os

signup_bp = Blueprint("signup", __name__)

@signup_bp.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        profile_image = request.files.get("profile_image")

        db = get_db()
        users_col = db["users"]

        # check if username/email already exists
        if users_col.find_one({"username": username}):
            flash("Username already exists", "danger")
            return redirect(url_for("signup.signup"))
        if users_col.find_one({"email": email}):
            flash("Email already exists", "danger")
            return redirect(url_for("signup.signup"))

        # hash password
        hashed_password = generate_password_hash(password, method="pbkdf2:sha256")

        # handle profile image
        image_path = None
        if profile_image and profile_image.filename != "":
            filename = secure_filename(profile_image.filename)
            upload_folder = os.path.join(current_app.root_path, "uploads")
            os.makedirs(upload_folder, exist_ok=True)
            save_path = os.path.join(upload_folder, filename)
            profile_image.save(save_path)
            image_path = f"/uploads/profile_pic/{filename}"

        # save user
        users_col.insert_one({
            "username": username,
            "email": email,
            "password": hashed_password,
            "profile_image": image_path
        })

        flash("Signup successful! Please login.", "success")
        return redirect(url_for("login.login"))

    return render_template("signup.html")
