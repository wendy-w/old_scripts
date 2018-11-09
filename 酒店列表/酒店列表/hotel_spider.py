import os
import re
import time
from random import random
from tomorrow import threads
import pymysql
from bs4 import BeautifulSoup
import requests
from urllib3.exceptions import InsecureRequestWarning

data_form = {
    'staydates': '2018_09_20_2018_09_21',
    'uguests': '1_1',
    'reqNum': '1'
}
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
success_record = "已抓取酒店url_v1.txt"
failed_record = "酒店请求失败url.txt"
failed_page = "full_page_failed.txt"
# pagenum_faild = "得不到页码url_v1.txt"
supliers = ['Agoda', 'BookingCN', 'CTripDaoDao', 'CTripINTDaoDao']


def get_mapping_id(provider, dic):
    src = dic[provider]
    id_url = "https://www.tripadvisor.cn/Commerce?p=%s&src=%s&from=HotelDataSearch_Hotel_Review&clt=D" % (provider, src)
    print(id_url)
    try:
        res = requests.get(id_url, headers=header, verify=False, timeout=10, proxies=proxy)
    except Exception as e:
        print(repr(e))
        return "ConnectFailed", ""

    # print(res.status_code)
    # print(res.text)
    try:
        if provider == "Agoda":
            r = re.findall(re.compile('HotelCode=(.*)"\);'), res.text)[0]
            # print(r)
            # print(res.text)
            return "1", r
        elif provider == "BookingCN":
            r = re.findall(re.compile("=hotel-(.*?)pool"), res.text)[0].strip("_")
            # print(r)
            # print(res.text)
            return "1", r
        elif provider == "CTripDaoDao":
            # print(res.text)
            r = re.findall(re.compile('%2Fname(.*)"'), res.text)
            if len(r) == 0:
                r = re.findall(re.compile('%2Fhotel%2F(.*)\.html'), res.text)
            print(r[0])
            # print(res.text)
            return "1", r[0]
        elif provider == "CTripINTDaoDao":
            r = re.findall(re.compile("nal%2f(.*)\.html"), res.text)[0]
            # print(r)
            # print(res.text)
            return "1", r
        else:
            return "1", 0
    except Exception:
        return "ConnectFailed", ""


def parse_id(url, name_):
    global header
    global data_form
    flag = 0
    # print(name_)
    try:
        # r2 = requests.get(url, headers=header, data=data_form, verify=False, timeout=10, proxies=proxy)
        rl = requests.post(url, headers=header, data=data_form, verify=False, timeout=10, proxies=proxy)
    except Exception:
        return "ConnectFailed", flag
    if rl.status_code == 200:
        global current
        if not os.path.exists(os.path.join(os.getcwd(), "hotel_details", str(current))):
            os.mkdir(os.path.join(os.getcwd(), "hotel_details", str(current)))

        dic_count = len(os.listdir(os.path.join(os.getcwd(), "hotel_details", str(current))))
        while dic_count >= 2000:
            if dic_count < 2000:
                current = current
            elif dic_count >= 2000:
                current += 1
                dic_count = len(os.listdir(os.path.join(os.getcwd(), "hotel_details", str(current))))
        page_path = os.path.join("hotel_details", str(current))
        if not os.path.exists(page_path):
            os.mkdir(page_path)
        html_name = url.split("/")[-1]
        with open(page_path + "/" + html_name, "w", encoding="utf-8") as detail_page:
            detail_page.write(rl.text)
    else:
        with open(failed_page, "a+", encoding="utf-8") as failed:
            failed.write(url + "\n")

    if rl.status_code == 200:
        soup = BeautifulSoup(rl.text, 'html.parser')
        flag_ = soup.find_all("div", attrs={'class': 'noAvailCommerce'})
        try:
            locationid = re.findall("-d(.*?)-R", url)[0]
        except:
            locationid = "NA"
        hotel_name = name_
        reqtime = time.strftime("%Y-%m-%d %H:%M")
        if len(flag_) == 0:
            res = soup.find_all("div", attrs={'class': 'ui_column viewAllText'})[0].find_all("span", attrs={
                'class': 'vendor'
            })
        else:
            return locationid, hotel_name, url, "", "", "", reqtime, "NA", flag
        r = [it.parent for it in res]
        # print(r)
        parm = {}
        ids = {}
        for j in r:
            locationid = j['data-locationid']
            vendorname = j['data-vendorname']
            provider = j['data-provider']
            contentid = re.findall(re.compile('div(.*)"=""'), str(j))[0].strip(" ")
            parm[provider] = contentid
            parm['locationid'] = locationid
            parm['vendorname'] = vendorname
        for suplier in supliers:
            if suplier in parm:
                temp = get_mapping_id(suplier, parm)
                if temp[0] == "ConnectFailed":
                    # global flag
                    flag = 1
                    ids[suplier] = temp[1]
                    continue
                ids[suplier] = temp[1]
            else:
                ids[suplier] = ""
        if ids['CTripDaoDao'] == "":
            return locationid, hotel_name, url, ids['Agoda'], ids['BookingCN'], ids[
                'CTripINTDaoDao'], reqtime, str(parm), flag
        else:
            return locationid, hotel_name, url, ids['Agoda'], ids['BookingCN'], ids[
                'CTripDaoDao'], reqtime, str(parm), flag
    else:
        return "0", flag


