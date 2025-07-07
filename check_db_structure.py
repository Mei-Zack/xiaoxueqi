import pymysql

# 连接数据库
connection = pymysql.connect(
    host='localhost',
    user='root',
    password='65353804778',
    database='diabetes_assistant'
)

try:
    with connection.cursor() as cursor:
        # 查看表结构
        cursor.execute("DESCRIBE glucose_records")
        table_structure = cursor.fetchall()
        print("=== glucose_records表结构 ===")
        for column in table_structure:
            print(column)
            
        # 查看表中的数据
        cursor.execute("SELECT * FROM glucose_records LIMIT 5")
        records = cursor.fetchall()
        print("\n=== glucose_records表数据示例 ===")
        for record in records:
            print(record)
finally:
    connection.close() 