
from database.connection import DatabaseConnection
import bcrypt

class AuthQueries:

    @staticmethod
    def getUserData(email: str):
        db_config = cursor = None
        try:
            db_config = DatabaseConnection()

            if db_config is None:
                return False, "Database connection failed"

            cursor = db_config.cursor(dictionary=True)

            query = """SELECT * FROM users WHERE email = %s"""

            cursor.execute(query, (email,))
            user = cursor.fetchone()

            if user:
                return True, user
            else:
                return False, "Email Not Exists"

        except Exception as e:
            return False, f"Something wrong in getUserData(): {e}"

        finally:
            if cursor:
                cursor.close()
            if db_config:
                db_config.close()

    # Create account
    @staticmethod
    def createUserAccount(username: str, email: str,
                          password: str, phone: str):
        db_config = cursor = None
        try:
            db_config = DatabaseConnection()

            if db_config is None:
                return False, "Database connection failed"

            cursor = db_config.cursor()

            query = """
            INSERT INTO users (username, email, hashpassword, phone)
            VALUES (%s, %s, %s, %s)
            """

            cursor.execute(query, (username, email, password, phone))
            db_config.commit()

            return True, "Account Created"

        except Exception as e:
            return False, f"Something wrong in createUserAccount(): {e}"

        finally:
            if cursor:
                cursor.close()
            if db_config:
                db_config.close()

    # Login user
    @staticmethod
    def loginUser(email: str, password: str):
        db_config = cursor = None

        try:
            db_config = DatabaseConnection()

            if db_config is None:
                return None

            cursor = db_config.cursor(dictionary=True)

            query = """
            SELECT * FROM users WHERE email = %s
            """

            cursor.execute(query, (email,))
            user = cursor.fetchone()

            if user:
                if bcrypt.checkpw(
                    password.encode('utf-8'),
                    user['hashpassword'].encode('utf-8')
                ):
                    return user

            return None

        except Exception as e:
            print(f"Login Error: {e}")
            return None

        finally:
            if cursor:
                cursor.close()
            if db_config:
                db_config.close()
