import mysql.connector
import json
import os

db_config = {
    'host': 'rann1926.mysql.pythonanywhere-services.com',
    'user': 'rann1926',
    'password': 'Rannalien_10',
    'database': 'rann1926$unique_chatbot'
}

try:
    # Attempt to connect to the MySQL database
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    # If the connection is successful, print a success message
    print("Successfully connected to the database.")

    # You can test the connection by executing a simple query
    cursor.execute("SELECT DATABASE()")  # This will return the current database name
    db_name = cursor.fetchone()
    print(f"Connected to database: {db_name[0]}")

except mysql.connector.Error as err:
    # Handle any errors that occur during the connection
    print(f"Error: {err}")

finally:
    # Close the connection if it was successfully established
    if conn.is_connected():
        cursor.close()
        conn.close()
        print("Connection closed.")
