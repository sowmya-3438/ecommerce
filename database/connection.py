import mysql.connector as SQLC

def DatabaseConnection():
    try:
        connection = SQLC.connect(
            host="localhost",
            user="root",
            password="root",
            database="ecommerce3"
        )

        if connection.is_connected():
            print("Database connected successfully")
            return connection

    except SQLC.Error as e:
        print(f"Database connection error: {e}")

    return None