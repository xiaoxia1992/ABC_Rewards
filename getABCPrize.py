#!/usr/bin/env python3
#  -*- coding： utf-8 -*-
# Created by FFJ on 2018/11/17

from requests.auth import HTTPBasicAuth
import requests
import json
import logging
import time
import re
import smtplib
import argparse
from email.mime.text import MIMEText


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

    # url2 = "https://m.10010.com/NumApp/NumberCenter/qryNum?callback=jsonp_vwkgzbdlkt&provinceCode={0}&" \
    #        "cityCode={1}&monthFeeLimit=0&searchCategory=3&net=01&amounts=200&codeTypeCode=&searchValue=&" \
    #        "qryType=02&goodsNet=4&goodsId=981805170635&channel=mall".format(province_code, city_code)
    #
    # ali_url = "https://wt.tmall.com/trade/detail/itemOp.do?itemId=39990583842&skuId=0&provId=110000&" \
    #           "cityId=110100&planId=22317&maxCount=30&network=WCDMA&m=SelectNum"

    r = requests.post(url, headers=HEADERS, timeout=3)
    response = r.text
    match = re.findall('1[0-9]{10}', response)
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

    with open(reward.num_file, 'a') as fa:
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


def union_pay_login(mobile, years, months):
    for i in range(5):
        try:
            post_data_first = {
                'ut': '034931765552222893',
                'type': 'game.html'
            }
            requests_first_url = 'http://credit.cmbond.com/unionpay_travel_act/addAccess.html'
            rf = requests.post(requests_first_url, data=post_data_first, headers=HEADERS)
            print(rf.text)

            post_data_second = {
                'ut': str(mobile)
            }
            requests_second_url = 'http://credit.cmbond.com/unionpay_travel_act/getTicket.html'
            rs = requests.post(requests_second_url, data=post_data_second, headers=HEADERS)
            print(rs.text)

            post_data_zero = {
                'ut': '034931765552222893',
                'tel': mobile,
                'destination': '%E9%A6%99%E6%B8%AF',
                'travelTime': '{0}-{1}'.format(years, months),
                'type': 'Unionpay'
            }
            requests_zero_url = 'http://credit.cmbond.com/unionpay_travel_act/addTravelRecorduAndUbion.html'
            rz = requests.post(requests_zero_url, data=post_data_zero, headers=HEADERS)

            post_data = {
                'tel': str(mobile),
                'travelMonth': '{0}-{1}'.format(years, months)
            }
            request_url = 'http://credit.cmbond.com/unionpay_travel_act/getCookieTelByTel.html'
            r = requests.post(request_url, data=post_data, headers=HEADERS)
            response = r.text
            if response.strip() != '':
                return response

        except Exception as e:
            login_error_message = '{0} 19年{1}月 银联 login 网络原因获取失败: {2}'.format(mobile, months, e)
            print(login_error_message)
            logging.error(login_error_message)
            time.sleep(0.03)

    login_error_message = '{0} 19年{1}月 银联 login 尝试了多次还是空值, 跳过'.format(mobile, months)
    print(login_error_message)
    logging.error(login_error_message)
    return ''


def union_pay_lotty(mobile, years, months):
    post_data = {
        'tel': mobile,
        'type': 'Unionpay',
        'travelMonth': '{0}-{1}'.format(years, months)
    }
    request_url = 'http://credit.cmbond.com/unionpay_travel_act/lottyPrizeuByTelAndTest.html'
    for i in range(3):
        try:
            r = requests.post(request_url, data=post_data, headers=HEADERS)
            response = r.text
            if response.strip() != '':
                return response
        except Exception as e:
            lottery_error_message = '19年{0}月 银联 lottery 网络原因获取失败: {1}'.format(months, e)
            print(lottery_error_message)
            logging.error(lottery_error_message)
        time.sleep(0.02)

    lottery_error_message = '19年{0}月 银联 lottery 尝试了多次还是空值, 跳过'.format(months)
    print(lottery_error_message)
    logging.error(lottery_error_message)
    return ''


def visa_login(mobile, years, months, destination):
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
            login_error_message = '{0} 19年{1}月 VISA login 网络原因获取失败: {2}'.format(mobile, months, e)
            print(login_error_message)
            logging.error(login_error_message)
        time.sleep(0.03)

    login_error_message = '{0} 19年{1}月 VISA login 尝试了多次还是空值, 跳过'.format(mobile, months)
    print(login_error_message)
    logging.error(login_error_message)
    return '', ''


