import pymysql

connection = pymysql.connect(
    host='localhost',
    user='root',
    password='zxc1015zxc',
    db='testdb',
    cursorclass=pymysql.cursors.DictCursor
)
try:
    with connection.cursor() as cursor:
        sql = "INSERT INTO `tripad_hotel` (`id`,`location`,`hotel_name`,`hotel_url`,`agodaid`,`ctripid`,`bookingcnid`," \
              "`reqnum`) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"
        cursor.execute(sql, (1, "test", "test", "test", "test", "test", "test", 1))
    connection.commit()
finally:
    connection.close()
