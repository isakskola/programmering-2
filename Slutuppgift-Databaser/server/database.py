import mysql.connector
from mysql.connector import Error

# Funktion för att ansluta till databasen för att slippa upprepning
def get_database_connection():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',
            database='forum'
        )
        return connection
    except Error as e:
        print(f"Fel vid anslutning till databasen: {e}")
        return None
