'''
Aur:恒星不见
@copyright 2024
date:2024.08.14
'''
#-----------Import-----------------------
import sensor, image, time,screen,gc
import pyb
from pyb import Timer
import os

#--------------Var-----------------------
roi_1 = [  (40 , 100 , 100 , 100),     #注册
           (200 , 100 , 100 , 100)    #匹配

           ]


rootpath = "/face"   #根目录下的face文件夹
RED_LED_PIN = 1
BLUE_LED_PIN = 3

count=0
skip=False

Path_Backup = {'path':'','id':0}
num=0
sensor.reset()                      # Reset and initialize the sensor.
sensor.set_pixformat(sensor.RGB565) # Set pixel format to RGB565 (or GRAYSCALE)
sensor.set_framesize(sensor.QVGA)   # Set frame size to QVGA (320x240)
sensor.skip_frames(time = 2000)     # Wait for settings take effect.
img = sensor.snapshot()
coyp = img.copy(0.5,0.5)#scls
img_drawing_board=sensor.alloc_extra_fb(320,240,sensor.RGB565)
#-------------Function-------------------
def calfun(cb):
    global count
    global skip
    count+=1
    if count>1:
        count=0
        skip=True

def face_register():
    global img,coyp,img_drawing_board
    img_drawing_board.draw_rectangle(0,0,320,240,fill=True,color=(0,0,0))

    dir_lists = os.listdir(rootpath)  # 路径下文件夹
    dir_num = len(dir_lists)          # 文件夹数量
    number = int(dir_num)+1
    new_dir = ("%s/s%d") % (rootpath, number)
    os.mkdir(new_dir)                 # 创建文件夹

    global skip
    cnt = 20      # 就是NUM_SUBJECTS_IMGS的数量
    while(cnt):
        #红灯亮
        pyb.LED(RED_LED_PIN).on()
        pyb.LED(RED_LED_PIN).off()
        pyb.LED(BLUE_LED_PIN).on()
        img = sensor.snapshot()
        img_drawing_board.draw_rectangle(0,0,320,240,fill=True,color=(0,0,0))
        img_drawing_board.draw_string(10,10,'count:'+str(cnt),scale=(2),color=(0,255,0),mono_space=False)
        img_drawing_board.b_or(img)
        screen.display(img_drawing_board)
        if skip:
            skip=False
            img.to_grayscale()
            coyp = img.copy(0.4,0.4)
            print(cnt)
            coyp.save("face/s%s/%s.pgm" % (number, cnt) ) # or "example.bmp" (or others)
            cnt -= 1
        pyb.LED(BLUE_LED_PIN).off()
          #将画板画布与感光器图像叠加

    if cnt == 0:
        pyb.delay(2000)
        pyb.hard_reset()




def min(pmin, a, s):
    global num
    if a<pmin:
        pmin=a
        num=s
    return pmin

face_threshold = 10000
def face_identify():
    global img,coyp,img_drawing_board
    img_drawing_board.draw_rectangle(0,0,320,240,fill=True,color=(0,0,0))
    # 拍摄当前人脸。
    img = sensor.snapshot()
    screen.display(img)
    img.to_grayscale()
    coyp = img.copy(0.4,0.4)
    coyp1=img.copy(1,1)
    #显示图像到屏幕，并获取触摸信息。不运行此函数，不会更新触屏信息。
    d0 = coyp.find_lbp((0, 0, coyp.width(), coyp.height()))
    #d0为当前人脸的lbp特征
    img1 = None
    pmin = 15000
    global num
    global face_threshold
    NUM_SUBJECTS_IMGS = 20    #就是face_register中cnt的值

    dir_lists = os.listdir(rootpath)  # 路径下文件夹
    dir_num = len(dir_lists)          # 文件夹数量

    for s in range(1, dir_num+1):
        dist = 0
        for i in range(1, NUM_SUBJECTS_IMGS+1):
            img1 = image.Image("face/s%d/%d.pgm"%(s, i))
#            print("face/s%d/%d.pgm"%(s, i))
            d1 = img1.find_lbp((0, 0, img1.width(), img1.height()))
            dist += image.match_descriptor(d0, d1)#计算d0 d1即样本图像与被检测人脸的特征差异度。
#        print("Average dist for subject %d: %d"%(s, dist/NUM_SUBJECTS_IMGS))
        pmin = min(pmin, dist/NUM_SUBJECTS_IMGS, s)#特征差异度越小，被检测人脸与此样本更相似更匹配。
#        print(pmin)

    if pmin <= face_threshold:
#        print(num)
        pyb.LED(BLUE_LED_PIN).on()
        #img.draw_string(70,80,"result:%s"%num,scale=(3),color=(255,0,0),mono_space=False)
    else:
        pyb.LED(RED_LED_PIN).on()
    img = sensor.snapshot()
    img_drawing_board.draw_string(10,10,'num:'+str(num),scale=(2),color=(0,255,0),mono_space=False)
    img_drawing_board.b_or(img)
    screen.display(img_drawing_board)
    while True:
        if screen.press:
            print(screen.x,screen.y)
            screen.x,screen.y=0,0
            pyb.delay(200)
            return
        screen.display(img_drawing_board)




def exp():
    pass
#----------Timer-------------------------
tim = Timer(4,freq=2)
tim.callback(calfun)
tim.init(freq=2)
#-----------------------------------------
clock = time.clock()    #声明时钟，用于获取帧速

i=0
screen.init()
def main():
    global img,coyp,img_drawing_board


    img_drawing_board.draw_rectangle(0,0,320,240,fill=True,color=(0,0,0))

    while(True):
        clock.tick()    #时钟记录点，用于获取帧速
        img = sensor.snapshot()
#        gray_img=img.to_grayscale()
        img_drawing_board.draw_rectangle(0,0,320,240,fill=True,color=(0,0,0))

        for m,r in enumerate(roi_1):
            img_drawing_board.draw_rectangle(r[0:4], color=(255, 0, 0),thickness=2)
            img_drawing_board.draw_string(10,40,'Face Register',scale=(3),color=(255,0,0),mono_space=False)
            img_drawing_board.draw_string(180,40,'Face Identify',scale=(3),color=(255,0,0),mono_space=False)
        img_drawing_board.b_or(img)    #将画板画布与感光器图像叠加
        if screen.press:
            print(screen.x,screen.y)
            for m,r in enumerate(roi_1):
                if screen.x > r[0] and screen.x < (r[0]+r[2]) :
                    if screen.y > r[1] and screen.y < (r[1]+r[3]) :
                        if m == 0:
                            print("face_register")
                            gc.collect()
                            face_register()
                        elif m == 1:
                            gc.collect()
                            face_identify()
        screen.display(img_drawing_board)
        img.to_grayscale()
        coyp = img.copy(0.4,0.4)#scls








if __name__=="__main__":
    main()
