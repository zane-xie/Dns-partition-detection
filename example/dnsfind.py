#!/usr/bin/python
#coding=utf-8
# by xz
# 2018-11-12
# version v1.0

import socket
import re
import json
import os
import time
import datx
import threading
import urllib2
import sys
import subprocess
import random


# 兼容中文字符串
defaultencoding = 'utf-8'
if sys.getdefaultencoding() != defaultencoding:
	reload(sys)
	sys.setdefaultencoding(defaultencoding)

# 定义api的基本数据
sk = socket.socket()
ip_port = ('127.0.0.1',1666)
sk.bind(ip_port)
sk.listen(20)


# 定义一个函数，根据域名获取备案信息
def get_domain_mess(domain):
        # 1、先查本地缓存（30天过期）
        # 2、本地没有缓存，通过第三方接口获取备案信息
        # 3、将第三方接口获取到的备案信息保存至本地，或者更新缓存

        now_time_sjc = int(time.time())
        domain_yu = '.' + domain.split('.')[-3] + '.' + domain.split('.')[-2] + '.' + domain.split('.')[-1]
        beian_mess = "notfd"

	try:
       	 with open ('/home/app/ipip/domain_mess.txt') as f:
       	         for line in f:
       	                 if domain_yu in line:
       	                         beian_mess = line.split()[2]
       	                         cache_time = line.split()[0]

       	                         # 判断缓存是否过期
       	                         if int(now_time_sjc) - int(cache_time) < 2592000:
       	                                 # 没过期则直接输出本地缓存数据
       	                                 return beian_mess
       	                         else:
       	                                 # 本地缓存过期了，从远端接口获取数据，并更新本地配置
       	                                 get_url = 'http://icp.chinaz.com/'+domain
       	                                 req = urllib2.Request(get_url)
       	                                 r = urllib2.urlopen(req , timeout = 5)

       	                                 html = r.read()               # 返回网页内容
       	                                 receive_header = r.info()    # 返回的报头信息

       	                                 p = re.compile(r'class')
       	                                 allmess = p.split(html)
       	                                 domain_yu = '.' + domain.split('.')[-3] + '.' + domain.split('.')[-2] + '.' + domain.split('.')[-1]

       	                                 for i in allmess:
       	                                         if '主办单位名称' in i:
       	                                                 beian_mess = i.split('>')[4].split('<')[0]
       	                                 # 删除本地缓存备份
       	                                 cmd1 = 'sed -i "/' + domain_yu +'/d" /home/app/ipip/domain_mess.txt'
       	                                 subprocess.call(cmd1, shell=True)
       	                                 # 增加记录
       	                                 cmd2 = 'echo "' + str(now_time_sjc) + ' ' +  str(domain_yu) + ' ' + str(beian_mess) + '" >> /home/app/ipip/domain_mess.txt'
       	                                 subprocess.call(cmd2, shell=True)
       	                                 return beian_mess
       	 # 假如本地没有缓存记录
       	 if beian_mess == 'notfd':
       	         # 本地没有任何缓存数据
       	         get_url = 'http://icp.chinaz.com/'+domain
       	         req = urllib2.Request(get_url)
       	         r = urllib2.urlopen(req , timeout = 5)

       	         html = r.read()               # 返回网页内容
       	         receive_header = r.info()    # 返回的报头信息

       	         p = re.compile(r'class')
       	         allmess = p.split(html)
       	         domain_yu = '.' + domain.split('.')[-3] + '.' + domain.split('.')[-2] + '.' + domain.split('.')[-1]

       	         for i in allmess:
       	                 if '主办单位名称' in i:
       	                         beian_mess = i.split('>')[4].split('<')[0]
       	                         # 增加记录
       	                         cmd2 = 'echo "' + str(now_time_sjc) + ' ' +  str(domain_yu) + ' ' + str(beian_mess) + '" >> /home/app/ipip/domain_mess.txt'
       	                         subprocess.call(cmd2, shell=True)
       	                         return beian_mess

	except:
		beian_mess = "任务超时或未获取到备案信息"


