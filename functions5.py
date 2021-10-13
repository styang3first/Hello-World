################################################################# 以下不用改
# pip install numpy
# pip install -U pure-python-adb
# pip install pywin32
# pip install opencv-python
# pip install ipython
# pip install pywin32
## 01212021 新增 Tesseract
# pip install pytesseract
# pip install imutils
####### image process tolls
#global time_saveimg_pre
def get_grayscale(image):
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

def thresholding(image):
    return cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

def hex_to_rgb(value):
    value = value.lstrip('#')
    lv = len(value)
    return tuple(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))

def rgb_to_hex(rgb):
    return '0x%02x%02x%02x' % rgb

####### windows api tools
def win_active():
    return win32gui.GetWindowText (win32gui.GetForegroundWindow())

def getIdleTime():
    return (win32api.GetTickCount() - win32api.GetLastInputInfo()) / 1000.0

####### adb bacis tools
def game_error():
    if 'kakao' not in device.shell('dumpsys input'):
        #print('遊戲閃退')
        raise ValueError("遊戲閃退")
    if getIdleTime()<20 and ('BlueStacks' in win_active()):
        #print('正在遊玩')
        raise ValueError("正在遊玩")
    
def screenshot_keep(save=1, mode=1):
    global image, time_image
    while True:        
        try:
            gamescreen = device.screencap()
            with open("screen"+str(adb_num)+".png", "wb") as fp:
                fp.write(gamescreen)
            image = cv2.imread("screen"+str(adb_num)+".png")
            time_image = time.time()
        except:
            print("截圖失敗")
        time.sleep(0.5)

def screenshot():
    global img, time_img
    try:
        gamescreen = device.screencap()
        with open("screen"+str(adb_num)+".png", "wb") as fp:
            fp.write(gamescreen)
        img = cv2.imread("screen"+str(adb_num)+".png")
        time_img = time.time()
        print("截圖成功")
    except:
        print("截圖失敗")
        time.sleep(3)
        screenshot()
        
def PixelSearch(lx, ly, rx, ry, pixel, sim, shot=1): # form the left, downward
    global time_img, img
    game_error()
        
    sim = sim + 5 
    rgb = hex_to_rgb('#'+pixel[2:8])
    if shot:
        screenshot()
    lx = int(reso_x*lx/960)
    rx = int(reso_x*rx/960)
    ly = int(reso_y*ly/540)
    ry = int(reso_y*ry/540)
    cx=lx
    cy=ly
    
    while cy<=ry:
        d = abs(rgb - img[cy,cx,])
        if max(d)<sim:
            return (cx, cy)
        else:
            cx=cx+1
        if cx>=rx:
            cx=lx
            cy=cy+1
    return (0, 0)


def SearchNPC(lx, ly, rx, ry, pixel1, pixel2, sim=10, shot=1):
    global time_img, img
    rgb1 = hex_to_rgb('#'+pixel1[2:8])
    rgb2 = hex_to_rgb('#'+pixel2[2:8])
    if shot:
        screenshot()
    lx = int(reso_x*lx/960)
    rx = int(reso_x*rx/960)
    ly = int(reso_y*ly/540)
    ry = int(reso_y*ry/540)
    subimg = img[ly:ry, lx:rx,]

    posi1 = np.where(np.max(abs(subimg-rgb1), axis=2)<sim)
    if len(posi1[0])==0:
        return(0, 0)
    for index in reversed(range(len(posi1[0]))):
        cy = posi1[0][index]
        cx = posi1[1][index]
        if len(np.where(np.max(abs(subimg[cy, cx:int(cx+20*reso_x/960),]-rgb2), axis=1)<sim)[0])>0:
            return(lx+cx, ly+cy)
    return(0, 0)

def PixelSearch2(lx, ly, rx, ry, pixel, sim, shot=1): # from the right, downward
    global time_img, img
    game_error()
    
    sim = sim + 5 
    rgb = hex_to_rgb('#'+pixel[2:8])
    if shot:
        screenshot()
    lx = int(reso_x*lx/960)
    rx = int(reso_x*rx/960)
    ly = int(reso_y*ly/540)
    ry = int(reso_y*ry/540)
    cx=rx
    cy=ly
    
    while cx>=lx:
        d = abs(rgb - img[cy,cx,])
        if max(d)<sim:
            return(cx, cy)
        else:
            cy=cy+1
        if cy>=ry:
            cy=ly
            cx=cx-1
    return (0, 0)

def ImgSearch(picture, template, threshold=0.8):
    w, h = picture.shape[:-1]
    res = cv2.matchTemplate(template, picture, cv2.TM_CCOEFF_NORMED)
    loc = np.where(res >= threshold)
    return loc

def waitpixeldisappear( lx, ly, rx, ry, pixel, sim, timemax=120, msg2=''):
    t = time.time()
    while PixelSearch(lx, ly, rx, ry, pixel, sim)[0]>0:
        if len(msg2)>0:
            print(msg2)                
        time.sleep(0.5)
        if (time.time()-t)>timemax:
            raise ValueError('執行超時')
        
