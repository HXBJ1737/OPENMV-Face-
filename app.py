import sensor, image, time,screen
import pyb
from pyb import Timer
import os

clock = time.clock()    #声明时钟，用于获取帧速

RED_LED_PIN = 1
BLUE_LED_PIN = 3

count=0
skip=False
def calfun(cb):
    global count
    global skip
    count+=1
    if count>1:
        count=0
        skip=True

tim = Timer(4,freq=1)
tim.callback(calfun)
tim.init(freq=1)


roi_1 = [  (40 , 100 , 100 , 100),     #注册
           (200 , 100 , 100 , 100)    #匹配
           ]

mode = 0      #模式
#number = 1    #已录入人脸的数目

'''
录入人脸函数：
'''
def make_file(n):
    # 指定你想在 SD 卡上创建新文件夹的位置
    path = "/face/s%s"%n  # 这是在根目录下创建 face 文件夹，并在其内部创建 s%s n文件夹

    try:
        # 创建目录
        os.mkdir(path)
        print("Directory created:", path)
    except OSError as e:
        # 如果目录已经存在或者有其他问题，则捕获异常
        print("Failed to create directory:", e)


rootpath = "/face"   #根目录下的face文件夹
def face_register():
    #######
    sensor.reset() # Initialize the camera sensor.
    sensor.set_pixformat(sensor.GRAYSCALE) # or sensor.GRAYSCALE
    #sensor.set_framesize(sensor.B128X128) # or sensor.QQVGA (or others)
    sensor.set_framesize(sensor.QQVGA)
    #sensor.set_windowing((92,112))
    sensor.set_windowing((120,115))
    sensor.skip_frames(10) # Let new settings take affect.

    #屏幕初始化。可写入参数：
    #screen_baudrate SPI频率，默认80，单位Mhz
    #pressure 压力阈值，默认1800，数值越大，需要压力越大
    screen.init()

    #创建用于绘图的画布，并填充白色
    img_drawing_board=sensor.alloc_extra_fb(120,115,sensor.GRAYSCALE)
    img_drawing_board.draw_rectangle(0,0,160,120,fill=True,color=(255,255,255))
    #######


#    global number
#    number +=1
#    make_file(number)
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
    #    sensor.skip_frames(time = 3000) # Give the user time to get ready.等待3s，准备一下表情。

        #红灯灭，蓝灯亮

        pyb.LED(RED_LED_PIN).off()
        pyb.LED(BLUE_LED_PIN).on()
        #保存截取到的图片到SD卡

        img = sensor.snapshot()
        if skip:
            skip=False
            img.save("face/s%s/%s.pgm" % (number, cnt) ) # or "example.bmp" (or others)
            print(cnt)
            cnt -= 1
        pyb.LED(BLUE_LED_PIN).off()

    #    print("Done! Reset the camera to see the saved image.")
        img.b_nor(img_drawing_board)    #将画板画布与感光器图像叠加
        screen.display(img) #显示图像到屏幕，并获取触摸信息。不运行此函数，不会更新触屏信息。

    if cnt == 0:
        pyb.hard_reset()


'''
匹配人脸函数：
'''
Path_Backup = {'path':'','id':0}
num=0
def min(pmin, a, s):
    global num
    if a<pmin:
        pmin=a
        num=s
    return pmin

