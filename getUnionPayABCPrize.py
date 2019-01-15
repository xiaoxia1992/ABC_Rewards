#!/usr/bin/env python3
#  -*- coding: utf-8 -*-
# Created by FFJ on 2018/11/30

# from requests.auth import HTTPBasicAuth
import requests
import json
import logging
import time
import random

# USER_AGENT = "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1"
USER_AGENT = 'Mozilla/5.0 (iPhone; CPU iPhone OS 12_1_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) ' \
             'Mobile/16C101 MicroMessenger/7.0.2(0x17000222) NetType/WIFI Language/zh_CN'
HEADERS = {'User-Agent': USER_AGENT}
DESTINATION = '%E4%B8%AD%E5%9B%BD%E9%A6%99%E6%B8%AF'


def getCookieTelByTel(mobile, years, months):
    post_data_zero = {
        'ut': '034931765552222893',
        'tel': mobile,
        'destination': '%E9%A6%99%E6%B8%AF',
        'travelTime': '{0}-{1}'.format(years, months),
        'type': 'Unionpay'
    }
    requests_zero_url = 'http://credit.cmbond.com/unionpay_travel_act/addTravelRecorduAndUbion.html'
    rz = requests.post(requests_zero_url, data=post_data_zero, headers=HEADERS)
    print(rz.text)

    # post_data_first = {
    #     'ut': '034931765552222893',
    #     'type': 'game.html'
    # }
    # requests_first_url = 'http://credit.cmbond.com/unionpay_travel_act/addAccess.html'
    # rf = requests.post(requests_first_url, data=post_data_first, headers=HEADERS)
    # print(rf.text)
    #
    # post_data_second = {
    #     'ut': str(mobile)
    # }
    # requests_second_url = 'http://credit.cmbond.com/unionpay_travel_act/getTicket.html'
    # rs = requests.post(requests_second_url, data=post_data_second, headers=HEADERS)
    # print(rs.text)

    post_data = {
        'tel': str(mobile),
        'travelMonth': '{0}-{1}'.format(years, months)
    }
    request_url = 'http://credit.cmbond.com/unionpay_travel_act/getCookieTelByTel.html'
    first_headers = {
        'Accept': 'application/json',
        'X-Requested-With': 'XMLHttpRequest',
        'Accept-Language': 'zh-cn',
        'Accept-Encoding': 'gzip, deflate',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Origin': 'http://credit.cmbond.com',
        'User-Agent': USER_AGENT,
        'Connection': 'keep-alive',
        'Referer': 'http://credit.cmbond.com/enjoy/yl/game.html?ut=034931765552222893&'
                   'tel={0}&type=Unionpay&travelMonth={1}-{2}'.format(mobile, years, months),

    }
    r = requests.post(request_url, data=post_data, headers=HEADERS)
    response = r.text
    print(response)
    # cookies = r.cookies
    # print('cookies: {}'.format(cookies))
    return response


def lottyPrizeuByTelAndTest(mobile, years, months):
    post_data = {
        'tel': mobile,
        'type': 'Unionpay',
        'travelMonth': '{0}-{1}'.format(years, months)
    }
    request_url = 'http://credit.cmbond.com/unionpay_travel_act/lottyPrizeuByTelAndTest.html'
    r = requests.post(request_url, data=post_data, headers=HEADERS)
    response = r.text
    return response


def findWinRecordByTel(mobile):
    post_data = {
        'tel': mobile
    }
    request_url = 'http://credit.cmbond.com/unionpay_travel_act/findWinRecordByTel.html'
    r = requests.post(request_url, data=post_data, headers=HEADERS)
    return r.text


def test(mobile):
    first = getCookieTelByTel(mobile, '2019', '02')
    print(first)
    second = lottyPrizeuByTelAndTest(mobile, '2019', '02')
    print(second)
    second = lottyPrizeuByTelAndTest(mobile, '2019', '02')
    print(second)
    third = findWinRecordByTel(mobile)
    print(third)


def run():
    with open('./杭州联通米粉卡号1130.txt', 'r') as fr:
        mobile_numbers = fr.readlines()

    for mobile_number in mobile_numbers:
        with open('./杭州联通米粉卡号输出1130.txt', 'a') as all_output, open('./bingo.txt', 'a') as bingo_output:
            mobile_number = mobile_number.strip()

            for index in range(3):
                if index == 0:
                    year = '2018'
                    month = '12'
                elif index == 1:
                    year = '2019'
                    month = '01'
                else:
                    year = '2019'
                    month = '02'

                # login_string, cookies = set_login(mobile_number, year, month, DESTINATION)
                # login_data = json.loads(login_string)

                lotty_string = getCookieTelByTel(mobile_number, year, month)
                lotty_data = json.loads(lotty_string)

                if lotty_data['data']['lottyNum'] != 3:
                    warning_message = '{0}    {1}年{2}月的已被使用，当月剩余次数' \
                                      '为{3}'.format(mobile_number, year, month, lotty_data['data']['lottyNum'])
                    print(warning_message)
                    logging.error(warning_message)
                    time.sleep(0.3)
                    continue

                for i in range(1, 4):
                    get_price_id_string = lottyPrizeuByTelAndTest(mobile_number, year, month)
                    get_price_id_data = json.loads(get_price_id_string)

                    prize_id = get_price_id_data['data']['prizeId']

                    bonus = ''

                    if prize_id == '1':
                        bonus = '65'
                    elif prize_id == '2':
                        bonus = '325'
                    elif prize_id == '3':
                        bonus = '650'
                    elif prize_id == '4':
                        bonus = '1300'
                    else:
                        bonus = 'none'

                    message = '{0} --- {1}-{2}得到 {3} 元券'.format(mobile_number, year, month, bonus)
                    print(message)
                    logging.warning(message)
                    all_output.write('{}\n'.format(message))

                    if bonus == '1300':
                        bingo_output.write('{}\n'.format(message))
                        print('\n\n\n中奖了！！{}\n\n\n'.format(message))
                        logging.critical('\n\n\n中奖了！！！{}\n\n\n'.format(message))


                all_awards_string = findWinRecordByTel(mobile_number)
                all_awards_data = json.loads(all_awards_string)

                if all_awards_data['msg'] == 'findWinRecordByTel success.':
                    all_awards_data_data = all_awards_data['data']
                    for award_data in all_awards_data_data:
                        prize_name = award_data['prizeName']
                        travel_month = award_data['travelMonth']

                        if prize_name == '1300':
                            bingo_output.write('{0} --- {1} {2}\n'.format(mobile_number, travel_month, prize_name))
                            print('\n\n\n中奖了！~\n{0} --- {1} {2}\n'.format(mobile_number, travel_month, prize_name))

                    # time.sleep(1 + 2*random.random())
                    time.sleep(0.03)

            print('\n')
            all_output.write('\n')
            logging.warning('\n')


if __name__ == '__main__':
    # logging.basicConfig(format='%(asctime)s|PID:%(process)d|%(levelname)s: %(message)s',
    #                     level=logging.WARNING, filename='./log.txt')
    # mob = '15521390483'
    # yy = '2018'
    # mm = '11'
    # dest = '%E4%B8%AD%E5%9B%BD%E9%A6%99%E6%B8%AF'

    # run()
    test('15521390412')
