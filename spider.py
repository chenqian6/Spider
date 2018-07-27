# -*- coding: utf-8 -*-
from selenium import webdriver
import time
import pymysql
from multiprocessing import Pool

#建立与mysql的连接
try:
    connection = pymysql.connect(host = "localhost", port = 3306, user = "root", password = "8023wmhh", db = "qqspider",charset = "utf8")
except:
    print("连接mysql数据库失败")
    assert 0
coursor = connection.cursor()#获取一个游标对象
try:
    coursor.execute("create table if not exists sstime (id INT NOT NULL UNIQUE ,shuo_time text,qzone_link text)")#在数据库中创建一个名为sstime的表
except:
    print("创建表失败")
    assert 0

#定义函数来保存说说信息到数据库
def save_to_database(the_list,shuo_time,qzone_link):
    try:
        coursor.execute("insert into sstime (id,shuo_time,qzone_link) VALUES (%d,'%s','%s');" % (the_list, shuo_time, qzone_link))
        connection.commit()
        the_list += 1
    except:
        print("第%d条说说信息保存到数据库失败" % the_list)

#模拟登陆
def register_qzone():
    driver = webdriver.PhantomJS(executable_path="D:\Anaconda\python2.7\phantomjs.exe")
    driver.set_window_position(20, 40)
    driver.set_window_size(1100, 700)
    driver.get("http://qzone.qq.com")
    driver.switch_to.frame("login_frame")
    driver.find_element_by_id("switcher_plogin").click()
    driver.find_element_by_id("u").clear()
    driver.find_element_by_id("u").send_keys("qq")
    driver.find_element_by_id("p").clear()
    driver.find_element_by_id("p").send_keys("qq密码")
    driver.find_element_by_id("login_button").click()
    time.sleep(3)
    driver.find_element_by_id("tab_menu_friend").find_element_by_class_name("qz-main").click()
    time.sleep(3)
    return driver
order = 1#创建一个全局变量来标示序号
#抓取前四个说说时间
def get_first_four(driver,the_list):
    for first_four in range(1,7):
        try:
            first_four_time = driver.find_element_by_xpath(
                "//li[%d][@class = 'f-single f-s-s']//div[@class = 'user-info']//div[@class = 'info-detail']" % first_four).text
            first_four_qzone_link = driver.find_element_by_xpath(
                "//li[%d][@class = 'f-single f-s-s']//div[@class = 'user-info']//div[@class = 'f-nick']/a[1]" % first_four).get_attribute("href")
            print(the_list, first_four_time, first_four_qzone_link)
            save_to_database(the_list, first_four_time, first_four_qzone_link)
        except:
            pass


#抓取后面的说说时间
def get_four_turn(driver,the_list,tot=0):
    time.sleep(3)
    js = "window.scrollTo(0,document.body.scrollHeight)"#JavaScript中的下拉指令
    driver.execute_script(js)
    time.sleep(2)
    driver.execute_script(js)
    time.sleep(2)

    #tot = 3   #每次下拉出现四个新的信息
    while(tot):
        for four_turn in range(1,5):
            try:
                four_turn_time = driver.find_element_by_xpath(
                    "//li[@class = 'feed_page_container']/ul[1]/li[%d]//div[@class = 'info-detail']" % four_turn).text
                four_turn_qzone_link = driver.find_element_by_xpath(
                    "//li[@class = 'feed_page_container']/ul[1]/li[%d]//div[@class = 'f-nick']/a[1]" % four_turn).get_attribute("href")
                print(the_list, four_turn_time, four_turn_qzone_link)
                save_to_database(the_list, four_turn_time, four_turn_qzone_link)
            except :
                pass
        tot -= 1
        js = "window.scrollTo(0,document.body.scrollHeight)"  # JavaScript中的下拉指令
        driver.execute_script(js)
        time.sleep(3)

#断开数据库的连接
def close_database(driver):
    coursor.close()#关闭游标
    connection.close()#关闭到数据库的连接，释放数据库资源
    #关闭网页
    driver.quit()

def main(total):
    dri = register_qzone()
    get_first_four(dri,order)
    get_four_turn(dri,order,total)
    close_database(dri)

if __name__ == "__main__":
    main(5)