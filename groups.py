from flask import Blueprint, request, redirect, url_for, session, abort, jsonify
from werkzeug.utils import secure_filename
from functools import wraps
from datetime import datetime
import os, secrets
from bson import ObjectId
from chat import get_ist_time

from db_config import get_db

groups_bp = Blueprint("groups", __name__)

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user" not in session:
            return redirect(url_for("login.login"))
        return f(*args, **kwargs)
    return decorated

@groups_bp.route("/groups/create", methods=["POST"])
@login_required
def create_group():
    try:
        db = get_db()
        groups_col = db["groups"]

        name = (request.form.get("name") or "").strip()
        description = (request.form.get("description") or "").strip()
        if not name:
            abort(400, "Group name required")

        selected_members = request.form.getlist("members")
        creator = session["user"]
        members = list({*(selected_members or []), creator})

        image_url = "/static/default_profile.png"
        file = request.files.get("image")
        if file and file.filename:
            uploads_dir = os.path.join(os.getcwd(), "uploads")
            os.makedirs(uploads_dir, exist_ok=True)
            base = secure_filename(file.filename)
            fname = f"group_{int(datetime.utcnow().timestamp())}_{base}"
            save_path = os.path.join(uploads_dir, fname)
            file.save(save_path)
            image_url = f"/uploads/{fname}"

        invite_code = secrets.token_hex(6)

        doc = {
            "name": name,
            "description": description,
            "created_by": creator,
            "invite_code": invite_code,
            "image": image_url,
            "members": members,
            "created_at": get_ist_time()
        }

        groups_col.insert_one(doc)
        return redirect(url_for("chat.chat_page"))
    except Exception as e:
        print("Error creating group:", e)
        return jsonify({"error": str(e)}), 500

@groups_bp.route("/update_group", methods=["POST"])
@login_required
def update_group():
    try:
        db = get_db()
        group_id = request.form.get("group_id")
        
        if not group_id:
            return jsonify({"error": "Missing group ID"}), 400
        
        update = {
            "name": request.form.get("name", "").strip(),
            "description": request.form.get("description", "").strip()
        }
        
        image = request.files.get("image")
        if image and image.filename:
            filename = f"group_{int(datetime.utcnow().timestamp())}_{secure_filename(image.filename)}"
            save_path = os.path.join(os.getcwd(), "uploads", filename)
            image.save(save_path)
            update["image"] = f"/uploads/{filename}"
        
        db["groups"].update_one(
            {"_id": ObjectId(group_id)}, 
            {"$set": update}
        )
        
        return jsonify({"success": True})
    
    except Exception as e:
        print(f"Error updating group: {e}")
        return jsonify({"error": str(e)}), 500
    
@groups_bp.route("/update_group_members", methods=["POST"])
@login_required
def update_group_members():
    db = get_db()
    groups_col = db["groups"]
    
    data = request.json
    group_id = data.get("group_id")
    members_to_add = data.get("add", [])
    members_to_remove = data.get("remove", [])
    
    if not group_id:
        return jsonify({"error": "Missing group ID"}), 400
    
    try:
        group = groups_col.find_one({"_id": ObjectId(group_id)})
        if not group:
            return jsonify({"error": "Group not found"}), 404
        
        if group["created_by"] != session["user"]:
            return jsonify({"error": "Not authorized"}), 403
        
        current_members = group.get("members", [])
        
        for username in members_to_remove:
            if username in current_members and username != session["user"]:
                current_members.remove(username)
        
        for username in members_to_add:
            if username not in current_members:
                current_members.append(username)
        
        groups_col.update_one(
            {"_id": ObjectId(group_id)},
            {"$set": {"members": current_members}}
        )
        
        return jsonify({"success": True}), 200
    except Exception as e:
        print(f"Error updating members: {str(e)}")
        return jsonify({"error": str(e)}), 500

@groups_bp.route("/group_profile/<group_id>", methods=["GET"])
@login_required
def group_profile(group_id):
    db = get_db()
    groups_col = db["groups"]
    users_col = db["users"]

    group = groups_col.find_one({"_id": ObjectId(group_id)})
    if not group:
        return {"error": "Group not found"}, 404

    members_data = []
    for username in group.get("members", []):
        user = users_col.find_one({"username": username})
        profile_image = "/static/default_profile.png"
        
        if user and "profile_image" in user:
            profile_image = user["profile_image"]
        
        members_data.append({
            "username": username,
            "profile_image": profile_image
        })

    return {
        "_id": str(group["_id"]),
        "name": group.get("name"),
        "description": group.get("description"),
        "image": group.get("image") or "/static/default_profile.png",
        "created_by": group.get("created_by"),
        "members": members_data,
        "can_edit": (group.get("created_by") == session.get("user"))
    }

@groups_bp.route("/available_users", methods=["GET"])
@login_required
def available_users():
    db = get_db()
    group_id = request.args.get("group_id")
    
    if not group_id:
        return jsonify({"error": "Missing group ID"}), 400
    
    try:
        group = db.groups.find_one({"_id": ObjectId(group_id)})
        if not group:
            return jsonify({"error": "Group not found"}), 404
        
        current_members = group.get("members", [])
        all_users = list(db.users.find({}, {"username": 1, "profile_image": 1}))
        
        members = []
        for username in current_members:
            user = next((u for u in all_users if u["username"] == username), None)
            profile_image = "/static/default_profile.png"
            if user and "profile_image" in user:
                profile_image = user["profile_image"]
            
            members.append({
                "username": username,
                "profile_image": profile_image
            })
        
        available = []
        for user in all_users:
            if user["username"] not in current_members:
                profile_image = user.get("profile_image", "/static/default_profile.png")
                available.append({
                    "username": user["username"],
                    "profile_image": profile_image
                })
        
        return jsonify({
            "members": members,
            "available": available
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@groups_bp.route("/user_profile/<username>", methods=["GET"])
@login_required
def user_profile(username):
    db = get_db()
    user = db["users"].find_one({"username": username})
    if not user:
        return jsonify({"error": "User not found"}), 404

    profile_image = user.get("profile_image", "/static/default_profile.png")
    
    return jsonify({
        "username": user["username"],
        "email": user.get("email", ""),
        "profile_image": profile_image
    })