from datetime import datetime

week = '{:%Y-%m-%d}'.format(datetime.now())
print('rundate={0}'.format(week))

# os.system('ls -l {0} {1}'.format(os.getcwd(),'/home/windriver/xiaozhan'))
# os.system('ls -l %s %s' % (os.getcwd(),'/home/windriver/xiaozhan'))
# command = 'runwassp -f {WASSP_PLAN} -E "WASSP_WIND_HOME={WASSP_WIND_HOME}"  -E "WASSP_HOME={WASSP_HOME}" -E "WASSP_WORKSPACE_HOME={WASSP_WORKSPACE_HOME}" -E "WASSP_LOGS_HOME={WASSP_LOGS_HOME}" --continueIfReleaseInvalid -s exec --exec-retries 5'.format(WASSP_PLAN = rerun_plan, WASSP_WIND_HOME = dvd, WASSP_HOME = wassp_home, WASSP_WORKSPACE_HOME = workspace, WASSP_LOGS_HOME = logs)
# os.system(command)
# upload_command = 'python3 /folk/hyan1/Nightly/common/load_ltaf.py --log {LOG} --rundate {RUNDATE} --release {RELEASE}'.format( LOG= logs, RUNDATE = run_date, RELEASE = release_name)
# os.system(upload_command)
print("{0[0]}.{0[1]}".format(('baidu', 'com')))
# baidu.com

print("{0:.2f} {1:.1f}".format(3.1415926, 4.23))
# 3.14  4.2     前面的0表示第一个参数，1表示第二个参数

# 基本语法是通过 {} 和 : 来代替以前的 %

msg = ['wang', 10]
print('my name is {0}, {0} age is {1}'.format(*msg))

msg = {'name': 'wang', 'age': 10}
print('my name is {name}, {name} age is {age}'.format(**msg))
# my name is wang, wang age is 10

# 左对齐
print('{:*<10}'.format('beijing'))
print('{:*^10}'.format('beijing'))   # 居中
# 右对齐

print('{:*>10}'.format('beijing'))   # 右对齐
a = '{:*>10}'.format('beijing')
print(a)

# 分割线*******
# ***分割线****
# *******分割线

print("{1:.3f},{0:02d}".format(5, 10.11))     # 10.110 , 05
# {0:02d}   表示位置为0的参数，宽度为2，类型为d,用0来补足

# 字符串格式化最简单的方法是用f格式，python3.6以后推出的功能
msg = {'name': 'wang', 'age': 10}
print(f'my name is {msg}')
