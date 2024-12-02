from PyQt5.QtCore import QThread, pyqtSignal, QCoreApplication
import numpy
import matplotlib.pyplot as plt
from ultralytics.yolo.data.converter import min_index

from MPC08E import *
from cjk_9114 import *
import time
import matplotlib.ticker as ticker
from numpy.linalg import inv  # 矩阵求逆
from numpy import dot  # 矩阵点乘
from numpy import mat  # 二维矩阵
import snap7
from scipy.signal import medfilt
from scipy.ndimage import uniform_filter

def get_ai():
    # 初始化轴卡
    result = mpc_lib.auto_set()
    print("轴数", result)
    result = mpc_lib.init_board()
    print("卡数", result)

    # 初始化采集卡
    card_number = 0  # 卡号
    card_handle = dask_dll.Register_Card(24, card_number)
    # 配置采集卡
    trigger_source = 1  # 触发源
    result1 = AI_9114_Config(card_handle, trigger_source)

    # 轴卡参数
    axis = 1
    # 采集卡参数
    channel = 0         # 传感器位置
    ad_range = 1
    read_count = 48
    sample_rate = 140000.0
    sync_mode = 1

    sudden_stop(axis)
    while (check_done(axis)):
        result = check_done(axis)
        print("查询运动状态", result)
    result = check_done(axis)
    print("查询运动状态", result)

    result = reset_pos(axis)
    print("当前位置置零", result)

    result = con_vmove(axis, 1)
    print("单轴连续运动", result)

    AI_0 = []
    AI_1 = []
    AI_2 = []
    AI_3 = []
    AI_4 = []
    AI_5 = []
    AI_6 = []
    axis_data = []

    i = 0
    while (check_done(axis)):
        buffer = [0] * read_count
        # _, filled_buffer = ai_cont_scan_channel(card_number, 7, ad_range, buffer, read_count, sample_rate, sync_mode)

        # _, filled_buffer = ai_cont_read_channel(card_number, 0, ad_range, buffer, read_count, sample_rate,
        #                                              sync_mode)
        filled_buffer = numpy.array(filled_buffer)
        ai_0 = numpy.mean(filled_buffer[numpy.arange(0, 48, 12)])
        ai_1 = numpy.mean(filled_buffer[numpy.arange(1, 48, 12)])
        ai_2 = numpy.mean(filled_buffer[numpy.arange(2, 48, 12)])
        ai_3 = numpy.mean(filled_buffer[numpy.arange(3, 48, 12)])
        ai_4 = numpy.mean(filled_buffer[numpy.arange(4, 48, 12)])
        ai_5 = numpy.mean(filled_buffer[numpy.arange(5, 48, 12)])
        ai_6 = numpy.mean(filled_buffer[numpy.arange(6, 48, 12)])
        print("读传感器0~6: ", ai_0, ai_1, ai_2, ai_3, ai_4, ai_5, ai_6)

        aa = ctypes.c_double(0)
        result = get_abs_pos(axis, ctypes.byref(aa))
        # print("读轴", result)
        print("读轴：", aa)

        AI_0.append(ai_0)
        AI_1.append(ai_1)
        AI_2.append(ai_2)
        AI_3.append(ai_3)
        AI_4.append(ai_4)
        AI_5.append(ai_5)
        AI_6.append(ai_6)
        axis_data.append(aa)

        if aa == 0:
            result = sudden_stop(axis)
            print("立即停止", result)

        i += 1
        if i == 1000:
            break

    print(AI_0, "\n", AI_1, "\n", AI_2, "\n", AI_3, "\n", AI_4, "\n", AI_5, "\n", AI_6, "\n", axis_data)
    # 释放采集卡资源
    result = dask_dll.Release_Card(card_number)
    if result == 0:
        print("采集卡资源释放成功")
    else:
        print("采集卡资源释放失败:", result)

    return AI_0, AI_1, AI_2, AI_3, AI_4, AI_5, AI_6, axis_data
