#!/usr/bin/env python3
#  -*- coding： utf-8 -*-
# Created by FFJ on 2018/11/17

from requests.auth import HTTPBasicAuth
import requests
import json
import logging
import time
import re
import sys

if len(sys.argv) == 4:
    NUM_FILE = './num/{0}{1}联通{2}.txt'.format(sys.argv[2], sys.argv[3],
                                              time.strftime("%Y%m%d", time.localtime()))

USER_AGENT = "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1"
HEADERS = {'user-agent': USER_AGENT}
DESTINATION = '%E4%B8%AD%E5%9B%BD%E9%A6%99%E6%B8%AF'

# def get_cookies():
#     request_url = 'https://abc.uncle-ad.com/abcluckydrew_newmarch/'
#     headers = {'user-agent': USER_AGENT}
#     req = requests.get(request_url, auth=HTTPBasicAuth('user', 'pass'), headers=headers)
#     print(req.cookies)


def find_district_code(province, city):
    with open('districtCode.json', 'r') as fr:
        district_json = json.load(fr)

        for province_value in district_json['provinceData']:
            if province_value['PROVINCE_NAME'] == province:
                province_code = province_value['PROVINCE_CODE']

                group_num = district_json['proGroupNum'][province_code]

                for city_value in district_json['cityData'][province_code]:
                    if city_value['CITY_NAME'] == city:
                        city_code = city_value['CITY_CODE']
                        return province_code, city_code, group_num

        print('找不到对应的城市')
        return '', '', ''


def achieve_num(province_code, city_code, group_num):
    url = "https://m.10010.com/NumApp/NumberCenter/qryNum?callback=jsonp_queryMoreNums&provinceCode={0}&" \
          "cityCode={1}&monthFeeLimit=0&groupKey={2}&searchCategory=3&net=01&amounts=200&codeTypeCode=&" \
          "searchValue=&qryType=02&goodsNet=4".format(province_code, city_code, group_num)
    r = requests.post(url, headers=HEADERS)
    response = r.text
    match = re.findall('[0-9]{11}', response)
    result = set()
    if match:
        for num in match:
            result.add(num)
    return result


def run_num(times, province, city):
    province_code, city_code, group_num = find_district_code(province, city)

    if province_code == '':
        return ''

    all_num_set = set()
    for i in range(times):
        all_num_set = all_num_set | achieve_num(province_code, city_code, group_num)
        print('正在获取号码：第 {0} 轮, 共 {1} 轮'.format(i+1, times))
        time.sleep(1)
    print('\n\n')
    all_num_list = list(all_num_set)
    all_num_list.sort()

    with open(NUM_FILE, 'a') as fa:
        for i, num in enumerate(all_num_list):
            if i == len(all_num_list):
                fa.write('num')
            else:
                fa.write('{}\n'.format(num))
    return 'ok'


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
    with open(NUM_FILE, 'r') as fr, open('./bingo.txt', 'a') as bingo_output:
        # mobile_numbers = fr.readline().split()
        mobile_numbers = fr.readlines()
        bingo_output.write('\n\n---{0} {1}{2}\n'.format(time.strftime("%Y.%m.%d", time.localtime()),
                                                        sys.argv[2], sys.argv[3]))

    for mobile_number in mobile_numbers:
        with open('{0}{1}'.format(NUM_FILE[:-4], '输出.txt'), 'a') as all_output, \
                open('./bingo.txt', 'a') as bingo_output:

            mobile_number = mobile_number.strip()

            for index in range(2):
                if index == 0:
                    year = '2019'
                    month = '1'
                else:
                    year = '2019'
                    month = '2'

                login_string, cookies = set_login(mobile_number, year, month, DESTINATION)

                if login_string.strip() == '':
                    error_message = '{0}    {1}年{2}月 请求失败'.format(mobile_number, year, month)
                    print(error_message)
                    logging.error(error_message)

                    continue

                login_data = json.loads(login_string)

                if login_data['nums'] != 3:
                    warning_message = '{0}    {1}年{2}月的已被使用，当月剩余次数' \
                                      '为{3}'.format(mobile_number, year, month, login_data['nums'])
                    print(warning_message)
                    logging.error(warning_message)
                    time.sleep(0.3)
                    continue

                uniqid = login_data['uniqid']

                for i in range(1, 4):
                    lottery_string = lottery(i, uniqid, year, month, DESTINATION, cookies)
                    lottery_data = json.loads(lottery_string)
                    bonus = lottery_data['msg']

                    sign = ''
                    if month == '1' or month == '2':
                        sign = '0'

                    message = '{0} --- {1}-{2}{3}得到 {4} 美元' \
                              '券'.format(mobile_number, year, sign, month, bonus)
                    print(message)
                    logging.warning(message)
                    all_output.write('{}\n'.format(message))

                    if bonus == 200:
                        bingo_output.write('{}\n'.format(message))
                        print('\n\n\n中奖了！！{}\n\n\n'.format(message))
                        logging.critical('\n\n\n中奖了！！！{}\n\n\n'.format(message))

                    # time.sleep(1 + 2*random.random())
                    time.sleep(0.03)

            print('\n')
            all_output.write('\n')
            logging.warning('\n')


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s|PID:%(process)d|%(levelname)s: %(message)s',
                        level=logging.WARNING, filename='./log.txt')

    if not len(sys.argv) == 4:
        print('\n参数1: 刷多少号码(x100) 参数2: 省份名 参数3: 城市名(直辖市就打两次)\n'
              '例: python3 getABCPrize.py 30 北京 北京\n')
    else:
        status = run_num(int(sys.argv[1]), sys.argv[2], sys.argv[3])
        if status == 'ok':
            run()