#print get_domain_mess('pcvideoyf.mgtv.com.cdn.xzdns.net')

# 定义一个函数，用于获取获取ip对应的区域名称
def get_ip_mess(ipaddr):
	# 获取ip区域
	try:
		c = datx.City("/home/app/ipip/mydata4vipday2.datx")
		mess_ip = (c.find(ipaddr))
		county = mess_ip[0]                        # 输出国家
		pro = mess_ip[1]                           # 输出省份
		city = mess_ip[2]                          # 输出城市
		isp = mess_ip[4]                           # 输出运营商
		ip_mess = county+'.'+pro+'.'+isp
	except:
		ip_mess = "IP归属地未知"

	return ip_mess



# 定义一个函数，用于获取获取ip对应的区域名称(精确到市)
def get_ipqy_mess(ipaddr):
	# 获取ip区域
	try:
		c = datx.City("/home/app/ipip/mydata4vipday2.datx")
		mess_ip = (c.find(ipaddr))
		county = mess_ip[0]                        # 输出国家
		pro = mess_ip[1]                           # 输出省份
		city = mess_ip[2]                          # 输出城市
		isp = mess_ip[4]                           # 输出运营商
		ip_mess = county+'.'+pro+'.'+city+'.'+isp
	except:
		ip_mess = "IP归属地未知"

	return ip_mess




# 定义一个函数，用于接受参数进行dig请求
def get_cname_digmess(localip,domain,now_time_sjc): 
        # 定义变量
        os.environ['dig_domain']=str(domain)
        os.environ['dig_ip']=str(localip)
        os.environ['dig_time']=str(now_time_sjc)

        try:
                # 重试5次获取数据
                n = 1
                m = 5

                while n < m:
                        cmd = "/home/app/ipip/dig @119.29.29.29 $dig_domain +subnet=$dig_ip +tries=1 +time=2 |grep CNAME |head -n 1|awk '{print $NF}'"
                        p = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE)
                        out,err = p.communicate()
                        for line in out.splitlines():
                            if '.' in str(line):
                                n = 12
                                domain_cname = str(line)[:-1]
                                # 获取dig后CNAME的备案信息
                                domain_ba = get_domain_mess(str(domain_cname))
                        else:
                                n += 1

        except:
                domain_cname = "notfind"
                domain_ba = "notfind"

        # 获取dig客户端ip区域
        localip_qy = get_ip_mess(localip)

        # 将信息保存到本地，格式为 /home/app/ipip/tmp/get-域名-时间戳
        wr_filename = '/home/app/ipip/tmp/get-' + str(domain) + '-' + str(now_time_sjc)
        #all_mess = '<tr><td>' + localip_qy + '</td><td>' + domain + '</td><td>' + 'CNAME' + '</td><td>' + str(domain_cname)  + '</td><td>' + str(domain_ba) + '</td></tr>'
        url302 = "http://dns.example.com/cname&passwd=xzdnss_dnsfind?inputmess=" + str(domain_cname)

        all_mess = '<tr><td>' + localip_qy + '</td><td>' + domain + '</td><td>' + 'CNAME' + '</td><td>' + "<a href='" + url302 + "' onclick=" + '"return confirm(' + "'点击确认查询该域名的CNAME记录, 查询域名为:" + domain_cname + "');" + '">' +str(domain_cname) + '</a></td><td>' + str(domain_ba) + '</td></tr>'
        h = open(wr_filename, 'a')
        h.write(all_mess)
        h.close()




