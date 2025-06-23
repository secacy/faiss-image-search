import pymysql

def connectdb():
    print("连接到mysql服务器...")
    db = pymysql.connect(
        host="localhost",
        user="root",
        passwd="1234",
        port=3306,
        db="pic_search",
        charset="utf8",
        cursorclass=pymysql.cursors.DictCursor
    )
    print("连接成功！")
    return db

connectdb()
