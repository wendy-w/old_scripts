import requests
from bs4 import BeautifulSoup

data_form = {
    'staydates': '2018_09_20_2018_09_21',
    'uguests': '1_1',
    'reqNum': '1'
}
proxies = {
    'https': 'http://113.200.27.10:53281'
}
appKey = "MldySkFwUXRnNGZzMURocjpyazFDNm94Nlh1OXppOWZF"
header = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/67.0.3396.99 Safari/537.36',
    'Referer': 'https://www.tripadvisor.cn/',
    'Host': 'www.tripadvisor.cn',
    'Accept': 'text/html, */*',
    'Accept-Encoding': 'gzip,deflate,br',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'Origin': 'https://www.tripadvisor.cn'
}
url = "https://www.tripadvisor.cn/Hotels-g293931-oa20-Armenia-Hotels.html"
ip_port = "transfer.mogumiao.com:9001"

r = requests.get(url,headers=header)
list_soup = BeautifulSoup(r.text, 'html.parser')
each_link = [each_item.parent['href'] for each_item in list_soup.find_all("div", class_="info")]
print(len(each_link),each_link)