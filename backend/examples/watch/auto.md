1. 创建 systemd 服务文件

vim /etc/systemd/system/astockwatch.service
2. 写入以下内容
[Unit]
Description=AstockQuant Watch Service
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/workspace/stock/AstockQuant/backend/examples/watch

# 使用 conda 环境运行程序
ExecStart=/bin/bash -c "source /root/miniconda3/etc/profile.d/conda.sh && conda activate astockquant && python watch_tels.py"

Restart=always
RestartSec=10s
StartLimitInterval=60
StartLimitBurst=5

# 环境变量
Environment=PYTHONPATH=/workspace/stock/AstockQuant/backend
Environment=PYTHONUNBUFFERED=1

# 日志配置（确保日志目录存在）
StandardOutput=file:/var/log/astockwatch.log
StandardError=file:/var/log/astockwatch.error.log

[Install]
WantedBy=multi-user.target
3. 重新加载 systemd 配置并启动服务
bash
# 重新加载配置
sudo systemctl daemon-reload

# 启动服务
sudo systemctl start astockwatch.service

# 设置开机自启
sudo systemctl enable astockwatch.service

# 查看服务状态
sudo systemctl status astockwatch.service

# 查看日志
sudo journalctl -u astockwatch.service -f