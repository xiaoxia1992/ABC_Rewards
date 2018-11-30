#!/usr/bin/env python3
#  -*- coding： utf-8 -*-
# Created by FFJ on 2018/11/30

from requests.auth import HTTPBasicAuth
import requests
import json
import logging
import time
import random


USER_AGENT = "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1"
HEADERS = {'user-agent': USER_AGENT}
DESTINATION = '%E4%B8%AD%E5%9B%BD%E9%A6%99%E6%B8%AF'


def getCookieTelByTel(mobile, years, months):
    post_data = {
        'tel': mobile,
        'travelMonth': '{0}-{1}'.format(years, months)
    }
    request_url = 'http://credit.cmbond.com/unionpay_travel_act/getCookieTelByTel.html'
    r = requests.post(request_url, data=post_data, headers=HEADERS)
    response = r.text
    print(response)
    cookies = r.cookies
    print('cookies: {}'.format(cookies))
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
    r = request.post(request_url, data=post_data, headers=HEADERS)
    return r.text


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

                    message = '{0} --- {1}-{2}{3}得到 {4} 元券'.format(mobile_number, year, sign, month, bonus)
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
    logging.basicConfig(format='%(asctime)s|PID:%(process)d|%(levelname)s: %(message)s',
                        level=logging.WARNING, filename='./log.txt')
    # mob = '15521390483'
    # yy = '2018'
    # mm = '11'
    # dest = '%E4%B8%AD%E5%9B%BD%E9%A6%99%E6%B8%AF'

    run()
