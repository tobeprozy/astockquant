import mysql.connector

# 连接到 MySQL 数据库
conn = mysql.connector.connect(
    host="localhost",# 因为 做了端口映射，所以这里可以直接用localhost，代表127.0.0.1，访问的时候127.0.0.1：3306-->docker:3306
    port=3306,  # 默认端口就是3306，如果docker不是这个端口就需要指定
    user="root",
    password="mypassword",
    database="mydatabase"
)

# 创建 cursor 对象来执行 SQL 语句
cursor = conn.cursor()

# 执行 SQL 查询
cursor.execute("SELECT * FROM your_table_name")

# 获取查询结果
records = cursor.fetchall()
for record in records:
    print(record)

# 关闭连接
cursor.close()
conn.close()
