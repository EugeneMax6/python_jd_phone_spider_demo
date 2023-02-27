# encoding='utf-8'
import os

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait
from selenium import webdriver
from bs4 import BeautifulSoup
from urllib import parse
import time
import csv

browser = webdriver.Chrome()
wait = WebDriverWait(browser, 10)


# 确定京东搜索的链接
def get_url(n, word, brand):
    print('爬取第' + str(n) + '页')
    # 确定搜索商品的内容
    keyword = {'keyword': word}
    # 页面n与参数page的关系 page = 2 * n - 1
    page = '&page=' + str(2 * n - 1)
    brand = '&ev=exbrand_' + brand
    # 为了在URL中输入中文，需要将中文关键字转为UrlEncode编码
    url = 'https://search.jd.com/Search?' + parse.urlencode(keyword) + brand + '&enc=utf-8' + page
    print('京东搜索页面链接:' + url)
    return url


def parse_page(url, brand, ostream):
    print('爬取信息并保存中...')
    browser.get(url)
    # 把滑轮慢慢下拉至底部，触发ajax
    for y in range(100):
        js = 'window.scrollBy(0,100)'
        browser.execute_script(js)
        time.sleep(0.1)
    wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, '#J_goodsList .gl-item')))
    html = browser.page_source
    soup = BeautifulSoup(html, 'html.parser')
    # 找到所有商品标签
    goods = soup.find_all('li', class_="gl-item")
    # 遍历每个商品，得到每个商品的信息
    for good in goods:
        try:
            num = good['data-sku']
            # 京东有些手机没发布也显示了
            money = good.find('div', class_="p-price").strong.i.string
            if money == '待发布':
                continue
            # 就是京东有些商品竟然没有店铺名，导检索store时找不到对应的节点导致报错
            store = good.find('div', class_="p-shop").span
            commit = good.find('div', class_="p-commit").strong.a.string
            name = good.find('div', class_="p-name p-name-type-2").a.em
            detail_addr = good.find('div', class_="p-img").find('a')['href']
        except Exception:
            continue
        if store is not None:
            new_store = store.a.string
        else:
            new_store = '没有找到店铺 - -！'
        new_name = ''
        for item in name.strings:
            new_name = new_name + item
        product = (num, brand, new_name, money, new_store, commit, detail_addr)
        save_to_csv(product, ostream)
        print(product)


def save_to_csv(result, ostream):
    ostream.writerow(result)


if __name__ == '__main__':
    # word = input('请输出你想要爬取的商品：')
    word = '手机'
    # brand = input('请输出你想要爬取的品牌：')
    brand = ['Apple', 'HUAWEI', '小米', 'OPPO', 'vivo', '荣耀（HONOR）', '真我（realme）', '魅族（meizu）']
    # pages = int(input('请输入你想要抓取的页数(范围是1-100):'))
    pages = 3
    for brd in brand:
        flag = False
        if not os.path.exists("information.csv"):
            flag = True
        with open("information.csv", 'a', newline='') as output:
            writer = csv.writer(output)
            # 京东最大页面数为100
            if flag:
                writer.writerow(
                    'info_num,info_brand,info_name,info_money,info_store,info_commit,info_detail'.split(','))
            if 1 <= pages <= 100:
                page = pages + 1
                for n in range(1, page):
                    try:
                        url = get_url(n, word, brd)
                    except Exception:
                        browser.close()
                        output.close()
                    try:
                        parse_page(url, brd, writer)
                    except Exception:
                        continue
                print(brd + '品牌' + word + '爬取完毕！')
    browser.close()
    output.close()

