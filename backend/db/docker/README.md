在这个 Dockerfile 中：

FROM mysql:5.7 指定了使用官方的 MySQL 5.7 镜像。
ENV 指令设置了一些基本的环境变量，如 MYSQL_ROOT_PASSWORD（root 用户的密码）、MYSQL_DATABASE（创建一个初始数据库）、MYSQL_USER（一个额外的数据库用户）、MYSQL_PASSWORD（该用户的密码）。
COPY ./sql-scripts/ /docker-entrypoint-initdb.d/ 是一个可选步骤，用于将任何 SQL 脚本复制到容器中，这些脚本将在数据库第一次启动时运行。您需要将您的 SQL 脚本放在主机的 sql-scripts 目录下。
EXPOSE 3306 指令告诉 Docker 在运行时暴露 3306 端口。
接下来，您需要在 Dockerfile 所在的目录下运行以下命令来构建 Docker 镜像：

```bash
docker build -t my-mysql .
```
这个命令会根据 Dockerfile 构建一个名为 my-mysql 的镜像。构建完成后，您可以使用以下命令来运行您的 MySQL 容器：

```bash
docker run --name some-mysql -p 3306:3306 -d my-mysql
```
这将启动一个名为 some-mysql 的容器，将容器的 3306 端口映射到主机的 3306 端口，并在后台运行。