import requests
import re
import headers as head
from  lxml import etree
from  selenium import  webdriver
import  time
import pymysql
import  threading
from queue import Queue
#请求头信息
headers={
	"Host": "www.dianping.com",
"If-Modified-Since": "Mon, 18 Mar 2019 09:08:05 GMT",
"If-None-Match": '"12d4baaa94fa976135ecc38c0f4ff2a6"',
"Upgrade-Insecure-Requests": "1",
"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.64 Safari/537.36"
}

address_queue=Queue(100)
score_queue=Queue(100)
test_queue=Queue(100)
environment_queue=Queue(100)
service_queue=Queue(100)
phone_queue=Queue(100)
price_queue=Queue(100)

with open("test.txt", "r")as f:
	one = f.read()

file_name = "大众点评美食类型_url.txt"
with open(file_name,'r')as f:
	type_url_str=f.readlines()
#获取地址信息
def get_address(response):
	address_str = re.findall('id="address">(.+?)</span>', response)[0]
	address_list = []  #地址存放的列表
	one_1=[]
	one_2=[]
	head_two = re.sub("<e", "",address_str.split(" ")[1])
	one_1.append("地址: ")
	one_1.append(head_two+" ")
	one_2.append(tuple(one_1))
	address_list.append(one_2)
	#分割，正则来获取所需要的信息
	for i in address_str.split(" "):
		i_str_1 = re.sub("</e>", "", i)
		i_str_2 = re.sub("</d>", "", i_str_1)
		i_str_3 = re.sub(">", "", i_str_2)
		i_str_4 = re.sub("<e", "", i_str_3)
		i_str_5 = re.sub("<d", "", i_str_4)
		re_a = re.findall('class="(.+?)"(.+?)/', i_str_5 + " /")
		address_list.append(re_a)

	address_data_list = []
	for i in address_list:
		if i:
			if i[0][1] != " ":
				address_data_list.append(i[0][0])
				address_data_list.append(i[0][1])
			else:
				address_data_list.append(i[0][0])
	address_content = []
	for i in address_data_list:
		if i.isalnum():
			if 'qfr' in i:
				address_content .append(get_text(i))
			else:
				address_content .append( get_digital(i))
		else:
			address_content .append( i.strip(" "))

	address_queue.put("".join(address_content))

#获取评论数
def get_score(response):
	score_str = re.findall('<span id="reviewCount" class="item">(.*?)</span>', response)[0]
	score_list = []
	one_1 = []
	one_2 = []
	head_two = re.sub("<d", "", score_str.split(" ")[1])
	one_1.append("评论数: ")
	one_1.append(head_two + " ")
	one_2.append(tuple(one_1))
	score_list.append(one_2)
	for i in score_str.split(" "):
		i_one=re.sub("></d>","",i)
		i_two=re.sub("<d","",i_one)
		i_three = re.sub("条评论", "", i_two)
		re_score=re.findall('class="(.+?)"(.+?)/',i_three+" /")
		score_list.append(re_score)
	score=[]
	for i in score_list:
		if i:
			if i[0][1]!=" ":
				score.append(i[0][0])
				score.append(i[0][1])
			else:
				score.append(i[0][0])
	score_data=[]
	for i in score:
		if 'vhk' in i:
			score_data.append(get_digital(i))
		else:
			score_data.append(i.strip(" "))
	
	score_queue.put("".join(score_data))

#获取口味评分
def get_test(html):
	test_str = html.xpath("//span[@id='comment_score']/span[1]//d/@class")
	taste_content_str = html.xpath("//span[@id='comment_score']/span[1]/text()")
	if test_str:
		test = []
		for i in test_str:
			test.append(get_digital(i))
		if len(test)==2:
			tes_str=taste_content_str[0].strip(" ")+test[0].strip(" ")+taste_content_str[1].strip(" ")+test[1].strip(" ")
		else:
			tes_str = taste_content_str[0].strip(" ") + test[0].strip(" ") + taste_content_str[1].strip(" ")
		test_queue.put(tes_str)
		
	elif taste_content_str:
		test_queue.put(taste_content_str[0])
		
	else:
		test_queue.put("无")
		
#获取环境评分
def get_environment(html):
	environment_str = html.xpath("//span[@id='comment_score']/span[2]//d/@class")
	environment_content_str = html.xpath("//span[@id='comment_score']/span[2]/text()")
	if environment_str:
		environment = []
		if len(environment_str)==2:
			for i in environment_str:
				environment.append(get_digital(i))
			enc_str=environment_content_str[0].strip(" ")+environment[0].strip(" ")+environment_content_str[1].strip(" ")+environment[1].strip(" ")
		else:
			environment.append(get_digital(environment_str[0]))
			enc_str = environment_content_str[0].strip(" ") + environment[0].strip(" ") + environment_content_str[1].strip(" ")
		
		environment_queue.put(enc_str)
	elif environment_content_str:
		environment_queue.put(environment_content_str[0])
		
	else:
		environment_queue.put("无")
		
