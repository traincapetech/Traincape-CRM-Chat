import os
from flask import Blueprint, session, request, redirect, url_for, send_from_directory, jsonify
from db_config import get_db
from functools import wraps
from datetime import datetime
from werkzeug.utils import secure_filename
from bson import ObjectId

send_bp = Blueprint("send", __name__)

UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "pdf", "docx", "txt", "zip"}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user" not in session:
            return redirect(url_for("login.login"))
        return f(*args, **kwargs)
    return decorated_function

@send_bp.route("/send_message", methods=["POST"])
@login_required
def send_message():
    db = get_db()
    sender = session["user"]
    receiver = request.form.get("receiver")
    chat_type = request.form.get("chat_type")
    message = request.form.get("message", "")
    file = request.files.get("file")

    # Reply info
    reply_message_id = request.form.get("reply_message_id")
    reply_message_text = request.form.get("reply_message_text")

    file_name = ""
    file_url = ""
    file_type = "text"

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(UPLOAD_FOLDER, filename))
        file_name = filename
        file_url = url_for("send.uploaded_file", filename=filename)
        ext = filename.rsplit(".", 1)[1].lower()
        file_type = "image" if ext in ["png", "jpg", "jpeg", "gif"] else "file"

    msg_doc = {
        "sender": sender,
        "type": file_type,
        "message": message,
        "file_name": file_name,
        "file_url": file_url,
        "status": "sent",
        "timestamp": datetime.utcnow()
    }

    # Attach replyTo if exists
    if reply_message_id and reply_message_text:
        try:
            msg_doc["replyTo"] = {
                "messageId": ObjectId(reply_message_id),
                "text": reply_message_text
            }
        except:
            msg_doc["replyTo"] = {
                "messageId": None,
                "text": reply_message_text
            }

    if chat_type == "user":
        msg_doc["receiver"] = receiver
        db["messages"].insert_one(msg_doc)
        return redirect(url_for("chat.chat_page", user=receiver))

    elif chat_type == "group":
        msg_doc["group_id"] = receiver
        db["group_messages"].insert_one(msg_doc)
        return redirect(url_for("chat.chat_page", group=receiver))

    return redirect(url_for("chat.chat_page"))

@send_bp.route("/uploads/<path:filename>")
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

@send_bp.route("/forward_message", methods=["POST"])
@login_required
def forward_message():
    db = get_db()
    data = request.get_json()
    msg_id = data.get("message_id")
    target_id = data.get("target_id")
    chat_type = data.get("chat_type")

    try:
        original = db["messages"].find_one({"_id": ObjectId(msg_id)}) \
                 or db["group_messages"].find_one({"_id": ObjectId(msg_id)})
    except Exception:
        return jsonify({"error": "Invalid message ID"}), 400

    if not original:
        return jsonify({"error": "Message not found"}), 404

    new_msg = {
        "sender": session["user"],
        "message": original.get("message"),
        "type": original.get("type", "text"),
        "file_url": original.get("file_url"),
        "file_name": original.get("file_name"),
        "timestamp": datetime.utcnow(),
    }

    if chat_type == "user":
        new_msg["receiver"] = target_id
        db["messages"].insert_one(new_msg)
    else:
        new_msg["group_id"] = target_id
        db["group_messages"].insert_one(new_msg)

    return jsonify({"success": True})