# @threads(15)
def do_main(x):
    connection = pymysql.connect(
        host='localhost',
        user='root',
        password='zxc1015zxc',
        db='trip_spider',
        cursorclass=pymysql.cursors.DictCursor
    )
    # 酒店url
    item = x[0]

    # 城市
    # location = hotel_location_list[x]

    # 酒店名字
    name = x[1]

    time.sleep(random() * 2)
    # print(item)
    print(item)
    a = parse_id(item, name)
    if a[0] == "ConnectFailed" or a[0] == "0":
        # global flag
        # flag = 1
        # 记录连接失败
        with open(failed_record, "a+", encoding="utf-8") as fail:
            fail.write(name + "," + item + "\n")
        return
    flag = a[-1]

    try:
        sql = "INSERT INTO `hotel_ids` (`locationid`,`hotel_name`,`hotel_url`,`agodaid`,`bookingcnid`," \
              "`ctripid`, `reqtime`,`mapping`) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"
        try:
            with connection.cursor() as cursor:
                cursor.execute(sql, a[:-1])
                connection.commit()
                print("Done")
                if flag == 0:
                    print(flag)
                    with open(success_record, "a+", encoding="utf-8") as succ:
                        succ.write(name + ";" + item + "\n")
                    pass
        except Exception as e:
            print("1：" + repr(e))
        finally:
            # connection.close()
            pass
    # 导入失败
    except Exception as e:
        print("2：" + repr(e))


def get_from_break():
    total_hotel_list = [item.split(";")[1].strip("\n") for item in
                        open("haoqiao_city_20180731.txt", "r", encoding="utf-8").readlines()]

    total_hotel_name_list = [item.split(";")[0].strip("\n") for item in
                             open("haoqiao_city_20180731.txt", "r", encoding="utf-8").readlines()]
    # for i in total_hotel_name_list:
    #     print(i.split(";")[0], i.split(";")[1])
    suc_hotel_list = [item.split(";")[1].strip("\n") for item in
                      open("已抓取酒店url_v1.txt", "r", encoding="utf-8").readlines()]
    suc_hotel_name_list = [item.split(";")[0].strip("\n") for item in
                           open("已抓取酒店url_v1.txt", "r", encoding="utf-8").readlines()]

    total = list(zip(total_hotel_list, total_hotel_name_list))
    suc = list(zip(suc_hotel_list, suc_hotel_name_list))

    for j in suc:
        total.remove(j)
    rest = total
    return rest


if __name__ == "__main__":
    start_flag = 0
    current = 1
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    hotel_list = get_from_break()
    # for i in hotel_list:
    #     print(i[0], i[1])
    result = [do_main(i) for i in hotel_list]
