import os
import time

import pymysql
import requests
from bs4 import BeautifulSoup
from tomorrow import threads
from urllib3.exceptions import InsecureRequestWarning

appKey = "MldySkFwUXRnNGZzMURocjpyazFDNm94Nlh1OXppOWZF"
header = {
    'Host': 'www.tripadvisor.cn',
    'Referer': 'https://www.tripadvisor.cn/Hotel_Review-g190356-d1767582-Reviews-or10-Novotel_Suites_'
               'Luxembourg-Luxembourg_City.html',
    'Connection': 'keep-alive',
    'Content': 'keep-alive',
    'X-Puid': 'W01f1H8AAAEAAJqYbXMAAAA6',
    'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
                  ' Chrome/67.0.3396.99 Safari/537.36',
    'X-Requested-With': 'XMLHttpRequest',
    "Proxy-Authorization": 'Basic ' + appKey
}
ip_port = "transfer.mogumiao.com:9001"

proxy = {"http": "http://" + ip_port, "https": "https://" + ip_port}
success_record = "已抓取城市url_v1.txt"
failed_record = "城市酒店失败url_v1.txt"
pagenum_faild = "得不到页码url_v1.txt"


# def getpagenum(url):
#     # 存在严重bug
#     data_form = {'offset': 0, 'cat': "1,2,3"}
#     r = requests.post(url, headers=header, data=data_form, verify=False, timeout=10, proxies=proxy)
#     if r.status_code == 200:
#         soup = BeautifulSoup(r.text, 'html.parser')
#         try:
#             num = soup.find(attrs={'class': 'unified ui_pagination standard_pagination ui_section listFooter'})[
#                 'data-numpages']
#         except Exception:
#             num = 1
#         return int(num)
#     else:
#         print("get pagenum failed!")
#         return 0

def getpagenum(url):
    data_form = {'offset': 0, 'cat': "1,2,3"}
    # noinspection PyBroadException
    try:
        r = requests.post(url, headers=header, data=data_form, verify=False, timeout=10, proxies=proxy)
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, 'html.parser')
            # noinspection PyBroadException
            try:
                num = soup.find(attrs={'class': 'unified ui_pagination standard_pagination ui_section listFooter'})[
                    'data-numpages']
            except Exception:
                num = 1
            return int(num)
        else:
            # print("get pagenum failed!")
            return 0
    except Exception:
        return 0


@threads(10)
def get_hotel_url(city_url):
    print(city_url)
    pagenum = getpagenum(city_url)  # req1
    print(pagenum)
    flag = 0
    city_location = get_location_name(city_url)

    if pagenum == 0:
        with open(pagenum_faild, "a+") as ym:
            ym.write(city_url + "\n")
        return
    else:
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='zxc1015zxc',
            db='trip_spider',
            cursorclass=pymysql.cursors.DictCursor
        )

        for x in range(pagenum):
            print(x)
            # data_form = {'offset': 0, 'cat': "1,2,3"}
            data_form = {'offset': str(x * 30), 'cat': "1,2,3"}
            try:
                # req2
                r2 = requests.post(city_url, headers=header, data=data_form, verify=False, timeout=10, proxies=proxy)
                s2 = BeautifulSoup(r2.content, 'html5lib')
                # html_30 = s2.find_all("div", class_='listing collapsed')
                url_30 = ["https://www.tripadvisor.cn" + j.find("a")['href'] for j in
                          s2.find_all('div', attrs={'class': 'listing_title'})]
                name_30 = [j.find("a").string for j in s2.find_all('div', attrs={'class': 'listing_title'})]
                for y in range(len(url_30)):
                    sql = "INSERT INTO  `city_hotels_0727_copy1`  (`city`,`hotel_name`,`hotel_url`,`city_url`) " \
                          "VALUES (%s,%s,%s,%s) "
                    a = (city_location, name_30[y], url_30[y], city_url)
                    try:
                        with connection.cursor() as cursor:
                            cursor.execute(sql, a)
                            connection.commit()
                            print("Done")
                    except Exception as e:
                        print(repr(e))
                    finally:
                        # connection.close()
                        pass
            except Exception as e:
                print(repr(e))
                if flag != 1:
                    with open(failed_record, "a+", encoding="utf-8") as f2:
                        f2.write(city_url + "\n")
                flag = 1
                continue
        if flag == 0:
            with open(success_record, "a+", encoding="utf-8") as suc:
                suc.write(city_url + "\n")


def get_from_break():
    try:
        f_sucess = open(success_record, "r", encoding="utf-8")
        sucess_list = [item.strip("\n") for item in f_sucess.readlines()]
    except FileNotFoundError:
        sucess_list = []
    for i in sucess_list:
        try:
            city_urls.remove(i)
        except:
            print("error")
            pass
    # print(len(sucess_list))
    # return list(set(city_urls).difference(set(sucess_list)))
    return city_urls


def get_location_name(city_url):
    index = city_urls.index(city_url)
    return city_locations[index]


if __name__ == "__main__":
    print(os.getcwd())
    base = os.path.join(os.getcwd(), "country_cities_20180725.txt")
    f = open(base, "r", encoding="utf-8")
    city_lists = [item.strip("\n") for item in f.readlines()]
    f.close()
    city_urls = ["https://www.tripadvisor.cn" + i.split(",")[2] for i in city_lists]
    city_locations = [i.split(",")[0] for i in city_lists]
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    # rest = ["https://www.tripadvisor.cn/Hotels-g293940-Phnom_Penh-Hotels.html"]
    rest = get_from_break()
    # location_lists = [get_location_name(ea) for ea in rest]
    # len_rest = len(rest)
    # rest = ["https://www.tripadvisor.cn/Hotels-g737144-Semey_East_Kazakhstan_Province-Hotels.html"]
    for i in rest:
        get_hotel_url(i)
