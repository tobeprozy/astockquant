import os

# 定义项目目录结构
project_structure = {
    "stock_quant_system": {
        "backend": {
            "app": {
                "__init__.py": "",
                "main.py": "",
                "config.py": "",
                "plugins": {
                    "__init__.py": "",
                    "macd_plugin.py": "",
                    "kdj_plugin.py": "",
                },
                "data_fetcher": {
                    "__init__.py": "",
                    "static_data.py": "",
                    "real_time_data.py": "",
                    "example": {}
                },
                "backtester": {
                    "__init__.py": "",
                    "backtest.py": ""
                },
                "utils": {
                    "__init__.py": "",
                    "plotting.py": ""
                }
            },
            "tests": {
                "__init__.py": "",
                "test_app.py": ""
            },
            "requirements.txt": ""
        },
        "frontend": {
            "public": {},
            "src": {
                "components": {},
                "pages": {},
                "services": {},
                "App.js": "",
                "index.js": ""
            },
            "package.json": "",
            "README.md": ""
        },
        "examples": {
            "platform1": {},
            "platform2": {},
            "platform3": {}
        },
        "docs": {
            "architecture.md": "",
            "api.md": "",
            "user_guide.md": ""
        },
        "README.md": ""
    }
}

def create_directory_structure(base_path, structure):
    for name, content in structure.items():
        path = os.path.join(base_path, name)
        if isinstance(content, dict):
            # 创建目录
            os.makedirs(path, exist_ok=True)
            # 递归创建子目录和文件
            create_directory_structure(path, content)
        else:
            # 创建文件
            with open(path, 'w') as f:
                f.write(content)

if __name__ == "__main__":
    base_path = os.getcwd()  # 当前工作目录
    create_directory_structure(base_path, project_structure)
    print("项目目录结构已生成！")

