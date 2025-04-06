from flask import Flask, request, jsonify
from flask_cors import CORS
from models import User, Thread

app = Flask(__name__)
CORS(app)

# Logga in
@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'message': 'Användarnamn och lösenord krävs'}), 400

    user = User.authenticate(username, password) # Kontrollerar att användaren finns och om lösenordet stämmer
    if user:
        return jsonify({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': user.role
        }), 200
    return jsonify({'message': 'Ogiltiga uppgifter'}), 401

# Skapa en ny användare
@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    success, message = User.create(username, email, password)
    if success:
        return '', 200
    return jsonify({'message': message}), 400

# Hämta alla trådar
@app.route('/api/threads', methods=['GET'])
def get_threads():
    success, threads = Thread.get_all() 
    if success:
        return jsonify({'threads': threads}), 200 # threads är en lista med alla trådar och deras information
    return jsonify({'message': 'Kunde inte hämta trådar'}), 500

# Skapa en ny tråd
@app.route('/api/threads', methods=['POST'])
def create_thread():
    data = request.get_json()
    title = data.get('title')
    user_id = data.get('user_id')

    success, message = Thread.create(title, user_id)
    if success:
        return '', 200
    return jsonify({'message': message}), 400

# Ta bort en tråd
@app.route('/api/threads/<int:thread_id>', methods=['DELETE'])
def delete_thread(thread_id):
    data = request.get_json()
    user_id = data.get('user_id')
    role = data.get('role')

    success, message = Thread.delete(thread_id, user_id, role)
    if success:
        return '', 200
    return jsonify({'message': message}), 400

if __name__ == '__main__':
    app.run(debug=True)
