# 使用官方 MySQL 镜像
FROM mysql:5.7

# 设置环境变量以初始化 MySQL 管理员用户和密码
ENV MYSQL_ROOT_PASSWORD mypassword
ENV MYSQL_DATABASE mydatabase
ENV MYSQL_USER myuser
ENV MYSQL_PASSWORD mypassword

# 可选：初始化脚本
COPY ./sql-scripts/ /docker-entrypoint-initdb.d/

# 暴露端口
EXPOSE 3306