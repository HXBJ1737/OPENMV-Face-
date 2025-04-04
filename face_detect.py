# 人脸识别例程
#
# 这个例子展示了OpenMV Cam的内置人脸检测功能。
#
# 人脸检测通过在图像上使用Haar Cascade特征检测器来工作。 haar级联是
# 一系列简单的区域对比检查。 对于内置的前表面探测器，有25个阶段的检查，
# 每个阶段有数百个检查一块。 Haar Cascades运行速度很快，因为只有在
# 以前的阶段过去后才会评估后期阶段。 此外，您的OpenMV使用称为
# 整体图像的数据结构来在恒定时间内快速执行每个区域对比度检查
#（特征检测仅为灰度的原因是因为整体图像的空间需求）。

import sensor, time, image

# 重置感光元件
sensor.reset()

# 感光元件设置
sensor.set_contrast(3)
sensor.set_gainceiling(16)
# HQVGA and GRAYSCALE are the best for face tracking.
# HQVGA和灰度对于人脸识别效果最好
sensor.set_framesize(sensor.HQVGA)
sensor.set_pixformat(sensor.GRAYSCALE)
#注意人脸识别只能用灰度图哦

# 加载Haar算子
# 默认情况下，这将使用所有阶段，更低的satges更快，但不太准确。
face_cascade = image.HaarCascade("frontalface", stages=25)
#image.HaarCascade(path, stages=Auto)加载一个haar模型。haar模型是二进制文件，
#这个模型如果是自定义的，则引号内为模型文件的路径；也可以使用内置的haar模型，
#比如“frontalface” 人脸模型或者“eye”人眼模型。
#stages值未传入时使用默认的stages。stages值设置的小一些可以加速匹配，但会降低准确率。
print(face_cascade)

# FPS clock
clock = time.clock()

while (True):
    clock.tick()

    # 拍摄一张照片
    img = sensor.snapshot()

    # Find objects.
    # Note: Lower scale factor scales-down the image more and detects smaller objects.
    # Higher threshold results in a higher detection rate, with more false positives.
    objects = img.find_features(face_cascade, threshold=0.75, scale=1.35)
    #image.find_features(cascade, threshold=0.5, scale=1.5),thresholds越大，
    #匹配速度越快，错误率也会上升。scale可以缩放被匹配特征的大小。

    #在找到的目标上画框，标记出来
    for r in objects:
        img.draw_rectangle(r)

    # 打印FPS。
    # 注：实际FPS更高，流FB使它更慢。
    print(clock.fps())