def waitpixelappear( lx, ly, rx, ry, pixel, sim, timemax=120, msg2=''):
    t = time.time()    
    while PixelSearch(lx, ly, rx, ry, pixel, sim)[0]==0:
        if len(msg2)>0:
            print(msg2)
        time.sleep(0.5)
        if (time.time()-t)>timemax:
            raise ValueError('執行超時')
        
def click(cx, cy, de=0.5, msg=''):
    if len(msg)>0:
        print(msg)
    else:
        print('點擊座標', cx, cy)
    device.shell('input tap ' + str(cx) + ' ' + str(cy))
    time.sleep(de)

def confirm_blue(shot=1, ci=3, timemax=15):
    E = PixelSearch(500, 250, 620, 400, "0xD7DB28", 5, shot) # search blue confirm
    myclick(E[0]+10, E[1]+10, ci, 540, 250, 620, 400, "0xD7DB28", 5, msg='確認', mode=4, timemax=timemax)

# mode: 0-just click, 1-until appear, 2-until disappear, 3-click until appear, 4-click until disappaer
# rs_x, rs_y: resolution for cx, cy
# de: click interval
def myclick(cx, cy, de=0.5, lx=0, ly=0, rx=0, ry=0, pixel=0xFFFFFF, sim=255, rs_x=0, rs_y=0, msg='', msg2='', mode=0, timemax=float('inf')):
    game_error()
    
    if lx>0 and mode==0:
        raise ValueError('請輸入正確的mode')
    if rs_x==0:
        rs_x, rs_y = reso_x, reso_y
    
    cx=int(cx*reso_x/rs_x)
    cy=int(cy*reso_y/rs_y)

    if mode==0:
        click(cx, cy, de, msg)
    elif mode==1: # wait until appear
        click(cx, cy, de, msg)
        waitpixelappear( lx, ly, rx, ry, pixel, sim, timemax, msg2)
    elif mode==2: # wait until disappear
        click(cx, cy, de, msg)
        waitpixeldisappear( lx, ly, rx, ry, pixel, sim, timemax, msg2)
    elif mode==3: # click until appear
        t=time.time() # for timemax
        E = (0, 0)
        while E[0]==0:
            t1=time.time()
            click(cx, cy, de=0.2, msg=msg)
            E = PixelSearch(lx, ly, rx, ry, pixel, sim)
            while (time.time()-t1)<de and E[0]==0: # keep checking pixel during click interval
                if len(msg2)>0:
                    print(msg2)
                E = PixelSearch(lx, ly, rx, ry, pixel, sim)
            if (time.time()-t)>timemax:
                raise ValueError('執行超時')
            
    elif mode==4: # click until disappear
        t=time.time() # for timemax
        E = (1, 1)
        while E[0]>0:
            t1=time.time()
            click(cx, cy, de=0.2, msg=msg)
            E = PixelSearch(lx, ly, rx, ry, pixel, sim)
            while (time.time()-t1)<de and E[0]>0: # keep checking pixel during click interval
                if len(msg2)>0:
                    print(msg2)
                E = PixelSearch(lx, ly, rx, ry, pixel, sim)
            if (time.time()-t)>timemax:
                raise ValueError('執行超時')
            
### status checking
def check_poisson():
    if PixelSearch2(79, 13, 197, 17, '0x6E44F3', 1, 1)[0]>0:
        myclick(110, 93, de=0.5, rs_x=1600, rs_y=900, mode=0)
    if PixelSearch(243, 60, 243, 60, '0xFFFFFF', 1, 1)[0]==0:
        myclick(473, 85, de=0.5, rs_x=1600, rs_y=900, mode=0)
    if PixelSearch(37, 258, 37, 258, '0xFFFFFF', 1, 1)[0]==0:
        myclick(55, 400, de=0.5, rs_x=1600, rs_y=900, mode=0)
    loc = ImgSearch(picture, template=img, threshold=0.5)
    if len(loc[0])>0:
        return True
    else:
        return False

def checkloading(shot=1):
    E1 = PixelSearch(478, 250, 478, 250, '0xFFFFFF', 0, shot) # search middle white
    E2 = PixelSearch(3, 524, 26, 536, '0xFFFFFF', 1, 0) # search white exp bar
    if E1[0]>0 and E2[0]==0:
        return(True)
    else:
        return(False)

def checkdead(shot=1):
    global time_img, img
    if shot:
        screenshot()
    ly, ry = int(450*reso_y/1080), int(500*reso_y/1080)
    lx, rx = int(1200*reso_x/1920), int(1250*reso_x/1920)
    E1 = sum(sum(sum(abs(img[ly:ry, lx:rx,]-(255,255,255))))) # pure white region
    E2 = PixelSearch(465, 315, 485, 325, '0xD4D725', 1, 0) # search middle blue
    if E1<10 and E2[0]>0:
        return(True)
    else:
        return(False)