# 定义一个函数，用于获取A记录
def get_ip_digmess(localip,domain,now_time_sjc,digdns):
        # 定义变量
        os.environ['dig_domain']=str(domain)
        os.environ['dig_ip']=str(localip)
        os.environ['dig_time']=str(now_time_sjc)
        os.environ['dig_dns']=str(digdns)
        wr_filename = '/home/app/ipip/tmp/get-' + str(domain) + '-' + str(now_time_sjc)

        filename = '/home/app/ipip/tmp/dig-' + str(localip) + '-' + domain + '-' + str(now_time_sjc) + '.log'

        try:
                # 试3次获取数据
                n = 1
                m = 3
                while n < m:
                        # 进行dig检测
                        cmd = "/home/app/ipip/dig @$dig_dns $dig_domain +subnet=$dig_ip +tries=1 +time=2 |egrep 'CLIENT-SUBNET|IN' |egrep '0$|1$|2$|3$|4$|5$|6$|7$|8$|9$'|awk '{print $(NF -1),$NF}'"
                        p = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE)
                        out,err = p.communicate()
                        for line in out.splitlines():
                                if 'CLIENT-SUBNET' in line:
                                        clientip = line.split(' ')[1].split('/')[0]
                                        # 获取dig客户端ip区域
                                        localip_qy = get_ip_mess(localip)
                        # 再次执行循环
                        for x in out.splitlines():
                                if 'CLIENT-SUBNET' not in line and '.' in line:
                                        serip = line.split(' ')[1]
                                        ip_qy_mess = get_ipqy_mess(str(serip))
                                        n = 10
                                        # 将信息保存到本地，格式为 /home/app/ipip/tmp/get-域名-时间戳
                                        all_mess = '<tr><td>' + localip_qy + '</td><td>' + domain + '</td><td>' + 'A' + '</td><td>' + str(serip)  + '</td><td>' + str(ip_qy_mess) + '</td></tr>'
                                        h = open(wr_filename, 'a')
                                        h.write(all_mess)
                                        h.close()
                                else:
                                        n += 1
        except:
                # 再次进行重试
                test = "test"




