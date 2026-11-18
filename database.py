import pymysql

def get_connection():
    try:
        conn = pymysql.connect(
            host="localhost",
            user="root",
            password="susmitha@123",
            database="talentbridge_ai",
            cursorclass=pymysql.cursors.DictCursor
        )
        return conn

    except Exception as e:
        print(e)
        return None