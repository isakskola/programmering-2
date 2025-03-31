import bcrypt
from database import get_database_connection

class User:
    def __init__(self, id, username, email, role):
        self.id = id
        self.username = username
        self.email = email
        self.role = role

    @staticmethod
    def authenticate(username, password):
        conn = get_database_connection()
        if not conn:
            return None

        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM Users WHERE username = %s", (username,))
            user_data = cursor.fetchone()

            if user_data and bcrypt.checkpw(password.encode('utf-8'), user_data['password_hash'].encode('utf-8')):
                return User(
                    user_data['id'],
                    user_data['username'],
                    user_data['email'],
                    user_data['role']
                )
            return None
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def create(username, email, password):

        conn = get_database_connection()
        if not conn:
            return False, "Databasanslutning misslyckades"

        try:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM Users WHERE username = %s", (username,))
            if cursor.fetchone():
                return False, "Användarnamnet finns redan"

            cursor.execute("SELECT id FROM Users WHERE email = %s", (email,))
            if cursor.fetchone():
                return False, "Emailen finns redan"

            password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            cursor.execute(
                "INSERT INTO Users (username, email, password_hash, role) VALUES (%s, %s, %s, 'user')",
                (username, email, password_hash.decode('utf-8'))
            )
            conn.commit()
            return True, "Användare skapad"
        except Exception as e:
            print(f"Error creating user: {e}")
            return False, "Ett fel uppstod vid skapandet av användaren"
        finally:
            cursor.close()
            conn.close()
