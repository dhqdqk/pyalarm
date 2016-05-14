#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'dhqdqk'

'''
#本程序用途
可以设定提醒周期，比较常用的是番茄软件的25min工作和5min休息时间周期；
为方便，报时时间固定为每小时的25分，35分，55分，0分；
'''

import Tkinter
import time
from multiprocessing import Process

time_work = 25 * 60 # 25min；工作周期时间; work time period
time_rest = 5 * 60 # 5min；休息周期时间; rest time period
# 闹钟每天生效时间段; effective time of alarm every day;the first one should be start-time
time_effect = ['19:00:00', '22:00:00', '03:00:00', '09:00:00']

class Alarm(object):
    def __init__(self, time_effect, time_work, time_rest):
        '''
        period: 一个工作周期
        alarm_state: 闹钟是否工作的标记
        tip: 已生效闹钟是否已执行的标记；默认为True，打开程序时提醒一次
        next_alarm_time: 下次有效闹钟的时间(UTC)
        state:标记当前是工作（Work）还是休息（Rest）状态
        now_year_month_day: 当前年月日时
        now_time：当前时分秒之时
        next_alarm_text：下次闹钟的时分秒之时
        state_time_len：程序闹钟当前状态的时间长度
        state_start:本次状态的时间起点
        state_end: 本次状态的时间终点
        effect：标记程序闹钟是否生效
        pause_alarm：标记闹钟停止时是否已提醒（只提醒一次）
        '''
        self.time_effect = time_effect
        self.time_effect_utc = []
        self.time_work = time_work
        self.time_rest = time_rest
        self.period = self.time_work + self.time_rest
        self.alarm_state = True
        self.state_start = 0
        self.state_end = 0
        self.tip = True
        self.next_alarm_time = 0
        self.state = ''
        self.now_year_month_day  = ''
        self.now_time = ''
        self.next_alarm_text = ''
        self.state_time_len = 0
        self.effect = True
        self.pause_alarm = False
        self.zero_time_utc = 0
        self.h24_time_utc = 0
    
    def time_setting(self):
        '''
        检测时间设定，并计算当天的0时与24时的UTC时间戳
        '''
        now_year = time.strftime('%Y')
        now_month_day_en = time.strftime('%a %b %d')
        hzero = "00:00:00"
        h24 = "23:59:59"
        
        if len(self.time_effect) % 2 == 0:
            for i in self.time_effect:
                self.time_effect_utc.append(time.mktime(time.strptime(now_month_day_en+' '+
                    i+' '+now_year, "%a %b %d %H:%M:%S %Y")))
        else:
            raise Exception("time_effect only accepts start-end time pairs")
        self.zero_time_utc = time.mktime(time.strptime(now_month_day_en+' '+
                    hzero+' '+now_year, "%a %b %d %H:%M:%S %Y"))
        self.h24_time_utc = time.mktime(time.strptime(now_month_day_en+' '+
                    h24+' '+now_year, "%a %b %d %H:%M:%S %Y")) + 1.0
        
    def init_alarm(self):
        '''
        初始化闹钟状态
        '''
        self.time_setting()
        now_utctime = time.time()
        
        # 检测当前时间所出的状态
        mintime = []
        for i, j in enumerate(self.time_effect_utc):
            if now_utctime < j:    
                mintime.append(j)
        mintime.sort()
        now_point = self.time_effect_utc.index(mintime[0])
        self.state_start = self.time_effect_utc[now_point-1]
        self.state_end = self.time_effect_utc[now_point]
        
        if now_point % 2 == 0:
            # 当前时间处于失效状态,发出失效通知
            self.effect = False
            self.pause_alarm = True
            self.next_alarm_time = self.state_end
            if self.state_start < self.state_end:
                self.state_time_len = self.state_end - self.state_start
            else:
                self.state_time_len = 24 * 60 * 60 - (self.state_start - self.state_end)
        else:
            self.effect = True
            if self.state_start < self.state_end:
                self.state_time_len = self.state_end - self.state_start
                space_time = (now_utctime - self.state_time_len) % self.period
                if space_time < self.time_work:
                    # 若程序起动时，时间在工作时间段，将状态置为工作，计算下一次休息时间；
                    # 否则对应是休息状态和下次工作时间
                    # True-'work time'; False-' Rest time'
                    self.alarm_state = True
                    self.next_alarm_time = self.period - space_time + time.time() - self.time_rest
                else: 
                    self.alarm_state = False
                    self.next_alarm_time = self.period - space_time + time.time()
            else:
                self.state_time_len = 24 * 60 * 60 - (self.state_start - self.state_end)
                if now_utctime < self.state_end:
                    space_time = (self.state_time_len - (self.state_end - now_utctime)) % self.period
                else:
                    space_time = (now_utctime - self.state_start) % self.period
                if space_time < self.time_work:
                    self.alarm_state = True
                    self.next_alarm_time = self.period - space_time + time.time() - self.time_rest
                else: 
                    self.alarm_state = False
                    self.next_alarm_time = self.period - space_time + time.time()
    
    def alarm(self):
        now_utctime = time.time()
        if now_utctime < self.state_end:
            # 切换闹钟的工作和休息状态并计算下次切换时间
            if now_utctime - self.next_alarm_time == 0:
                self.tip = False
                if self.alarm_state:
                    self.alarm_state = False
                    self.next_alarm_time += self.time_work
                else:
                    self.alarm_state = True
                    self.next_alarm_time += self.time_rest
        else:
            # 闹钟状态将改变， 重置闹钟
            self.init_alarm()
    
    def alarmMessage(self):
        #　显示年月日
        self.now_year_month_day = time.strftime('%Y-%m-%d')
        # 显示当前时间
        self.now_time = time.strftime('%H:%M:%S %A')
        # 显示当前状态
        self.state = 'Work' if self.alarm_state else 'Rest'
        # 下次提醒时间
        self.next_alarm_text = time.strftime("%H:%M:%S", time.localtime(self.next_alarm_time))
        if self.effect:
            message = self.now_year_month_day + "\n" + self.now_time + \
                            "\nWork State: " + self.state + "\nNext Alarm: " + \
                            self.next_alarm_text
        else:
            message = "now alarm is inffective.\n" + \
                    "next effective time is:\n" + \
                    time.strftime("%H:%M:%S", time.localtime(self.state_end))
        return message


