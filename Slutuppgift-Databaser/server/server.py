from flask import Flask, request, jsonify
from flask_cors import CORS
from models import User

app = Flask(__name__)
CORS(app)

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'Användarnamn och lösenord krävs'}), 400

    user = User.authenticate(username, password)
    if user:
        return jsonify({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': user.role
        })
    return jsonify({'error': 'Ogiltiga uppgifter'}), 401

@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not all([username, email, password]):
        return jsonify({'success': False, 'message': 'Alla fält krävs'}), 400

    success, message = User.create(username, email, password)
    if success:
        return jsonify({'success': True, 'message': message})
    return jsonify({'success': False, 'message': message}), 400

if __name__ == '__main__':
    app.run(debug=True)
