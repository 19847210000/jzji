import bisect
from PyQt5.QtCore import QThread, pyqtSignal, QObject
import numpy
import matplotlib.pyplot as plt
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
import re

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

    # print(AI_0, "\n", AI_1, "\n", AI_2, "\n", AI_3, "\n", AI_4, "\n", AI_5, "\n", AI_6, "\n", axis_data)
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
    try:
        # 创建一个大小为 4 字节的 bytearray 来存储 REAL 类型的值
        data = bytearray(4)
        # 将 real_value 转换为 4 字节并写入 data
        snap7.util.set_real(data, 0, real_value)  # 将 REAL 类型的值写入数据字节数组
        print(f"Data size: {len(data)} bytes")
        print(f"Data (hex): {data.hex()}")  # 打印数据的十六进制形式，便于调试
        # 将数据写入 MK 区域的指定 byte_address 地址
        result = plc.write_area(snap7.types.Areas.MK, 0, byte_address, data)
        if result == 0:
            print("Write successful")
        else:
            print(f"Error writing to PLC:: {result}")
    except Exception as e:
        print(f"Error in write_real: {e}")
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
    chart_signal = pyqtSignal(list)
    def __init__(self, task_id):
        super().__init__()  # 正确调用父类的构造函数
        self.EN = True
        self.task_id = task_id
        self.mc_circle = 20765
        self.axis = 1
        self.num_pulses = 20765      # 电机旋转一周，编码器返回脉冲数

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
            self.yyfffyy()
        elif self.task_id == 3:
            self.yyyyyyy()
        elif self.task_id == 4:
            self.yfffffy()
        else:
            return
    def perform_task1(self):
        c = 0
        num = 0
        value1 = ctypes.c_short(0)
        value2 = ctypes.c_short(0)
        value3 = ctypes.c_short(0)
        value4 = ctypes.c_short(0)
        value5 = ctypes.c_short(0)
        value6 = ctypes.c_short(0)
        value7 = ctypes.c_short(0)
        aa = ctypes.c_long(0)
        while (self.EN):
            num += 1
            num %= 25
            c += 1
            c %= 3
            AI_ReadChannel(self.card_number, 0, self.ad_range, ctypes.pointer(value1))
            AI_ReadChannel(self.card_number, 1, self.ad_range, ctypes.pointer(value2))
            AI_ReadChannel(self.card_number, 2, self.ad_range, ctypes.pointer(value3))
            AI_ReadChannel(self.card_number, 3, self.ad_range, ctypes.pointer(value4))
            AI_ReadChannel(self.card_number, 4, self.ad_range, ctypes.pointer(value5))
            AI_ReadChannel(self.card_number, 5, self.ad_range, ctypes.pointer(value6))
            AI_ReadChannel(self.card_number, 6, self.ad_range, ctypes.pointer(value7))
            get_encoder(self.axis, ctypes.byref(aa))
            dir = get_cur_dir(self.axis)
            # self.log_widget.append(f"轴卡：{aa.value}，采集卡：{ai_0, ai_1, ai_2, ai_3, ai_4, ai_5, ai_6}")
            if c == 0:
                color = "rgba(0, 220, 220, 1)"
            elif c == 1:
                color = "rgba(0, 240, 100, 1)"
            else:
                color = "rgba(0, 100, 240, 0.7)"

            if num == 0:
                message = f"轴卡：{-1 * round(aa.value)}，采集卡：{round(32767 - value1.value), round(32767 - value2.value), round(32767 - value3.value), round(32767 - value4.value), round(32767 - value5.value), round(32767 - value6.value), round(32767 - value7.value)}{dir}"
                html_message = f'<span style="color: {color};">{message}</span>'

                self.caiji_signal.emit(html_message)
            self.chart_signal.emit([(32767 - value1.value)/655.35, (32767 - value2.value)/655.35, (32767 - value3.value)/655.35,
                                    (32767 - value4.value)/655.35, (32767 - value5.value)/655.35, (32767 - value6.value)/655.35,
                                    (32767 - value7.value)/655.35])
            # self.log_widget.append(html_message)
            # # QCoreApplication.processEvents()
            # self.log_widget.ensureCursorVisible()
            time.sleep(0.02)
    def yyfffyy(self):
        result = sudden_stop(self.axis)
        # result = 0
        if result < 0:
            self.end_signal.emit(True)
            return
            # bar_mo = [round(1.2, 2),
            #           round(2.1, 2),
            #           round(1.3, 2),
            #           round(1.6, 2),
            #           round(0.7, 2),
            #           round(1.2, 2),
            #           round(1.9, 2)]
            # bar_xj = [0,
            #           0,
            #           0,
            #           0,
            #           0,
            #           0,
            #           0]
            # kesai = [87, 1, 1]
            # print("二乘线程完毕，返回信号")
            # self.ec_signal.emit(bar_mo, bar_xj, kesai)
            # return
            AI_0, axis_data = self.generate_circle_points(20000, (2.3, 0.4), 1000, 0.7)
            AI_1, _ = self.generate_circle_points(20000, (-1, -1), 1213, 0.9)
            AI_2, _ = self.generate_circle_points(20000, (0, 2000), 3231, 0.1)
            AI_3, _ = self.generate_circle_points(20000, (0, 2000), 1212, 0.1)
            AI_4, _ = self.generate_circle_points(20000, (0, 2000), 1213, 0.1)
            AI_5, _ = self.generate_circle_points(20000, (1, 2), 3432, 0.1)
            AI_6, _ = self.generate_circle_points(20000, (2, 2), 1323, 0.1)
            axis_data = numpy.where(axis_data < 0, axis_data + 360, axis_data)
        else:
            AI_0, AI_1, AI_2, AI_3, AI_4, AI_5, AI_6, axis_data = self.get_ai()
        print(len(AI_0))
        if len(AI_0) <= 500:
            self.end_signal.emit(True)
            return
        print("数据采回，准备拟合")
        massage = f'北1传感器：{max(AI_0) - min(AI_0)}，北2传感器：{max(AI_1) - min(AI_1)}，南6传感器：{max(AI_5) - min(AI_5)}，南7传感器：{max(AI_6) - min(AI_6)}'
        print(massage)
        self.caiji_signal.emit(massage)
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
            jz_x7, jz_y7, jz_R7 = self.get_circle(AI_6, axis_data)
            # 最小值索引[0，360）对应的索引
            min_index3 = numpy.argmin(AI_2)
            min_index4 = numpy.argmin(AI_3)
            min_index5 = numpy.argmin(AI_4)
            self.kesai = sorted([axis_data[min_index3], axis_data[min_index4], axis_data[min_index5]])[1]
            axis_data_new, AI_1_new = self.remove_data(axis_data, AI_1, self.kesai % 90, 10)
            axis_data_new, AI_1_new = self.remove_data(axis_data_new, AI_1_new, self.kesai % 90 + 90, 10)
            axis_data_new, AI_1_new = self.remove_data(axis_data_new, AI_1_new, self.kesai % 90 + 180, 10)
            axis_data_new, AI_1_new = self.remove_data(axis_data_new, AI_1_new, self.kesai % 90 + 270, 10)
            jz_x2, jz_y2, jz_R2 = self.get_circle(AI_1_new, axis_data_new)
            axis_data_new_1, AI_5_new = self.remove_data(axis_data, AI_5, self.kesai % 90, 10)
            axis_data_new_1, AI_5_new = self.remove_data(axis_data_new_1, AI_5_new, self.kesai % 90 + 90, 10)
            axis_data_new_1, AI_5_new = self.remove_data(axis_data_new_1, AI_5_new, self.kesai % 90 + 180, 10)
            axis_data_new_1, AI_5_new = self.remove_data(axis_data_new_1, AI_5_new, self.kesai % 90 + 270, 10)
            jz_x6, jz_y6, jz_R6 = self.get_circle(AI_5_new, axis_data_new_1)
            # 找平角度[0,90)
            kesai3 = axis_data[min_index3] % 90
            kesai4 = axis_data[min_index4] % 90
            kesai5 = axis_data[min_index5] % 90
            # 找平角度对应的索引
            index3_0 = self.find_closest_index(kesai3, axis_data)
            index4_0 = self.find_closest_index(kesai4, axis_data)
            index5_0 = self.find_closest_index(kesai5, axis_data)
            index3_1 = self.find_closest_index(kesai3 + 90, axis_data)
            index4_1 = self.find_closest_index(kesai4 + 90, axis_data)
            index5_1 = self.find_closest_index(kesai5 + 90, axis_data)
            index3_2 = self.find_closest_index(kesai3 + 180, axis_data)
            index4_2 = self.find_closest_index(kesai4 + 180, axis_data)
            index5_2 = self.find_closest_index(kesai5 + 180, axis_data)
            index3_3 = self.find_closest_index(kesai3 + 270, axis_data)
            index4_3 = self.find_closest_index(kesai4 + 270, axis_data)
            index5_3 = self.find_closest_index(kesai5 + 270, axis_data)
            # 算偏移
            jz_y3 = - AI_2[index3_3] + AI_2[index3_1]
            jz_x3 = - AI_2[index3_2] + AI_2[index3_0]
            jz_y4 = - AI_3[index4_3] + AI_3[index4_1]
            jz_x4 = - AI_3[index4_2] + AI_3[index4_0]
            jz_y5 = - AI_4[index5_3] + AI_4[index5_1]
            jz_x5 = - AI_4[index5_2] + AI_4[index5_0]

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

        bar_mo = [round(mo1/350, 2),
                  round(mo2/350, 2),
                  round(mo3/700, 2),
                  round(mo4/700, 2),
                  round(mo5/700, 2),
                  round(mo6/350, 2),
                  round(mo7/350, 2)]
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
    def yyyyyyy(self):
        result = sudden_stop(self.axis)
        # result = 0
        if result < 0:
            self.end_signal.emit(True)
            return
        else:
            AI_0, AI_1, AI_2, AI_3, AI_4, AI_5, AI_6, axis_data = self.get_ai()
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

            jz_x1, jz_y1, jz_R1 = self.get_circle(AI_0, axis_data)
            jz_x2, jz_y2, jz_R2 = self.get_circle(AI_1, axis_data)
            jz_x3, jz_y3, jz_R3 = self.get_circle(AI_2, axis_data)
            jz_x4, jz_y4, jz_R4 = self.get_circle(AI_3, axis_data)
            jz_x5, jz_y5, jz_R5 = self.get_circle(AI_4, axis_data)
            jz_x6, jz_y6, jz_R6 = self.get_circle(AI_5, axis_data)
            jz_x7, jz_y7, jz_R7 = self.get_circle(AI_6, axis_data)

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

        bar_mo = [round(mo1/350, 2),
                  round(mo2/350, 2),
                  round(mo3/350, 2),
                  round(mo4/350, 2),
                  round(mo5/350, 2),
                  round(mo6/350, 2),
                  round(mo7/350, 2)]
        bar_xj = [xj1,
                  xj2,
                  xj3,
                  xj4,
                  xj5,
                  xj6,
                  xj7]
        kesai = [0]
        print("二乘线程完毕，返回信号")
        self.ec_signal.emit(bar_mo, bar_xj, kesai)
        print("信号返回完毕")
    def yfffffy(self):
        result = sudden_stop(self.axis)
        if result < 0:
            self.end_signal.emit(True)
            return
        else:
            AI_0, AI_1, AI_2, AI_3, AI_4, AI_5, AI_6, axis_data = self.get_ai()
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

            AI_1 = uniform_filter(AI_1, size=19)
            AI_2 = uniform_filter(AI_2, size=19)
            AI_3 = uniform_filter(AI_3, size=19)
            AI_4 = uniform_filter(AI_4, size=19)
            AI_5 = uniform_filter(AI_5, size=19)
            jz_x1, jz_y1, jz_R1 = self.get_circle(AI_0, axis_data)
            jz_x7, jz_y7, jz_R7 = self.get_circle(AI_6, axis_data)
            # 最小值索引[0，360）对应的索引
            min_index2 = numpy.argmin(AI_1)
            min_index3 = numpy.argmin(AI_2)
            min_index4 = numpy.argmin(AI_3)
            min_index5 = numpy.argmin(AI_4)
            min_index6 = numpy.argmin(AI_5)
            # 找平角度[0,90)
            kesai2 = axis_data[min_index2] % 90
            kesai3 = axis_data[min_index3] % 90
            kesai4 = axis_data[min_index4] % 90
            kesai5 = axis_data[min_index5] % 90
            kesai6 = axis_data[min_index6] % 90
            # 找平角度对应的索引
            index2_0 = self.find_closest_index(kesai2, axis_data)
            index3_0 = self.find_closest_index(kesai3, axis_data)
            index4_0 = self.find_closest_index(kesai4, axis_data)
            index5_0 = self.find_closest_index(kesai5, axis_data)
            index6_0 = self.find_closest_index(kesai6, axis_data)
            index2_1 = self.find_closest_index(kesai2 + 90, axis_data)
            index3_1 = self.find_closest_index(kesai3 + 90, axis_data)
            index4_1 = self.find_closest_index(kesai4 + 90, axis_data)
            index5_1 = self.find_closest_index(kesai5 + 90, axis_data)
            index6_1 = self.find_closest_index(kesai6 + 90, axis_data)
            index2_2 = self.find_closest_index(kesai2 + 180, axis_data)
            index3_2 = self.find_closest_index(kesai3 + 180, axis_data)
            index4_2 = self.find_closest_index(kesai4 + 180, axis_data)
            index5_2 = self.find_closest_index(kesai5 + 180, axis_data)
            index6_2 = self.find_closest_index(kesai6 + 180, axis_data)
            index2_3 = self.find_closest_index(kesai2 + 270, axis_data)
            index3_3 = self.find_closest_index(kesai3 + 270, axis_data)
            index4_3 = self.find_closest_index(kesai4 + 270, axis_data)
            index5_3 = self.find_closest_index(kesai5 + 270, axis_data)
            index6_3 = self.find_closest_index(kesai6 + 270, axis_data)
            # 算偏移
            jz_y2 = - AI_1[index2_3] + AI_1[index2_1]
            jz_x2 = - AI_1[index2_2] + AI_1[index2_0]
            jz_y3 = - AI_2[index3_3] + AI_2[index3_1]
            jz_x3 = - AI_2[index3_2] + AI_2[index3_0]
            jz_y4 = - AI_3[index4_3] + AI_3[index4_1]
            jz_x4 = - AI_3[index4_2] + AI_3[index4_0]
            jz_y5 = - AI_4[index5_3] + AI_4[index5_1]
            jz_x5 = - AI_4[index5_2] + AI_4[index5_0]
            jz_y6 = - AI_5[index6_3] + AI_5[index6_1]
            jz_x6 = - AI_5[index6_2] + AI_5[index6_0]

        except:
            print("二乘矩阵奇异")
            self.end_signal.emit(True)
            return

        mo1 = numpy.sqrt(jz_x1 ** 2 + jz_y1 ** 2)
        xj1 = numpy.arctan2(jz_y1, jz_x1) * 180 / numpy.pi
        mo2 = numpy.sqrt(jz_x2 ** 2 + jz_y2 ** 2)
        xj2 = numpy.arctan2(jz_y2, jz_x2) * 180 / numpy.pi
        mo3 = numpy.sqrt(jz_x3 ** 2 + jz_y3 ** 2)
        xj3 = (numpy.arctan2(jz_y3, jz_x3) * 180 / numpy.pi)    # - kesai3
        mo4 = numpy.sqrt(jz_x4 ** 2 + jz_y4 ** 2)
        xj4 = (numpy.arctan2(jz_y4, jz_x4) * 180 / numpy.pi)    # - kesai4
        mo5 = numpy.sqrt(jz_x5 ** 2 + jz_y5 ** 2)
        xj5 = (numpy.arctan2(jz_y5, jz_x5) * 180 / numpy.pi)    # - kesai5
        mo6 = numpy.sqrt(jz_x6 ** 2 + jz_y6 ** 2)
        xj6 = numpy.arctan2(jz_y6, jz_x6) * 180 / numpy.pi
        mo7 = numpy.sqrt(jz_x7 ** 2 + jz_y7 ** 2)
        xj7 = numpy.arctan2(jz_y7, jz_x7) * 180 / numpy.pi

        bar_mo = [round(mo1/350, 2),
                  round(mo2/700, 2),
                  round(mo3/700, 2),
                  round(mo4/700, 2),
                  round(mo5/700, 2),
                  round(mo6/700, 2),
                  round(mo7/350, 2)]
        bar_xj = [xj1,
                  xj2,
                  xj3,
                  xj4,
                  xj5,
                  xj6,
                  xj7]
        kesai = [kesai2, kesai3, kesai4, kesai5, kesai6]
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
                AI_ReadChannel(self.card_number, 5, self.ad_range, ctypes.pointer(value6))
                AI_ReadChannel(self.card_number, 6, self.ad_range, ctypes.pointer(value7))
                get_encoder(self.axis, ctypes.byref(aa))
                # print("读轴：", aa)
                AI_0.append(value1.value)
                AI_1.append(value2.value)
                AI_2.append(value3.value)
                AI_3.append(value4.value)
                AI_4.append(value5.value)
                AI_5.append(value6.value)
                AI_6.append(value7.value)
                axis_data.append(-1 * numpy.sign(aa.value) * (abs(aa.value) % self.num_pulses) * 360 / self.num_pulses)
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
    def find_closest_index(self, target, float_list):
        # 使用二分查找找到目标值应该插入的位置
        pos = bisect.bisect_left(float_list, target)
        # 判断插入位置周围的元素，选择最接近的
        if pos == 0:
            return 0  # 如果目标值小于等于列表中最小值
        if pos == len(float_list):
            return len(float_list) - 1  # 如果目标值大于等于列表中最大值
        # 计算目标值与相邻两个元素的差值
        before = float_list[pos - 1]
        after = float_list[pos]
        # 判断哪个元素与目标值更接近
        if abs(before - target) <= abs(after - target):
            return pos - 1
        else:
            return pos
    def remove_data(self, x, y, kesai, edge):
        lower_bound = kesai - edge
        upper_bound = kesai + edge

        # 处理边界情况
        if lower_bound < 0:
            lower_bound += 360
        if upper_bound >= 360:
            upper_bound -= 360

        # 找到需要删除的索引
        if lower_bound < upper_bound:
            indices_to_remove = numpy.where((x >= lower_bound) & (x <= upper_bound))[0]
        else:
            indices_to_remove_1 = numpy.where(x >= lower_bound)[0]
            indices_to_remove_2 = numpy.where(x <= upper_bound)[0]
            indices_to_remove = numpy.concatenate((indices_to_remove_1, indices_to_remove_2))

        # 删除对应索引的数据
        new_x = numpy.delete(x, indices_to_remove)
        new_y = numpy.delete(y, indices_to_remove)

        return new_x, new_y
