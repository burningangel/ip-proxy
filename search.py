import requests
from bs4 import BeautifulSoup
import time


class Search:
    """
    先实例化，然后运行
    search = search.Search()  # 实例化
    search.get_menu()
    ip_list = search.get_proxies("国内高匿代理", 5)
    ip_list返回的类型详情看方法介绍
    """
    def __init__(self):
        self.base_url = 'http://www.xicidaili.com'
        self.headers = {'Accept-Encoding': 'gzip, deflate, sdch',
                        'Accept-Language': 'zh-CN,zh;q=0.8',
                        'Connection': 'keep-alive',
                        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 9_1 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13B143 Safari/601.1'}
        self.menu_array = {}  # 菜单栏的代理项及其链接

    def get_menu(self):
        r = requests.get(url=self.base_url, headers=self.headers, allow_redirects=False, timeout=10)
        soup = BeautifulSoup(r.text, "lxml")
        menu = soup.find_all("a", class_="false")
        del menu[-1]
        for item in menu:
            self.menu_array[item.string] = self.base_url + item['href']
            # return menu_array

    def get_ip_list(self, url):
        ip_info = []
        r = requests.get(url=url, headers=self.headers, allow_redirects=False, timeout=10)
        soup = BeautifulSoup(r.text, "lxml")
        ip_list = soup.find_all(class_="odd")
        for each_ip in ip_list:
            ip = each_ip.strings
            temp = ""
            for _ip_info in ip:
                _ip_info = _ip_info.replace("\n", "")
                _ip_info = _ip_info.replace("\t", "")
                if _ip_info == "":
                    continue
                temp = temp + "\t" + _ip_info
            if "HTTP" not in temp.split("\t")[5]:  # 舍弃没有城市信息的代理
                continue
            ip_info.append(temp + "\n")
        next_page = soup.find(class_="next_page")
        try:
            return ip_info, self.base_url + next_page['href']
        except KeyError:  # 没有下一页
            return ip_info, 0

    def is_available(self, proxies):
        url = "http://blog.csdn.net"  # 测试网页
        try:
            r = requests.get(url=url, headers=self.headers,
                             proxies=proxies, allow_redirects=False, timeout=5)
        except:
            return 0
        if r.status_code == requests.codes.ok and r.headers != {'Server': 'Proxy'}:
            # if "用户" in r.text:
            #     print(proxies)
            return 1
        else:
            return 0

    def get_proxies(self, proxies_type, ip_num):
        """
        :param proxies_type:国内高匿代理
        :param ip_num: 需要代理ip的数量
        :return: 一个list，list中的格式为：
                /t ip /t port /t city address /t 高匿 /t HTTPS /t 存活时间 /t 验证时间/n
        """
        url = self.menu_array[proxies_type]
        # for item in menu:
        #     print(menu[item])
        num = 0  # 有效数量
        count = 0  # 查询次数
        ip_proxies = []  # 有效ip的结果
        while url != "" and num < ip_num:
            time.sleep(6)
            ip_list = self.get_ip_list(url)
            if ip_list[1] == 0:  # 无下一页
                break
            url = ip_list[1]
            for each_ip_info in ip_list[0]:
                if num >= ip_num:
                    break
                ip_info = each_ip_info.split("\t")
                ip = ip_info[1]
                port = ip_info[2]
                proxies = {"http": "http://{}:{}".format(ip, port),
                           "https": "https://{}:{}".format(ip, port)}
                ip_state = self.is_available(proxies)
                if ip_state == 1:
                    num += 1
                    ip_proxies.append(each_ip_info)
                    # with open("proxies", "a") as out:
                    #     out.writelines(ip_list)
                count += 1
                print("已查询了{}条，{}条有效！\n".format(count, num))
        return ip_proxies
