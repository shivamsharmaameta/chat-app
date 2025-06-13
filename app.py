# app.py
from flask import Flask, render_template, request, redirect, url_for, session
from flask_socketio import SocketIO, join_room, leave_room, send
import uuid
import random
import string

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

# In-memory storage for users and rooms
rooms = {}

def generate_room_code():
    return ''.join(random.choices(string.ascii_uppercase, k=4))

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        username = request.form['username']
        room = request.form['room']
        session['username'] = username
        session['room'] = room
        return redirect(url_for('chat'))
    return render_template('index.html')

@app.route('/chat')
def chat():
    if 'username' not in session or 'room' not in session:
        return redirect(url_for('index'))
    return render_template('chat.html', username=session['username'], room=session['room'])

@socketio.on('join')
def handle_join(data):
    username = data['username']
    room = data['room']
    join_room(room)
    send({'msg': f"{username} has joined the room."}, to=room)

@socketio.on('message')
def handle_message(data):
    room = data['room']
    send({'msg': f"{data['username']}: {data['message']}"}, to=room)

@socketio.on('leave')
def handle_leave(data):
    username = data['username']
    room = data['room']
    leave_room(room)
    send({'msg': f"{username} has left the room."}, to=room)

if __name__ == '__main__':
    socketio.run(app)
