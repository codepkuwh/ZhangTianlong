import requests

# level4-4
html = requests.post("http://level4.python-site.com/level4-4/?a=1", data={"name": "张天龙", "age": 24})
data = html.text
print(data)
print("-------------------")

# level4-6
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Safari/537.36',
    'Referer': 'codepku.com'
}
response = requests.get("http://level4.python-site.com/level4-6/", headers=headers)
print(response.text)
print(response.request.headers)
print("-------------------")

# level4-8
from bs4 import BeautifulSoup

url = "http://level4.python-site.com/level4-8/"
while True:
    html = requests.get(url)
    soup = BeautifulSoup(html.text, "lxml")
    try:
        url = soup.find("a").get("href")
        print(soup.find("a").text)
    except:
        print(html.text)
        break
    

# TODO: cookie 验证