# 定义一个计算函数，多线程执行任务
def get_all_mess(domain,type):
	# 定义一个全国各个区域的ip列表
	iplist = [ 
	"219.147.198.242",
	"202.97.224.69",
	"211.137.241.36",
	"219.149.194.55",
	"202.98.0.68",
	"211.141.16.99",
	"219.148.204.66",
	"202.96.64.68",
	"211.137.32.188",
	"1.180.207.132",
	"202.99.224.67",
	"211.138.91.1",
	"202.106.46.151",
	"202.106.169.115",
	"211.136.17.107",
	"221.238.23.102",
	"202.99.96.68",
	"211.137.160.5",
	"222.222.202.202",
	"202.99.166.4",
	"111.11.4.239",
	"219.146.0.130",
	"202.102.134.68",
	"218.201.96.130",
	"219.149.135.188",
	"202.99.216.113",
	"211.138.106.2",
	"123.160.10.66",
	"202.102.224.68",
	"211.138.24.66",
	"218.30.19.40",
	"221.11.1.67",
	"211.137.130.2",
	"222.75.152.129",
	"221.199.12.157",
	"218.203.123.116",
	"202.100.64.66",
	"221.7.34.10",
	"218.203.160.194",
	"61.128.114.133",
	"221.7.1.20",
	"218.202.152.130",
	"202.98.224.69",
	"221.13.65.56",
	"211.139.73.34",
	"202.100.128.68",
	"221.207.58.58",
	"211.138.75.123",
	"202.98.96.68",
	"211.137.96.205",
	"183.221.253.100",
	"222.172.200.68",
	"221.3.131.11",
	"211.139.29.150",
	"61.128.128.68",
	"221.7.92.86",
	"218.201.17.1",
	"119.1.109.109",
	"211.92.136.81",
	"211.139.5.29",
	"202.103.224.68",
	"221.7.128.68",
	"211.138.240.100",
	"202.96.128.68",
	"210.21.4.130",
	"211.136.20.203",
	"202.100.192.68",
	"221.11.132.2",
	"221.11.141.9",
	"202.103.24.68",
	"218.104.111.112",
	"211.137.58.20",
	"202.102.192.68",
	"218.104.78.2",
	"211.138.180.3",
	"218.2.135.1",
	"58.240.57.33",
	"112.4.16.200",
	"118.118.118.51",
	"140.207.223.153",
	"211.136.112.50",
	"202.101.224.69",
	"220.248.192.12",
	"211.141.90.68",
	"222.246.129.80",
	"58.20.126.98",
	"211.142.211.124",
	"202.101.172.48",
	"221.12.102.227",
	"211.140.10.2",
	"202.101.107.54",
	"218.104.128.106",
	"211.138.151.66",
	"211.161.124.199",
	"124.14.16.3",
	"211.167.230.100",
	"101.47.94.10",
	"175.188.188.135",
	"211.162.31.80",
	"211.162.32.116",
	"211.162.208.12",
	"211.162.130.33",
	"202.112.30.157",
	"202.113.48.10",
	"202.120.2.100",
	"202.115.32.36",
	"211.69.143.1",
	"23.236.115.24",
	"128.1.64.246",
	"23.236.107.67",
	"107.155.16.200",
	"128.1.87.249",
	"202.116.0.1"
	]

	# 定义固定首页
	all_mess = '<h1><font color="purple">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;DNS记录查询系统</h1><p></p><form action="http://dns.example.com/cname&passwd=xzdnss_dnsfind"; method="GET">&nbsp;CNAME记录查询入口-->&nbsp;请输入需要查询域名:&nbsp;<input  type="text" name="inputmess" />&nbsp;<input  type="submit" value="查询"></form><p></p>'
	all_mess += '<form action="http://dns.example.com/getip&passwd=xzdnss_dnsfind"; method="GET">&nbsp;<font color="azure">MA</font>A<font color="azure">AA</font>记录查询入口-->&nbsp;请输入需要查询域名:&nbsp;<input  type="text" name="inputmess" />&nbsp;<input  type="submit" value="查询"></form><p></p>'
        all_mess += '<form action="http://dns.example.com/ipmes&passwd=xzdnss_dnsfind"; method="GET">&nbsp;<font color="azure">MM</font>IP<font color="azure">M</font>地域查询入口-->&nbsp;请输入需要查ip地址:&nbsp;<input  type="text" name="inputmess" />&nbsp;<input  type="submit" value="查询"></form><p></p>'
	all_mess += '&nbsp;<p></p>'
	all_mess += '&nbsp;1、本系统查询的解析结果是EDNS解析得来，不完全代表整个区域的实际解析情况，解析结果仅供参考，不具备故障证据之作用。<p></p>'
	all_mess += '&nbsp;2、域名备案信息通过第三方获取（本地会缓存30天）。<p></p>'
	all_mess += '&nbsp;3、开发者联系邮箱xiezan@yfcloud.com。<p></p>'	

	now_time_sjc = int(time.time())
        # 定义每次任务存储路径
        allwr_filename = '/home/app/ipip/tmp/get-' + str(domain) + '-' + str(now_time_sjc)

        # 针对不同参数调用不同的函数
        if type == "cname":
                # 调用获取CNAME的函数
                all_mess += '<table border="1" cellspacing="0"><tr><th>&nbsp;&nbsp;&nbsp;区域&nbsp;&nbsp;&nbsp;</th><th>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;查询域名&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</th><th>记录类型</th><th>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;查询结果(可以点击进行二次查询)&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</th><th>&nbsp;&nbsp;&nbsp;&nbsp;CNAME备案信息&nbsp;&nbsp;&nbsp;&nbsp;</th></tr>'

                # 多线程进行计算处理
                for i in iplist:
                        t = threading.Thread(target=get_cname_digmess,args=(i,domain,now_time_sjc))
                        t.start()

                # 等待其他线程执行完成
                time.sleep(3)

                # 读取返回结果
                with open(allwr_filename) as f:
                        for line in f:
                                all_mess += line

                return all_mess
                os.remove(allwr_filename)	

	elif type == "getip":
		# 调用获取ip的函数
		all_mess += '<table border="1" cellspacing="0"><tr><th>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;区域&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</th><th>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;查询域名&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</th><th>记录类型</th><th>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;server ip&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</th><th>&nbsp;&nbsp;&nbsp;&nbsp;serverip区域信息&nbsp;&nbsp;&nbsp;&nbsp;</th></tr>'

                # 多线程进行计算处理
                for i in iplist:
                        # 随机使用dns
                        dnslist = ["119.28.28.28","119.29.29.29","182.254.116.116","182.254.118.118"]
                        digdns = random.sample(dnslist,1)[0]
                        t = threading.Thread(target=get_ip_digmess,args=(i,domain,now_time_sjc,digdns))
                        t.start()

                # 等待其他线程执行完成
                time.sleep(1)

                # 读取返回结果
                with open(allwr_filename) as f:
                        for line in f:
                                all_mess += line

                return all_mess
                os.remove(allwr_filename)


