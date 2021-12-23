import win32gui, win32con, win32ui, win32api
from PIL import Image
import cv2
import numpy as np
import time
from numpy import frombuffer, uint8
from ctypes import windll
from pywinauto import Application


def hex_to_rgb(value):
    value = value.lstrip('#')
    lv = len(value)
    origin = tuple(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))
    return origin[::-1]
def rgb_to_hex(rgb):
    return '0x%02x%02x%02x' % rgb
def win_active():
    return win32gui.GetWindowText (win32gui.GetForegroundWindow())
def getIdleTime():
    return (win32api.GetTickCount() - win32api.GetLastInputInfo()) / 1000.0

class Game_obj:
    def __init__(self, title, hwnd):
        self.title = title
        self.hwnd = hwnd
        self.hwndEX = hwnd
        self.win = Application().connect(handle=hwnd).window()

    ### Eyes
    def getWindowRect(self):
            x1, y1, x2, y2 = win32gui.GetWindowRect(self.hwndEX)
            x1, y1, x2, y2 = x1+8, y1+32, x2-9, y2-9
            w, h = x2 - x1, y2 - y1            
            return x1, y1, w, h
    
    def screenshot(self):
        try:
            while win32gui.IsIconic(self.hwnd):
                win32gui.ShowWindow(self.hwnd, 4)
            hwndDC = win32gui.GetWindowDC(self.hwndEX)
            mfcDC  = win32ui.CreateDCFromHandle(hwndDC)
            saveDC = mfcDC.CreateCompatibleDC()
            saveBitMap = win32ui.CreateBitmap()
            _, _, w, h = self.getWindowRect()            
            saveBitMap.CreateCompatibleBitmap(mfcDC, w, h)
            saveDC.SelectObject(saveBitMap)
            # Change the line below depending on whether you want the whole window or just the client area. 
            result = windll.user32.PrintWindow(hwnd, saveDC.GetSafeHdc(), 1) #result = windll.user32.PrintWindow(hwnd, saveDC.GetSafeHdc(), 0)
            bmpinfo = saveBitMap.GetInfo()
            bmpstr = saveBitMap.GetBitmapBits(True)

            img = Image.frombuffer('RGB', (bmpinfo['bmWidth'], bmpinfo['bmHeight']), bmpstr, 'raw', 'BGRX', 0, 1)

            win32gui.DeleteObject(saveBitMap.GetHandle())
            saveDC.DeleteDC()
            mfcDC.DeleteDC()
            win32gui.ReleaseDC(hwnd, hwndDC)            
            return np.asarray(img)        
        except Exception as e:
            print(e)
            print('Error: winkey-screenshot2')
    def PixelExist(self, c_x1, c_y1, c_x2, c_y2, pixel, tol=5):
        try:
            _, _, w, h = self.getWindowRect()
            rgb = hex_to_rgb('#'+pixel[2:8])
            img = self.screenshot()
            img_sub = img[int(c_y1*h):int(c_y2*h)+1, int(c_x1*w):int(c_x2*w)+1,]
            return (np.max(abs(img_sub-rgb),axis=2)<tol).any()
            
        except Exception as e:
            print(e)
            print('Error: winkey-PixelExist')
    
    ### Hands    
    def send(self, key, delay=1, msg=''):
        if win_active()==self.title and getIdleTime()<20:
            print('正在遊玩')
            time.sleep(10)
            return
        if len(msg)>0:
            print(msg)
        self.win.send_keystrokes(key)
        time.sleep(delay)

    def click(self, x, y, delay=1, msg=''):
        if win_active()==self.title and getIdleTime()<20:
            print('正在遊玩')
            time.sleep(10)
            return
        if len(msg)>0:
            print(msg)
        _, _, w, h = self.getWindowRect()
        x, y = int(x*w), int(y*h)
        old_pos = win32gui.GetCursorPos()
        ok = windll.user32.BlockInput(True) #block input
        win32api.SetCursorPos(win32gui.ClientToScreen(self.hwnd, (x,y)))    
        win32gui.SendMessage(hwnd, win32con.WM_ACTIVATE, win32con.WA_ACTIVE, 0)
        win32api.SendMessage(hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, 0)
        win32api.SendMessage(hwnd, win32con.WM_LBUTTONUP, win32con.MK_LBUTTON, 0)
        time.sleep(0.01)    
        win32api.SetCursorPos(old_pos)
        ok = windll.user32.BlockInput(False) #enable input
        time.sleep(delay)
    ### functions
    def getPosition(self):
        x0, y0 = win32gui.GetCursorPos()
        x1, y1, w, h = self.getWindowRect()        
        return( (x0-x1)/w, (y0-y1)/h)
    
    def decompose(self, delay=1 ):
        self.click(930/960, 30/540, delay, msg='執行功能: 裝備分解')
        self.click(600/960, 100/540, delay)
        self.click(780/960, 80/540, delay)
        while not self.PixelExist(230/960, 158/540, 230/960, 158/540, '0x5B5B5B', 5):
            self.click(500/960, 493/540, delay)
        self.send("{ESC}", delay)
        
    def sell(self, delay=1):
        self.click(1461/1600, 46/900, delay, msg='執行功能: 呼叫商店')
        if not self.PixelExist(0.8923694779116466, 0.7510729613733905,0.8923694779116466, 0.7510729613733905, "0xD3D727", 5):
            print("無法呼叫商店")
            self.send("{ESC}", delay)
            return 0
        self.click(1497/1600, 686/900, delay)
        self.click(1000/1600, 550/900, delay)
        
        # sell 
        self.click(168/960, 50/540, delay)
        self.click(280/960, 495/540, delay)
        self.send("{ESC}", delay)
    def storage(self, delay=1):
        self.click(930/960, 30/540, delay, msg='執行功能: 夥伴跑腿')
        self.click(600/960, 260/540, delay)
        if not self.PixelExist(0.35903614457831323, 0.9227467811158798,0.35903614457831323, 0.9227467811158798, "0x6B6152", 5):
            print("無法跑腿")
            self.send("{ESC}", delay)
            return 0        
        self.click(300/960, 500/540, delay)
        self.click(580/960, 325/540, delay)

        # save items
        self.click(800/960, 500/540, 0.2)
        self.click(900/960, 500/540, 0.2)
        self.send("{ESC}", delay)        
    def switch_twice(self, delay=2):
        self.send("{TAB}", delay, msg='切換技能頁')
        self.send("{TAB}", delay, msg='切換技能頁')
    def checkweight(self):
        return self.PixelExist(892/960, 37/540, 892/960, 39/540, "0xECA647", 5) # blue bar
    def checkdead(self):
        E1 = self.PixelExist(0.5, 0.6, 0.5, 0.6, '0xD4D725', 5) # search middle blue
        E2 = self.PixelExist(0.5, 0.6666, 0.5, 0.66666, '0x6B6152', 5) # search middle gray
        return (E1 and E2)
    ###### debugging
    def check_WindowRect(self, vertex = 1):
        rect = self.getWindowRect()
        if vertex:
            win32api.SetCursorPos((rect[0],rect[1]))
        else:
            win32api.SetCursorPos((rect[0]+rect[2],rect[1]+rect[3]))
            
title = "Moonlight_Taiwan"
hwnd = win32gui.FindWindow(None, title)
Game = Game_obj(title, hwnd)

while True:
    if Game.checkdead():
        Game.click(475/960, 270/540, 1, msg='自動復活')
        Game.click(0.28032128514056226, 0.9184549356223176, 1, msg='開始戰鬥')
    print(Game.checkweight())
    if Game.checkweight():
        Game.sell()
    if Game.checkweight():
        Game.decompose()
    if Game.checkweight():
        Game.storage()        
    Game.switch_twice(2)