def checkrunning(shot=1):
    E1 = PixelSearch(465, 420, 485, 430, '0xF2F7F5', 10, shot) # mileage
    E2 = PixelSearch(430, 420, 450, 430, '0xF2F7F5', 10, shot) # mileage
    loading = checkloading()
    if E1[0]==0 or E2[0]>0 or loading:
        return(False)
    else:
        return(True)

def checkweight(shot=1):
    E1 = PixelSearch(892, 37, 892, 39, "0xECA647", 5, shot) # blue bar
    E2 = PixelSearch(3, 524, 26, 536, '0xFFFFFF', 1, 0) # search white exp bar
    if E1[0]*E2[0]>0:
        return(True)
    else:
        return(False)

def check500(shot=1):
    E1 = PixelSearch(260, 18, 270, 33, '0x38C4FF', 3, shot) # 500 reward
    E2 = PixelSearch(3, 524, 26, 536, '0xFFFFFF', 1, 0) # search white exp bar
    if E1[0]*E2[0]>0:
        return(True)
    else:
        return(False)
    
def checkmessage(shot=1):
    E1 = PixelSearch(935, 65, 937, 67, '0x6B6054', 1, shot) # gray cross
    E2 = PixelSearch(903, 67, 903, 67, '0xFFFFFF', 1, 0)
    if E1[0]*E2[0]>0:
        return(True)
    else:
        return(False)

def checktask(shot=1):
    now = datetime.now()
    hour = now.strftime("%H")
    if int(hour)<-1:
        return -1

    y_increment = 0
    E3 = PixelSearch(3, 524, 26, 536, '0xFFFFFF', 1, 0) # search white exp bar
    while y_increment<=0 and E3[0]>0:
        E1 = PixelSearch(872, 250+y_increment, 878, 257+y_increment, '0x36BCF8', 5, shot) # check yellow text
        E2 = PixelSearch(765, 230+y_increment, 780, 250+y_increment, '0x67C292', 5, 0) # check green
        E4 = PixelSearch(927, 250+y_increment, 935, 257+y_increment, '0xF3F3F3', 10, 0) # check white
        if E1[0]*E2[0]*E3[0]*E4[0]>0:
            return y_increment
        else:
            y_increment = 8 + y_increment
    return -1
    
###### simple function wont change gameplay screen
def waitloading(timemax=120):
    time.sleep(5)
    t = time.time()
    while checkloading():
        time.sleep(1)
        if (time.time()-t)>timemax:
            raise ValueError('執行超時')
        
def waitrunning(timemax=120):
    time.sleep(1)
    t = time.time()
    while checkrunning():
        time.sleep(1)
        if (time.time()-t)>timemax:
            raise ValueError('執行超時')

def getreward():
    myclick(249, 20, 0.5, rs_x=960, rs_y=540, mode=0)
    myclick(249, 20, 0.5, rs_x=960, rs_y=540, mode=0)
    myclick(249, 20, 0.5, rs_x=960, rs_y=540, mode=0)

def cleanmessage():
    print('清除通知')
    myclick(936, 70, 0.5, rs_x=960, rs_y=540, mode=0)
    while checkmessage():
        print('清除通知')
        myclick(936, 70, 0.5, rs_x=960, rs_y=540, mode=0)

def fight(f, shot=1): # fight=1, stop=0
    E1 = PixelSearch(260, 482, 265, 502, '0xFFFFFF', 15, shot) # fight region white
    E2 = PixelSearch(3, 524, 26, 536, '0xFFFFFF', 1, 0) # search white exp bar
    if E1[0]==0 and E2[0]>0 and f==1: # fight but stop
        if "釣" in char_name:
            device.shell('input swipe 269 495 269 495 2000')
            myclick(270, 404, 0.5, rs_x=960, rs_y=540, msg='半自動', mode=0)
        else:
            myclick(269, 495, 0.5, rs_x=960, rs_y=540, msg='開始戰鬥', mode=0)
    elif E1[0]>0 and E2[0]>0 and f==0: # stop but fingting
        myclick(269, 495, 0.2, rs_x=960, rs_y=540, msg='停止戰鬥', mode=0)

def move(d=2, de=0.1):
    if d==1:
        print('上移')
        device.shell('input swipe 500 200 500 0 ' + str(int(de*1000)))
    elif d==2:
        print('下移')
        device.shell('input swipe 500 200 500 400 ' + str(int(de*1000)))
    elif d==3:
        print('左移')
        device.shell('input swipe 500 200 300 200 ' + str(int(de*1000)))
    elif d==4:
        print('右移')
        device.shell('input swipe 500 200 700 200 ' + str(int(de*1000)))

def use_item(num, msg=''):
    if num>0:
        if len(msg)==0:
            myclick(1090+77*num, 750, 0.5, rs_x=1600, rs_y=900, msg='使用物品 ' + str(num), mode=0)
        else:
            myclick(1090+77*num, 750, 0.5, rs_x=1600, rs_y=900, msg=msg, mode=0)                

