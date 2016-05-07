#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'dhqdqk'

'''
#本程序用途
可以设定提醒周期，比较常用的是番茄软件的25min工作和5min休息时间周期；
为方便，报时时间固定为每小时的25分，35分，55分，0分；
'''

import Tkinter
import tkMessageBox
import time
from multiprocessing import Process

time_work = 25 * 60 # 25min；工作周期时间; work time period
time_rest = 5 * 60 # 5min；休息周期时间; rest time period
#time_pause_day = [['12:00:00', '13:00:00'], ['19:00:00', '08:30:00']]
#time_pause_night = [['06:00:00', '19:00:00'], ]
time_effect = ['19:00:00', '07:00:00'] # 程序闹钟每天生效时间段; effective time of alarm every day;

class Alarm(object):
    def __init__(self, time_work, time_active, time_rest):
        self.time_work = time_work
        self.time_active = time_active
        self.time_rest = time_rest
        self.alarm_state = True
        self.tip = True
        self.next_alarm_time = 0
        self.state = ''
        self.now_year_month_day  = ''
        self.now_time = ''
        self.next_alarm_text = ''
        self.time_effect_len = 0
        self.next_effect_time = 0
        self.next_ineffect_time = 0
        self.effect = True
        self.pause = 0
    
    def init_alarm(self):
        now_year = time.strftime('%Y')
        now_month_day_en = time.strftime('%a %b %d')
        
        time_effect_start = time.mktime(time.strptime(now_month_day_en+' '+self.time_work[0]+' '+now_year, "%a %b %d %H:%M:%S %Y"))
        
        time_effect_end = time.mktime(time.strptime(now_month_day_en+' '+self.time_work[1]+' '+now_year, "%a %b %d %H:%M:%S %Y"))
        
        self.time_effect_len = time_effect_end - time_effect_start
        self.next_pause_time = time_effect_end
        
        now_utctime = time.time()
        
        if time_effect_end > time_effect_start:
            # 当前时间在生效期间内
            if (now_utctime >= time_effect_start) and (now_utctime < time_effect_end):
                self.effect = True
                self.next_effect_time = time_effect_start + 24 * 60 * 60
                self.next_ineffect_time = time_effect_end
                init_time = (now_utctime - time_effect_start) % 1800
                
                if init_time < self.time_active:
                    # 若程序起动时，时间在工作时间段，将状态置为工作，计算下一次休息时间；否则对应是休息状态和下次工作时间
                    self.alarm_state = True # True-'work time'; False-' Rest time'
                    self.next_alarm_time = 1800 - init_time + time.time() - self.time_rest
                else: 
                    self.alarm_state = False
                    self.next_alarm_time = 1800 - init_time + time.time()
            else:
                # 已在罢工期间
                self.effect = False
                if now_utctime < time_effect_start:
                    self.next_effect_time = time_effect_start
                else:
                    self.next_effect_time = time_effect_start + 24 * 60 * 60
                self.next_ineffect_time = self.next_effect_time + self.time_effect_len
                
        else:               
            if (now_utctime >=  time_effect_end) and (now_utctime <= time_effect_start):
                # 已在罢工期间
                self.effect = False
                self.next_effect_time = time_effect_start + 24 * 60 * 60 - self.time_effect_len
                self.next_ineffect_time = self.next_effect_time + self.time_effect_len
            else:
                # 当前时间在生效期间内
                self.effect = True
                self.next_effect_time = time_effect_start
                if now_utctime < time_effect_end:
                    self.next_ineffect_time = time_effect_end
                    init_time = (self.time_effect_len - (time_effect_end - now_utctime)) % 1800
                else:
                    self.next_ineffect_time = self.next_effect_time + self.time_effect_len
                    init_time = (now_utctime - time_effect_start) % 1800
                    self.next_ineffect_time = self.next_effect_time + self.time_effect_len
                
                if init_time < self.time_active:
                    # 若程序起动时，时间在工作时间段，将状态置为工作，计算下一次休息时间；否则对应是休息状态和下次工作时间
                    self.alarm_state = True # True-'work time'; False-' Rest time'
                    self.next_alarm_time = 1800 - init_time + time.time() - self.time_rest
                else: 
                    self.alarm_state = False
                    self.next_alarm_time = 1800 - init_time + time.time()
                
    
    def alarm(self):
        now_utctime = time.time()
        # 判断是否状态将改变，是则切换状态并计算下次切换时间
        if self.next_pause_time - now_utctime < self.time_effect_len:
            if now_utctime - self.next_alarm_time == 0:
                self.tip = False
                if self.alarm_state:
                    self.alarm_state = False
                    self.next_alarm_time += self.time_active
                else:
                    self.alarm_state = True
                    self.next_alarm_time += self.time_rest
        
        #　显示年月日
        self.now_year_month_day = time.strftime('%Y-%m-%d')
        # 显示当前时间
        self.now_time = time.strftime('%H:%M:%S %A')
        # 显示当前状态
        self.state = 'Work' if self.alarm_state else 'Rest'
        # 下次提醒时间
        self.next_alarm_text = time.strftime("%H:%M:%S", time.localtime(self.next_alarm_time))
        
        
        
def alarm_show():
    tkMessageBox.showinfo(title='alarm', message=message)

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
    
    #hi = Tkinter.Button(mainwin, text="hi", command=sayhi)
    #hi.pack(side=Tkinter.LEFT)    
    
    mainwin.mainloop()

if __name__ == "__main__":
    myalarm = Alarm(time_effect, time_work, time_rest)
    myalarm.init_alarm()
    while True:
        if myalarm.effect:
            # print "work"
            myalarm.alarm()
            if myalarm.tip:
                message = myalarm.now_year_month_day + "\n" + myalarm.now_time + \
                            "\nWork State: " + myalarm.state + "\nNext Alarm: " + \
                            myalarm.next_alarm_text
                p_alarm = Process(target=alarmGUI, args=(message,))
                p_alarm.start()
                myalarm.tip = False
            time.sleep(1)
        else:
            # print "pause"
            if not myalarm.pause:
                p_message = "now alarm is inffective.\n" + \
                            "next effective time is:\n" + \
                            time.strftime("%H:%M:%S", time.localtime(myalarm.next_effect_time))
                pp_alarm = Process(target=alarmGUI, args=(p_message,))
                pp_alarm.start()
                myalarm.pause = 1
            time.sleep(10)
