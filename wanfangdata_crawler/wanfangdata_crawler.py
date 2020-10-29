#万方网站爬虫
import requests
from bs4 import BeautifulSoup
import re
import os, sys
import pandas
import time
import pymysql

header = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'
}
proxy = ''
data_info = {
    '出版年份': [],
    '文章题目': [],
    '英文题目': [],
    '期刊名称': [],
    '作者': [],
    '摘要': [],
    '关键词': [],
    '被引数': [],
    '参考文献数': [],
    '下载链接': []
}


def get_full_info(topic, type):
    url = 'http://s.wanfangdata.com.cn/Paper.aspx?q=' + topic + '%20DBID%3AWF_' + type + '&f=top'
    html = requests.get(url=url, headers=header, proxies={'http': proxy}).text
    soup = BeautifulSoup(html, 'html.parser')
    total_records = soup.select('.total-records')[0].find('span').string
    return total_records


def get_url(topic, type, page_num):
    url = 'http://s.wanfangdata.com.cn/Paper.aspx?q='+topic+'%20DBID%3AWF_'+type+'&f=top&p='+str(page_num)
    html = requests.get(url=url, headers=header, proxies={'http': proxy}).text
    soup = BeautifulSoup(html, 'html.parser')

    records = soup.select('.record-item')
    for rec in records:
        title = rec.select('.title')[0].prettify()
        name = re.match('<a.*?blank">(.*?)</a>', title, re.S).group(1).replace('<em>', '').replace('</em>', '').replace('\n', '').replace(' ', '')

        detail_url = rec.select('.title')[0]['href']
        if rec.select('.download'):
            download_url = rec.select('.download')[0]['href']
        else:
            download_url = 'null'
        print(name)
        print(detail_url)
        try:
            date, doi, title_en, abstract, magazine_name, author_name, keyword, cited_num, ref_num = get_detail(detail_url)
            #print(download_url)
            #print(date, doi, title_en, abstract, magazine_name, author_name, keyword, cited_num, ref_num)
            data_info['出版年份'].append(date)
            data_info['文章题目'].append(name)
            data_info['英文题目'].append(title_en)
            data_info['作者'].append(author_name)
            data_info['关键词'].append(keyword)
            data_info['摘要'].append(abstract)
            data_info['期刊名称'].append(magazine_name)
            data_info['被引数'].append(cited_num)
            data_info['参考文献数'].append(ref_num)
            data_info['下载链接'].append(download_url)
            print('*****************************')
            time.sleep(1)
        except:
            data_info['出版年份'].append('null')
            data_info['文章题目'].append(name)
            data_info['英文题目'].append('null')
            data_info['作者'].append('null')
            data_info['关键词'].append('null')
            data_info['摘要'].append('null')
            data_info['期刊名称'].append('null')
            data_info['被引数'].append('null')
            data_info['参考文献数'].append('null')
            data_info['下载链接'].append(download_url)
            print("详细信息获取失败", sys.exc_info()[0])
            print('*****************************')


def get_detail(detail_url):
    a = str(detail_url).split('/')
    paper_id = a[len(a)-1]
    date = re.findall('\d+', paper_id)[0][0:4]
    html = requests.get(detail_url, headers=header, proxies={'http': proxy}).text
    detail_soup = BeautifulSoup(html, 'html.parser')
    doi = detail_soup.select('.baseinfo-feild')[1].select('.row')[0].find('a').string

    if detail_soup.select('.section-baseinfo')[0].find('h2'):
        title_en = detail_soup.select('.section-baseinfo')[0].find('h2').string
    else:
        title_en = 'null'
    abstract = detail_soup.select('.row')[0].select('.text')[0].string
    magazine_name = detail_soup.select('.row-magazineName')[0].select('.text')[0].find('a').string
    authors = detail_soup.select('.row-author')[0].find_all('a')
    author_name = ''
    for author in authors:
        author_name = author_name + ',' + author.string
    keyword = ''
    key_words = detail_soup.select('.row-keyword')[0].select('.text')[0].find_all('a')
    for key_word in key_words:
        if key_word.string:
            keyword = keyword + ',' + key_word.string
        else:
            continue

    cited_num, ref_num = get_cite_info(paper_id)
    return date, doi, title_en, abstract, magazine_name, author_name.lstrip(','), keyword.lstrip(','), cited_num, ref_num


def get_cite_info(paper_id):
    url = 'http://d.old.wanfangdata.com.cn/CiteRelation/Map?id=' + str(paper_id)
    cite_data = requests.get(url=url, headers=header, proxies={'http': proxy}).text
    cite_soup = BeautifulSoup(cite_data, 'html.parser')
    if cite_soup.select('.refciteMap'):
        cited_num = cite_soup.select('.cite1')[0].select('.count')[0].string.strip('(').strip(')')
        ref_num = cite_soup.select('.ref1')[0].select('.count')[0].string.strip('(').strip(')')
    else:
        cited_num = '0'
        ref_num = '0'
    return int(cited_num), int(ref_num)


if __name__ == '__main__':
    topic = input('请输入文献主题：')
    type = input('请输入文献类型：')
    total_num = get_full_info(topic, type)
    print('万方上共搜索到', total_num, '相关主题文献数据')
    page_num = int(int(input('请输入获取数量:'))/10)
    for i in range(1, page_num+1):
        get_url(topic, type, i)
    data = pandas.DataFrame(data_info)
    filename = topic+'-'+type+'-文献信息.xls'
    if(os.path.exists(filename)):
        os.remove(filename)
        data.to_excel(filename, encoding='utf-8', index=True, header=True)
    else:
        data.to_excel(filename, encoding='utf-8', index=True, header=True)
    print('※※※※※※※※※※※※※※※※'+'抓取完毕'+'※※※※※※※※※※※※※※※※')