####################### large functions ########################
# de: mode=0 click delay, ci: mode>1 click interval 
def home_screen(shot=1, de=0.5, timemax=float('inf')):
    game_error()
    
    if shot==0: # 先按返回
        device.shell('input keyevent 4')

    myclick(780, 18, rs_x=1600, rs_y=900)
    t = time.time()
    while True: # keep esc until standard screen
        E1 = PixelSearch2(79, 13, 197, 17, '0x6E44F3', 1, 1) # blood bar
        E2 = PixelSearch(858, 37, 858, 39, "0xECA647", 5, 0) # weight blue bar
        E3 = PixelSearch2(900, 500, 900, 500, '0xD3D724', 5, 0) # if logout icon
        E4 = PixelSearch2(370, 250, 370, 330, '0x696055', 5, 0) # cancel icon
        E5 = PixelSearch2(580, 250, 580, 330, '0xD7DB28', 5, 0) # confirm icon
        E6 = PixelSearch(540, 450, 541, 451, "0x6B6152", 0, 0) # ecomode
        E7 = PixelSearch(3, 524, 26, 536, '0xFFFFFF', 1, 0) # search white exp bar
        dead = checkdead(0) # dead
        if E6[0]>0:
            myclick(478, 452, 0.5, 3, 524, 26, 536, '0xFFFFFF', 1, rs_x=960, rs_y=540, msg='解除省電模式', msg2='等待', mode=1, timemax=10)
            device.shell('input keyevent 4')
            break
        elif dead: # dead
            print("你已死亡")
            if resurrect:
                print("自動復活")
                myclick(475, 270, de=de, rs_x=960, rs_y=540, mode=0)
                waitpixelappear(79, 13, 197, 17, '0x6E44F3', 1, timemax=120) # blood
                time.sleep(1)
                move(3, 1)
                myclick(780, 18, rs_x=1600, rs_y=900)
                myclick(269, 495, 0.5, rs_x=960, rs_y=540, msg='開始戰鬥', mode=0)
            break
        elif E3[0]>0: # find logout icon
            print('返回遊戲主畫面')
            if "雜" not in char_name:
                myclick(930, 30, de, 900, 500, 900, 500, '0xD3D724', 5, rs_x=960, rs_y=540, mode=2, msg='')
            break
        elif E4[0]>0 and E5[0]>0: # find exit game
            print('取消')    
            myclick(E4[0], E4[1]+10, de, 370, 250, 370, 330, '0x696055', 5, rs_x=reso_x, rs_y=reso_y, mode=2)
            break
        elif E2[0]==0: # no weight bar 
            print('返回遊戲主畫面')
            device.shell('input keyevent 4')
            time.sleep(de)
        elif E7[0]>0:
            # change back to page 1
            if '月' in char_name and PixelSearch(935, 475, 945, 480, '0xFFFFFF', 10, 0)[0]==0:
                myclick(1862, 912, 0, rs_x=1920, rs_y=1080, msg='校正技能頁', mode=0)
            break
        
    
    
    
def ecomode(de=1):
    print('執行功能: 進入省電模式')
    if PixelSearch(899, 472, 899, 472, '0xDBDD2C', 3)[0]==0:
        myclick(930, 30, de, 899, 472, 899, 472, '0xDBDD2C', 3, rs_x=960, rs_y=540, msg='選單', mode=1, timemax=10)
    myclick(660, 500, de, rs_x=960, rs_y=540, msg='省電模式', mode=0)

def finish_ecomode(ci=3):
    print('執行功能: 解除省電模式')
    if PixelSearch(330, 250, 470, 390, '0x696055', 1, 1)[0]>0:
        click(int(444*reso_x/960), int(333*reso_x/960), de=0.2, msg='取消') # 結束遊戲: 取消
    myclick(478, 452, 1, 3, 524, 26, 536, '0xFFFFFF', 1, rs_x=960, rs_y=540, msg='解除省電模式', msg2='等待', mode=1, timemax=10)
    home_screen(shot=1, de=1, timemax=10)

def finish_ecomode_old(ci=3):
    print('執行功能: 解除省電模式')
    t=time.time() # for timemax
    E = (0, 0)
    while E[0]==0:
        t1=time.time()
        click(int(478*reso_x/960), int(452*reso_x/960), de=0.2, msg='解除省電模式') #
        if PixelSearch(330, 250, 470, 390, '0x696055', 1, 1)[0]>0:
            click(int(333*reso_x/960), int(444*reso_x/960), de=0.2, msg='取消') # 結束遊戲: 取消
        E = PixelSearch(3, 524, 26, 536, '0xFFFFFF', 1) # search exp bar
        while (time.time()-t1)<ci and E[0]==0: # keep checking pixel during click interval
            E = PixelSearch(3, 524, 26, 536, '0xFFFFFF', 1) # search exp bar
        if (time.time()-t)>10:
            raise ValueError('執行超時')

