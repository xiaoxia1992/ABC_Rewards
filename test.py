
smtp = smtplib.SMTP()
smtp.connect('smtp.163.com:25')
username = 'paddyfu@163.com'
password = 'airlemon1'
smtp.login(username, password)
mail = MIMEText('正文测试{}'.format(3))
mail['Subject'] = '这是邮件主题'
mail['From'] = username
mail['To'] = 'lemonjush@163.com'
smtp.sendmail(username, 'lemonjush@163.com', mail.as_string())
smtp.quit()