def get_center(r, theta):
    r = numpy.array(r)
    theta = numpy.array(theta)
    x = r * numpy.cos(numpy.pi * theta / 180)
    y = r * numpy.sin(numpy.pi * theta / 180)
    # 计算质心
    centroid_x = numpy.mean(x)      # 计算 x 坐标的平均值
    centroid_y = numpy.mean(y)      # 计算 y 坐标的平均值
    return centroid_x, centroid_y, (numpy.mean((centroid_x - x) ** 2 + (centroid_y - y) ** 2)) ** 0.5
def get_circle(r, theta):
    r = numpy.array(r).reshape(len(r), -1)
    theta = numpy.array(theta).reshape(len(theta), -1)
    theta = numpy.pi * theta / 180
    b = r ** 2
    b = mat(b).reshape(len(b), -1)
    A = mat(numpy.ones((len(theta), 3)))
    A[:, 0] = 2 * r * numpy.cos(theta)
    A[:, 1] = 2 * r * numpy.sin(theta)
    BcA, BsA, C = dot(dot(inv(dot(A.T, A)), A.T), b)
    # print(numpy.linalg.matrix_rank(dot(A.T, A)))
    BcA, BsA, C = float(BcA), float(BsA), float(C)
    B = (BcA ** 2 + BsA ** 2) ** 0.5
    thta = numpy.arctan2(BsA, BcA)
    thta = (180 * thta / numpy.pi)
    if thta < 0:
        thta = 360 + thta
    # print(B, thta, (B ** 2 + C) ** 0.5)
    # return B, thta, (B ** 2 + C) ** 0.5
    return B * numpy.cos(thta * numpy.pi / 180), B * numpy.sin(thta * numpy.pi / 180), (B ** 2 + C) ** 0.5
def generate_circle_points(num, center, radius, n):
    angles = numpy.linspace(0, 2 * numpy.pi, num, endpoint=False)  # 生成均匀的角度
    R = numpy.random.uniform(radius - n, radius + n, num)
    x = center[0] + R * numpy.cos(angles)  # 计算 x 坐标
    y = center[1] + R * numpy.sin(angles)  # 计算 y 坐标
    # print(x,y)
    r = numpy.sqrt(x**2 + y**2)  # 计算半径
    theta = numpy.arctan2(y, x)   # 计算角度
    # print(theta * 180 / numpy.pi)
    return r, theta * 180 / numpy.pi
def set_bit(byte, bit, value):
    if value:
        return byte | (1 << bit)
    else:
        return byte & ~(1 << bit)
def write_bool_200(plc, byte_address, bit, value):
    data = plc.read_area(snap7.types.Areas.MK, 0, byte_address, 1)
    snap7.util.set_bool(data, 0, bit, value)
    plc.write_area(snap7.types.Areas.MK, 0, byte_address, data)
    # print("cgl")
def write_bool(client, db_number, start_byte, bool_value):
    try:
        # db_data = client.db_read(db_number, 0, 1)  # 读取DB块数据
        byte_offset = start_byte // 8
        bit_offset = start_byte % 8
        write_bool_200(client, byte_offset, bit_offset, bool_value)
        # db_data[byte_offset] = set_bit(db_data[byte_offset], bit_offset, bool_value)
        # client.db_write(db_number, 0, db_data)  # 写回DB块
        return True
    except Exception as e:
        return False
def write_real(plc, byte_address, real_value):
    # 由于 REAL 类型需要 4 个字节, 我们构造一个 bytearray
    data = bytearray(4)
    snap7.util.set_real(data, 0, real_value)  # 将 REAL 类型的值写入数据字节数组
    plc.write_area(snap7.types.Areas.MK, 0, byte_address, data)  # 写入 MK 区域的 byte_address 地址
def read_bool(plc, start_byte):
    # 读取 1 字节的数据
    byte_address = start_byte // 8
    bit = start_byte % 8
    data = plc.read_area(snap7.types.Areas.MK, 0, byte_address, 1)
    return snap7.util.get_bool(data, 0, bit)  # 获取特定字节的位值 (0 表示从字节的第 0 位开始)
