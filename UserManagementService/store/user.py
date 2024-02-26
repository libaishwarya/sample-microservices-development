# from .utils import get_connection
from store.utils import get_connection
import jsonify


def insert_user(user_id, name, email, hashed_password, is_admin = False):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        conn.start_transaction(readonly=False)
        cursor.execute('INSERT INTO user_management (id, name, email, password, is_admin) VALUES (%s, %s, %s, %s, %s)', (user_id, name, email, hashed_password, is_admin))
        conn.commit()
        conn.close()

    except Exception as err:
        return err
    
def get_user(email, hashed_password):
    try: 
        conn = get_connection()
        cursor = conn.cursor()
        conn.start_transaction(readonly=True)
        cursor.execute('SELECT * FROM user_management WHERE email = %s AND password = %s ', (email, hashed_password))
        user = cursor.fetchone()
        return user
    except Exception as err:
        return err
    
def read_user(ids):
     try:
         conn = get_connection()
         cursor = conn.cursor()
         conn.start_transaction(readonly=True)
         cursor.execute('SELECT * FROM user_management WHERE id = %s ', (ids,))
         user = cursor.fetchone()
         conn.close()
         user_dict = {
                                 "ids": user[0],
                                 "name": user[1],
                                 "email": user[2],
                                 }
         return user_dict
     except Exception as err:
         return err
    
def user_update(name, email, ids):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        conn.start_transaction(readonly=False)
        cursor.execute('UPDATE user_management SET name = %s, email = %s WHERE id = %s', (name, email, ids))
        conn.commit()
        conn.close()

    except Exception as e:
        raise e

def user_delete(ids):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        conn.start_transaction(readonly=False)
        cursor.execute('DELETE FROM user_management WHERE id = %s', (ids,))
        conn.commit()
        conn.close()
        
    except Exception as e:
        raise e