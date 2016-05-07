# pyalarm
Pyalarm can work periodic duty  with alarm to tell you when to work（25min) or rest(5min)。 

pyalarm可以设定工作和休息时间并轮流提醒，类似于番茄时间；默认是工作25min，休息5min。
# rely-on/依赖
`sudo pip install multiprocessing`

pyalarm use Process of module "multiprocessing" to run a son-process for alarm window coded with Tkinter。

提醒弹窗口（Tkinter编写）用多进程方式打开。
# 设置
```
# pyalarm.py

time_work = 25 * 60 # 25min；工作周期时间; work time period
time_rest = 5 * 60 # 5min；休息周期时间; rest time period

time_effect = ['19:00:00', '07:00:00'] # 程序闹钟每天生效时间段; effective time of alarm every day;
# ['19:00:00', '07:00:00']: 19,20,21 ,.. 24, 1,.., 7
# ['07:00:00', '19:00:00']: 7, 8, 9, ..., 12, 1, ..., 19
```
