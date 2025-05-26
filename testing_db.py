import mysql.connector
from mysql.connector import Error

try:
    connection = mysql.connector.connect(
        host="localhost",       # or your DB host
        user="root",            # your DB user
        password="CenaVsPunk2011!",# your DB password
        database="security_app"  # your DB name
    )

    if connection.is_connected():
        print("✅ Connected to MySQL database")
        cursor = connection.cursor()
        cursor.execute("SELECT DATABASE();")
        record = cursor.fetchone()
        print("📂 You're connected to database:", record)

except Error as e:
    print("❌ Error while connecting to MySQL", e)

finally:
    if 'connection' in locals() and connection.is_connected():
        cursor.close()
        connection.close()
        print("🔌 MySQL connection closed")