class LeastSquaresFitting:
    def __init__(self, rr, tt):
        # 将极坐标转换为直角坐标
        rr = numpy.array(rr)
        tt = numpy.array(tt)
        tt = tt * numpy.pi / 180
        self.points = [(r * numpy.cos(theta), r * numpy.sin(theta)) for r, theta in zip(rr, tt)]
        self.m_nNum = len(self.points)
        self.m_fCenterX = 0
        self.m_fCenterY = 0
        self.m_fRadius = 0

    def least_squares_fitting(self):
        if self.m_nNum < 3:
            return

        X1 = sum(p[0] for p in self.points)
        Y1 = sum(p[1] for p in self.points)
        X2 = sum(p[0]**2 for p in self.points)
        Y2 = sum(p[1]**2 for p in self.points)
        X3 = sum(p[0]**3 for p in self.points)
        Y3 = sum(p[1]**3 for p in self.points)
        X1Y1 = sum(p[0] * p[1] for p in self.points)
        X1Y2 = sum(p[0] * p[1]**2 for p in self.points)
        X2Y1 = sum(p[0]**2 * p[1] for p in self.points)

        N = self.m_nNum
        C = N * X2 - X1**2
        D = N * X1Y1 - X1 * Y1
        E = N * X3 + N * X1Y2 - (X2 + Y2) * X1
        G = N * Y2 - Y1**2
        H = N * X2Y1 + N * Y3 - (X2 + Y2) * Y1

        a = (H * D - E * G) / (C * G - D**2)
        b = (H * C - E * D) / (D**2 - G * C)
        c = -(a * X1 + b * Y1 + X2 + Y2) / N

        A = a / -2
        B = b / -2
        R = numpy.sqrt(a**2 + b**2 - 4 * c) / 2

        self.m_fCenterX = A
        self.m_fCenterY = B
        self.m_fRadius = R
class Worker_zzt(QThread):
    update_signal = pyqtSignal(list)  # 信号用于通知UI更新
    def __init__(self, values):
        super().__init__()
        self.values = values
    def run(self):
        # 在子线程中处理绘图逻辑
        print("开始绘图")
        bar_mo = self.values  # 获取数据
        categories = ['Sensor1', 'Sensor2', 'Sensor3', 'Sensor4', 'Sensor5', 'Sensor6', 'Sensor7']
        fig, axs = plt.subplots(1, 7, figsize=(14, 6))

        for i in range(7):
            ax = axs[i]
            ax.clear()
            color = 'red' if bar_mo[i] >= 2 else 'green'
            ax.bar(categories[i], bar_mo[i], width=0.2, color=color)
            ax.set_ylim(bottom=0.45, top=5.5)
            ax.set_yscale('log', base=numpy.e)
            ax.yaxis.set_major_formatter(ticker.ScalarFormatter())
            ax.axhline(y=2, color='black', linestyle='--', linewidth=1)
            ax.axhline(y=1, color='black', linestyle='--', linewidth=1)
            ax.set_title(f'{bar_mo[i]}', fontsize=14)
            ax.tick_params(axis='y', labelsize=14)
            ax.tick_params(axis='x', labelsize=14)
            ax.yaxis.set_major_locator(ticker.MaxNLocator(integer=True))

        # 一次性绘制所有图表
        self.update_signal.emit(bar_mo)  # 发送信号通知主线程更新UI

