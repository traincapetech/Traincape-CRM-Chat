# Traincape-CRM-Chat

A simple chatbot web application built with Flask, Socket.IO, HTML, CSS, and JavaScript. It features one-on-one and group chat, file and image sharing, user profiles, and group management.

---

## Features

- **User authentication**: Login, logout, profile update
- **Chat**: Real-time messaging (private & group) with reply, forward, copy functions
- **File sharing**: Send images and documents (with preview)
- **Group management**: Create, edit, and manage group members
- **Profile**: Update user info and profile picture
- **Search**: Filter users, groups, and messages

---

## Screenshots

> Add screenshots here for login, chat, group, and file sharing screens

---

## Setup

### 1. Clone the repo

```bash
git clone https://github.com/traincapetech/Traincape-CRM-Chat.git
cd Traincape-CRM-Chat
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment

- Create a `.env` file with your secrets (example below):

```
FLASK_SECRET_KEY=your_secret_key
MONGO_URI=your_mongodb_uri
```

### 4. Run the app

```bash
python app.py
```

- Go to [http://localhost:5000](http://localhost:5000) in your browser

---

## Folder structure

```text
.
├── app.py               # Main Flask app
├── chat.py              # Chat logic (routes, sockets)
├── db_config.py         # Database setup
├── templates/           # HTML files
│   ├── chat.html
│   ├── login.html
│   ├── ...etc
├── static/              # Static assets (CSS, JS, images)
│   ├── styles.css
│   ├── default_profile.png
│   ├── ...etc
├── requirements.txt     # Python dependencies
└── README.md
```

---

## Example usage

### Sending a message

```python
# send_message route in Flask
@app.route('/send', methods=['POST'])
def send_message():
    # Get message, receiver, and type from request
    # Save to MongoDB
    # Emit message via SocketIO
```

### Creating a group

```python
# groups.create_group route
@app.route('/groups/create', methods=['POST'])
def create_group():
    # Get group name, members, and image
    # Save group to database
```

---

## Technologies used

- **Backend**: Flask, Flask-SocketIO, PyMongo (MongoDB)
- **Frontend**: HTML, CSS, JavaScript, jQuery, Socket.IO-client

---


## Contribution

- Fork the repo
- Make changes
- Submit a pull request (optional)
