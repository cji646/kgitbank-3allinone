import pymysql


def get_db_connection():
    return pymysql.connect(
        host="40.40.4.2",
        port=3306,
        user="travel_app2",
        password="travel",
        database="travel_safe",
        charset="utf8",
        cursorclass=pymysql.cursors.DictCursor
    )
