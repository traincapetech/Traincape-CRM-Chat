from flask import Flask, session, redirect, url_for
from login import login_bp
from signup import signup_bp
from chat import chat_bp
from send_message import send_bp
from profiles import profile_bp
from groups import groups_bp
from flask_socketio import SocketIO

app = Flask(__name__)
# socketio = SocketIO(app, cors_allowed_origins="*")
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")

app.secret_key = "supersecretkey"

# Register blueprints
app.register_blueprint(login_bp)
app.register_blueprint(signup_bp)
app.register_blueprint(chat_bp)
app.register_blueprint(send_bp)
app.register_blueprint(profile_bp)
app.register_blueprint(groups_bp)

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login.login"))

if __name__ == "__main__":
    # app.run(debug=True)
    socketio.run(app, debug=True)