def map(nx, ny, de=0.5, rs_x=0, rs_y=0):
    if rs_x==0:
        rs_x, rs_y = reso_x, reso_y    
    myclick(900, 200, de, 950, 23, 960, 33, '0x6B6153', 3, rs_x=960, rs_y=540, msg='開啟地圖', mode=1, timemax=10) # map
    myclick(nx, ny, de, rs_x=rs_x, rs_y=rs_y, mode=0)
    home_screen(shot=1, de=de)
    
def enhance(de=0.5):
    print('執行功能: 裝備特化')
    myclick(930, 30, ci, 899, 480, 899, 480, '0xDBDD2C', 3, rs_x=960, rs_y=540, msg='開啟選單', mode=1, timemax=10)
    myclick(790, 100, ci, 899, 480, 899, 480, '0xDBDD2C', 3, rs_x=960, rs_y=540, msg='裝備特化', mode=2, timemax=10)
    myclick(661, 100, ci, 660, 100, 665, 105, '0xFFFFFF', 3, rs_x=960, rs_y=540, msg='裝備特化: 全部', mode=1, timemax=10) # '全部'變白
    myclick(737, 500, de, rs_x=960, rs_y=540, msg='自動選擇', mode=0)
    E = PixelSearch(835, 488, 842, 498, '0xD7DC28', 3)
    while E[0]>0:
        myclick(911, 495, de, rs_x=960, rs_y=540, msg='強化', mode=0, timemax=10)
        myclick(737, 500, de, rs_x=960, rs_y=540, msg='自動選擇', mode=0, timemax=10)
        E = PixelSearch(835, 488, 845, 498, '0xD7DC28', 3)
    home_screen(shot=0, de=de)

def decompose(shot=1, de=0.5, ci=3):
    if checkweight(shot):
        print('執行功能: 裝備分解')
        myclick(930, 30, de, 899, 480, 899, 480, '0xDBDD2C', 3, rs_x=960, rs_y=540, msg='開啟選單', mode=1, timemax=10)
        myclick(660, 100, de, 899, 480, 899, 480, '0xDBDD2C', 3, rs_x=960, rs_y=540, msg='裝備改造', mode=2, timemax=10)
        myclick(780, 80, de, 775, 80, 780, 85, '0xDEDEDE', 3, rs_x=960, rs_y=540, msg='分解', mode=1, timemax=10)
        time.sleep(1)
        # second_row = PixelSearch(230, 222, 231, 223, '0x5B5B5B', 2, 1) # check second row dim color
        myclick(500, 493, 0.1, 230, 158, 231, 159, '0x5B5B5B', 0, rs_x=960, rs_y=540, msg="分解", mode=3, timemax=50) # click until dim color
        home_screen(shot=0, de=de)
        weight = checkweight(1)
        #return (second_row[0]>0)
        return weight
    return False

def sell(mx, my, fx, fy, f=0, fb=0, fbx=0, fby=0, de=0.5, ci=3, waitnpc=10, red=0, blue=0):
    print('找商人賣雜物功能')
    E=(0,0) # 確認是否叫出購買選單
    while E[0]==0:
        print('(再次)前往商人')
        fight(0)
        move(3, 0.2)
        time.sleep(0.2)
        if f==0:
            map(mx, my, de) # go to merchant
            print('跑步中')
            time.sleep(10)
            waitpixelappear(210, 120, 750, 450, '0xFFFF00', 0, timemax=120, msg2='跑步中')
        elif f==1:
            use_item(num=1, msg='使用回程卷軸')
            time.sleep(2)            


        # click default spot
        myclick(480, 250, de=2, rs_x=960, rs_y=540, msg='點擊商人', mode=0) # click and wait skip icon
        E = PixelSearch(730, 393, 745, 417, '0xD3D724', 5) # check whether click the merchant
        tt = time.time()
        while E[0]==0 and time.time()-tt<120:
            print('點擊商人')
            while E[0]==0  and time.time()-tt<120 :
                time.sleep(1)
                move(1, 0.1)
                time.sleep(0.1)
                move(2, 0.1)
                E = SearchNPC(210, 120, 750, 450, pixel1='0xFFFF00', pixel2='0xFFFFFF') #search NPC
                print(E)
                if E[0]==0:
                    map(mx, my)

            print('找到商人')
            t1=time.time()
            myclick(E[0]+15, E[1]+int(50*reso_x/960), de, mode=0) # click and wait skip icon
            E = (0,0)
            while (time.time()-t1)<waitnpc and E[0]==0:
                E = PixelSearch(730, 393, 745, 417, '0xD3D724', 5) ## check whether actually click it

    loc = [tuple()]
    while len(loc[0])==0: 
        screenshot()
        w, h = icon_bns.shape[:-1]
        # icon2 = imutils.resize(icon_bns, width = int(icon_bns.shape[1] * reso_x/1600))
        # res = cv2.matchTemplate(img_rgb, icon2, cv2.TM_CCOEFF_NORMED)
        res = cv2.matchTemplate(img, icon_bns, cv2.TM_CCOEFF_NORMED)
        threshold = .8
        loc = np.where(res >= threshold)
        # loc = ImgSearch(icon_bns, template=img, threshold=0.8)
    E = (int(loc[1][0]), int(loc[0][0]))
    myclick(E[0], E[1], de, 950, 23, 960, 33, '0x6B6153', 3, msg='販賣/購買', mode=1, timemax=10) # buy/sell

    # sell 
    myclick(168, 50, ci, 165, 47, 170, 52, '0xFFFFFF', 3, rs_x=960, rs_y=540, msg='販賣', mode=3, timemax=10) # sell
    myclick(280, 495, ci, 35, 95, 40, 100, '0xEEEEEE', 3, rs_x=960, rs_y=540, msg='全部販賣', mode=3, timemax=10) # sell all
    home_screen(shot=0, de=de)
    print('反回打怪地點')
    if fb==1:
        if fbx==0:
            fbx, fby = fx, fy
            
        map(fbx, fby)
        myclick(1025, 854, ci, 500, 250, 620, 400, "0xD7DB28", 5, rs_x=1920, rs_y=1080, msg='傳送', msg2='等待傳送確認', mode=1) # fly
        confirm_blue(shot=0, ci=ci) # confirm
        time.sleep(1)
            
    map(fx, fy)
    print('跑步中')
    fight(1)
    time.sleep(0.1)
            
