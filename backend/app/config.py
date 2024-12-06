import os

class Config:
    DEBUG = True
    DATABASE_URI = os.getenv('DATABASE_URI', 'sqlite:///data.db')  # 示例数据库配置
    API_KEY = os.getenv('API_KEY', 'your_api_key_here')  # 示例 API 密钥