#获取服务评分
def get_service(html):
	service_str = html.xpath("//span[@id='comment_score']/span[3]//d/@class")
	service_content_str = html.xpath("//span[@id='comment_score']/span[3]/text()")
	if service_str:
		service = []
		for i in service_str:
			service.append(get_digital(i))
		if len(service)==2:
			ser_str=service_content_str[0].strip(" ")+service[0].strip(" ")+service_content_str[1].strip(" ")+service[1].strip(" ")
		else:
			ser_str = service_content_str[0].strip(" ") + service[0].strip(" ") + service_content_str[1].strip(" ")
		service_queue.put(ser_str)
		
	elif service_content_str:
		service_queue.put(service_content_str[0])
		
	else:
		service_queue.put("无")
		
#获取电话信息
def get_phone(response):
	phone_str = re.findall('name">电话：</span>(.+?)</p>', response)[0]
	on = re.findall('(无) <a',phone_str[0])
	if on and on[0].strip(" ")=='无':
		return "电话:无"
	else:
		phone_list = []
		for i in phone_str.split(" "):
			for j in i.split("</"):
				one_num = re.findall('(1)', j)
				phone_list.append(one_num)
				middle_num = re.findall("(&nbsp;)", j)
				if middle_num:
					phone_list.append(middle_num)
				re_phone = re.findall('class="(.+?)"', j)
				phone_list.append(re_phone)
		phone_data_list = []
		for i in phone_list:
			if i:
				if i[0] != " ":
					if i[0] == '&nbsp;':
						phone_data_list.append("/")
					else:
						phone_data_list.append(i[0])
		phone_num = []
		for i in phone_data_list:
			if i.strip(" ") == '1' or i.strip(" ") == "1-" or i.strip(" ") == '/':
				phone_num .append( i.strip(" "))
			else:
				phone_num .append( get_digital(i))
		phone_queue.put("电话:" + "".join(phone_num))
		# return "电话:" + "".join(phone_num)
#获取人均价格
def get_Price(response):
	price_str = re.findall('<span id="avgPriceTitle" class="item">(.+?)</span>', response)[0]
	price_list=[]
	for i in price_str.split(" "):
		for j in i.split("</"):
			one_num=re.findall("(1)",j)
			if one_num:
				price_list.append(one_num)
			one_zog=re.findall('"(vhk.+?)">',j)
			price_list.append(one_zog)
	price=[]
	for i in price_list:
		if i:
			if 'vhk' in i[0]:
				price.append(get_digital(i[0]))
			else:
				price .append( str(i[0]))

	price_queue.put("人均:"+"".join(price)+"元")
	

#发起详细页面请求
def get_number(url):
	t_list=[]
	response = requests.get(url, headers=headers).text
	
	html=etree.HTML(response)
	logo=html.xpath('//div[@id="not-found-tip"]/text()')
	#判断当前页面是否为验证码，页面
	if logo:
		validation_url = "http://www.dianping.com/shanghai/ch10/g113"
		browser = webdriver.Chrome()
		browser.get(validation_url)
		time.sleep(20)
		response = requests.get(url, headers=headers).text
		html = etree.HTML(response)
		browser.close()
		# print(logo[0])

	#获取评论数

	t_score=threading.Thread(target=get_score,args=(response,))
	t_list.append(t_score)
	

	#获取口味评分

	t_test=threading.Thread(target=get_test,args=(html,))
	t_list.append(t_test)

	#获取环境评分

	t_environment=threading.Thread(target=get_environment,args=(html,))
	t_list.append(t_environment)
	

	#获取服务评分

	t_service=threading.Thread(target=get_service,args=(html,))
	t_list.append(t_service)
	
	#获取地址
	t_address=threading.Thread(target=get_address,args=(response,))
	t_list.append(t_address)
	

	#获取电话号码
	t_phone=threading.Thread(target=get_phone,args=(response,))
	t_list.append(t_phone)
	

	# 获取人均价格

	t_price=threading.Thread(target=get_Price,args=(response,))
	t_list.append(t_price)
	

	#获取饮食类型
	species=html.xpath("//div[@class ='breadcrumb']/a[2]/text()")
	#判断是否存在
	if species:
		species=species[0]
	else:
		species="无"

	#获取地区信息
	region_one=html.xpath("//div[@class ='breadcrumb']/a[3]/text()")
	region_two=html.xpath("//div[@class ='breadcrumb']/a[4]/text()")
	#判断是否存在
	if region_one:
		if region_one and region_two :
			region=region_one[0].strip(" ")+"-"+region_two[0].strip(" ")
		else:
			region = region_one[0].strip(" ")
	else:
		region="无"

	#获取店家名
	store_name=html.xpath("//h1[@class='shop-name']/text()")[0]

	#获取星级
	star=html.xpath("//div[@class='brief-info']/span/@title")[0]

	# print(len(t_list),t_list)
	for i in t_list:
		i.start()

	for i in t_list:
		i.join()

	score=score_queue.get()
	price=price_queue.get()
	test=test_queue.get()
	environment=environment_queue.get()
	service=service_queue.get()
	address=address_queue.get()
	phone=phone_queue.get()

	print(store_name, star, species, region, score, price, test, environment, service, address, phone)

	save_mysql_store_url(store_name,star,species,region,score,price,test,environment,service,address,phone)

