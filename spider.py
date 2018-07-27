# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.common.exceptions import TimeoutException,NoSuchElementException
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
    coursor.execute("create table if not exists monthtime (id INT NOT NULL UNIQUE auto_increment,qq text,shuo_time text)")#在数据库中创建一个名为monthtime的表
except:
    print("创建表失败")
    assert 0

#将数据存储到数据库monthtime表中
def save_to_db(qqnumber,shuoshuo_time):
    try:
        coursor.execute("insert into monthtime (qq,shuo_time) VALUES ('%s','%s');" % (qqnumber, shuoshuo_time))
        connection.commit()
    except:
        pass

#模拟登陆到自己的空间
driver = webdriver.Chrome()
#driver = webdriver.PhantomJS(executable_path="D:\Anaconda\python2.7\phantomjs.exe")
driver.set_window_position(20, 40)
driver.set_window_size(1100,700)

driver.get("http://qzone.qq.com")
driver.switch_to.frame("login_frame")
driver.find_element_by_id("switcher_plogin").click()
driver.find_element_by_id("u").clear()
driver.find_element_by_id("u").send_keys("qq")
driver.find_element_by_id("p").clear()
driver.find_element_by_id("p").send_keys("qq密码")
driver.find_element_by_id("login_button").click()
time.sleep(3)

#下拉函数
def drop_down():
    js = "window.scrollTo(0,document.body.scrollHeight)"#JavaScript中的下拉指令
    driver.execute_script(js)
    time.sleep(2)

#进入好友说说页面并获取总的说说页面数
def shuoshuo_total(qqnumber):
    try:
        # 进入好友的说说页面
        driver.get("https://user.qzone.qq.com/{}/311".format(qqnumber))
        time.sleep(2)
        print("正在进入%s的说说页面" % qqnumber)
        #判断是否有权限进入
        try:
            driver.find_element_by_class_name("apply_access access_option")
                                    #如果没有权限，页面会有一个元素为class = apply_access access_option
            a = False
            #driver.quit()
        except NoSuchElementException:#有权限进入就找不到那个元素，程序发生异常：NoSuchElementException
            a = True

        if a == True:
            # 将页面拉到底部获取说说总页数
            drop_down()
            drop_down()
            time.sleep(2)
            driver.switch_to.frame("app_canvas_frame")
            total_page = int(driver.find_element_by_xpath("//a[@title = '末页']").text)
            return total_page
    except TimeoutException:#程序运行过程中由于网络原因极容易发生超时异常，此时只需要再重新加载一遍就可以
        return shuoshuo_total(qqnumber)

#跳转到指定的说说页面
def enter_shuoshuo(page):
    print("进入说说第%s页" % page)
    try:
        # 输入页面
        driver.find_element_by_xpath("//span[@class = 'mod_pagenav_turn']/input").clear()
        driver.find_element_by_xpath("//span[@class = 'mod_pagenav_turn']/input").send_keys(page)
        driver.find_element_by_xpath("//span[@class = 'mod_pagenav_turn']/button").click()
        time.sleep(2)
        print("进入成功")
    except:
        print("进入失败，再次尝试")
        return enter_shuoshuo(page)

#通过QQ号获取好友说说信息
def get_shuoshuo_information(qqnumber):
    try:
        total_page = shuoshuo_total(qqnumber)
        #开始获取好友说说信息
        for page in range(1,total_page+1):
            enter_shuoshuo(page)
            #获取说说时间信息
            for i in range(1,30):
                try:
                    shuoshuo_time = driver.find_element_by_xpath("//li[%d]//div[@class = 'box bgr3']//div[@class = 'ft']/div/span" % i).text
                    #将说说信息存储到数据库
                    save_to_db(qqnumber,shuoshuo_time)
                except:
                    break

    except:
        pass


def main(qqnumber):
    get_shuoshuo_information(qqnumber)

if __name__ == '__main__':
    #获取QQ号
    inpath = 'QQ号.txt'
    uipath = unicode(inpath, "utf8")#由于存在中文，所以需要编译一下
    f = open(uipath)
    #读取信息
    # for qq in f:
    #     main(qq)
    pool = Pool()
    pool.map(main,[qq for qq in f])

    #所有好友说说信息读取完毕，关闭文件
    f.close()
    # 断开数据库的连接
    coursor.close()  # 关闭游标
    connection.close()  # 关闭到数据库的连接，释放数据库资源
    # 关闭网页
    driver.quit()

    # pool = Pool()
    # pool.map(main,[qq for qq in f])
#断开数据库的连接
# coursor.close()#关闭游标
# connection.close()#关闭到数据库的连接，释放数据库资源
#关闭网页
#driver.quit()