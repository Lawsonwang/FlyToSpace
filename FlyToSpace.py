import pygame
import os
from math import *
from memory_pic import *

from base64 import *


def get_pic(pic_code, pic_name):
    image = open(pic_name, 'wb')
    image.write(b64decode(pic_code))
    image.close()


os.mkdir('_')
get_pic(earthfromnorthpole_png, '_\\earthfromnorthpole.png')
get_pic(fire_png, '_\\fire.png')
get_pic(ship_png, '_\\ship.png')
get_pic(icon_ico, '_\\icon.ico')
get_pic(moon_png, '_\\moon.png')


def main():
    def trans_x2u(x):
        return int((x - x0) * Kshow + u0)

    def trans_y2v(y):
        return int(-(y - y0) * Kshow + v0)

    def trans_xy2uv(x, y):
        return int((x - x0) * Kshow + u0), int(-(y - y0) * Kshow + v0)

    def is_in_rect(pos, rect):  # 是否在矩形区域内
        x, y = pos
        rx, ry, rw, rh = rect
        if (rx <= x <= rx + rw) and (ry <= y <= ry + rh):
            return True
        return False

    def calc_Kshow_x0_y0(zoom_type):
        #global Kshow
        #global x0
        #global y0
        if zoom_type == 0:  # Earth & spaceship
            Kshow = height / 2.0 / max(Re, Dse) / Cshow
            x0 = 0
            y0 = 0
        elif zoom_type == 1:  # Earth & spaceship & MOON
            Kshow = height / 2.0 / max(Re, max(Dse, Dem)) / Cshow
            x0 = 0
            y0 = 0
        elif zoom_type == 2:    # moon & spaceship
            Kshow = height / 2.0 / max(Rm, Dsm) / Cshow
            x0 = Xm
            y0 = Ym
        return (Kshow,x0,y0)

    #################################### var.py ####################################

    dt = base_dt = 3

    # 地球
    Re = 6371.4e3
    Me = 5.972e24
    Xe = 0
    Ye = 0

    # 月球
    Rm = 1731.1e3
    Mm = 7.36e22
    Vm_0 = 1.023e3  # m/s
    Vmx = 0
    Vmy = Vm_0
    Sta_m = 0
    Dem = 384400e3 * 0.99  # Re + 29000e3
    Xm = Dem
    Ym = 0

    # 飞船
    Rs = 300e3
    Ms = 1000
    Vsx = 0
    Vsy = 0  # 7.6e3 # 7.6
    Xs =  Re#+300e3#200e3
    ##Vsy=8e3
    ##Xs=Re+300e3
    Ys = 0

    ##Vsy = 3.0746311898429766e3  #地球同步轨道参数
    ##Xs = 42163.772928313745e3  #

