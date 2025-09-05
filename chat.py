from flask import Blueprint, render_template, session, redirect, url_for, request, jsonify
from db_config import get_db
from functools import wraps
from bson import ObjectId
from datetime import datetime, timedelta

def get_ist_time():
    try:
        from zoneinfo import ZoneInfo
        return datetime.now(ZoneInfo("Asia/Kolkata"))
    except Exception:
        return datetime.utcnow()

chat_bp = Blueprint("chat", __name__)

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user" not in session:
            return redirect(url_for("login.login"))
        return f(*args, **kwargs)
    return decorated_function

@chat_bp.route("/chat")
@login_required
def chat_page():
    db = get_db()
    users_col = db["users"]
    groups_col = db["groups"]

    current_user = users_col.find_one({"username": session["user"]})
    profile_image = current_user.get("profile_image") if current_user else None

    other_users = list(users_col.find({"username": {"$ne": session["user"]}}))

    my_groups = list(groups_col.find({"members": session["user"]}))
    selected_user = request.args.get("user")
    selected_group_id = request.args.get("group")

    messages = []
    selected_group = None
    
    ist_now = get_ist_time()
    today_ist = ist_now.strftime("%Y-%m-%d")
    yesterday_ist = (ist_now - timedelta(days=1)).strftime("%Y-%m-%d")

    if selected_user:
        messages = list(db["messages"].find({
            "$or": [
                {"sender": session["user"], "receiver": selected_user},
                {"sender": selected_user, "receiver": session["user"]}
            ]
        }).sort("timestamp", 1))
        for m in messages:
            if isinstance(m.get("timestamp"), datetime):
                m["timestamp"] = m["timestamp"].strftime("%Y-%m-%dT%H:%M:%S")

    elif selected_group_id:
        try:
            group_obj_id = ObjectId(selected_group_id)
        except Exception:
            return "Invalid group ID", 400

        selected_group = groups_col.find_one({"_id": group_obj_id})
        messages = list(db["group_messages"].find({
            "group_id": str(group_obj_id)
        }).sort("timestamp", 1))
        for m in messages:
            if isinstance(m.get("timestamp"), datetime):
                m["timestamp"] = m["timestamp"].strftime("%Y-%m-%dT%H:%M:%S")


    return render_template(
        "chat.html",
        user=session["user"],
        users=other_users,
        groups=my_groups,
        selected_user=selected_user,
        selected_group=selected_group,
        messages=messages,
        profile_image=profile_image,
        today_ist=today_ist,
        yesterday_ist=yesterday_ist
    )