def return_task(fx, fy, f=0, fb=0, fbx=0, fby=0, de=0.5, ci=3, waitnpc=10):
    print(checktask(0))
    if checktask(0)<0:
        return 0
    print('回覆/接收任務')
    if f: # if fly
        myclick(1686, 483, de, rs_x=1920, rs_y=1080, msg='前往任務', mode=0)
        myclick(1025, 854, ci, 500, 250, 620, 400, "0xD7DB28", 5, rs_x=1920, rs_y=1080, msg='傳送', msg2='等待傳送確認', mode=1, timemax=10) # fly
        confirm_blue(shot=0, ci=ci, timemax=5)
    else:
        myclick(1686, 483, de, rs_x=1920, rs_y=1080, msg='前往任務', mode=0)
        time.sleep(3)
        move(3,0.1)   
        
    myclick(1686, 483, ci, 910, 20, 930, 30, '0x696055', 1, rs_x=1920, rs_y=1080, msg='交付任務', mode=3) # click until skip icon appear
    myclick(910, 30, de, rs_x=960, rs_y=540, msg='跳過skip', mode=0, timemax=10) # skip
    home_screen(shot=1, de=de) # ESC first

    SKIP=(0,0)
    NPC_posi=(0,0)
    # Searching task NPC
    tt = time.time()
    
    print('點擊重複任務NPC')
    while SKIP[0]==0 and time.time()-tt<120:
        while NPC_posi[0]==0 and time.time()-tt<120:
            move(1, 0.1)
            time.sleep(0.1)
            move(2, 0.1)
            red_icon = PixelSearch(280, 120, 680, 420, '0x3D59FF', 5, 0)
            if red_icon[0]>0:
                print(red_icon)
                NPC_posi = (red_icon[0], red_icon[1] + int(100*reso_x/960))
            else: # if not find red
                NPC = SearchNPC(280, 120, 680, 420, pixel1='0xC3EBFF', pixel2='0xFFFFFF') #search NPC
                if NPC[0]>0:
                    NPC_posi = (NPC[0], NPC[1] + int(70*reso_x/960))

            print('找到NPC!')
            t1=time.time()
            myclick(NPC_posi[0], NPC_posi[1], de, mode=0) # click NPC
            while (time.time()-t1)<waitnpc and SKIP[0]==0: # wait skip
                SKIP = PixelSearch( 910, 20, 930, 30, '0x696055', 2, 1)

    myclick(910, 30, ci, 500, 250, 620, 400, "0xD7DB28", 5, rs_x=960, rs_y=540, msg='跳過skip', mode=3, timemax=10) # skip
    confirm_blue(shot=0, ci=ci)
    
    print('反回打怪地點')
    if fb==1:
        if fbx==0:
            fbx, fby = fx, fy
        map(fbx, fby)
        myclick(1025, 854, de, 500, 250, 620, 400, "0xD7DB28", 5, rs_x=1920, rs_y=1080, msg='傳送', mode=3, timemax=10) # fly
        confirm_blue(shot=0, ci=ci) # confirm
        time.sleep(1)
            
    map(fx, fy)
    print('跑步中')
    fight(1, 0)
    time.sleep(0.1)
    
