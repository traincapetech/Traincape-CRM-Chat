from flask import Blueprint, request, jsonify, session, current_app
from werkzeug.security import generate_password_hash
from db_config import get_db
import os
from bson import ObjectId

profile_bp = Blueprint("profile", __name__)

@profile_bp.route("/update_profile", methods=["POST"])
def update_profile():
    if "user" not in session:
        return jsonify({"error": "Not logged in"}), 401

    db = get_db()
    users_col = db["users"]

    username = session["user"]
    user = users_col.find_one({"username": username})
    if not user:
        return jsonify({"error": "User not found"}), 404

    update_data = {}

    # Update fields if provided
    if "username" in request.form and request.form["username"]:
        update_data["username"] = request.form["username"]
        session["user"] = request.form["username"]  # update session

    if "email" in request.form and request.form["email"]:
        update_data["email"] = request.form["email"]

    if "password" in request.form and request.form["password"]:
        update_data["password"] = generate_password_hash(request.form["password"])

    # Profile picture upload
    if "profile_pic" in request.files:
        file = request.files["profile_pic"]
        if file and file.filename != "":
            # Define upload folder inside the function
            upload_folder = os.path.join(current_app.root_path, "uploads", "profile_pic")
            os.makedirs(upload_folder, exist_ok=True)

            # Save the new file
            filename = file.filename
            filepath = os.path.join(upload_folder, filename)
            file.save(filepath)

            # Update the profile_image URL in the database (not profile_pic)
            update_data["profile_image"] = f"/uploads/profile_pic/{filename}"  # store URL

            # Optionally, remove the old profile image from the server
            old_profile_image = user.get("profile_image")
            if old_profile_image:
                old_file_path = os.path.join(current_app.root_path, old_profile_image.lstrip('/'))
                if os.path.exists(old_file_path):
                    os.remove(old_file_path)

    if update_data:
        users_col.update_one({"_id": user["_id"]}, {"$set": update_data})

    return jsonify({"success": True, "message": "Profile updated"})

@profile_bp.route("/user_profile/<username>", methods=["GET"])
def view_user_profile(username):
    db = get_db()
    users_col = db["users"]
    user = users_col.find_one({"username": username}, {"_id":0, "username":1, "email":1, "profile_image":1})
    if not user:
        return jsonify({"error": "User not found"}), 404

    if not user.get("profile_image"):
        from flask import url_for
        user["profile_image"] = url_for("static", filename="default_profile.png")
    return jsonify(user)



@profile_bp.route("/group_profile/<group_id>", methods=["GET"])
def view_group_profile(group_id):
    db = get_db()
    groups_col = db["groups"]

    try:
        group = groups_col.find_one(
            {"_id": ObjectId(group_id)},
            {"_id": 0, "name": 1, "description": 1, "image": 1, "members": 1}
        )
    except Exception:
        return jsonify({"error": "Invalid group ID"}), 400

    if not group:
        return jsonify({"error": "Group not found"}), 404

    return jsonify(group)

