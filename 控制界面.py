'''
OpenMV电阻式触摸屏扩展板 图像预览与绘图示例程序
20220317

QQ群 245234784
taobao shop111000005.taobao.com
bilibili @程欢欢的智能控制集
'''
import sensor, image, time,screen

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

roi_1 = [  (40 , 100 , 100 , 100),     #注册
           (200 , 100 , 100 , 100)    #匹配
           ]

fps=0   #帧速变量

img = sensor.snapshot() #获取感光器画面

while True:
    clock.tick()    #时钟记录点，用于获取帧速


    press_x = 0
    press_y = 0

    for m,r in enumerate(roi_1):

        img.draw_rectangle(r[0:4], color=(255, 0, 0))

        if screen.press:    #如果触屏被按下

            img_drawing_board.draw_cross(screen.x,screen.y,color=(0,0,0))

            if screen.x > r[0] and screen.x < (r[0]+r[2]) :
                if screen.y > r[1] and screen.y < (r[1]+r[3]) :
                    print(m)
                    if m == 0:
                        #print(screen.x,screen.y)
                        print("face_register")
                        break
                    elif m == 1:
                        #print(screen.x,screen.y)
                        print("face_identify")
                        break

    img.b_nor(img_drawing_board)    #将画板画布与感光器图像叠加
    img.draw_string(10,40,'Face Register',scale=(3),color=(255,0,0),mono_space=False)
    img.draw_string(180,40,'Face Identify',scale=(3),color=(255,0,0),mono_space=False)
    screen.display(img) #显示图像到屏幕，并获取触摸信息。不运行此函数，不会更新触屏信息。
    fps=clock.fps() #获取帧速