class MySignals(QObject):
    log_update = pyqtSignal(str)  # 发送日志文本
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

def remove_data(x, y, kesai, edge):
    lower_bound = kesai - edge
    upper_bound = kesai + edge

    # 处理边界情况
    if lower_bound < 0:
        lower_bound += 360
    if upper_bound > 360:
        upper_bound -= 360

    # 找到需要删除的索引
    if lower_bound < upper_bound:
        indices_to_remove = numpy.where((x >= lower_bound) & (x <= upper_bound))[0]
    else:
        indices_to_remove_1 = numpy.where(x >= lower_bound)[0]
        indices_to_remove_2 = numpy.where(x <= upper_bound)[0]
        indices_to_remove = numpy.concatenate((indices_to_remove_1, indices_to_remove_2))

    # 删除对应索引的数据
    new_x = numpy.delete(x, indices_to_remove)
    new_y = numpy.delete(y, indices_to_remove)

    return new_x, new_y

if __name__ == "__main__":
    with open('TF-data/sy1.txt', 'r') as f:
        content = f.read().replace('\n', '')  # 移除换行符

        # 使用正则表达式提取所有方括号内的内容
    parts = re.findall(r'\[([^\]]*)\]', content)  # 提取所有方括号内的内容

    # 转换为整数列表（假设每个方括号对应一个变量）
    d1 = numpy.array(list(map(int, parts[0].split())))
    d5 = numpy.array(list(map(int, parts[1].split())))
    z = numpy.array(list(map(float, parts[2].split())))
    z = z * 21265 / 20765
    d1 = d1

