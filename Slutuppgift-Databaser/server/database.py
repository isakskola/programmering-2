import mysql.connector
from mysql.connector import Error

# Funktion för att ansluta till databasen för att slippa upprepning
def get_database_connection():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='admin',
            database='forum'
        )
        return connection
    except Error as e:
        print(f"Fel vid anslutning till databasen: {e}")
        return None

# ! för att testa ha många trådar
# def generate_threads(amount):
#     connection = get_database_connection()
#     cursor = connection.cursor()
#     for i in range(amount):
#         cursor.execute(f"INSERT INTO `forum`.`threads` (`title`, `user_id`) VALUES ('Test{i}', 4);")
#     connection.commit()
#     cursor.close()
#     connection.close()

# def delete_threads():
#     connection = get_database_connection()
#     cursor = connection.cursor()
#     cursor.execute("DELETE FROM `forum`.`threads`;")
#     connection.commit()
#     cursor.close()
#     connection.close()

# delete_threads()
# generateThreads(100)