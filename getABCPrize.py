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
import smtplib
from email.mime.text import MIMEText


if len(sys.argv) == 5:
    if sys.argv[1] == 'r':
        NUM_FILE = './num/{0}{1}联通{2}.txt'.format(sys.argv[3], sys.argv[4],
                                                  time.strftime("%Y%m%d%H", time.localtime()))
        BINGO_FILE = './bingo/{0}{1}联通中奖纪录{2}.txt'.format(sys.argv[3], sys.argv[4],
                                                          time.strftime("%Y%m%d%H", time.localtime()))


USER_AGENT = "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1"
HEADERS = {'user-agent': USER_AGENT}
DESTINATION = '%E4%B8%AD%E5%9B%BD%E9%A6%99%E6%B8%AF'


def send_email(msg):
    smtp = smtplib.SMTP()
    smtp.connect('smtp.163.com:25')
    username = 'paddyfu@163.com'
    password = 'airlemon1'
    smtp.login(username, password)
    mail = MIMEText(msg)
    mail['Subject'] = '连月中奖通知'
    mail['From'] = username
    mail['To'] = 'lemonjush@163.com'
    smtp.sendmail(username, 'lemonjush@163.com', mail.as_string())
    smtp.quit()


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


def achieve_chu_num(province_code, city_code, group_num):
    url = "https://m.10010.com/NumApp/NumberCenter/qryNum?callback=jsonp_queryMoreNums&provinceCode={0}&" \
          "cityCode={1}&monthFeeLimit=0&groupKey={2}&searchCategory=3&net=01&amounts=200&codeTypeCode=&" \
          "searchValue=&qryType=02&goodsNet=4".format(province_code, city_code, group_num)

    url2 = "https://m.10010.com/NumApp/NumberCenter/qryNum?callback=jsonp_vwkgzbdlkt&provinceCode={0}&" \
           "cityCode={1}&monthFeeLimit=0&searchCategory=3&net=01&amounts=200&codeTypeCode=&searchValue=&" \
           "qryType=02&goodsNet=4&goodsId=981805170635&channel=mall".format(province_code, city_code)

    ali_url = "https://wt.tmall.com/trade/detail/itemOp.do?itemId=39990583842&skuId=0&provId=110000&" \
              "cityId=110100&planId=22317&maxCount=30&network=WCDMA&m=SelectNum"

    r = requests.post(url, headers=HEADERS, timeout=3)
    response = r.text
    match = re.findall('[0-9]{11}', response)
    result = set()
    if match:
        for num in match:
            result.add(num)
    return result


def run_chu_num(times, province, city):
    province_code, city_code, group_num = find_district_code(province, city)

    if province_code == '':
        return ''

    all_num_set = set()
    for i in range(times):
        try:
            new_nums = achieve_chu_num(province_code, city_code, group_num)
        except Exception as e:
            login_error_message = '第{0}轮号码获取失败, 跳过: {1}'.format(i+1, e)
            print(login_error_message)
            logging.error(login_error_message)
            continue
        
        all_num_set = all_num_set | new_nums
        print('正在获取号码：第 {0} 轮, 共 {1} 轮'.format(i+1, times))
        time.sleep(0.03)
    print('\n\n')
    all_num_list = list(all_num_set)
    all_num_list.sort()

    with open(NUM_FILE, 'a') as fa:
        for i, num in enumerate(all_num_list):
            if i == len(all_num_list) - 1:
                fa.write(num)
            else:
                fa.write('{}\n'.format(num))
    return 'ok'


def init_empty_nums(front_six_num):
    first_num = '{}00001'.format(front_six_num)
    final_num = '{}99999'.format(front_six_num)
    file_name = './num/{}.txt'.format(front_six_num)
    with open(file_name, 'w') as fw:
        for i in range(int(first_num), int(final_num)):
            if i == int(final_num) - 1:
                fw.write(str(i))
            else:
                fw.write('{}\n'.format(str(i)))
    return file_name


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
            r = requests.post(request_url, data=post_data, auth=HTTPBasicAuth('user', 'pass'),
                              headers=HEADERS, timeout=2)
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


