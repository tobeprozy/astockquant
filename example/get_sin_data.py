import requests

# 获取某只股票的实时数据
stock_code = "sh600000"
url = f"http://hq.sinajs.cn/list={stock_code}"
response = requests.get(url)
print(response.text)