def auto_login(num, shot=1, de=0.5, ci=3):
    if getIdleTime()<20 and ('BlueStacks' in win_active()):
        #print('正在遊玩')
        raise ValueError('正在遊玩')
    if 'kakao' not in device.shell('dumpsys input'):
        print('自動重登')
        device.shell('am force-stop com.kakaogames.moonlighttw')
        time.sleep(2)        
        device.shell('am start -n com.kakaogames.moonlighttw/com.kakaogame.KGUnityPlayerActivity t70')
        time.sleep(20)
        
        E1 = (0, 0)
        # looping in finding logout icon
        # if not, check stuck and maintainence icon
        t_login=time.time()
        while PixelSearch(840, 20, 860, 40, '0x696055', 5)[0]==0: 
            if time.time()-t_login>120:
                while 'kakao' in device.shell('dumpsys input'):
                    print('關閉遊戲')
                    device.shell('am force-stop com.kakaogames.moonlighttw')
                raise ValueError('畫面卡住: 自動重登')

            if PixelSearch(700, 290, 750, 305, '0xC1C87F', 5)[0]>0: # maintainence icon
                myclick(730, 297, 2, rs_x=960, rs_y=540)
            time.sleep(2)

            
        myclick(470, 10, ci, 870, 85, 930, 340, '0xD7D928', 0, msg='等待腳色選擇', rs_x=960, rs_y=540, mode=3) # wait select char
        if num==1:
            myclick(900, 95, ci, 870, 85, 930, 95, '0xD7D928', 0, rs_x=960, rs_y=540, msg='選擇腳色 1', mode=4) 
        if num==2:
            myclick(900, 171, ci, 870, 170, 930, 175, '0xD7D928', 0, rs_x=960, rs_y=540, msg='選擇腳色 2', mode=4) 
        time.sleep(40)
        waitloading()
        home_screen(shot=1, de=de)
        move(1, 0.1)
        fight(1)

def pet_resurrect(num, pet_time, until=False, shot=1, de=0.5, ci=3):
    if num>0:
        E = PixelSearch(2, 138, 15, 370, '0x6E44F3', 0, shot) # check whether the pet is dead
        E1 = PixelSearch(322, 18, 322, 18, '0xFFFFFF', 0, 0) # check chat panel
        if E[0]==0 and E1[1]==0:
            if time.time() - pet_time < 61: # return death time
                return pet_time
            else:
                if PixelSearch(20, 290, 30, 300, "0xFFFFFF", 35, 1)[0]>0:
                    myclick(40, 600, de, rs_x=1600, rs_y=900, msg='開啟寵物', mode=0)
                else:
                    myclick(40, 500, de, rs_x=1600, rs_y=900, msg='開啟寵物', mode=0)
                print('復活寵物功能')
                myclick(1300, 65 + 125*num, de, rs_x=1600, rs_y=900, msg='選擇寵物 '+str(num), mode=0)
                if until:                
                    myclick(820, 816, ci, 485, 489, 495, 490, '0xFFFFFF', 3, rs_x=1600, rs_y=900, msg='復活', mode=3)
                else:
                    myclick(820, 816, de, rs_x=1600, rs_y=900, msg='復活', mode=0)
                home_screen(shot=1, de=de)
    return time.time()

def storage_fish(take=1):
    t_save = time.time()
    # myclick(25, 170, ci, 350, 500, 350, 500, '0x696055', 5, rs_x=960, rs_y=540, msg='夥伴', mode=1, timemax=10) # friend
    myclick(930, 30, de, 899, 472, 899, 472, '0xDBDD2C', 3, rs_x=960, rs_y=540, msg='選單', mode=1, timemax=10)
    myclick(720, 260, ci, 350, 500, 350, 500, '0x696055', 5, rs_x=960, rs_y=540, msg='夥伴', mode=1, timemax=10) # friend
    myclick(300, 500, ci, 610, 325, 615, 330, '0xD3D725', 5, rs_x=960, rs_y=540, msg='跑腿', mode=1, timemax=10)
    myclick(580, 325, ci, 610, 325, 615, 330, '0xD3D725', 5, rs_x=960, rs_y=540, msg='確認', mode=2, timemax=10)

    # save items
    myclick(800, 500, de, rs_x=960, rs_y=540, msg='多選', mode=0)
    myclick(900, 500, de, rs_x=960, rs_y=540, msg='存物品', mode=0)

    if take:
        # take baits
        myclick(140, 50, de, rs_x=960, rs_y=540, msg='消耗品', mode=0)
        myclick(40, 100, ci, 500, 480, 505, 485, '0xD3D725', 5, rs_x=960, rs_y=540, msg='魚餌', mode=1, timemax=10)
        myclick(470, 470, de, rs_x=960, rs_y=540, msg='領取', mode=0)

        device.shell('input swipe 600 300 600 300 2000')
        myclick(600, 400, de, rs_x=960, rs_y=540, msg='確認', mode=0) #
    home_screen(shot=1)


