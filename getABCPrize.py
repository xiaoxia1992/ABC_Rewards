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
    BINGO_FILE = './{0}{1}中奖纪录{2}.txt'.format(sys.argv[2], sys.argv[3], time.strftime("%Y%m%d", time.localtime()))

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
    r = requests.post(url, headers=HEADERS, timeout=3)
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
        try:
            new_nums = achieve_num(province_code, city_code, group_num)
        except Exception as e:
            login_error_message = '第{0}轮号码获取失败, 跳过: {1}'.format(i, e)
            print(login_error_message)
            logging.error(login_error_message)
            continue
        
        all_num_set = all_num_set | new_nums
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
    for i in range(5):        
        try:
            r = requests.post(request_url, data=post_data, auth=HTTPBasicAuth('user', 'pass'), headers=HEADERS, timeout=2)
            response = r.text
            cookies = r.cookies
            if response.strip() != '':
                return response, cookies
        except Exception as e:
            login_error_message = '{0} 19年{1}月 login 网络原因获取失败: {2}'.format(mobile, months, e)
            print(login_error_message)
            logging.error(login_error_message)
        time.sleep(0.03)

    login_error_message = '{0} 19年{1}月 login 尝试了多次还是空值, 跳过'.format(mobile, months)
    print(login_error_message)
    logging.error(login_error_message)
    return '', ''


def lottery(position_index, uni_qid, years, months, destination, cookies):
    post_data = {
        'positionindex': position_index,
        'uniqid': uni_qid,
        'years': years,
        'months': months,
        'destination': destination
    }
    for i in range(3):
        try:
            request_url = 'https://abc.uncle-ad.com/abcluckydrew_newmarch/service/operAction.php?action=lottery'
            r = requests.post(request_url, data=post_data, auth=HTTPBasicAuth('user', 'pass'),
                              headers=HEADERS, cookies=cookies, timeout=2)
            response = r.text
            if response.strip() != '':
                return response
        except Exception as e:
            lottery_error_message = '19年{0}月 lottery 网络原因获取失败: {1}'.format(months, e)
            print(lottery_error_message)
            logging.error(lottery_error_message)
        time.sleep(0.02)

    lottery_error_message = '19年{0}月 lottery 尝试了多次还是空值, 跳过'.format(months)
    print(lottery_error_message)
    logging.error(lottery_error_message)
    return ''


def run():
    with open(NUM_FILE, 'r') as fr, open(BINGO_FILE, 'a') as bingo_output:
        # mobile_numbers = fr.readline().split()
        mobile_numbers = fr.readlines()
        bingo_output.write('\n---{0} {1}{2}\n'.format(time.strftime("%Y.%m.%d", time.localtime()),
                                                        sys.argv[2], sys.argv[3]))

    for mobile_number in mobile_numbers:
        with open('{0}{1}'.format(NUM_FILE[:-4], '输出.txt'), 'a') as all_output, \
                open(BINGO_FILE, 'a') as bingo_output:

            mobile_number = mobile_number.strip()

            bonus_flag = 0
            for index in range(2):
                if index == 0:
                    year = '2019'
                    month = '1'
                else:
                    year = '2019'
                    month = '2'

                login_string, cookies = set_login(mobile_number, year, month, DESTINATION)

                if login_string == '':
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

                    if lottery_string == '':
                        continue

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
                        print('\n\n200刀中奖 {}\n\n'.format(message))
                        logging.critical('\n\n200刀中奖 {}\n\n'.format(message))

                        if bonus_flag > 0:
                            bingo_output.write('连月中奖！\n')
                            print('\n\n\n连月中奖了！！{}\n\n\n'.format(message))
                            logging.critical('\n\n\n连月中奖了！！！{}\n\n\n'.format(message))

                        bonus_flag += 1

                    # time.sleep(1 + 2*random.random())
                    time.sleep(0.015)

            print('\n')
            all_output.write('\n')
            logging.warning('\n')


if __name__ == '__main__':
    if not len(sys.argv) == 4:
        print('\n参数1: 刷多少号码(x100) 参数2: 省份名 参数3: 城市名(直辖市就打两次)\n'
              '例: python3 getABCPrize.py 30 北京 北京\n')
    else:
        logging.basicConfig(format='%(asctime)s|PID:%(process)d|%(levelname)s: %(message)s', level=logging.WARNING, filename='./log/{0}{1}log{2}.txt'.format(sys.argv[2], sys.argv[3], time.strftime("%Y%m%d", time.localtime())))

        status = run_num(int(sys.argv[1]), sys.argv[2], sys.argv[3])
        if status == 'ok':
            run()
