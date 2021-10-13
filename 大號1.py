# encoding:utf-8
import os
from IPython.display import clear_output
from ppadb.client import Client
global reso_x, reso_y, screenshot_mode, adb_num
import numpy as np
import time
import math
import win32api
import cv2
import win32gui
import sys
import subprocess
import imutils
from shutil import copyfile
from datetime import datetime
import threading
#import matplotlib.pyplot as plt
#import matplotlib.image as mpimg
os.system('chcp 936')
subprocess.Popen([r"cmd"])
subprocess.Popen([r"C:\platform-tools\adb", r"devices"])
os.chdir('C:\\platform-tools\\moonlight\\遊戲截圖')
adb = Client(host='127.0.0.1', port=5037)
exec(open('C:\\platform-tools\\moonlight\\functions\\functions5.py',encoding="utf-8").read())

#################  腳本說明區  #############################
# 功能介紹: 
# 0. 閃退後自動重登第一隻腳色
# 1. 自動領500隻怪的徽章
# 1. 自動特化分解裝備
# 2. 負重97%找商人賣雜物:
#       到商人座標mx, my後, 再回到打怪座標fx, fy
# 4. 自動回復+領重複任務 (請鎖定任務欄且取消其他任務:
#       鎖定任務欄且讓任務欄只留下重複任務
# 5. 自動切換技能頁:
#       switch = True 會自動切換，switch = False 不會自動切換
##################  設定區  #########################
## 角色名子，主號的話一定要有包含"主"在裡面
char_name = "主"
## ADB 接口編號，請看你的模擬器偏好設定
adb_num = 5564

## 自動重登腳色編號: 第一隻 = 1, 第二隻=2,...
char_login = 1

## 是否進行重複任務: 要=Ture 不要=False
task = False

## 重複使用道具編號(第一頁): 0=不使用, 1~5=使用物品號碼
item = 0

## 是否使用蝴蝶復活: 要=Ture 不要=False
resurrect = True

## 是否使用省電模式: 要=Ture 不要=False
eco=True

## 切換技能頁間格秒數: 0=不切換
switch = 10

## 省電模式，檢查負重, 重複任務, 復活寵物間隔: 
check_interval= 120

## 寵物編號
pet = 1

## mx, my: 商人座標
mx, my = 270, 270 # 魔窟

## fx, fy: 掛機座標
fx, fy = 1010, 210 # foggy

## 回掛機座標前的傳送點
fbx, fby = 0, 0


## sell_fly1, sell_fly2: 賣東西和返回是否傳送，是=1, 否=0
## task_fly1, task_fly2: 回復任務和返回是否傳送，是=1, 否=0
sell_f, sell_fb = 1, 0
task_f, task_fb = 0, 0
############# 自動判斷解析度 #############
device = adb.device('emulator-'+str(adb_num))
screenshot()

print(char_name)
dim = cv2.imread('screen'+str(adb_num)+'.png').shape
reso_x, reso_y = dim[1], dim[0]
icon_bns = cv2.imread('C:\\platform-tools\\moonlight\\functions\\icon_bns_'+str(reso_x)+'x'+str(reso_y)+'.png')
de, ci = 0.5, 3
## start screening
global image, img, time_image, time_img
############# 功能測試區: 要測試的話把 # 移除 ###########
## 買賣功能
#sell(mx=mx, my=my, fx=fx, fy=fy, f=sell_f, fb=sell_fb, fbx=fbx, fby=fby, de=1, ci=3, waitnpc=10)

## 分解裝備功能
#decompose(shot = 0)

## 領任務功能
#return_task(fx, fy, f=task_fly1, fb=task_fly2)

######################################################### 以下不要改
print('Python月光雕刻師腳本: 腳本初始化')
pet_time=time.time()
while True:
    t1 = time.time()
    try:
    #if True:
        ## 是否重登
        auto_login(num=char_login, shot=1)
        print(char_name)
        ## 返回遊戲畫面: 開點數, 復活, 回主畫面, 技能頁1(截圖)
        home_screen(shot=1, de=de, timemax=10)
        
        # 開打
        fight(1, shot=0)
        # 復活寵物
        pet_time = pet_resurrect(num=pet, pet_time=pet_time, shot=0)
        # 重複任務
        if task:
            return_task(fx=fx, fy=fy, f=task_f, fb=task_fb, fbx=fbx, fby=fby, de=de, ci=ci, waitnpc=10)
        # 賣東西
        weight = decompose(shot = 0)
        if weight:
            print('雜物過多!', end=' ')
            sell(mx=mx, my=my, fx=fx, fy=fy, f=sell_f, fb=sell_fb, fbx=fbx, fby=fby, de=1, ci=3, waitnpc=10)
            storage_fish(take=0)
            
        tt = time.time()
        while time.time()-tt < check_interval:
            if switch>0 :
                t_switch=time.time()
                myclick(780, 18, rs_x=1600, rs_y=900)
                myclick(1862, 912, 0.5, rs_x=1920, rs_y=1080, msg='執行: 切換技能頁', mode=0)
                myclick(1862, 912, 0.5, rs_x=1920, rs_y=1080, msg='執行: 切換技能頁', mode=0)
                home_screen()
                use_item(item)
            if eco:
                print("省電模式: "+str(time.time()-tt))
                ecomode()
                E = (1,1)
                while time.time()-tt<check_interval and E[0]>0: # ecomode for check_interal time
                    myclick(780, 18, rs_x=1600, rs_y=900)
                    E = PixelSearch(540, 450, 541, 451, "0x6B6152", 0, 1)
                    
            else:
                while time.time()-t_switch<switch:
                    pass
                 
    except Exception as e:
        print(e)
        time.sleep(5)
    
    
    