#地址解密
def get_text(id):
	#获取加密的值的x，y坐标，例如：zogwtn
	re_wqd=re.compile(r"\.%s{background:-(\d+)\.0px -(\d+)\.0px;}" % id)
	time.sleep(0.1)
	wqd = re.findall(re_wqd, one)
	x=wqd[0][0] #x坐标
	y=wqd[0][1] #y坐标
	sum_x=int((int(x)/14))  #计算x偏移量
	sum_y=round(int(y)/34)  #计算y的偏移量
	if sum_y!=0:
		sum_y -=1
	# print("x轴:{},y轴:{}|x偏移量:{},y偏移量:{}".format(e,f,sum_e,sum_f))
	#获取到加密的数字组
	url_qfr="http://s3plus.meituan.net/v1/mss_0a06a471f9514fc79c981b5466f56b91/svgtextcss/882b981e5726db198e310153eb7a2615.svg"
	response=requests.get(url_qfr,headers=head.headers).text
	get_wqd=re.findall(">(.+?)</text>",response)
	wqd_list=[]
	for i in get_wqd:
		wqd_list.append(list(i))
	return wqd_list[sum_y][sum_x]

#数字解密
def get_digital(id):
	re_zog=re.compile(r"\.%s{background:-(\d+)\.0px -(\d+)\.0px;}"%id)
	time.sleep(0.1)
	zog=re.findall(re_zog,one)
	if zog:
		x=zog[0][0]
		y=zog[0][1]
		sum_x=int((int(x)/14))
		sum_y=int(int(y)/31)
		if sum_y!=0:
			sum_y -=1
		# print("x轴:{},y轴:{}|x偏移量:{},y偏移量:{}".format(e,f,sum_e,sum_f))
		url_vhk="http://s3plus.meituan.net/v1/mss_0a06a471f9514fc79c981b5466f56b91/svgtextcss/0ee22f3a58f5e1ab68822292803d52d8.svg"

		response=requests.get(url_vhk,headers=head.headers).text
		get_zog=re.findall(">(.+?)</text>",response)
		zog_list=[]
		for i in get_zog:
			zog_list.append(list(i))
		# print(num_list[sum_f][sum_e-1])

		return zog_list[sum_y][sum_x]
	else:
		return '0'

#获取餐饮类型的一些信息包括url，并保存下来
def get_type_url():
	headers = {
		"Host": "www.dianping.com",
		"Upgrade-Insecure-Requests": "1",
		"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.64 Safari/537.36"}
	url='http://www.dianping.com/shanghai/ch10'
	response_type=requests.get(url,headers=headers).text
	print(response_type)
	html_type=etree.HTML(response_type)
	type_url=html_type.xpath("//div[@id='classfy']/a/@href")
	type_name=html_type.xpath("//div[@id='classfy']/a/span/text()")
	file_name = "大众点评美食类型_url.txt"
	for url,name in zip(type_url,type_name):
		print(name)
		# with open(file_name, "a")as f:
		# 	f.write("菜的类型：" + name+"\n")
		response=requests.get(url,headers=headers).text
		html=etree.HTML(response)
		next_type_url=html.xpath("//div[@id='classfy-sub']/a/@href")
		next_type_name=html.xpath("//div[@id='classfy-sub']/a/span/text()")
		if next_type_url:
			for i_url,i_name in zip(next_type_url[1:],next_type_name[1:]):
				with open(file_name,"a")as f:
					f.write(i_url+"\n")
					# f.write("菜的分类："+i_name+'\t'+"url:"+i_url+"\n")
		else:
			with open(file_name, "a")as f:
				f.write(url + "\n")
		print(next_type_url,next_type_name)
		time.sleep(3)

#从文本中读取餐饮类型的url
def read_type_url(num,page):
	for i in range(num,len(type_url_str)):
		save_type_url(type_url_str[i].strip("\n"))
		if i==num:
			get_store_url(type_url_str[i].strip("\n"),page)
		else:
			get_store_url(type_url_str[i].strip("\n"), 0)