##    Xs = Xm + Rm * 1.5
##    Ys = 0

    Dse = 0
    Dsm = 0

    # 万有引力常数
    G = 6.67430e-11

    Fsex = 0
    Fsmx = 0
    Fsey = 0
    Fsmy = 0
    Fsx = 0
    Fsy = 0

    ###############################################################################

    pygame.init()
    width = 1000  # 800
    height = 1000  # 800
    size = [width, height]
    Cshow = 1.2
    Kshow = height / 2.0 / Re / Cshow
    Zoom_Type = 0
    Kfire = 10000
    u0 = width / 2
    v0 = height / 2
    x0 = 0
    y0 = 0
    Erotate = 0
    SecondPerDegree = 240  # 8
    Edrotate = dt / SecondPerDegree
    Sscale = 0.2
    Srotate = -90
    Fscale = 0.1
    Sdrotate = 1  # d_r

    Fhigh = 0
    Fdhigh = 0.05
    FhighMax = 1
    total_time = 0

    historytemp = 0
    historyid = 0
    historyN = 500
    history_s_XY = [(0, 0)] * historyN
    history_m_XY = [(0, 0)] * historyN

    screen = pygame.display.set_mode(size)
    pygame.display.set_caption("“飞向太空”——万有引力仿真程序")
    icon = pygame.image.load("_\\icon.ico").convert_alpha()
    pygame.display.set_icon(icon)
    keepGoing = True
    fonts = pygame.font.SysFont('consolas', 20)
    earthpic0 = pygame.image.load("_\\earthfromnorthpole.png").convert_alpha()
    earthpic = earthpic0
    earthRect = earthpic.get_rect()

    moonpic0 = pygame.image.load("_\\moon.png").convert_alpha()
    moonpic = moonpic0
    moonRect = moonpic.get_rect()

    ship0 = pygame.image.load("_\\ship.png").convert_alpha()
    ship0 = pygame.transform.smoothscale(ship0, (
        int(ship0.get_rect().width * Sscale), int(ship0.get_rect().height * Sscale)))  # Unrotate Ship
    fire0 = pygame.image.load("_\\fire.png").convert_alpha()
    fire0 = pygame.transform.smoothscale(fire0, (
        int(fire0.get_rect().width * Fscale), int(fire0.get_rect().height * Fscale)))  # Unrotate Fire
    ship = ship0
    shipRect = ship0.get_rect()
    fire = fire1 = fire0  # fire1: Scaled but not rotate
    fireRect = fire0.get_rect()
    IsFireAllowed = True
    IsTurnAllowed = True
    IsOnEarth = True
    IsOnMoon = False
    IsFireReverse = False
    picx = 0
    picy = 0
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    RED = (255, 0, 0)
    EBLUE = (14, 80, 164)
    timer = pygame.time.Clock()
    while keepGoing:  # Game loop
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                keepGoing = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    keepGoing = False
                elif event.key == pygame.K_r:  ## 'R'
                    if IsFireAllowed and (not IsOnEarth) and (Fhigh == 0):
                        IsTurnAllowed = not IsTurnAllowed
                elif event.key == pygame.K_z:  ## 'Z'
                    Zoom_Type = (Zoom_Type + 1) % 3
        ##        if event.type == pygame.MOUSEBUTTONDOWN:
        ##            if is_in_rect(event.pos,[width-140,height-40,135,35]):
        ##                file = '火箭发射.mp4'
        ##                os.system('%ProgramFiles(x86)%\Windows Media Player\wmplayer.exe '+ file)

        if IsOnEarth:
            IsTurnAllowed = True

        keys = pygame.key.get_pressed()
        if keys[pygame.K_1]:
            dt = base_dt
            IsFireAllowed = True
        elif keys[pygame.K_2]:
            dt = base_dt * 2
            IsFireAllowed = False
        ##        IsTurnAllowed=False
        elif keys[pygame.K_3]:
            dt = base_dt * 4
            IsFireAllowed = False
        ##        IsTurnAllowed=False
        elif keys[pygame.K_4]:
            dt = base_dt * 8
            IsFireAllowed = False
        ##        IsTurnAllowed=False
        elif keys[pygame.K_5]:
            dt = base_dt * 16
            IsFireAllowed = False
        ##        IsTurnAllowed=False
        elif keys[pygame.K_6]:
            dt = base_dt * 32
            IsFireAllowed = False
        ##        IsTurnAllowed=False
        elif keys[pygame.K_7]:
            dt = base_dt * 64
            IsFireAllowed = False
        ##        IsTurnAllowed=False
        elif keys[pygame.K_8]:
            dt = base_dt * 128
            IsFireAllowed = False
        ##        IsTurnAllowed=False
        elif keys[pygame.K_9]:
            dt = base_dt * 256
            IsFireAllowed = False
        ##        IsTurnAllowed=False

        if (not IsFireAllowed) and (not IsOnEarth):
            IsTurnAllowed = False

        if keys[pygame.K_LEFT]:
            Srotate += Sdrotate
        if keys[pygame.K_RIGHT]:
            Srotate -= Sdrotate
        ##        ship=pygame.transform.rotate(ship0, Srotate)
        ##        if Fhigh > 1e-5:
        ##            fire=pygame.transform.rotate(fire1, Srotate)
        if keys[pygame.K_DOWN]:
            Fhigh += Fdhigh
            if Fhigh > FhighMax:
                Fhigh = FhighMax
            IsFireReverse = True
        elif not keys[pygame.K_UP]:
            Fhigh = 0
            IsFireReverse = False

        if keys[pygame.K_UP]:
            Fhigh += Fdhigh
            if Fhigh > FhighMax:
                Fhigh = FhighMax
        elif not keys[pygame.K_DOWN]:
            Fhigh = 0

        Dse = sqrt((Xs - Xe) * (Xs - Xe) + (Ys - Ye) * (Ys - Ye))
        Dsm = sqrt((Xs - Xm) * (Xs - Xm) + (Ys - Ym) * (Ys - Ym))
        Fse = G * Me * Ms / Dse / Dse
        Fsex = -Fse * (Xs - Xe) / Dse
        Fsey = -Fse * (Ys - Ye) / Dse
        Fsm = G * Mm * Ms / Dsm / Dsm
        Fsmx = -Fsm * (Xs - Xm) / Dsm
        Fsmy = -Fsm * (Ys - Ym) / Dsm
        if IsFireAllowed:
            Ffire = Kfire * Fhigh
        else:
            Ffire = 0
        if IsFireReverse:
            Ffire = -Ffire
        Ffirex = -Ffire * sin(Srotate / 180 * pi)
        Ffirey = Ffire * cos(Srotate / 180 * pi)

        Fsx = Fsex + Fsmx + Ffirex
        Fsy = Fsey + Fsmy + Ffirey

        Vsx += dt * Fsx / Ms
        Vsy += dt * Fsy / Ms
        Xs += Vsx * dt
        Ys += Vsy * dt

        # 月球运动
        Sta_m += Vm_0 / Dem * dt
        if Sta_m > (2*pi):
            Sta_m -= (2*pi)
        Xm = Dem * cos(Sta_m)
        Ym = Dem * sin(Sta_m)
        Vmx = - Vm_0 * sin(Sta_m)
        Vmy = Vm_0 * cos(Sta_m)
        (Kshow, x0, y0) = calc_Kshow_x0_y0(Zoom_Type)

        # 地球自转
        Edrotate = dt / SecondPerDegree
        Erotate += Edrotate
        Erotate %= 360

        if sqrt((Xs - Xe) * (Xs - Xe) + (Ys - Ye) * (Ys - Ye)) <= Re:
            IsOnEarth = True
            Xs -= Vsx * dt
            Ys -= Vsy * dt
            Vsx, Vsy = 0, 0
            Xt = Xs - Xe
            Yt = Ys - Ye
            theta = asin(Yt / Dse)
            if Xt <= 0:
                theta = pi - theta
            theta += Edrotate * (pi / 180)
            Vsx = -(pi / SecondPerDegree / 180) * Re * sin(theta)
            Vsy = (pi / SecondPerDegree / 180) * Re * cos(theta)
            Ys = Ye + Re * sin(theta)
            Xs = Xe + Re * cos(theta)
            Srotate += Edrotate
        else:
            IsOnEarth = False
        
        if sqrt((Xs - Xm) * (Xs - Xm) + (Ys - Ym) * (Ys - Ym)) <= Rm:
            Xs -= Vsx * dt
            Ys -= Vsy * dt
            if not IsOnMoon:
                XXms = Xs - Xm
                YYms = Ys - Ym
            Vsx, Vsy = Vmx, Vmy
            Xs = Xm + XXms
            Ys = Ym + YYms
            IsOnMoon = True
            # Vsx = Vsy = Vs = 0
