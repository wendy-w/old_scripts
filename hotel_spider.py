import re
import time
from random import random
from tomorrow import threads
import pymysql
from bs4 import BeautifulSoup
import requests

url_list = [item.split(",")[3].strip("\n") for item in open("酒店URL（不带HTML）.txt", "r", encoding="utf-8").readlines()]

hotel_location_list = [item.split(",")[1].strip("\n") for item in
                       open("酒店URL（不带HTML）.txt", "r", encoding="utf-8").readlines()]
hotel_name_list = [item.split(",")[2].strip("\n") for item in
                   open("酒店URL（不带HTML）.txt", "r", encoding="utf-8").readlines()]

data_form = {
    'staydates': '2018_09_20_2018_09_21',
    'uguests': '1_1',
    'reqNum': '1'
}
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
    'X-Puid': 'W01f1H8AAAEAAJqYbXMAAAA6',
    'X-Requested-With': 'XMLHttpRequest'
}
supliers = ['Agoda', 'CTripINTDaoDao', 'BookingCN']


def get_mapping_id(provider, dic):
    src = dic[provider]
    id_url = "https://www.tripadvisor.cn/Commerce?p=%s&src=%s&from=HotelDataSearch_Hotel_Review&clt=D" % (provider, src)
    res = requests.get(id_url)
    print(res.status_code)
    if provider == "Agoda":
        r = re.findall(re.compile('HotelCode=(.*)"\);'), res.text)[0]
        # print(r)
        # print(res.text)
        return r
    elif provider == "BookingCN":
        r = re.findall(re.compile("hotel-(.*)pool"), res.text)[0].strip("_")
        # print(r)
        # print(res.text)
        return r
    elif provider == "CTripINTDaoDao":
        r = re.findall(re.compile("nal%2f(.*)\.html"), res.text)[0]
        # print(r)
        # print(res.text)
        return r
    else:
        return 0


def parse_id(url, name_, location_):
    global header
    global data_form
    # print(url)

    rl = requests.post(url, headers=header, data=data_form)
    soup = BeautifulSoup(rl.text, 'html.parser')
    flag = soup.find_all("div", attrs={'class': 'noAvailCommerce'})
    try:
        locationid = re.findall("-d(.*?)-R", url)[0]
    except:
        print("locationid exception")
        locationid = "NA"
    # print(locationid + "----------------" + str(i) + "/237787")
    hotel_location = location_
    hotel_name = name_
    reqtime = time.strftime("%Y-%m-%d %H:%M")
    if len(flag) == 0:
        res = soup.find_all("div", attrs={'class': 'ui_column viewAllText'})[0].find_all("span", attrs={
            'class': 'vendor'
        })
    else:
        return locationid, hotel_location, hotel_name, url, "AgodaNA", "BookingCNNA", "CTripINTDaoDaoNA", reqtime, "NA"
    r = [it.parent for it in res]
    parm = {}
    ids = {}
    for j in r:
        # print(j['data-locationid'])
        locationid = j['data-locationid']
        # print(j['data-vendorname'])
        vendorname = j['data-vendorname']
        # print(j['data-provider'])
        provider = j['data-provider']
        # print(re.findall(re.compile('div(.*)"=""'), str(j))[0].strip(" "))
        contentid = re.findall(re.compile('div(.*)"=""'), str(j))[0].strip(" ")
        parm[provider] = contentid
        parm['locationid'] = locationid
        parm['vendorname'] = vendorname
        # print("\n")
    # print(parm)
    # print(str(parm))
    for suplier in supliers:
        # print(suplier)
        # print(parm)
        if suplier in parm:
            ids[suplier] = get_mapping_id(suplier, parm)
        else:
            # print("Not contain:")
            # print(suplier)
            ids[suplier] = str(suplier) + "NA"
    return locationid, hotel_location, hotel_name, url, ids['Agoda'], ids['BookingCN'], ids[
        'CTripINTDaoDao'], reqtime, str(parm)


def break_start():
    break_flag = open("error_websites.txt", "r", encoding="utf-8").readlines()[-1].split(",")[0]
    print(break_flag)
    start = int(break_flag) + 1
    return start


@threads(100)
def do_main(x):
    connection = pymysql.connect(
        host='localhost',
        user='root',
        password='zxc1015zxc',
        db='mul_thread_test',
        cursorclass=pymysql.cursors.DictCursor
    )

    item = url_list[x]
    location = hotel_location_list[x]
    name = hotel_name_list[x]

    time.sleep(random() * 2)
    # print(item)
    try:
        a = parse_id(item, name, location)
        print(item)
        sql = "INSERT INTO `tripad_hotel_copy1` (`locationid`,`location`,`hotel_name`,`hotel_url`,`agodaid`,`ctripid`," \
              "`bookingcnid`, `reqtime`,`mapping`) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)"

        try:
            with connection.cursor() as cursor:
                cursor.execute(sql, a)
                connection.commit()
                global f
                f.write(str(a)[0] + "," + name + "\n")
                print("Done")
        except Exception as e:
            print(repr(e))
        finally:
            connection.close()

    except Exception as e:
        with open("uncral_" + now + ".txt", "a+") as un:
            un.write(item + "\n")
        print(repr(e))

    # global cursor
    # except Exception as e:
    #     print(repr(e)) 
    # with open("error_websites.txt", "a", encoding='utf-8') as err:
    #     err.write(str(x + 1) + "," + item + "\n")


def download_pages(x):
    item = url_list[x]
    location = hotel_location_list[x]
    name = hotel_name_list[x]
    time.sleep(random() * 2)


if __name__ == "__main__":
    now = time.strftime("%Y%m%d%H%M")
    f = open("task_" + now + ".txt", "w")
    # start_flag = 2714
    start_flag = 0
    lens = len(url_list)
    li = list(range(start_flag, lens))
    result = [do_main(i) for i in li]

    f.close()

    # try:
    #     with connection.cursor() as cursor:
    #         lens = len(url_list)
    #         # start_flag = break_start()
    #         start_flag = 2714
    #         for i in range(start_flag, lens):
    #
    #             item = url_list[i]
    #             try:
    #                 time.sleep(random() * 2)
    #                 print(item)
    #                 location = hotel_location_list[i]
    #                 name = hotel_name_list[i]
    #                 a, b, c, d, e, f, g, h, i = parse_id(item, name, location)
    #                 sql = "INSERT INTO `tripad_hotel` (`locationid`,`location`,`hotel_name`,`hotel_url`,`agodaid`,`ctripid`," \
    #                       "`bookingcnid`, `reqtime`,`mapping`) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)"
    #                 cursor.execute(sql, (a, b, c, d, e, f, g, h, i,))
    #                 connection.commit()
    #             except Exception as e:
    #                 print(repr(e))
    #                 with open("error_websites.txt", "a", encoding='utf-8') as err:
    #                     err.write(str(i + 1) + "," + item + "\n")

    # try:
    #     with connection.cursor() as cursor:
    #         lens = len(url_list)
    #         # start_flag = break_start()
    #         start_flag = 2714
    #         li = list(range(start_flag, lens))
    #         result = [do_main(i) for i in li]
    #
    # finally:
    #     connection.close()
    # for item in url_list[:100]:
    #     a, b, c, d = parse_id(item)
    #     print(a, b, c, d)
    # print(url_list[:5])
