import random
import re
import time

import pymysql
import requests
from bs4 import BeautifulSoup
from tomorrow import threads
from urllib3.exceptions import InsecureRequestWarning

from city_spider import chk, get_name

appKey = "MldySkFwUXRnNGZzMURocjpyazFDNm94Nlh1OXppOWZF"
header = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/67.0.3396.99 Safari/537.36',
    'Referer': 'https://www.tripadvisor.cn/Hotel_Review-g190356-d1767582-Reviews-or10-Novotel_Suites_'
               'Luxembourg-Luxembourg_City.html',
    'Host': 'www.tripadvisor.cn',
    'Accept': 'text/html, */*',
    'Accept-Encoding': 'gzip,deflate,br',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'Origin': 'https://www.tripadvisor.cn',
    "Proxy-Authorization": 'Basic ' + appKey
}

ip_port = "transfer.mogumiao.com:9001"
init_record = "列表页失败链接.txt"
failed_record = "列表页失败链接_temp.txt"
proxy = {"http": "http://" + ip_port, "https": "https://" + ip_port}


def get_country_url(oa_url):
    pattern = re.compile("-oa\d+?-")
    return re.sub(pattern, "-", oa_url)


# def get_city_list(page_list1):
#     cities = []
#     range_ = []
#     links = []
#     countries_url = []
#     print("Page_list:" + str(page_list1))
#     for item in page_list1:
#         print(item)
#         country_url = get_country_url(item)
#         time.sleep(random.random() * 2)
#         try:
#             s = requests.get(item, headers=header, timeout=2, verify=False, proxies=proxy)
#             print(s.status_code)
#             if s.status_code != 200:
#                 with open("列表页失败链接_temp.txt", "a+", encoding="utf-8") as f:
#                     f.write(item + "\n")
#                 continue
#         except Exception as e:
#             print(repr(e))
#             with open("列表页失败链接_temp.txt", "a+", encoding="utf-8") as f:
#                 f.write(item + "\n")
#             continue
#         list_soup = BeautifulSoup(s.text, 'html.parser')
#         try:
#             if chk(item):
#                 # 不包括oa
#                 b = [k.string for k in list_soup.find_all("div", class_="linkText")]
#                 cities += b
#                 each_link = [each.parent['href'] for each in list_soup.find_all("div", class_="linkText")]
#                 links += each_link
#                 range_ += [str(j) for j in list(range(1, len(b) + 1))]
#                 countries_url += [country_url] * len(b)
#                 pass
#             else:
#                 # 包括 oa
#                 c = list_soup.find_all("span", class_="name")[:-1]
#                 cities += [re.findall(re.compile(r'class="name">(.*?)<span'), str(ink))[0] for ink in c]
#                 range_ += [item.string for item in list_soup.find_all("span", class_="rank")]
#                 links += [each_item.parent['href'] for each_item in list_soup.find_all("div", class_="info")]
#                 countries_url += [country_url] * len(c)
#                 pass
#         except Exception as e:
#             print(repr(e))
#             cities += [item]
#     print(cities)
#     print(range_)
#     return cities, range_, links, countries_url
#
#
# def insert_db(page_lists):
#     cities, range_, links, countries_url = get_city_list(page_lists)
#     print(len(cities), cities)
#     print(len(range_), range_)
#     print(len(countries_url), countries_url)
#     if cities != "0" and range_ != "0":
#         cities_len = len(cities)
#         connection = pymysql.connect(
#             host='localhost',
#             user='root',
#             password='zxc1015zxc',
#             db='trip_spider',
#             cursorclass=pymysql.cursors.DictCursor
#         )
#         for each in range(0, cities_len):
#             sql = "INSERT INTO  `country_cities`  (`country`,`city`,`range`,`check_url`,`city_url`) VALUES (%s,%s,%s,%s,%s) "
#             ab = (countries_url[each], cities[each], range_[each], get_name(countries_url[each]), links[each])
#             try:
#                 with connection.cursor() as cursor:
#                     cursor.execute(sql, ab)
#                     connection.commit()
#                     print("Done")
#             except Exception as e:
#                 print(repr(e))
#             finally:
#                 # connection.close()
#                 pass
#     else:
#         print(cities, range_)
#         pass


def get_city(url):
    print(url)
    country_url = get_country_url(url)
    time.sleep(random.random() * 2)
    try:
        s = requests.get(url, headers=header, timeout=10, verify=False, proxies=proxy)
        print(s.status_code)
        if s.status_code != 200:
            with open(failed_record, "a+", encoding="utf-8") as f:
                f.write(url + "\n")
            return "0", "0", "0", "0"
    except Exception as e:
        print(repr(e))
        with open(failed_record, "a+", encoding="utf-8") as f:
            f.write(url + "\n")
        return "0", "0", "0", "0"
    list_soup = BeautifulSoup(s.text, 'html.parser')
    try:
        if chk(url):
            # 不包括oa
            b = [k.string for k in list_soup.find_all("div", class_="linkText")]
            cities = b
            each_link = [each.parent['href'] for each in list_soup.find_all("div", class_="linkText")]
            links = each_link
            range_ = [str(j) for j in list(range(1, len(b) + 1))]
            countries_url = [country_url] * len(b)
            pass
        else:
            # 包括 oa
            c = list_soup.find_all("span", class_="name")[:-1]
            cities = [re.findall(re.compile(r'class="name">(.*?)<span'), str(ink))[0] for ink in c]
            range_ = [item.string for item in list_soup.find_all("span", class_="rank")]
            links = [each_item.parent['href'] for each_item in list_soup.find_all("div", class_="info")]
            countries_url = [country_url] * len(c)
            pass
    except Exception as e:
        print(repr(e) + " —— 解析错误")
        cities = [url]
        return cities, "0", "0", "0"

    # return country,city,range_,check_url,city_url
    return cities, range_, countries_url, links


@threads(2)
def insert_db2(url):
    cities_1, range_1, check_url_1, city_url_1 = get_city(url)
    if cities_1 == "0" and range_1 == "0" and check_url_1 == "0" and city_url_1 == "0":
        return
    len_res = len(cities_1)
    country = get_name(get_country_url(url))

    connection = pymysql.connect(
        host='localhost',
        user='root',
        password='zxc1015zxc',
        db='trip_spider',
        cursorclass=pymysql.cursors.DictCursor
    )
    try:
        with connection.cursor() as cursor:
            for i in range(len_res):
                sql = "INSERT INTO  `country_cities`  (`country`,`city`,`range`,`check_url`,`city_url`) VALUES (%s,%s,%s,%s,%s) "
                res = (country, cities_1[i], range_1[i], check_url_1[i], city_url_1[i])
                cursor.execute(sql, res)
                connection.commit()
                print("Done")
    except Exception as e:
        print(repr(e))
    finally:
        connection.close()


if __name__ == "__main__":
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    init = open(init_record, "r", encoding="utf-8").readlines()
    page_list = [str(i).strip("\n") for i in init]
    for i in page_list:
        insert_db2(i)
