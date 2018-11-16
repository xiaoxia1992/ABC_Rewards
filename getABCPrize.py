#!/usr/bin/env python3
#  -*- coding： utf-8 -*-
# Created by FFJ on 2018/11/17

from requests.auth import HTTPBasicAuth
import requests
import json
import logging


USER_AGENT = "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1"
HEADERS = {'user-agent': USER_AGENT}
DESTINATION = '%E4%B8%AD%E5%9B%BD%E9%A6%99%E6%B8%AF'


# def get_cookies():
#     request_url = 'https://abc.uncle-ad.com/abcluckydrew_newmarch/'
#     headers = {'user-agent': USER_AGENT}
#     req = requests.get(request_url, auth=HTTPBasicAuth('user', 'pass'), headers=headers)
#     print(req.cookies)


def set_login(mobile, years, months, destination):
    post_data = {
        'mobile': mobile,
        'years': years,
        'months': months,
        'destination': destination
    }
    request_url = 'https://abc.uncle-ad.com/abcluckydrew_newmarch/service/operAction.php?action=setLogin'
    r = requests.post(request_url, data=post_data, auth=HTTPBasicAuth('user', 'pass'), headers=HEADERS)
    response = r.text
    cookies = r.cookies
    return response, cookies


def lottery(postitionindex, uniqid, years, months, destination, cookies):
    post_data = {
        'positionindex': postitionindex,
        'uniqid': uniqid,
        'years': years,
        'months': months,
        'destination': destination
    }
    request_url = 'https://abc.uncle-ad.com/abcluckydrew_newmarch/service/operAction.php?action=lottery'
    r = requests.post(request_url, data=post_data, auth=HTTPBasicAuth('user', 'pass'),
                      headers=HEADERS, cookies=cookies)
    response = r.text
    return response


def run():
    with open('./numbers.txt', 'r') as fr:
        mobile_numbers = fr.readlines()

    for mobile_number in mobile_numbers:
        for index in range(4):

            if index == 0:
                year = '2018'
                month = '11'
            elif index == 1:
                year = '2018'
                month = '12'
            elif index == 2:
                year = '2019'
                month = '1'
            else:
                year = '2019'
                month = '2'

            login_string, cookies = set_login(mobile_number, year, month, DESTINATION)
            login_data = json.loads(login_string)

            if login_data['nums'] != 3:
                warning_message = '{0} {1}年{2}月的已被使用，当月剩余次数' \
                                  '为{3}\n'.format(mobile_number, year, month, login_data['num'])
                print(warning_message)
                logging.error(warning_message)
                continue

            uniqid = login_data['uniqid']

            with open('./output.txt', 'a') as fa:
                for i in range(1, 4):
                    lottery_string = lottery(i, uniqid, year, month, DESTINATION, cookies)
                    lottery_data = json.loads(lottery_string)
                    message = '{0} --- {1}年{2}月得到 {3} 美元' \
                              '券\n'.format(mobile_number, year, month, lottery_data['msg'])
                    print(message)
                    logging.warning(message)
                    fa.write(message)


if __name__ == '__main__':
    # mob = '15521390483'
    # yy = '2018'
    # mm = '11'
    # dest = '%E4%B8%AD%E5%9B%BD%E9%A6%99%E6%B8%AF'

    run()
