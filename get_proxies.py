import random
import re

import requests
from bs4 import BeautifulSoup


def get_proxies():
    header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/67.0.3396.99 Safari/537.36',
        'Referer': 'https://www.baidu.com/',
        'Host': 'www.xicidaili.com',
        'Accept': 'text/html, */*',
        'Accept-Encoding': 'gzip,deflate,br',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Origin': 'https://www.xicidaili.com',
        'Connection': 'close'
    }

    header2 = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/67.0.3396.99 Safari/537.36',
        'Referer': 'https://www.tripadvisor.cn/',
        'Host': 'www.tripadvisor.cn',
        'Accept': 'text/html, */*',
        'Accept-Encoding': 'gzip,deflate,br',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Origin': 'https://www.tripadvisor.cn'
    }

    xici = ["http://www.xicidaili.com/nn/" + str(index) for index in range(1, 6)]
    ip_list, port_list, type_list = [], [], []
    for item in xici:
        r = requests.get(item, headers=header)
        soup = BeautifulSoup(r.text, "html.parser").find_all("table", attrs={"id": "ip_list"})[0]
        ip_pattern = re.compile("\d+\.\d+\.\d+\.\d")
        # print(re.findall(ip_pattern, str(soup)))
        ip_list += [i.string for i in soup.select(" tr > td:nth-of-type(2)")]
        port_list += [i.string for i in soup.select(" tr > td:nth-of-type(3)")]
        type_list += [i.string for i in soup.select(" tr > td:nth-of-type(6)")]

    x = len(ip_list)
    http_list = []
    https_list = []
    for item in range(x):
        if type_list[item] == "HTTP":
            http_list.append("http://" + ip_list[item] + ":" + port_list[item])
        elif type_list[item] == "HTTPS":
            https_list.append("https://" + ip_list[item] + ":" + port_list[item])
    print(https_list)

    https_ = []

    for k in https_list:
        try:
            s = requests.get("https://www.tripadvisor.cn/Hotels-g187275-oa3700-Germany-Hotels.html", headers=header2,
                             timeout=1, proxies={'https': k})
            if s.status_code == 200:
                https_.append(k)
                print(k)
        except Exception as e:
            print(repr(e))

    print(https_)
    return https_


with open("proxies.txt", "w") as f:
    for each in get_proxies():
        f.write(str(each) + "\n")