############# 多线程 ########################################################################################################
class WorkerThread(QThread):
    end_signal = pyqtSignal(bool)
    ec_signal = pyqtSignal(list, list, list)
    caiji_signal = pyqtSignal(str)
    def __init__(self, task_id):
        super().__init__()  # 正确调用父类的构造函数
        self.EN = True
        self.task_id = task_id
        self.mc_num = 800
        self.mc_circle = 84500
        self.axis = 1
        self.num_pulses = 21125      # 电机旋转一周，编码器返回脉冲数

        # 初始化采集卡
        self.card_number = 0    # 卡号
        self.card_handle = dask_dll.Register_Card(24, self.card_number)     # 24=>ad_range(1,2,3,4),25=>ad_range(1,10,11,12)
        # 配置采集卡
        self.trigger_source = 1 # 触发源
        AI_9114_Config(self.card_handle, self.trigger_source)
        # 采集卡参数
        self.channel = 5        # 传感器位置
        self.ad_range = 1       # 1=>正负10；2=>正负5；3=>正负2.5；4=>正负1.25；10=>正负1；11=>正负0.1；12=>正负0.01
        # self.read_count = 48
        self.sample_rate = 100000.0  # 最高100000.0
        self.sync_mode = 1      # 1=>SYNCH_OP同步;2=>ASYNCH_OP异步;

    def run(self):
        if self.task_id == 1:
            self.perform_task1()
        elif self.task_id == 2:
            self.perform_task2()
        else:
            return
    def perform_task1(self):
        c = 0
        value1 = ctypes.c_short(0)
        value2 = ctypes.c_short(0)
        value3 = ctypes.c_short(0)
        value4 = ctypes.c_short(0)
        value5 = ctypes.c_short(0)
        value6 = ctypes.c_short(0)
        value7 = ctypes.c_short(0)
        aa = ctypes.c_long(0)
        while (self.EN):
            c += 1
            c %= 3
            AI_ReadChannel(self.card_number, 0, self.ad_range, ctypes.pointer(value1))
            AI_ReadChannel(self.card_number, 1, self.ad_range, ctypes.pointer(value2))
            AI_ReadChannel(self.card_number, 2, self.ad_range, ctypes.pointer(value3))
            AI_ReadChannel(self.card_number, 3, self.ad_range, ctypes.pointer(value4))
            AI_ReadChannel(self.card_number, 4, self.ad_range, ctypes.pointer(value5))
            AI_ReadChannel(self.card_number, 6, self.ad_range, ctypes.pointer(value6))
            AI_ReadChannel(self.card_number, 5, self.ad_range, ctypes.pointer(value7))
            get_encoder(self.axis, ctypes.byref(aa))
            dir = get_cur_dir(self.axis)
            # self.log_widget.append(f"轴卡：{aa.value}，采集卡：{ai_0, ai_1, ai_2, ai_3, ai_4, ai_5, ai_6}")
            if c == 0:
                color = "rgba(0, 220, 220, 1)"
            elif c == 1:
                color = "rgba(0, 240, 100, 1)"
            else:
                color = "rgba(0, 100, 240, 0.7)"

            message = f"轴卡：{round(aa.value)}，采集卡：{round(32767 - value1.value), round(32767 - value7.value)}{dir}"
            html_message = f'<span style="color: {color};">{message}</span>'

            self.caiji_signal.emit(html_message)
            # self.log_widget.append(html_message)
            # # QCoreApplication.processEvents()
            # self.log_widget.ensureCursorVisible()
            time.sleep(0.42)
    def perform_task2(self):
        result = sudden_stop(self.axis)
        # result = 0
        if result < 0:
            self.end_signal.emit(True)
            return
            AI_0, axis_data = generate_circle_points(25000, (2.3, 0.4), 1000, 0.7)
            AI_1, _ = self.generate_circle_points(25000, (-1, -1), 1213, 0.9)
            AI_2, _ = self.generate_circle_points(25000, (2000, 2000), 3231, 0.1)
            AI_3, _ = self.generate_circle_points(25000, (2000, 2000), 1212, 0.1)
            AI_4, _ = self.generate_circle_points(25000, (2000, 2000), 1213, 0.1)
            AI_5, _ = self.generate_circle_points(25000, (1, 2), 3432, 0.1)
            AI_6, _ = self.generate_circle_points(25000, (2, 2), 1323, 0.1)
        else:
            AI_0, AI_1, AI_2, AI_3, AI_4, AI_5, AI_6, axis_data = self.get_ai()
        l_data = len(AI_0)
        print(len(AI_0))
        if len(AI_0) <= 500:
            self.end_signal.emit(True)
            return
        print("数据采回，准备拟合")
        try:
            AI_0 = 32767 - AI_0
            AI_1 = 32767 - AI_1
            AI_2 = 32767 - AI_2
            AI_3 = 32767 - AI_3
            AI_4 = 32767 - AI_4
            AI_5 = 32767 - AI_5
            AI_6 = 32767 - AI_6

            AI_0 = medfilt(AI_0, kernel_size=19)
            AI_1 = medfilt(AI_1, kernel_size=19)
            AI_2 = medfilt(AI_2, kernel_size=19)
            AI_3 = medfilt(AI_3, kernel_size=19)
            AI_4 = medfilt(AI_4, kernel_size=19)
            AI_5 = medfilt(AI_5, kernel_size=19)
            AI_6 = medfilt(AI_6, kernel_size=19)

            AI_2 = uniform_filter(AI_2, size=19)
            AI_3 = uniform_filter(AI_3, size=19)
            AI_4 = uniform_filter(AI_4, size=19)
            jz_x1, jz_y1, jz_R1 = self.get_circle(AI_0, axis_data)
            jz_x2, jz_y2, jz_R2 = self.get_circle(AI_1, axis_data)
            jz_x6, jz_y6, jz_R6 = self.get_circle(AI_5, axis_data)
            jz_x7, jz_y7, jz_R7 = self.get_circle(AI_6, axis_data)

            min_index3 = numpy.argmin(AI_2)
            min_index4 = numpy.argmin(AI_3)
            min_index5 = numpy.argmin(AI_4)

            kesai3 = axis_data[min_index3] % 90
            kesai4 = axis_data[min_index4] % 90
            kesai5 = axis_data[min_index5] % 90

            index3 = min_index3 % (l_data // 4)
            index4 = min_index4 % (l_data // 4)
            index5 = min_index5 % (l_data // 4)
            jz_y3 = - AI_2[index3 + (3 * l_data // 4)] + AI_2[index3 + (1 * l_data // 4)]
            jz_x3 = - AI_2[index3 + (l_data // 2)] + AI_2[index3]
            jz_y4 = - AI_3[index4 + (3 * l_data // 4)] + AI_3[index4 + (1 * l_data // 4)]
            jz_x4 = - AI_3[index4 + (l_data // 2)] + AI_3[index4]
            jz_y5 = - AI_4[index5 + (3 * l_data // 4)] + AI_4[index5 + (1 * l_data // 4)]
            jz_x5 = - AI_4[index5 + (l_data // 2)] + AI_4[index5]

        except:
            print("二乘矩阵奇异")
            self.end_signal.emit(True)
            return

        mo1 = numpy.sqrt(jz_x1 ** 2 + jz_y1 ** 2)
        xj1 = numpy.arctan2(jz_y1, jz_x1) * 180 / numpy.pi
        mo2 = numpy.sqrt(jz_x2 ** 2 + jz_y2 ** 2)
        xj2 = numpy.arctan2(jz_y2, jz_x2) * 180 / numpy.pi
        mo3 = numpy.sqrt(jz_x3 ** 2 + jz_y3 ** 2)
        xj3 = (numpy.arctan2(jz_y3, jz_x3) * 180 / numpy.pi)# - kesai3
        mo4 = numpy.sqrt(jz_x4 ** 2 + jz_y4 ** 2)
        xj4 = (numpy.arctan2(jz_y4, jz_x4) * 180 / numpy.pi)# - kesai4
        mo5 = numpy.sqrt(jz_x5 ** 2 + jz_y5 ** 2)
        xj5 = (numpy.arctan2(jz_y5, jz_x5) * 180 / numpy.pi)# - kesai5
        mo6 = numpy.sqrt(jz_x6 ** 2 + jz_y6 ** 2)
        xj6 = numpy.arctan2(jz_y6, jz_x6) * 180 / numpy.pi
        mo7 = numpy.sqrt(jz_x7 ** 2 + jz_y7 ** 2)
        xj7 = numpy.arctan2(jz_y7, jz_x7) * 180 / numpy.pi

        bar_mo = [round(mo1, 2),
                  round(mo2, 2),
                  round(mo3, 2),
                  round(mo4, 2),
                  round(mo5, 2),
                  round(mo6, 2),
                  round(mo7, 2)]
        bar_xj = [xj1,
                  xj2,
                  xj3,
                  xj4,
                  xj5,
                  xj6,
                  xj7]
        kesai = [kesai3, kesai4, kesai5]
        print("二乘线程完毕，返回信号")
        self.ec_signal.emit(bar_mo, bar_xj, kesai)
        print("信号返回完毕")
    def get_ai(self):
        try:
            sudden_stop(self.axis)
            # while (check_done(self.axis)):
            #     time.sleep(0.2)
            result = reset_pos(self.axis)
            print("当前位置置零", result)
            print("准备启动电机")
            try:
                fast_pmove(self.axis, self.mc_circle)
            except:
                return 0, 0, 0, 0, 0, 0, 0, 0
            print("启动电机")
            AI_0 = []
            AI_1 = []
            AI_2 = []
            AI_3 = []
            AI_4 = []
            AI_5 = []
            AI_6 = []
            axis_data = []
            i = 0
            value1 = ctypes.c_short(0)
            value2 = ctypes.c_short(0)
            value3 = ctypes.c_short(0)
            value4 = ctypes.c_short(0)
            value5 = ctypes.c_short(0)
            value6 = ctypes.c_short(0)
            value7 = ctypes.c_short(0)
            aa = ctypes.c_long(0)
            print("开始采集")
            while (self.EN):
                if check_done(self.axis) == 0:
                    break
                AI_ReadChannel(self.card_number, 0, self.ad_range, ctypes.pointer(value1))
                AI_ReadChannel(self.card_number, 1, self.ad_range, ctypes.pointer(value2))
                AI_ReadChannel(self.card_number, 2, self.ad_range, ctypes.pointer(value3))
                AI_ReadChannel(self.card_number, 3, self.ad_range, ctypes.pointer(value4))
                AI_ReadChannel(self.card_number, 4, self.ad_range, ctypes.pointer(value5))
                AI_ReadChannel(self.card_number, 6, self.ad_range, ctypes.pointer(value6))
                AI_ReadChannel(self.card_number, 5, self.ad_range, ctypes.pointer(value7))
                get_encoder(self.axis, ctypes.byref(aa))
                # print("读轴：", aa)
                AI_0.append(value1.value)
                AI_1.append(value2.value)
                AI_2.append(value3.value)
                AI_3.append(value4.value)
                AI_4.append(value5.value)
                AI_5.append(value6.value)
                AI_6.append(value7.value)
                axis_data.append((aa.value % self.num_pulses) * 360 / self.num_pulses)
                # print("单步存数据")
                # if aa.value >= self.num_pulses - 2:
                #     result = sudden_stop(self.axis)
                #     print("立即停止", result)
            return (numpy.array(AI_0), numpy.array(AI_1), numpy.array(AI_2), numpy.array(AI_3),
                    numpy.array(AI_4), numpy.array(AI_5), numpy.array(AI_6), numpy.array(axis_data))
        except Exception as e:
            print(f"轴卡连接失败{e}")
            AI_0, axis_data = generate_circle_points(3, (2.3, 0.4), 12, 0.7)
            AI_1, _ = self.generate_circle_points(3, (-1, -1), 12, 0.9)
            AI_2, _ = self.generate_circle_points(3, (1, 0), 12, 0.1)
            AI_3, _ = self.generate_circle_points(3, (1, 1), 12, 0.1)
            AI_4, _ = self.generate_circle_points(3, (2, 1), 12, 0.1)
            AI_5, _ = self.generate_circle_points(3, (1, 2), 12, 0.1)
            AI_6, _ = self.generate_circle_points(3, (2, 2), 12, 0.1)
            return (numpy.array(AI_0), numpy.array(AI_1), numpy.array(AI_2), numpy.array(AI_3),
                    numpy.array(AI_4), numpy.array(AI_5), numpy.array(AI_6), numpy.array(axis_data))
    def stop(self):
        sudden_stop(self.axis)
        self.EN = False
        # self.log_widget.append(f"正在停止采集")
        # self.log_widget.ensureCursorVisible()
    def stop_init(self):
        self.EN = True
        # self.log_widget.append(f"成功停止采集")
        # self.log_widget.ensureCursorVisible()
    # 输入为角度（非弧度）
    def get_center(self, r, theta):
        r = numpy.array(r)
        theta = numpy.array(theta)
        x = r * numpy.cos(numpy.pi * theta / 180)
        y = r * numpy.sin(numpy.pi * theta / 180)
        # 计算质心
        centroid_x = numpy.mean(x)  # 计算 x 坐标的平均值
        centroid_y = numpy.mean(y)  # 计算 y 坐标的平均值
        return centroid_x, centroid_y, (numpy.mean((centroid_x - x) ** 2 + (centroid_y - y) ** 2)) ** 0.5
    # 输入为角度（非弧度）
    def get_circle(self, r, theta):
        r = numpy.array(r).reshape(len(r), -1)
        theta = numpy.array(theta).reshape(len(theta), -1)
        theta = numpy.pi * theta / 180
        b = r ** 2
        b = mat(b).reshape(len(b), -1)
        A = mat(numpy.ones((len(theta), 3)))
        A[:, 0] = 2 * r * numpy.cos(theta)
        A[:, 1] = 2 * r * numpy.sin(theta)
        BcA, BsA, C = dot(dot(inv(dot(A.T, A)), A.T), b)
        # print(numpy.linalg.matrix_rank(dot(A.T, A)))
        BcA, BsA, C = float(BcA), float(BsA), float(C)
        B = (BcA ** 2 + BsA ** 2) ** 0.5
        thta = numpy.arctan2(BsA, BcA)
        thta = (180 * thta / numpy.pi)
        if thta < 0:
            thta = 360 + thta
        # print(B, thta, (B ** 2 + C) ** 0.5)
        # return B, thta, (B ** 2 + C) ** 0.5
        return B * numpy.cos(thta * numpy.pi / 180), B * numpy.sin(thta * numpy.pi / 180), (B ** 2 + C) ** 0.5
    # 随机生成角度（非弧度）、模长
    def generate_circle_points(self, num, center, radius, n):
        angles = numpy.linspace(0, 2 * numpy.pi, num, endpoint=False)  # 生成均匀的角度
        R = numpy.random.uniform(radius - n, radius + n, num)
        x = center[0] + R * numpy.cos(angles)  # 计算 x 坐标
        y = center[1] + R * numpy.sin(angles)  # 计算 y 坐标
        # print(x,y)
        r = numpy.sqrt(x ** 2 + y ** 2)  # 计算半径
        theta = numpy.arctan2(y, x)  # 计算角度
        # print(theta * 180 / numpy.pi)
        return r, theta * 180 / numpy.pi

def test(r, theta):
    # 调用 get_circle 函数
    x1, y1, R1 = get_circle(r, theta)
    x, y, R = get_center(r, theta)
    fitting = LeastSquaresFitting(r, theta)
    fitting.least_squares_fitting()
    print(f"统计二乘: Center: ({fitting.m_fCenterX}, {fitting.m_fCenterY}), Radius: {fitting.m_fRadius}")
    # 可视化结果
    plt.figure(figsize=(8, 8))
    plt.scatter(r * numpy.cos(numpy.radians(theta)), r * numpy.sin(numpy.radians(theta)), label='gen')
    plt.title('gen')
    plt.axis('equal')
    # 绘制拟合圆
    circle = plt.Circle((x, y), R, color='r', fill=False, label='zhi_xin')
    plt.gca().add_artist(circle)
    print("质心圆心：", x, y, "    半径：", R)
    print("矩阵二乘圆心：", x1, y1, "    半径：", R1)
    # plt.subplot(122)
    plt.scatter(x, y, label='center', color='orange')
    plt.title('ec')
    plt.axis('equal')

    # plt.scatter(X1, Y1, label='zhi_xin', color='red')
    # plt.title('ec')
    # plt.axis('equal')
    # print("质心圆心：", (X1, Y1))

    plt.legend()
    plt.show()

if __name__ == "__main__":
    # AI_0, AI_1, AI_2, AI_3, AI_4, AI_5, AI_6, axis_data = get_ai()
    #
    # test(AI_1, axis_data)
    # test(AI_2, axis_data)
    # test(AI_3, axis_data)
    # test(AI_4, axis_data)
    # test(AI_5, axis_data)
    # test(AI_6, axis_data)
    # test(AI_7, axis_data)

    r, theta = generate_circle_points(1000, (12, 11), 30, 0.2)

    # test(r, theta)