##            Xt = Xs - Xm
##            Yt = Ys - Ym
##            theta = asin(Yt / Dse)
##            if Xt <= 0:
##                theta = pi - theta
##            theta += Edrotate * (pi / 180)
##            Vsx = -(pi / SecondPerDegree / 180) * Re * sin(theta)
##            Vsy = (pi / SecondPerDegree / 180) * Re * cos(theta)
##            Ys = Ye + Re * sin(theta)
##            Xs = Xe + Re * cos(theta)
##            Srotate += Edrotate
        else:
            IsOnMoon = False


        if ((not IsFireAllowed) and (not IsOnEarth)) or (IsFireAllowed and (not IsTurnAllowed) and (Fhigh == 0)):
            if Zoom_Type <= 1:
                Vs = sqrt(Vsx * Vsx + Vsy * Vsy) # follow the direction
                theta = acos(Vsy / Vs) / pi * 180
                if Vsx > 0:
                    theta = 360 - theta
            elif Zoom_Type == 2:
                Vs_m = sqrt((Vsx - Vmx) * (Vsx - Vmx) + (Vsy - Vmy) * (Vsy - Vmy))  # follow the direction
                if Vs_m != 0:
                    theta = acos((Vsy-Vmy) / Vs_m) / pi * 180
                if (Vsx - Vmx) > 0:
                    theta = 360 - theta
            Srotate = theta

        # 总时间
        total_time += dt
        temp_time = total_time
        days = temp_time // (24 * 3600)
        temp_time %= (24 * 3600)
        hours = temp_time // (3600)
        temp_time %= (3600)
        minutes = temp_time // (60)

        historytemp += dt // base_dt
        if historytemp >= 256:
            historytemp = 0;

        if (historytemp % 64 == 0):
            history_s_XY[historyid] = (Xs, Ys)
            history_m_XY[historyid] = (Xm, Ym)
            historyid += 1;
            if historyid >= historyN:
                historyid = 0

        ship = pygame.transform.rotate(ship0, Srotate)
        fire1 = pygame.transform.smoothscale(fire0, (fire0.get_rect().width, int(fire0.get_rect().height * Fhigh)))
        if Fhigh > 1e-5:
            fire = pygame.transform.rotate(fire1, Srotate)
        else:
            fire = fire1

        if IsFireReverse:
            ship = pygame.transform.rotate(ship, 180)
            fire = pygame.transform.rotate(fire, 180)

        earthpic = pygame.transform.smoothscale(earthpic0, (int(Re * Kshow * 2), int(Re * Kshow * 2)))
        earthpic = pygame.transform.rotate(earthpic, Erotate)

        moonpic = pygame.transform.smoothscale(moonpic0, (int(Rm * Kshow * 2), int(Rm * Kshow * 2)))
        ##    moonpic=pygame.transform.rotate(moonpic, Erotate)

        screen.fill(BLACK)

        earthRect = earthpic.get_rect()
        earthRect.center = trans_xy2uv(0, 0)
        screen.blit(earthpic, earthRect)
        moonRect = moonpic.get_rect()
        moonRect.center = trans_xy2uv(Xm, Ym)
        screen.blit(moonpic, moonRect)

        ##    pygame.draw.circle(screen,WHITE,trans_xy2uv(Xm,Ym),int(Rm*Kshow),0)
        ##    pygame.draw.circle(screen,EBLUE,trans_xy2uv(0,0),int(Re*Kshow),0)
        ##    pygame.draw.circle(screen,RED,trans_xy2uv(Xs,Ys),int(Rs*Kshow),0)
        txt = fonts.render("Speed = " + str(int(sqrt(Vsx * Vsx + Vsy * Vsy))) + " m/s", True, WHITE)
        screen.blit(txt, (10, 10))
        txt = fonts.render("Distance to Earth = " + str(int((Dse - Re) / 1000)) + " km", True, WHITE)
        screen.blit(txt, (10, 40))
        txt = fonts.render("PlaySpeed X" + str(int(dt // base_dt)), True, WHITE)
        txtRect = txt.get_rect()
        txtRect.top = 10
        # txtRect.right=width-10
        txtRect.left = width - 164
        # print(txtRect.left)
        screen.blit(txt, txtRect)  # (600, 10)
        Shours = "%02d" % int(hours)
        Sminutes = "%02d" % int(minutes)
        txt = fonts.render("Total Time: " + str(int(days)) + "Days " + Shours + "Hours " + Sminutes + "Minutes", True,
                           WHITE)
        txtRect = txt.get_rect()
        txtRect.top = height - 20
        txtRect.centerx = width // 2
        screen.blit(txt, txtRect)  # (200, height-20)
        SIFA = "True" if IsTurnAllowed else "False"
        txt = fonts.render("Is Turn Allowed: " + SIFA, True, WHITE)
        txtRect = txt.get_rect()
        txtRect.top = 40
        ##    txtRect.right=width-10
        ##    print(txtRect.left)
        txtRect.left = width - 250;
        screen.blit(txt, txtRect)
        ##    shipRect.left,shipRect.top=(trans_x2u(Xs)-shipRect.width//2,trans_y2v(Ys)-shipRect.height//2)
        shipRect.center = (trans_x2u(Xs), trans_y2v(Ys))
        newShipRect = ship.get_rect(center=shipRect.center)

        fireRect.center = (trans_x2u(Xs), trans_y2v(Ys))
        newFireRect = fire.get_rect(center=fireRect.center)

        if IsFireAllowed:
            screen.blit(fire, newFireRect)
        screen.blit(ship, newShipRect)

        ##    screen.blit()
        # pygame.draw.rect(screen, [0,0,255],[width-140,height-40,135,35],1)
        # txt=fonts.render("Demo Show", True, WHITE)
        # screen.blit(txt, (width-120,height-30))
        # for (x, y) in history_s_XY:
        #     if x > 100e3 or y > 100e3:
        #         if Zoom_Type==0:
        #             pygame.draw.rect(screen, [0, 0, 255], [trans_x2u(x), trans_y2v(y), 3, 3], 1)  # 画1*1的矩形，线宽为1，这里不能是0，因为1*1无空白区域。
        #         elif Zoom_Type==1:
        #             pygame.draw.rect(screen, [0, 0, 255], [trans_x2u(x-), trans_y2v(y), 3, 3], 1)
        for index in range(len(history_s_XY)):
            x = history_s_XY[index][0]
            y = history_s_XY[index][1]
            xm = history_m_XY[index][0]
            ym = history_m_XY[index][1]
            if abs(x) > 100e3 or abs(y) > 100e3:
                if Zoom_Type<=1:
                    pygame.draw.rect(screen, [0, 0, 255], [trans_x2u(x), trans_y2v(y), 3, 3], 1)  # 画1*1的矩形，线宽为1，这里不能是0，因为1*1无空白区域。
                elif Zoom_Type==2:
                    pygame.draw.rect(screen, [0, 0, 255], [trans_x2u(x + (Xm - xm)), trans_y2v(y + (Ym - ym)), 3, 3], 1)

        pygame.display.update()
        timer.tick(60)
    pygame.quit()  # Exit


if __name__ == "__main__":
    try:
        main()
    ##    except SystemExit:
    ##        pass
    ##    except:
    finally:
        #traceback.print_exc()
        os.remove('_\\earthfromnorthpole.png')
        os.remove('_\\fire.png')
        os.remove('_\\ship.png')
        os.remove('_\\icon.ico')
        os.remove('_\\moon.png')
        os.rmdir('_')
        pygame.quit()
