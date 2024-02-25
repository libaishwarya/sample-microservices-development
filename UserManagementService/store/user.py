from .utils import get_connection

def insert_user(user_id, name, email, hashed_password):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        conn.start_transaction(readonly=False)
        cursor.execute('INSERT INTO user_management (id, name, email, password) VALUES (%s, %s, %s, %s)', (user_id, name, email, hashed_password))
        conn.commit()
        conn.close()

    except Exception as err:
        return err