#######################################################################################################################

    kesai = 19          # 19
    edge = 10
    #
    # new_x, new_y = remove_data(z, d1, kesai, edge)
    # new_x, new_y = remove_data(new_x, new_y, kesai + 90, edge)
    # new_x, new_y = remove_data(new_x, new_y, kesai + 180, edge)
    # new_x, new_y = remove_data(new_x, new_y, kesai + 270, edge)
    # print(len(z), len(new_x))
    new_x5, new_y5 = remove_data(z, d5, kesai, edge)
    new_x5, new_y5 = remove_data(new_x5, new_y5, kesai + 90, edge)
    new_x5, new_y5 = remove_data(new_x5, new_y5, kesai + 180, edge)
    new_x5, new_y5 = remove_data(new_x5, new_y5, kesai + 270, edge)
    # print(len(z), len(new_x5))
    # plt.figure(figsize=(10, 6))
    # plt.plot(new_x, new_y, linestyle='--', marker='', color='blue', linewidth=0.5)
    # plt.plot(z, d1, linestyle='-', marker='', color='blue', linewidth=0.5, label='d1 vs z')
    # plt.plot(new_x5, new_y5, linestyle='-', marker='', color='red', linewidth=0.5)
    # plt.plot(z, d5, linestyle='--', marker='', color='red', linewidth=0.5, label='d5 vs z')
    # plt.axvline(x=kesai, color='green', linestyle='--', linewidth=1)
    # plt.axvline(x=kesai + 90, color='green', linestyle='--', linewidth=1)
    # plt.axvline(x=kesai + 180, color='green', linestyle='--', linewidth=1)
    # plt.axvline(x=kesai + 270, color='green', linestyle='--', linewidth=1)
    #
    # plt.axvline(x=kesai - edge, color='black', linestyle='--', linewidth=1)
    # plt.axvline(x=kesai + 90 - edge, color='black', linestyle='--', linewidth=1)
    # plt.axvline(x=kesai + 180 - edge, color='black', linestyle='--', linewidth=1)
    # plt.axvline(x=kesai + 270 - edge, color='black', linestyle='--', linewidth=1)
    #
    # plt.axvline(x=kesai + edge, color='black', linestyle='--', linewidth=1)
    # plt.axvline(x=kesai + 90 + edge, color='black', linestyle='--', linewidth=1)
    # plt.axvline(x=kesai + 180 + edge, color='black', linestyle='--', linewidth=1)
    # plt.axvline(x=kesai + 270 + edge, color='black', linestyle='--', linewidth=1)
    # plt.title('Curve Plot of Points')
    # plt.xlabel('X-axis')
    # plt.ylabel('Y-axis')
    # plt.grid(True)
    # plt.show()
    #
    # jz_x, jz_y, jz_R = get_circle(d1, z)
    # print('去除推方前：',jz_x,jz_y)
    # print((jz_x ** 2 + jz_y ** 2) ** 0.5 / 300)
    #
    # jz_xx, jz_yy, jz_RR = get_circle(new_y, new_x)
    # print('去除推方后：',jz_x,jz_y)
    # print((jz_xx ** 2 + jz_yy ** 2) ** 0.5 / 300)
    #
    jz_x, jz_y, jz_R = get_circle(d5, z)
    print('去除推方前：',jz_x,jz_y)
    print((jz_x ** 2 + jz_y ** 2) ** 0.5 / 300)

    jz_xx, jz_yy, jz_RR = get_circle(new_y5, new_x5)
    print('去除推方后：',jz_x,jz_y)
    print((jz_x ** 2 + jz_y ** 2) ** 0.5 / 300)
    # # self.kesai = sorted(self.list_kesai)[1]