face_threshold = 10000
def face_identify():
    #######
    sensor.reset() # Initialize the camera sensor.
    sensor.set_pixformat(sensor.GRAYSCALE) # or sensor.GRAYSCALE
    #sensor.set_framesize(sensor.B128X128) # or sensor.QQVGA (or others)
    sensor.set_framesize(sensor.QQVGA)
    #sensor.set_windowing((92,112))
    sensor.set_windowing((120,115))
    sensor.skip_frames(10) # Let new settings take affect.

    #屏幕初始化。可写入参数：
    #screen_baudrate SPI频率，默认80，单位Mhz
    #pressure 压力阈值，默认1800，数值越大，需要压力越大
    screen.init()

    #创建用于绘图的画布，并填充白色
    img_drawing_board=sensor.alloc_extra_fb(120,115,sensor.GRAYSCALE)
    img_drawing_board.draw_rectangle(0,0,160,120,fill=True,color=(255,255,255))

    ######

    sensor.skip_frames(time = 3000) #等待3s
    # 拍摄当前人脸。
    img = sensor.snapshot()
    screen.display(img) #显示图像到屏幕，并获取触摸信息。不运行此函数，不会更新触屏信息。
    #img = image.Image("singtown/%s/1.pgm"%(SUB))
    d0 = img.find_lbp((0, 0, img.width(), img.height()))
    #d0为当前人脸的lbp特征
    img = None
    pmin = 15000
    global num
    global face_threshold
    NUM_SUBJECTS_IMGS = 20    #就是face_register中cnt的值

    dir_lists = os.listdir(rootpath)  # 路径下文件夹
    dir_num = len(dir_lists)          # 文件夹数量

    for s in range(1, dir_num+1):
        dist = 0
        for i in range(1, NUM_SUBJECTS_IMGS+1):
            img = image.Image("face/s%d/%d.pgm"%(s, i))
            print("face/s%d/%d.pgm"%(s, i))
            d1 = img.find_lbp((0, 0, img.width(), img.height()))
            #d1为第s文件夹中的第i张图片的lbp特征
            dist += image.match_descriptor(d0, d1)#计算d0 d1即样本图像与被检测人脸的特征差异度。
        print("Average dist for subject %d: %d"%(s, dist/NUM_SUBJECTS_IMGS))
        pmin = min(pmin, dist/NUM_SUBJECTS_IMGS, s)#特征差异度越小，被检测人脸与此样本更相似更匹配。
        print(pmin)

    if pmin <= face_threshold:
        print(num)
        pyb.LED(BLUE_LED_PIN).on()
        #img.draw_string(70,80,"result:%s"%num,scale=(3),color=(255,0,0),mono_space=False)
    else:
        pyb.LED(RED_LED_PIN).on()

    pyb.delay(5000)
    if num:
        pyb.hard_reset()



def main():
    #######
    sensor.reset()
    sensor.set_pixformat(sensor.RGB565)
    sensor.set_framesize(sensor.QVGA)

    clock = time.clock()    #声明时钟，用于获取帧速

    #屏幕初始化。可写入参数：
    #screen_baudrate SPI频率，默认80，单位Mhz
    #pressure 压力阈值，默认1800，数值越大，需要压力越大
    screen.init()

    #创建用于绘图的画布，并填充白色
    img_drawing_board=sensor.alloc_extra_fb(320,240,sensor.RGB565)
    img_drawing_board.draw_rectangle(0,0,320,240,fill=True,color=(255,255,255))

    ######

    global mode

    fps=0   #帧速变量

#    width, height = sensor.width(), sensor.height()
#    print(width, height)
#    img = image.Image(width, height, sensor.RGB565)   #内存爆炸了


    img = sensor.snapshot()

    while True:
        clock.tick()    #时钟记录点，用于获取帧速

        for m,r in enumerate(roi_1):

            img.draw_rectangle(r[0:4], color=(255, 0, 0),thickness=20)

            if screen.press:    #如果触屏被按下

                img_drawing_board.draw_cross(screen.x,screen.y,color=(0,0,0))

                if screen.x > r[0] and screen.x < (r[0]+r[2]) :
                    if screen.y > r[1] and screen.y < (r[1]+r[3]) :
                        print(m)
                        if m == 0:
                            #print(screen.x,screen.y)
                            print("face_register")
                            face_register()
                            break
                        elif m == 1:
                            #print(screen.x,screen.y)
                            print("face_identify")
                            face_identify()
                            break

        img.b_nor(img_drawing_board)    #将画板画布与感光器图像叠加
        img.draw_string(10,40,'Face Register',scale=(3),color=(255,0,0),mono_space=False)
        img.draw_string(180,40,'Face Identify',scale=(3),color=(255,0,0),mono_space=False)
        screen.display(img) #显示图像到屏幕，并获取触摸信息。不运行此函数，不会更新触屏信息。
        fps=clock.fps() #获取帧速




main()