# 定义一个函数,用于返回ip查询归属地信息
def get_ipmess(in_mess):
	# 定义首页
	all_mess = '<h1><font color="purple">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;DNS记录查询系统</h1><p></p>'
	# 获取查询ip基础信息
	ipqy = get_ipqy_mess(in_mess)

	all_mess += '<form action="http://dns.example.com/cname&passwd=xzdnss_dnsfind"; method="GET">&nbsp;CNAME记录查询入口-->&nbsp;请输入需要查询域名:&nbsp;<input  type="text" name="inputmess" />&nbsp;<input  type="submit" value="查询"></form><p></p>'
        all_mess += '<form action="http://dns.example.com/getip&passwd=xzdnss_dnsfind"; method="GET">&nbsp;<font color="azure">AM</font>A<font color="azure">AA</font>记录查询入口-->&nbsp;请输入需要查询域名:&nbsp;<input  type="text" name="inputmess" />&nbsp;<input  type="submit" value="查询"></form><p></p>'
        all_mess += '<form action="http://dns.example.com/ipmes&passwd=xzdnss_dnsfind"; method="GET">&nbsp;<font color="azure">MM</font>IP<font color="azure">M</font>地域查询入口-->&nbsp;请输入需要查ip地址:&nbsp;<input  type="text" name="inputmess" />&nbsp;<input  type="submit" value="查询"></form><p></p>'

	all_mess += '&nbsp<p></p>'
	all_mess += '&nbsp;您查询的ip地址为: ' + str(in_mess) + '&nbsp;&nbsp;该ip归属地为:<font color="darkorange">' + str(ipqy) + '</font><p></p>'

        all_mess += '&nbsp;<p></p>'
        all_mess += '&nbsp;1、本系统查询的解析结果是EDNS解析得来，不完全代表整个区域的实际解析情况，解析结果仅供参考，不具备故障证据之作用。<p></p>'
        all_mess += '&nbsp;2、域名备案信息通过第三方获取（本地会缓存30天）。<p></p>'
        all_mess += '&nbsp;3、开发者联系邮箱xiezan@yfcloud.com。<p></p>'

        return all_mess
			


# 定义一个函数,用于返回域名备案信息信息
def get_dmbnmess(in_mess):
	# 定义首页
	all_mess = '<h1><font color="purple">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;DNS记录查询系统</h1><p></p>'
	# 获取查询ip基础信息
	ipqy = get_domain_mess(in_mess)

	all_mess += '<form action="http://dns.example.com/cname&passwd=xzdnss_dnsfind"; method="GET">&nbsp;CNAME记录查询入口-->&nbsp;请输入需要查询域名:&nbsp;<input  type="text" name="inputmess" />&nbsp;<input  type="submit" value="查询"></form><p></p>'
        all_mess += '<form action="http://dns.example.com/getip&passwd=xzdnss_dnsfind"; method="GET">&nbsp;<font color="azure">AM</font>A<font color="azure">AA</font>记录查询入口-->&nbsp;请输入需要查询域名:&nbsp;<input  type="text" name="inputmess" />&nbsp;<input  type="submit" value="查询"></form><p></p>'
        all_mess += '<form action="http://dns.example.com/ipmes&passwd=xzdnss_dnsfind"; method="GET">&nbsp;<font color="azure">MM</font>IP<font color="azure">M</font>地域查询入口-->&nbsp;请输入需要查ip地址:&nbsp;<input  type="text" name="inputmess" />&nbsp;<input  type="submit" value="查询"></form><p></p>'

	all_mess += '&nbsp<p></p>'
	all_mess += '&nbsp;您查询的域名为: ' + str(in_mess) + '&nbsp;该域名备案归属为:<font color="darkorange">' + str(ipqy) + '</font><p></p>'

        all_mess += '&nbsp;<p></p>'
        all_mess += '&nbsp;1、本系统查询的解析结果是EDNS解析得来，不完全代表整个区域的实际解析情况，解析结果仅供参考，不具备故障证据之作用。<p></p>'
        all_mess += '&nbsp;2、域名备案信息通过第三方获取（本地会缓存30天）。<p></p>'
        all_mess += '&nbsp;3、开发者联系邮箱xiezan@yfcloud.com。<p></p>'

        return all_mess
			


