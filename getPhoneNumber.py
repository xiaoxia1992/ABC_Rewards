#!/usr/bin/env python3
#  -*- coding： utf-8 -*-
# Created by FFJ on 2018/11/

import requests
import re
import os
import logging

USER_AGENT = "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1"
HEADERS = {'user-agent': USER_AGENT}

USED_NUM_FILE = './pingxiang_used.txt'
ALL_NUM_FILE = './pingxiang_all.txt'


class ABCReward(object):
def achieve_num():
    url = "https://m.10010.com/NumApp/NumberCenter/qryNum?callback=jsonp_queryMoreNums&" \
          "provinceCode=75&cityCode=758&monthFeeLimit=0&groupKey=67237076&searchCategory=3&" \
          "net=01&amounts=200&codeTypeCode=&searchValue=&qryType=02&goodsNet=4"
    r = requests.post(url, headers=HEADERS)
    response = r.text
    match = re.findall('[0-9]{11}', response)
    result = []
    if match:
        for num in match:
            result.append(num)
    return result


def load_links(self):
    # 载入link到内存
    try:
        if os.path.exists(USED_NUM_FILE):
            with open(USED_NUM_FILE, 'r') as fr:
                for line in fr:
                    line = line.strip()
                    self.crawled_links_list.append(line)
    except Exception as e:
        logging.error('Load links to crawled list: {}'.format(e))

    try:
        if os.path.exists(ALL_NUM_FILE):
            with open(ALL_NUM_FILE, 'r') as fr:
                for line in fr:
                    line = line.strip()
                    if line not in self.crawled_links_list:
                        if line not in self.link_queue:
                            self.link_queue.append(line)
    except Exception as e:
        logging.error('Load links to Queue: {}'.format(e))

    if not self.link_queue:
        self.link_queue.append(self.seed_url)
    logging.warning("Load links success")


def save_crawled_links(self, link):
    # 保存已经抓取的link到 ./crawled_link_file
    try:
        with open(self.crawled_link_file, 'a') as fw:
            fw.write(link + '\n')
    except Exception as e:
        logging.error('Save crawled link：{}'.format(e))


def save_all_links(self, html):
    # 获取页面所有匹配的link并保存到 ./links_base_file
    try:
        all_links = get_all_links(html)
        with open(self.links_base_file, 'a') as fw:
            for link in all_links:
                link = re.sub(r'[^\x00-\x7f]', ' ', link)
                if not self.is_special_pattern_url(link):
                    continue
                if link not in self.link_queue:
                    if link not in self.crawled_links_list:
                        self.link_queue.append(link)
                        fw.write(link + '\n')
        return True
    except Exception as e:
        logging.error('Save all links：{}'.format(e))
        return False