def alarmGUI(message):
    mainwin = Tkinter.Tk()
    mainwin.title = 'PyAlarm'
    mainwin.geometry('400x200')
    mainwin.resizable(width=True, height=True)
    
    #view_alarm = Tkinter.Button(mainwin, text='view alarm', command=show)
    
    w = Tkinter.Label(mainwin, text=message, font=("Arial", 20))
    w.pack(side=Tkinter.TOP)
    
    #b = Tkinter.Button(mainwin, text='alarm', command=alarm_show)
    #b.pack(side=Tkinter.LEFT)
    #b.pack(expand=Tkinter.YES, fill=Tkinter.BOTH)
    
    mainwin.mainloop()

if __name__ == "__main__":
    myalarm = Alarm(time_effect, time_work, time_rest)
    myalarm.init_alarm()
    while True:
        if myalarm.effect:
            # print "work"
            myalarm.alarm()
            if myalarm.tip:
                p_alarm = Process(target=alarmGUI, args=(myalarm.alarmMessage(),))
                p_alarm.start()
                myalarm.tip = False
            time.sleep(1)
        else:
            # print "pause"
            if myalarm.pause_alarm:
                pp_alarm = Process(target=alarmGUI, args=(myalarm.alarmMessage(),))
                pp_alarm.start()
                myalarm.pause_alarm = False
            time.sleep(10)