# 定义一个主界面返回函数
def index(clientip):
	# 定义首页
	all_mess = '<h1><font color="purple">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;DNS记录查询系统</h1><p></p>'
	# 获取当前客户端出口ip的区域
	ipqy = get_ipqy_mess(clientip)
	all_mess += '&nbsp;您当前出口ip地址为: ' + str(clientip) + '&nbsp;&nbsp;该ip归属地为:<font color="darkorange">' + str(ipqy) + '</font><p></p>'

	all_mess += '<form action="http://dns.example.com/cname&passwd=xzdnss_dnsfind"; method="GET">&nbsp;CNAME记录查询入口-->&nbsp;请输入需要查询域名:&nbsp;<input  type="text" name="inputmess" />&nbsp;<input  type="submit" value="查询"></form><p></p>'
	all_mess += '<form action="http://dns.example.com/getip&passwd=xzdnss_dnsfind"; method="GET">&nbsp;<font color="azure">AM</font>A<font color="azure">AA</font>记录查询入口-->&nbsp;请输入需要查询域名:&nbsp;<input  type="text" name="inputmess" />&nbsp;<input  type="submit" value="查询"></form><p></p>'
	all_mess += '<form action="http://dns.example.com/ipmes&passwd=xzdnss_dnsfind"; method="GET">&nbsp;<font color="azure">MM</font>IP<font color="azure">M</font>地域查询入口-->&nbsp;请输入需要查ip地址:&nbsp;<input  type="text" name="inputmess" />&nbsp;<input  type="submit" value="查询"></form><p></p>'

	all_mess += '&nbsp;<p></p>'
	all_mess += '&nbsp;1、本系统查询的解析结果是EDNS解析得来，不完全代表整个区域的实际解析情况，解析结果仅供参考，不具备故障证据之作用。<p></p>'
	all_mess += '&nbsp;2、域名备案信息通过第三方获取（本地会缓存30天）。<p></p>'
	all_mess += '&nbsp;3、开发者联系邮箱xiezan@yfcloud.com。<p></p>'	

	return all_mess


# 定义mian函数
# 三个访问页面 http://dns.example.com/xzdns&passwd=xzdnss_dnsfind
# http://dns.example.com:1666/cname&passwd=xzdnss_dnsfind?inputmess=afafafa
# http://dns.example.com:1666/getip&passwd=xzdnss_dnsfind?inputmess=afafafa

