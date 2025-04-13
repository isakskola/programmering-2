import bcrypt
from database import get_database_connection

# Klass för att hantera användare
class User:
    def __init__(self, id, username, email, role):
        self.id = id
        self.username = username
        self.email = email
        self.role = role

    # Inloggning, static metod för att kunna användas utan att skapa en instans av klassen
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

    # Skapa en ny användare, static metod för att kunna användas utan att skapa en instans av klassen
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
            return True, ''
        except Exception as e:
            print(f"Misslyckades att skapa användare: {e}")
            return False, "Ett fel uppstod vid skapandet av användaren"
        finally:
            cursor.close()
            conn.close()

# Klass för att hantera trådar
class Thread:
    def __init__(self, id, title, user_id, last_activity, created_at):
        self.id = id
        self.title = title
        self.user_id = user_id
        self.last_activity = last_activity
        self.created_at = created_at
        
    # Hämta alla trådar, static metod för att kunna användas utan att skapa en instans av klassen
    @staticmethod
    def get_all():
        conn = get_database_connection()
        if not conn:
            return False, []

        try:
            cursor = conn.cursor(dictionary=True)
            # Hämta alla trådar och skaparnas namn genom att joina ihop tabellerna Threads och Users med hjälp av användarens id
            cursor.execute("""
                SELECT Threads.*, Users.username as creator_name 
                FROM Threads
                JOIN Users ON Threads.user_id = Users.id
                ORDER BY Threads.last_activity DESC
            """)
            threads = cursor.fetchall()
            return True, [{
                'id': thread['id'],
                'title': thread['title'],
                'creator': thread['creator_name'],
                'last_activity': thread['last_activity'].strftime('%Y-%m-%d %H:%M:%S'),
                'created_at': thread['created_at'].strftime('%Y-%m-%d %H:%M:%S')
            } for thread in threads]
        except Exception as e:
            print(f"Misslyckades att hämta trådar: {e}")
            return False, []
        finally:
            cursor.close()
            conn.close()
    
    # Hämta en specifik tråd, static metod för att kunna användas utan att skapa en instans av klassen
    @staticmethod
    def get_last_created():
        conn = get_database_connection()
        if not conn:
            return False, "Databasanslutning misslyckades"
        
        try:
            cursor = conn.cursor(dictionary=True)
            # Hämta den senaste tråden genom att sortera efter id i fallande ordning och
            # hämta namnet på skaparen genom att joina ihop tabellerna Threads och Users med hjälp av användarens id
            cursor.execute("""
                SELECT Threads.*, Users.username as creator_name 
                FROM Threads
                JOIN Users ON Threads.user_id = Users.id
                ORDER BY Threads.id DESC
                LIMIT 1
            """)
            thread = cursor.fetchone()
            
            # Ifall något går fel så returneras False och ett felmeddelande
            if not thread:
                return False, "Inga trådar hittades"
            
            return True, {
                'id': thread['id'],
                'title': thread['title'],
                'creator': thread['creator_name'],
                'last_activity': thread['last_activity'].strftime('%Y-%m-%d %H:%M:%S'),
                'created_at': thread['created_at'].strftime('%Y-%m-%d %H:%M:%S')
            }
        except Exception as e:
            print(f"Misslyckades att hämta tråd: {e}")
            return False, "Ett fel uppstod vid hämtningen av tråden"
        finally:
            cursor.close()
            conn.close()
            

    # Skapa en ny tråd, static metod för att kunna användas utan att skapa en instans av klassen
    @staticmethod
    def create(title, user_id):
        conn = get_database_connection()
        if not conn:
            return False, "Databasanslutning misslyckades"
        
        try:
            cursor = conn.cursor()
            
            cursor.execute(
                "INSERT INTO Threads (title, user_id) VALUES (%s, %s)", 
                (title, user_id)
            )
            conn.commit()
            return True, ''
        except Exception as e:
            print(f"Misslyckades att skapa tråd: {e}")
            return False, "Ett fel uppstod vid skapandet av tråden"
        finally:
            cursor.close()
            conn.close()

    # Ta bort en tråd, static metod för att kunna användas utan att skapa en instans av klassen
    @staticmethod
    def delete(thread_id, user_id, role):
        conn = get_database_connection()
        if not conn:
            return False, "Databasanslutning misslyckades"
        
        try:
            cursor = conn.cursor()
            
            cursor.execute("SELECT user_id FROM Threads WHERE id = %s", (thread_id,))
            thread = cursor.fetchone()
            
            if not thread:
                return False, "Tråden finns inte"
            
            # Kontrollerar om användaren är admin eller moderator eller om användaren är skaparen av tråden
            if thread[0] != user_id and role not in ['admin', 'moderator']:
                return False, "Du har inte behörighet att ta bort denna tråd"
            
            cursor.execute("DELETE FROM Threads WHERE id = %s", (thread_id,))
            conn.commit()
            return True, ''
        except Exception as e:
            print(f"Misslyckades att ta bort tråd: {e}")
            return False, "Ett fel uppstod vid borttagning av tråden"
        finally:
            cursor.close()
            conn.close()
            
class Post:
    def __init__(self, id, thread_id, user_id, content, created_at):
        self.id = id
        self.thread_id = thread_id
        self.user_id = user_id
        self.content = content
        self.created_at = created_at
        
    @staticmethod
    def get_thread_posts(thread_id):
        conn = get_database_connection()
        if not conn:
            return False, []

        try:
            cursor = conn.cursor(dictionary=True)

            cursor.execute("""
                SELECT Posts.*, Users.username as creator_name 
                FROM Posts
                JOIN Users ON Posts.user_id = Users.id
                WHERE Posts.thread_id = %s
                ORDER BY Posts.created_at ASC
            """, (thread_id,))
            posts = cursor.fetchall()
            return True, [{
                'id': post['id'],
                'thread_id': post['thread_id'],
                'content': post['content'],
                'creator': post['creator_name'],
                'created_at': post['created_at'].strftime('%Y-%m-%d %H:%M:%S')
            } for post in posts]

        except Exception as e:
            print(f"Misslyckades att hämta posts: {e}")
            return False, []
        finally:
            cursor.close()
            conn.close()
            
    @staticmethod
    def create(content, thread_id, user_id):
        conn = get_database_connection()
        if not conn:
            return False, "Databasanslutning misslyckades"
        
        try:
            cursor = conn.cursor()
            
            cursor.execute(
                "INSERT INTO Posts (content, thread_id, user_id) VALUES (%s, %s, %s)", 
                (content, thread_id, user_id)
            )
            conn.commit()
            return True, ''
        except Exception as e:
            print(f"Misslyckades att skapa inlägg: {e}")
            return False, "Ett fel uppstod vid skapandet av inlägget"
        finally:
            cursor.close()
            conn.close()
            
            
