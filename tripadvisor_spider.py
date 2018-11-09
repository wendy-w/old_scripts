import os

import requests
from bs4 import BeautifulSoup

url = "https://www.tripadvisor.cn/Lvyou"
test_url = "https://www.tripadvisor.cn/Hotels-g293991-Saudi_Arabia-Hotels.html"
count = 0
di = {
    'bubble_50': '5',
    'bubble_40': '4',
    'bubble_30': '3',
    'bubble_20': '2',
    'bubble_10': '1'
}
header = {
    'Host': 'www.tripadvisor.cn',
    'Connection': 'keep-alive',
    'Content': 'keep-alive',
    'X-Puid': 'W01f1H8AAAEAAJqYbXMAAAA6',
    'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36',
    'X-Requested-With': 'XMLHttpRequest'
}


# 从首页全部目的地取到所有目的地酒店列表
def get_all_url(u):
    r = requests.get(u)
    soup = BeautifulSoup(r.text, "html.parser")
    # <class 'bs4.element.Tag'>
    res = soup.find_all(attrs={'id': 'tab-body-wrapper'})[0].find_all("a")
    urls = []
    des_name = []
    for i in res:
        u = "https://www.tripadvisor.cn" + i["href"]
        u = u.replace("Tourism", "Hotels").replace("Vacations", "Hotels")
        # print(u)
        urls.append(u)
        des_name.append(i.string)
    c = list(zip(urls, des_name))
    return c


def getpagenum(url):
    data_form = {'offset': 0, 'cat': "1,2,3"}
    r = requests.post(url, headers=header, data=data_form)
    soup = BeautifulSoup(r.text, 'html.parser')
    try:
        num = soup.find(attrs={'class': 'unified ui_pagination standard_pagination ui_section listFooter'})[
            'data-numpages']
    except Exception:
        num = 0
    return int(num)


def get_hotel_url(city_url, city_location):
    print(city_url)
    pagenum = getpagenum(city_url)
    print(pagenum)

    for x in range(pagenum):
        data_form = {'offset': str(x * 30), 'cat': "1,2,3"}
        r2 = requests.post(city_url, headers=header, data=data_form)
        s2 = BeautifulSoup(r2.content, 'html5lib')
        # html_30 = s2.find_all("div", class_='listing collapsed')
        url_30 = ["https://www.tripadvisor.cn" + j.find("a")['href'] for j in
                  s2.find_all('div', attrs={'class': 'listing_title'})]
        name_30 = [j.find("a").string for j in s2.find_all('div', attrs={'class': 'listing_title'})]
        for y in range(len(url_30)):
            with open("酒店详情URL.txt", "a", encoding='utf-8') as f:
                f.write(city_location + "," + name_30[y] + "," + url_30[y] + "," + city_url + "\n")


def write_city_url(base_url):
    if os.path.exists("地区酒店URL.txt"):
        os.remove("地区酒店URL.txt")
    c = get_all_url(base_url)
    for item in c:
        with open("地区酒店URL.txt", "a", encoding='utf-8') as f:
            f.write(item[0] + ", " + item[1] + "\n")


def read_from_location(path):
    temp = open(path, 'r', encoding='utf-8').readlines()
    return [tuple(x.split(",")) for x in temp]


if os.path.exists("酒店详情URL.txt"):
    os.remove("酒店详情URL.txt")

c = read_from_location("地区酒店URL.txt")
for item in c:
    each_url = item[0]
    location = item[1].strip("\n")
    get_hotel_url(each_url, location)
    # print(each_url)