##################################################################################################################3

    # 转换为笛卡尔坐标
    x = d5 * numpy.cos(numpy.deg2rad(z))
    y = d5 * numpy.sin(numpy.deg2rad(z))
    # 创建一个新的图形窗口
    plt.figure(figsize=(800, 800))
    plt.scatter(x, y, cmap='hsv', s=1)
    plt.colorbar(label='Angle (degrees)')
    # 自定义圆心坐标
    center_x = jz_x
    center_y = jz_y
    circle_radii = [jz_R]
    circle_angles = numpy.linspace(0, 2 * numpy.pi, 100)
    for radius in circle_radii:
        circle_x = center_x + radius * numpy.cos(circle_angles)
        circle_y = center_y + radius * numpy.sin(circle_angles)
        plt.plot(circle_x, circle_y, color='black', linestyle='--')
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.title('Polar Scatter Plot')
    plt.axis('equal')
    plt.grid(True)

    # 转换为笛卡尔坐标
    x = new_y5 * numpy.cos(numpy.deg2rad(new_x5))
    y = new_y5 * numpy.sin(numpy.deg2rad(new_x5))
    # 创建一个新的图形窗口
    plt.figure(figsize=(800, 800))
    plt.scatter(x, y, cmap='hsv', s=1)
    plt.colorbar(label='Angle (degrees)')
    # 自定义圆心坐标
    center_x = jz_xx
    center_y = jz_yy
    circle_radii = [jz_RR]
    circle_angles = numpy.linspace(0, 2 * numpy.pi, 100)
    for radius in circle_radii:
        circle_x = center_x + radius * numpy.cos(circle_angles)
        circle_y = center_y + radius * numpy.sin(circle_angles)
        plt.plot(circle_x, circle_y, color='black', linestyle='--')
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.title('Polar Scatter Plot')
    plt.axis('equal')
    plt.grid(True)
    plt.show()