### disable
def home_sell(de=1, ci=3, waitnpc=10):
    if PixelSearch(721, 123, 725, 130, '0xFFFFFF', 0)[0]==0:
        print('回家CD中')
        return 0
    print('執行功能: 回家賣雜物')
    fight(0)
    move(3, 0.1)
    time.sleep(1)

    ct=0
    while (checkloading()==False) and ct<3:
        ct += 1
        myclick(724, 121, de, rs_x=960, rs_y=540, mode=0) 
        print('確認')
        myclick(554, 322, de, rs_x=960, rs_y=540, mode=0)
        time.sleep(2)

    if checkloading():
        print('loading')
        waitloading()
    else:
        return 0

    E=(0,0) # 確認是否叫出購買選單
    while E[0]==0:
        print('(再次)前往商人')
        E=(0,0)
        while E[0]==0:
            print('點擊商人')
            while E[0]==0:
                map(204, 214, de, 960, 540)
                time.sleep(1)
                waitrunning()
                home_screen()
                E = SearchNPC(280, 120, 680, 420, pixel1='0xFFFF00', pixel2='0xFFFFFF') #search NPC
            print('找到商人')
            t1=time.time()
            myclick(E[0], E[1]+int(50*reso_x/960), de, mode=0) # click and wait skip icon
            E = (0,0)
            while (time.time()-t1)<waitnpc and E[0]==0:
                E = PixelSearch(730, 393, 745, 417, '0xD3D724', 5) ## check whether actually click it

    myclick(804, 380, de, 950, 23, 960, 33, '0x6B6153', 3, msg='販賣/購買', mode=1, timemax=10) # buy/sell
    myclick(168, 50, ci, 165, 47, 170, 52, '0xFFFFFF', 3, rs_x=960, rs_y=540, msg='販賣', mode=3, timemax=10) # sell
    myclick(280, 495, ci, 35, 95, 40, 100, '0xEEEEEE', 3, rs_x=960, rs_y=540, msg='全部販賣', mode=3, timemax=10) # sell all
    
    E=(0, 0)
    while E[0]==0:
        home_screen()
        map(204, 214, de, 960, 540)
        myclick(677, 70, 7, rs_x=960, rs_y=540, msg='前往壁爐', mode=0) # click fireplace
        E = PixelSearch(520, 320, 530, 330, '0xD4D725', 10)

    confirm_blue(shot=0, ci=ci)
    print('loading')
    waitloading()
    fight(1)

def drink_red(red_num=0, red_percent=0, fly_num=0, fly_percent=0, shot=0):
    blood = checkblood(shot)
    loc = ImgSearch(icon_poison, img[110:145, 0:280,], 0.6)
    print('目前血量: '+str(blood))
    print('目前狀態: '+str(len(loc[0])))
    if len(loc[0])<-1:
        print('中毒!')
        use_item(num=5)
        time.sleep(0.5)
    elif fly_num>0 and blood<fly_percent:
        print('危險!')
        use_item(num=fly_num)
        time.sleep(2)
        t_org = time.time()
        while time.time()-t_org<20:
            map(mx, my)
        map(fx, fy)
        fight(1)
    elif blood<red_percent:
        print('血量少!')
        use_item(num=red_num)


def wait_read(start_time, timemax=60):
    global time_img, img
    
    while time.time()-time_start<timemax: # 60秒內
        if time_start<time_img: # 圖片還沒更新
            print("截圖等待時間: "+str(time_img)-time_start)
            return 0
        
    print("圖片無法更新")    
    while 'kakao' in device.shell('dumpsys input'):
        print('關閉遊戲')
        device.shell('am force-stop com.kakaogames.moonlighttw')
    raise ValueError('畫面卡住: 自動重登')



def checkwater2(ini, shot=1):
    if shot:
        if PixelSearch(935, 475, 945, 480, '0xFFFFFF', 10, 0)[0]==0:  # if on page 2
                myclick(1862, 912, 0, rs_x=1920, rs_y=1080, msg='執行: 切換技能頁', mode=0)
            
    E1 = PixelSearch(744, 459, 751, 463, '0xFFFFFF', 10, shot=0)
    E2 = PixelSearch(744+8, 459, 751+8, 463, '0xFFFFFF', 10, shot=0)
    E3 = PixelSearch(764, 459, 767, 463, '0xFFFFFF', 10, shot=0)
    if E1[0]==0 and E2[0]>0 and E3[0]==0:
        copyfile('screen'+str(adb_num)+'.png', 'temp'+str(adb_num)+'.png')
        return (ini+1)
    else:
        return 0

def checkblood(shot=1):
    t0 = time.time()
    rx = PixelSearch2(79, 13, 197, 17, '0x6E44F3', 0, shot)[0]
    while rx==0:
        rx = PixelSearch2(79, 13, 197, 17, '0x6E44F3', 0, 1)[0]
        if time.time()-t0>3:
            return 1
    # plt.imshow(img[15:35, 131:329,]) # under 1600*900
    output = round( (rx*960/reso_x-79)/(197-79), 2)
    return output


def follow(num, shot=1):
    if num>0:
        E = PixelSearch(180, 85, 190, 235, '0xF3D39D', 3, shot) # search following target
        if E[0]==0:
            if num==1:
                myclick(186, 110, 0.5, rs_x=960, rs_y=540, msg='跟隨隊友 1', mode=0)
            if num==2:
                myclick(186, 160, 0.5, rs_x=960, rs_y=540, msg='跟隨隊友 2', mode=0)
            if num==3:
                myclick(186, 210, 0.5, rs_x=960, rs_y=540, msg='跟隨隊友 3', mode=0)
