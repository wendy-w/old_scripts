import json
import re
import time
import random

import pymysql
import requests
from bs4 import BeautifulSoup
from tomorrow import threads
from urllib3.exceptions import InsecureRequestWarning

# from get_proxies import get_proxies

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


def get_name(u):
    return name_list[url_list.index(u)]


ip_port = "transfer.mogumiao.com:9001"

proxy = {"http": "http://" + ip_port, "https": "https://" + ip_port}
url_list = [item.split(",")[0].strip("\n") for item in open("地区酒店URL.txt", "r", encoding="utf-8").readlines()]
name_list = [item.split(",")[1].strip("\n") for item in open("地区酒店URL.txt", "r", encoding="utf-8").readlines()]


# 补抓时传入
# url_list1 = [item.split(",")[0].strip("\n") for item in open("国家页失败链接.txt", "r", encoding="utf-8").readlines()]
# name_list1 = [get_name(item) for item in url_list1]


def get_proxies():
    a = requests.get(
        "http://piping.mogumiao.com/proxy/api/get_ip_bs?appKey=a69390b84f784590b9ee15a1f3369f56&count=30&expiryDate=0&format=2&newLine=3")
    res = a.text.split("\n")
    try:
        res.remove("")
    except:
        pass
    return ["https://" + str(item) for item in res]


def chk(s):
    return not re.search(r'-oa(\d+)-', s)


def get_page_list(country_url):
    part1, part2, part3 = re.split(re.compile("(-g.*?-)"), country_url)
    try:
        s1 = requests.get(country_url, headers=header, verify=False, timeout=10, proxies=proxy)
        country_soup = BeautifulSoup(s1.text,
                                     'html.parser')
        if s1.status_code != 200:
            with open("国家页失败链接.txt", "a+", encoding="utf-8") as f:
                f.write(country_url + "\n")
            return "0", "0"
    except Exception as e:
        with open("国家页失败链接.txt", "a+", encoding="utf-8") as f:
            f.write(country_url + "\n")
        return "0", "0", "0"
    try:
        page = country_soup.find_all("div", class_="pagination_wrapper")[0].find_all("div",
                                                                                     class_="prw_rup prw_common_standard_pagination_resp")[
            0].find_all("a", class_=re.compile("pageNum last taLnk"))[0]
        page_num = page['data-page-number']
        page_list = [country_url] + [part1 + part2 + "oa" + str(i) + "-" + part3 for i in
                                     range(20, int(page_num) * 20, 20)]
    except IndexError as e:
        page_list = [country_url]
    cities = []
    links = []
    range_ = []
    print("Page_list:" + str(page_list))
    for item in page_list:
        print(item)
        time.sleep(random.random() * 2)
        try:
            s = requests.get(item, headers=header, timeout=2, verify=False, proxies=proxy)
            print(s.status_code)
            if s.status_code != 200:
                with open("列表页失败链接.txt", "a+", encoding="utf-8") as f:
                    f.write(item + "\n")
                continue
        except Exception as e:
            print(repr(e))
            with open("列表页失败链接.txt", "a+", encoding="utf-8") as f:
                f.write(item + "\n")
            continue
        list_soup = BeautifulSoup(s.text, 'html.parser')

        try:
            if chk(item):
                # 不包括oa
                b = [k.string for k in list_soup.find_all("div", class_="linkText")]
                each_link = [each.parent['href'] for each in list_soup.find_all("div", class_="linkText")]
                cities += b
                links += each_link
                range_ += [str(j) for j in list(range(1, len(b) + 1))]
                pass
            else:
                # 包括 oa
                cities += [re.findall(re.compile(r'class="name">(.*?)<span'), str(ink))[0] for ink in
                           list_soup.find_all("span", class_="name")[:-1]]
                range_ += [item.string for item in list_soup.find_all("span", class_="rank")]
                links += [each_item.parent['href'] for each_item in list_soup.find_all("div", class_="info")]
                pass
        except Exception as e:
            print(repr(e))
            cities += [item]
    print(cities)
    print(range_)
    return cities, range_, links


@threads(10)
def insert_db(country_url, country):
    cities, range_, links = get_page_list(country_url)
    if cities != "0" and range_ != "0":
        cities_len = len(cities)
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='zxc1015zxc',
            db='trip_spider',
            cursorclass=pymysql.cursors.DictCursor
        )
        for each in range(0, cities_len):
            sql = "INSERT INTO  `country_cities`  (`country`,`city`,`range`,`check_url`,`city_url`) VALUES (%s,%s,%s,%s,%s) "
            a = (country_url, cities[each], range_[each], country, links[each])
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
    else:
        print(cities, range_)
        pass


if __name__ == "__main__":
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    lens = len(url_list)
    total = {}
    for i in range(lens):
        insert_db(url_list[i], name_list[i])
    # print(len(url_list1),url_list1)
    # print(len(name_list1),name_list1)