def main():
	while True:
		conn,address = sk.accept()
		#clientip = address[0]            # 获取客户端ip
		# 获取客户所带数据，并进行相关判断
		data = conn.recv(1024)
		# 利用正则获取自己想要的相关数据
		p = re.compile(r'\n')
		mess = p.split(data)

		try:
			for a in mess:
				if 'X-Real-IP' in a:
					clientip = str(a[11:])            # 获取客户端ip
			for i in mess:
				if 'GET' in i and 'favicon.ico' not in i:
					if 'passwd=' not in i:
						# 假如请求参数不全，则直接返回错误提示
						content = 'HTTP/1.1 403 forbidden\r\nContent-Type: text/html; charset=UTF-8\r\n\r\n'
						content += '<p><font color="red" size="3">请求出错-请求参数不全 ！！！</p>'
						conn.send(content.encode('utf-8'))
						conn.close()
					# 主页信息获取
					elif 'passwd' in i and '?' not in i:
						p1 = re.compile(r'&')
						mess1 = p1.split(i)
						for a in mess1:
							if 'GET' in a:
								type = a[-5:]
							if 'passwd=' in a:	
								passwd = a[7:21]
					# 针对主页输入的信息进行判断
					elif 'passwd' in i and '?' in i:
						p1 = re.compile(r'\?')
						mess1 = p1.split(i)
						for a in mess1:
							if 'inputmess' in a:
								inputmess = a[10:]
								in_mess = inputmess.split(' ')[0].strip()
							else:
								p2 = re.compile(r'&')
								mess2 = p2.split(a)
								for b in mess2:
									if 'GET' in b:
										type = a[-27:-22]
									elif 'passwd=' in b:
										passwd = a[18:32]

					# 针对获取参数，进行相关判断
					if type == 'xzdns' and passwd == 'xzdnss_dnsfind':
						# 返回主页
						all_dns_mess = index(clientip)
						content = 'HTTP/1.1 200 ok\r\nContent-Type: text/html; charset=UTF-8\r\n\r\n'
						content += '<p><font color="purple" size="DNS分区查询首页"></p>'
						content += str(all_dns_mess)
						conn.send(content.encode('utf-8'))
						conn.close()
					elif type == 'cname' and passwd == 'xzdnss_dnsfind':
						# 获取CNAME信息
						all_dns_mess = get_all_mess(in_mess,type)
						content = 'HTTP/1.1 200 ok\r\nContent-Type: text/html; charset=UTF-8\r\n\r\n'
						content += '<p><font color="purple" size="域名CNAME记录分区查询"></p>'
						content += str(all_dns_mess)
						conn.send(content.encode('utf-8'))
						conn.close()
					elif type == 'getip' and passwd == 'xzdnss_dnsfind':
						# 获取CNAME信息
						all_dns_mess = get_all_mess(in_mess,type)
						content = 'HTTP/1.1 200 ok\r\nContent-Type: text/html; charset=UTF-8\r\n\r\n'
						content += '<p><font color="purple" size="域名IP记录分区查询"></p>'
						content += str(all_dns_mess)
						conn.send(content.encode('utf-8'))
						conn.close()
					elif type == 'ipmes' and passwd == 'xzdnss_dnsfind':
						# 获取IP的归属地信息
						all_dns_mess = get_ipmess(in_mess)
						content = 'HTTP/1.1 200 ok\r\nContent-Type: text/html; charset=UTF-8\r\n\r\n'
						content += '<p><font color="purple" size="IP归属地查询"></p>'
						content += str(all_dns_mess)
						conn.send(content.encode('utf-8'))
						conn.close()
					elif type == 'getdm' and passwd == 'xzdnss_dnsfind':
						# 获取域名备案信息
						all_dns_mess = get_dmbnmess(in_mess)
						content = 'HTTP/1.1 200 ok\r\nContent-Type: text/html; charset=UTF-8\r\n\r\n'
						content += '<p><font color="purple" size="域名备案信息查询"></p>'
						content += str(all_dns_mess)
						conn.send(content.encode('utf-8'))
						conn.close()

					else:
						# 其他默认拒绝
						content = 'HTTP/1.1 403 forbidden\r\nContent-Type: text/html; charset=UTF-8\r\n\r\n'
						content += '<p><font color="red" size="3">请求出错-出现其它未知错误 ^_^</p>'
						conn.send(content.encode('utf-8'))
						conn.close()
		except:
			# 其它错误
			content = 'HTTP/1.1 403 forbidden\r\nContent-Type: text/html; charset=UTF-8\r\n\r\n'
			content += '<p><font color="red" size="3">请求出错-没有合适记录返回或者出现其它未知错误 ^_^</p>'
			conn.send(content.encode('utf-8'))
			conn.close()

	# 所有信息读取完后，断开连接
	conn.close()					




# 执行main函数
if __name__ == "__main__":
	main()