def visa_lottery(position_index, uni_qid, years, months, destination, cookies):
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
            lottery_error_message = '19年{0}月 VISA lottery 网络原因获取失败: {1}'.format(months, e)
            print(lottery_error_message)
            logging.error(lottery_error_message)
        time.sleep(0.02)

    lottery_error_message = '19年{0}月 VISA lottery 尝试了多次还是空值, 跳过'.format(months)
    print(lottery_error_message)
    logging.error(lottery_error_message)
    return ''


def visa_get_prize_list(cookies):
    for i in range(3):
        try:
            request_url = 'https://abc.uncle-ad.com/abcluckydrew_newmarch/service/operAction.php?action=getPrizeLsit'
            r = requests.post(request_url, auth=HTTPBasicAuth('user', 'pass'),
                              headers=HEADERS, cookies=cookies, timeout=2)
            response = r.text
            if response.strip() != '':
                return response
        except Exception as e:
            lottery_error_message = 'VISA 获取历史奖品 网络原因获取失败: {}'.format(e)
            print(lottery_error_message)
            logging.error(lottery_error_message)
        time.sleep(0.02)

    lottery_error_message = 'VISA 获取历史奖品 尝试了多次还是空值, 跳过'
    print(lottery_error_message)
    logging.error(lottery_error_message)
    return ''