def run(file=''):
    if file:
        num_file = file
        bingo_file = './bingo/{}中奖记录.txt'.format(file[6:-4])
        # output_file = '{}输出.txt'.format(file[:-4])
    else:
        num_file = NUM_FILE
        bingo_file = BINGO_FILE
        # output_file = '{}输出.txt'.format(NUM_FILE[:-4])

    with open(num_file, 'r') as fr, open(bingo_file, 'a') as bingo_output:
        # mobile_numbers = fr.readline().split()
        mobile_numbers = fr.readlines()
        if sys.argv[1] == 'r':
            bingo_output.write('\n---{0} {1}{2}\n'.format(time.strftime("%Y.%m.%d.%H", time.localtime()),
                                                          sys.argv[3], sys.argv[4]))
        if sys.argv[1] == 'e':
            bingo_output.write('\n---{0} {1}\n'.format(time.strftime("%Y.%m.%d.%H", time.localtime()), sys.argv[2]))

    for mobile_number in mobile_numbers:
        if mobile_number == '':
            continue
        if mobile_number[0] != '1':
            continue
        with open(bingo_file, 'a') as bingo_output:
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

                try:
                    login_data = json.loads(login_string)
                except Exception as e:
                    login_error_message = '{0} 19年{1}月 login json载入失败: {2}'.format(mobile_number, month, e)
                    print(login_error_message)
                    logging.error(login_error_message)
                    continue

                if not 'nums' in login_data.keys():
                    continue

                if login_data['nums'] != 3:
                    warning_message = '{0}    {1}年{2}月的已被使用，当月剩余次数' \
                                      '为{3}'.format(mobile_number, year, month, login_data['nums'])
                    print(warning_message)
                    logging.error(warning_message)
                    time.sleep(0.01)
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
                    # all_output.write('{}\n'.format(message))

                    if bonus == 200:
                        bingo_output.write('{}\n'.format(message))
                        print('\n\n200刀中奖 {}\n\n'.format(message))
                        logging.critical('\n\n200刀中奖 {}\n\n'.format(message))

                        if bonus_flag > 0 and index == 1:
                            bingo_output.write('连月中奖！\n')
                            print('\n\n\n连月中奖了！！{}\n\n\n'.format(message))
                            logging.critical('\n\n\n连月中奖了！！！{}\n\n\n'.format(message))

                            try:
                                if sys.argv[1] == 'r':
                                    send_email('{0} {1}{2} 连月中奖了'.format(mobile_number, sys.argv[3], sys.argv[4]))
                                else:
                                    send_email('{} (空号) 连月中奖了'.format(mobile_number))
                            except Exception as e:
                                print('发邮件的问题: 号码:{0} 错误:{1}'.format(mobile_number, e))
                                logging.error('发邮件的问题: 号码:{0} 错误:{1}'.format(mobile_number, e))
                                continue
                            

                        bonus_flag += 1

                    # time.sleep(1 + 2*random.random())
                    time.sleep(0.01)

            print('\n')
            # all_output.write('\n')
            logging.warning('\n')


if __name__ == '__main__':
    if len(sys.argv) == 1:
        print('\n参数1 模式:e为空号循环 r为真实联通\n'
              '    若为r:\n'
              '        参数2: 刷多少号码(x100) 参数3: 省份名 参数4: 城市名(直辖市就打两次)\n'
              '        例: python3 getABCPrize.py r 30 北京 北京\n'
              '    若为e:\n'
              '        参数2: 输入空号号段的头6位数\n'
              '        例: python3 getABCPrice.py e 145999\n')
    else:
        if sys.argv[1] == 'r':
            logging.basicConfig(format='%(asctime)s|PID:%(process)d|%(levelname)s: %(message)s', level=logging.WARNING,
                                filename='./log/{0}{1}联通log{2}.txt'.format(sys.argv[3], sys.argv[4],
                                                                           time.strftime("%Y%m%d%H", time.localtime())))
            status = run_chu_num(int(sys.argv[2]), sys.argv[3], sys.argv[4])
            if status == 'ok':
                run()

        elif sys.argv[1] == 'e':
            logging.basicConfig(format='%(asctime)s|PID:%(process)d|%(levelname)s: %(message)s', level=logging.WARNING,
                                filename='./log/{0}log{1}.txt'.format(sys.argv[2],
                                                                      time.strftime("%Y%m%d%H", time.localtime())))
            if len(sys.argv[2]) == 6:
                FILE_NAME = init_empty_nums(sys.argv[2])
                run(FILE_NAME)
            else:
                print('参数2输入有误, 需要输入号段头6位数字')

        else:
            print('参数1输入有误, 只能为e或r')