#保存页数的url
def save_mysql_page_url(url,page):
	db = pymysql.connect("192.168.111.132", "root", "123456", "pymsql")
	cur = db.cursor()
	# 判断数据是否存在数据库中，不存在便插入，存在便跳过
	insert_sql="""insert into dazhong_page_url(page_url,page) VALUE (%s,%s)"""
	try:
		# 执行数据库命令
		cur.execute(insert_sql, (url,page))
		# 提交
		db.commit()
		print("写入数据库成功！")
		print("*" * 30)
	except Exception as e:
		db.rollback()
		print(e)
		print("写入数据库失败！")
	db.close()

#将获取的数据保存在数据库中
def save_mysql_store_url(store_name,star,species,region,score,price,test,environment,service,address,phone):
	db = pymysql.connect("192.168.111.132", "root", "123456", "pymsql")
	cur = db.cursor()
	# 判断数据是否存在数据库中，不存在便插入，存在便跳过
	insert_sql = """INSERT INTO  dazhong_store_url(餐厅名,星级,类型,地区,评论,人均,口味,环境,服务,地址,电话) SELECT %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s FROM  DUAL 
		WHERE  NOT  EXISTS (SELECT * FROM  dazhong_store_url WHERE  餐厅名=%s)"""
	try:
		# 执行数据库命令
		cur.execute(insert_sql, (store_name,star,species,region,score,price,test,environment,service,address,phone,store_name))
		# 提交
		db.commit()
		print("写入数据库成功！")
		print("*" * 30)
	except Exception as e:
		db.rollback()
		print(e)
		print("写入数据库失败！")
	db.close()

#保存餐饮类型的url
def save_type_url(url):
	db = pymysql.connect("192.168.111.132", "root", "123456", "pymsql")
	cur = db.cursor()
	# 判断数据是否存在数据库中，不存在便插入，存在便跳过
	insert_sql = """INSERT INTO  dazhong_type_url(type_url) SELECT %s FROM  DUAL 
		WHERE  NOT  EXISTS (SELECT * FROM  dazhong_type_url WHERE  type_url=%s)"""
	try:
		# 执行数据库命令
		cur.execute(insert_sql, (url,url))
		# 提交
		db.commit()
		print("写入数据库成功！")
		print("*" * 30)
	except Exception as e:
		db.rollback()
		print(e)
		print("写入数据库失败！")
	db.close()

#发起页面数的请求
def get_store_url(url,page):
	headers={
		"Host": "www.dianping.com",
		"Upgrade-Insecure-Requests": "1",
		"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.64 Safari/537.36"}
	for i in range(page,31):
		save_mysql_page_url(url, i)
		url_page=url+'p'+str(i+1)
		response=requests.get(url_page,headers=headers)
		response.encoding="utf-8"
		print(response.url)
		html=etree.HTML(response.text)

		validation=html.xpath('//div[@id="not-found-tip"]/text()')
		# print(validation)
		if validation:
			validation_url="http://www.dianping.com/shanghai/ch10/g113"
			browser = webdriver.Chrome()
			browser.get(validation_url)
			time.sleep(20)
			response = requests.get(url_page, headers=headers)
			response.encoding = "utf-8"
			print(response.url)
			html = etree.HTML(response.text)
			browser.close()

		store_url=html.xpath("//div[@class='txt']/div[@class='tit']/a[1]/@href")
		next_page=html.xpath("//a[@class='next']/text()")
		if not next_page:
			print("最后一页了！")
			for i in store_url:
				print(i)
				get_number(i)
			break
		# print(next_page)
		for i in store_url:
			print(i)
			get_number(i)
			# time.sleep(0.3)

#程序执行
def main():
	db = pymysql.connect("192.168.111.132", "root", "123456", "pymsql")
	cur = db.cursor()
	# 读取数据库中的数据
	cur.execute("select * from dazhong_page_url")
	url_list = cur.fetchall()
	cur.execute("select * from dazhong_type_url")
	type_url_list=cur.fetchall()
	db.close()
	# 判断数据中是否存在数据，来证明是否已经开始爬取
	# 如果有数据，将获取最后一条数据，来实现断点续爬
	if url_list:
		print("已经爬取到当前的url:{}的第{}页:".format(url_list[-1][0],url_list[-1][1]))
		read_type_url(len(type_url_list)-1,int(url_list[-1][1]))
	else:
		print("还没开始爬！\n现在开始爬取！")
		print("=" * 30)
		read_type_url(0,0)


def test():
	url="http://www.dianping.com/shop/121937518"
	browser = webdriver.Chrome()
	browser.get(url)
	time.sleep(20)
	browser.close()
	
if __name__=='__mian__':
	main()