class Rewards:
    def __init__(self):
        if args.mode == 'r':
            self.bingo_file = './bingo/{0}{1}联通中奖纪录{2}.txt'.\
                format(args.p, args.c, time.strftime("%Y%m%d%H", time.localtime()))
            self.num_file = './num/{0}{1}联通{2}.txt'.\
                format(args.p, args.c, time.strftime("%Y%m%d%H", time.localtime()))

        self.bonus_flag = 0
        self.visa_flag = 0
        self.history_flag = 0
        self.try_flag = 0

    def visa_loop(self, mobile_number):
        self.bonus_flag = 0
        self.history_flag = 0
        self.try_flag = 0

        for index in range(2):
            year = '2019'
            if index == 0:
                month = '1'
            else:
                month = '2'

            visa_login_string, cookies = visa_login(mobile_number, year, month, DESTINATION)

            if visa_login_string == '':
                continue

            try:
                visa_login_data = json.loads(visa_login_string)
            except Exception as e:
                login_error_message = '{0} 19年{1}月 VISA login json载入失败: {2}'.format(mobile_number, month, e)
                print(login_error_message)
                logging.error(login_error_message)
                continue

            if 'nums' not in visa_login_data.keys():
                continue

            if visa_login_data['nums'] != 3:
                warning_message = '{0}    {1}年{2}月的 VISA 已被使用，当月剩余次数' \
                                  '为{3}'.format(mobile_number, year, month, visa_login_data['nums'])
                print(warning_message)
                logging.error(warning_message)
                time.sleep(0.01)

                if self.try_flag == 1:
                    continue

                visa_prize_list_string = visa_get_prize_list(cookies)

                if visa_prize_list_string != '':
                    try:
                        visa_prize_list_data = json.loads(visa_prize_list_string)

                        if 'msg' in visa_prize_list_data.keys():
                            if len(visa_prize_list_data['msg']) > 0:
                                for each in visa_prize_list_data['msg']:
                                    each_year = each['years']
                                    each_month = each['months']
                                    each_prize = each['type']
                                    if each_year == '2019' and each_prize == '200':

                                        message = '{0} --- {1}-{2} VISA 查看历史获得 {3} 美元' \
                                                  '券'.format(mobile_number, each_year, each_month, each_prize)
                                        self.save_bingo_file('{}\n'.format(message))
                                        print('\n\nVISA 200刀历史记录中奖 {}\n\n'.format(message))
                                        logging.critical('\n\nVISA 200刀历史记录中奖 {}\n\n'.format(message))

                                        if self.history_flag > 99:
                                            self.save_bingo_file('VISA 历史记录连月中奖！\n')
                                            print('\n\n\nVISA 历史记录连月中奖了！！{}\n\n\n'.format(message))
                                            logging.critical('\n\n\nVISA 历史记录连月中奖了！！！{}\n\n\n'.format(message))

                                            try:
                                                if args.mode == 'r':
                                                    send_email(
                                                        '{0} {1}{2} VISA 历史记录连月中奖了'.format(mobile_number, args.p, args.c))
                                                else:
                                                    send_email('{} (空号) VISA 历史记录连月中奖了'.format(mobile_number))
                                            except Exception as e:
                                                print('发邮件的问题: 号码:{0} 错误:{1}'.format(mobile_number, e))
                                                logging.error('发邮件的问题: 号码:{0} 错误:{1}'.format(mobile_number, e))
                                                continue
                                        self.history_flag += 100

                    except Exception as e:
                        login_error_message = '{0} 19年{1}月 VISA 获取历史奖品 json载入失败: {2}'.format(mobile_number, month, e)
                        print(login_error_message)
                        logging.error(login_error_message)
                        continue
                continue

            self.try_flag += 1
            uni_qid = visa_login_data['uniqid']
            for i in range(1, 4):
                visa_lottery_string = visa_lottery(i, uni_qid, year, month, DESTINATION, cookies)

                if visa_lottery_string == '':
                    continue

                try:
                    visa_lottery_data = json.loads(visa_lottery_string)
                except Exception as e:
                    login_error_message = '{0} 19年{1}月 VISA lottery json载入失败: {2}'.format(mobile_number, month, e)
                    print(login_error_message)
                    logging.error(login_error_message)
                    continue

                if 'msg' not in visa_lottery_data.keys():
                    continue

                bonus = visa_lottery_data['msg']

                message = '{0} --- {1}-{2} VISA 得到 {3} 美元' \
                          '券'.format(mobile_number, year, month, bonus)
                print(message)
                logging.warning(message)

                if bonus == 200:
                    self.save_bingo_file('{}\n'.format(message))
                    print('\n\nVISA 200刀中奖 {}\n\n'.format(message))
                    logging.critical('\n\nVISA 200刀中奖 {}\n\n'.format(message))

                    if self.bonus_flag > 0 and index == 1:
                        self.save_bingo_file('VISA 连月中奖！\n')
                        print('\n\n\nVISA 连月中奖了！！{}\n\n\n'.format(message))
                        logging.critical('\n\n\nVISA 连月中奖了！！！{}\n\n\n'.format(message))

                        try:
                            if args.mode == 'r':
                                send_email('{0} {1}{2} VISA 连月中奖了'.format(mobile_number, args.p, args.c))
                            else:
                                send_email('{} (空号) VISA 连月中奖了'.format(mobile_number))
                        except Exception as e:
                            print('发邮件的问题: 号码:{0} 错误:{1}'.format(mobile_number, e))
                            logging.error('发邮件的问题: 号码:{0} 错误:{1}'.format(mobile_number, e))
                            continue

                    self.bonus_flag += 1
                    self.visa_flag += 1

                # time.sleep(1 + 2*random.random())
                time.sleep(0.01)

    def union_pay_loop(self, mobile_number):
        self.bonus_flag = 0
        for index in range(2):
            year = '2019'
            if index == 0:
                month = '01'
            else:
                month = '02'

            union_pay_login_string = union_pay_login(mobile_number, year, month)

            if union_pay_login_string == '':
                continue

            try:
                union_pay_login_data = json.loads(union_pay_login_string)
            except Exception as e:
                login_error_message = '{0} 19年{1}月 银联 login json载入失败: {2}'.format(mobile_number, month, e)
                print(login_error_message)
                logging.error(login_error_message)
                continue

            if 'data' not in union_pay_login_data.keys():
                continue
            if 'lottyNum' not in union_pay_login_data['data'].keys():
                continue

            if union_pay_login_data['data']['lottyNum'] == 3:
                for i in range(1, 4):
                    union_pay_lottery_string = union_pay_lotty(mobile_number, year, month)
                    if union_pay_lottery_string == '':
                        continue

                    try:
                        union_pay_lottery_data = json.loads(union_pay_lottery_string)
                    except Exception as e:
                        login_error_message = '{0} 19年{1}月 银联 lotty json载入失败: {2}'.format(mobile_number, month, e)
                        print(login_error_message)
                        logging.error(login_error_message)
                        continue

                    prize_id = union_pay_lottery_data['data']['prizeId']

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

                    message = '{0} --- {1}-{2} 银联 得到 {3} 人民币' \
                              '券'.format(mobile_number, year, month, bonus)
                    print(message)
                    logging.warning(message)

                    if bonus == 200:
                        self.save_bingo_file('{}\n'.format(message))
                        print('\n\n银联 1300元中奖 {}\n\n'.format(message))
                        logging.critical('\n\n银联 1300元中奖 {}\n\n'.format(message))

                        if self.visa_flag > 0:
                            self.save_bingo_file('VISA 银联 两开花！\n')
                            print('\n\n\nVISA 银联 两开花！{}\n\n\n'.format(message))
                            logging.critical('\n\n\nVISA 银联 两开花！{}\n\n\n'.format(message))

                            try:
                                if args.mode == 'r':
                                    send_email(
                                        '{0} {1}{2} VISA 银联 两开花！'.format(mobile_number, args.p, args.c))
                                else:
                                    send_email('{} (空号) VISA 银联 两开花！'.format(mobile_number))
                            except Exception as e:
                                print('发邮件的问题: 号码:{0} 错误:{1}'.format(mobile_number, e))
                                logging.error('发邮件的问题: 号码:{0} 错误:{1}'.format(mobile_number, e))
                                continue

                        if self.bonus_flag > 0 and index == 1:
                            self.save_bingo_file('银联 连月中奖！\n')
                            print('\n\n\n银联 连月中奖了！！{}\n\n\n'.format(message))
                            logging.critical('\n\n\n银联 连月中奖了！！！{}\n\n\n'.format(message))

                            try:
                                if args.mode == 'r':
                                    send_email(
                                        '{0} {1}{2} 银联 连月中奖了'.format(mobile_number, args.p, args.c))
                                else:
                                    send_email('{} (空号) 银联 连月中奖了'.format(mobile_number))
                            except Exception as e:
                                print('发邮件的问题: 号码:{0} 错误:{1}'.format(mobile_number, e))
                                logging.error('发邮件的问题: 号码:{0} 错误:{1}'.format(mobile_number, e))
                                continue

                        self.bonus_flag += 1

                    time.sleep(0.01)
            else:
                warning_message = '{0}    {1}年{2}月的 银联 已被使用，当月剩余次数' \
                                  '为{3}'.format(mobile_number, year, month, union_pay_login_data['data']['lottyNum'])
                print(warning_message)
                logging.error(warning_message)
                time.sleep(0.01)
                # continue

    def save_bingo_file(self, content):
        with open(self.bingo_file, 'a') as bingo_output:
            bingo_output.write(content)

    # def save_num_file(self, content):

    def run(self):
        with open(self.num_file, 'r') as fr:
            # mobile_numbers = fr.readline().split()
            mobile_numbers = fr.readlines()
            if args.mode == 'r':
                self.save_bingo_file('\n---{0} {1}{2}\n'.format(time.strftime("%Y.%m.%d.%H", time.localtime()),
                                                                args.p, args.c))
            if args.mode == 'e':
                self.save_bingo_file('\n---{0} {1}\n'.format(time.strftime("%Y.%m.%d.%H", time.localtime()),
                                                             args.f))

        for mobile_number in mobile_numbers:
            if mobile_number == '':
                continue
            if mobile_number[0] != '1':
                continue
            mobile_number = mobile_number.strip()
            self.visa_flag = 0

            self.visa_loop(mobile_number)

            # self.union_pay_loop(mobile_number)

            print('\n')
            logging.warning('\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('mode', help='e为空号循环 r为真实联通')
    parser.add_argument('-n', help='刷多少号码(x100) 默认1', type=int, default=1)
    parser.add_argument('-p', help='省份名', type=str, default='广东')
    parser.add_argument('-c', help='城市名(直辖市就打两次)', type=str, default='深圳')
    parser.add_argument('-f', help='如果是e模式, 输入号段头6位数字', type=str, default='145666')
    args = parser.parse_args()
    mode = args.mode

    reward = Rewards()

    if mode == 'r':
        logging.basicConfig(format='%(asctime)s|PID:%(process)d|%(levelname)s: %(message)s', level=logging.WARNING,
                            filename='./log/{0}{1}联通log{2}.txt'.format(args.p, args.c,
                                                                       time.strftime("%Y%m%d%H", time.localtime())))
        status = run_chu_num(int(args.n), args.p, args.c)
        if status == 'ok':
            reward.run()

    elif mode == 'e':
        logging.basicConfig(format='%(asctime)s|PID:%(process)d|%(levelname)s: %(message)s', level=logging.WARNING,
                            filename='./log/{0}log{1}.txt'.format(args.f,
                                                                  time.strftime("%Y%m%d%H", time.localtime())))
        if len(args.f) == 6:
            init_empty_nums(args.f)
            reward.run()
        else:
            print('参数-f输入有误, 需要输入号段头6位数字')

    else:
        print('参数mode输入有误, 只能为e或r')
