import threading
import time
from PyQt5.QtWidgets import (QLineEdit, QHBoxLayout, QPushButton, QTextEdit, QScrollArea,
                             QFormLayout, QApplication, QTabWidget, QRadioButton, QButtonGroup,
                             QMessageBox, QSpacerItem, QSizePolicy, QComboBox)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtGui import QIntValidator, QDoubleValidator
import matplotlib.ticker as ticker
from sympy.stats.sampling.sample_numpy import numpy
from PyQt5.QtCore import  QCoreApplication
from my_function import *
from ui_widge import *
from MPC08E import *
import numpy as np
import tulun
import snap7
import sys
import os

class MainWindow(QTabWidget):
    def __init__(self):
        super().__init__()
        self.mc_circle = 20765
        self.resize(1350, 1120)  # 设置初始大小
        # self.setFixedSize(1200, 1000)  # 设置固定大小
        # 最大化窗口
        self.showMaximized()
        self.work_id = 'yyfffyy'
        # 连接标签切换信号
        self.currentChanged.connect(self.on_tab_changed)
        self.setWindowTitle('矫直机')
        self.setWindowIcon(QIcon('images/UI/L.jpg'))
        self.card_number = 0  # 卡号
        self.ad_range = 1
        self.axis = 1
        self.mc_num = self.mc_circle
        # self.PLC_IP = '192.168.1.11'  # 替换为PLC的 IP地址、机架和插槽
        self.PLC_IP = '172.16.32.105'  # 替换为PLC的 IP地址、机架和插槽
        self.PLC_rack = 0
        self.PLC_slot = 1
        self.PLC_PORT = 502  # Modbus TCP 默认端口
        # 创建日志窗口
        self.log_widget = QTextEdit()
        self.log_widget.setReadOnly(True)
        # 设置轴卡
        r1 = mpc_lib.auto_set()
        r2 = mpc_lib.init_board()
        set_outmode(self.axis, 1, 1)
        set_conspeed(self.axis, 500)
        set_maxspeed(self.axis, 8000)
        reset_pos(self.axis)
        set_getpos_mode(self.axis, 1)
        self.f_tulun = tulun.Thita_with_Dis()
        self.auto()
        self.half_auto()
        self.hand()
        self.param_ui()
        self.sensor()
        self.about_me()
        self.load_param()
        self.log_widget.append(f"轴数:{r1}\n卡数:{r2}\n默认控制1轴")
        self.client_xmz = snap7.client.Client()
        # 绘制柱状图
        self.plot_bar_chart([0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00])
        self.auto_plot_bar_chart([0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00])
        try:
            self.client_xmz.connect(self.PLC_IP, self.PLC_rack, self.PLC_slot)
            color = 'green'
            message = f"成功连接PLC：：\n设备IP：{self.PLC_IP}"
            html_message = f'<span style="color: {color};">{message}</span>'
            self.hand_log_widget.append(html_message)
            self.hand_log_widget.ensureCursorVisible()
            self.auto_log_widget.append(html_message)
            self.auto_log_widget.ensureCursorVisible()
            self.log_widget.append(html_message)
            self.log_widget.ensureCursorVisible()
            # # 获取PLC的状态
            # status = self.client_xmz.get_cpu_state()
            # print(f"当前PLC状态: {status}")
            # # 如果PLC不在运行状态，则将其设置为运行状态
            # if status != snap7.types.CpuStatus.Run:
            #     self.client_xmz.plc_control(snap7.types.PlcControlCommand.Run)
            #     new_status = self.client_xmz.get_cpu_state()
            #     print(f"已尝试将PLC设置为运行状态，新状态: {new_status}")

        except Exception as e:
            color = 'red'
            message = f"连接失败：：{e} \n 设备IP：{self.PLC_IP}"
            html_message = f'<span style="color: {color};">{message}</span>'
            self.hand_log_widget.append(html_message)
            self.hand_log_widget.ensureCursorVisible()
            self.auto_log_widget.append(html_message)
            self.auto_log_widget.ensureCursorVisible()
            self.log_widget.append(html_message)
            self.log_widget.ensureCursorVisible()
        self.worker_thread = WorkerThread(1)
        self.worker_thread.caiji_signal.connect(self.new_data_info_ui)
        self.worker_thread.end_signal.connect(self.end_Thread)
        self.worker_thread.chart_signal.connect(self.updata_chart)
        self.circle_mode = "自动"

        self.signals = MySignals()  # 初始化信号
        self.signals.log_update.connect(self.update_log)  # 连接信号到槽
        self.yyfffyy = WorkerThread(2)
        self.yyfffyy.ec_signal.connect(self.new_data_hand_ui)
        self.yyfffyy.end_signal.connect(self.end_Thread)
        self.yfffffy = WorkerThread(4)
        self.yfffffy.ec_signal.connect(self.new_data_hand_ui)
        self.yfffffy.end_signal.connect(self.end_Thread)
        self.yyyyyyy = WorkerThread(3)
        self.yyyyyyy.ec_signal.connect(self.new_data_hand_ui)
        self.yyyyyyy.end_signal.connect(self.end_Thread)

        self.worker_thread_auto = self.yyfffyy
        self.list_kesai = [0, 0, 0]
        self.bar_mo = [0, 0, 0, 0, 0, 0, 0]
        self.bar_xj = [0, 0, 0, 0, 0, 0, 0]
        self.kesai = 0
        self.EN = True
        self.youliao = False
        self.yunxing = False
        self.PLC_isrun = True
        self.work_isrun = True
        self.ya_n = 0
        self.thita = 0
        self.Tulun = tulun.Thita_with_Dis()

        # self.list_kesai = [14, 15, 16]
        # self.bar_mo = [2.2, 3.7, 3.9, 2.6, 4.8, 2.7, 3.1]
        # self.bar_xj = [56, 65, 63, 37, 75, 26, 95]
        # self.kesai = 15
        # ok, ya_n, ya_real, thita = self.ya_strategy(0)

    def auto(self):
        data_widget = QWidget(self)     # 数据窗口（幅值、相角）
        ss1 = QWidget(self)  # 传感器
        ss2 = QWidget(self)  # 传感器
        ss3 = QWidget(self)  # 传感器
        ss4 = QWidget(self)  # 传感器
        ss5 = QWidget(self)  # 传感器
        ss6 = QWidget(self)  # 传感器
        ss7 = QWidget(self)  # 传感器

        layout_data = QHBoxLayout(data_widget)
        layout_ss1 = QVBoxLayout(ss1)
        layout_ss2 = QVBoxLayout(ss2)
        layout_ss3 = QVBoxLayout(ss3)
        layout_ss4 = QVBoxLayout(ss4)
        layout_ss5 = QVBoxLayout(ss5)
        layout_ss6 = QVBoxLayout(ss6)
        layout_ss7 = QVBoxLayout(ss7)

        layout_data.addWidget(ss1)
        layout_data.addWidget(ss2)
        layout_data.addWidget(ss3)
        layout_data.addWidget(ss4)
        layout_data.addWidget(ss5)
        layout_data.addWidget(ss6)
        layout_data.addWidget(ss7)

        ss1.setFixedSize(130, 450)  # 设置固定大小
        ss2.setFixedSize(130, 450)  # 设置固定大小
        ss3.setFixedSize(130, 450)  # 设置固定大小
        ss4.setFixedSize(130, 450)  # 设置固定大小
        ss5.setFixedSize(130, 450)  # 设置固定大小
        ss6.setFixedSize(130, 450)  # 设置固定大小
        ss7.setFixedSize(130, 450)  # 设置固定大小

        # 创建柱状图控件
        self.auto_figure1, self.auto_ax1 = plt.subplots(figsize=(1.8, 3.15))
        self.auto_figure2, self.auto_ax2 = plt.subplots(figsize=(1.8, 3.15))
        self.auto_figure3, self.auto_ax3 = plt.subplots(figsize=(1.8, 3.15))
        self.auto_figure4, self.auto_ax4 = plt.subplots(figsize=(1.8, 3.15))
        self.auto_figure5, self.auto_ax5 = plt.subplots(figsize=(1.8, 3.15))
        self.auto_figure6, self.auto_ax6 = plt.subplots(figsize=(1.8, 3.15))
        self.auto_figure7, self.auto_ax7 = plt.subplots(figsize=(1.8, 3.15))
        self.auto_canvas1 = FigureCanvas(self.auto_figure1)
        self.auto_canvas2 = FigureCanvas(self.auto_figure2)
        self.auto_canvas3 = FigureCanvas(self.auto_figure3)
        self.auto_canvas4 = FigureCanvas(self.auto_figure4)
        self.auto_canvas5 = FigureCanvas(self.auto_figure5)
        self.auto_canvas6 = FigureCanvas(self.auto_figure6)
        self.auto_canvas7 = FigureCanvas(self.auto_figure7)
        layout_ss1.addWidget(self.auto_canvas1)
        layout_ss2.addWidget(self.auto_canvas2)
        layout_ss3.addWidget(self.auto_canvas3)
        layout_ss4.addWidget(self.auto_canvas4)
        layout_ss5.addWidget(self.auto_canvas5)
        layout_ss6.addWidget(self.auto_canvas6)
        layout_ss7.addWidget(self.auto_canvas7)
        # layout_zzt.addStretch()
        self.auto_cs_widget1 = CircleWidget(angle=90)
        self.auto_cs_widget1.setMinimumSize(115, 115)
        layout_ss1.addWidget(self.auto_cs_widget1)
        self.auto_cs_widget2 = CircleWidget(angle=90)
        self.auto_cs_widget2.setMinimumSize(115, 115)
        layout_ss2.addWidget(self.auto_cs_widget2)
        self.auto_cs_widget3 = SqrtWidget(angle=90)
        self.auto_cs_widget3.setMinimumSize(115, 115)
        layout_ss3.addWidget(self.auto_cs_widget3)
        self.auto_cs_widget4 = SqrtWidget(angle=90)
        self.auto_cs_widget4.setMinimumSize(115, 115)
        layout_ss4.addWidget(self.auto_cs_widget4)
        self.auto_cs_widget5 = SqrtWidget(angle=90)
        self.auto_cs_widget5.setMinimumSize(115, 115)
        layout_ss5.addWidget(self.auto_cs_widget5)
        self.auto_cs_widget6 = CircleWidget(angle=90)
        self.auto_cs_widget6.setMinimumSize(115, 115)
        layout_ss6.addWidget(self.auto_cs_widget6)
        self.auto_cs_widget7 = CircleWidget(angle=90)
        self.auto_cs_widget7.setMinimumSize(115, 115)
        layout_ss7.addWidget(self.auto_cs_widget7)
        # data_widget.setFixedSize(2040, 600)  # 设置固定大小

        for i, figure in enumerate([self.auto_figure1, self.auto_figure2,
                                    self.auto_figure3,
                                    self.auto_figure4, self.auto_figure5,
                                    self.auto_figure6, self.auto_figure7]):
            figure.tight_layout(pad=1.0)
        self.auto_cs_widget7.setAngle(10)

        self.works = QComboBox(self)
        self.works.addItems(["    ⚪⚪ ■ ■ ■ ⚪⚪", "    ⚪⚪⚪⚪⚪⚪⚪", "    ⚪ ■ ■ ■ ■ ■ ⚪"])
        self.works.setStyleSheet("QComboBox QAbstractItemView::item { text-align: center; }")
        self.works.currentIndexChanged.connect(self.works_changed)

        layout_works = QFormLayout()
        layout_works.addRow('当前校正轴管模式：：', self.works)

        font_big = QFont('楷体', 18)
        # 创建各级窗口################################################################################
        Auto_widget = QWidget()
        Auto_up_widget = QWidget()
        Auto_down_widget = QWidget()
        Auto_Run_widget = QWidget()

        # 定义布局####################################################################################
        Auto_up_layout = QHBoxLayout()
        Auto_run_layout = QHBoxLayout()
        Auto_down_layout = QHBoxLayout()
        Auto_layout = QVBoxLayout()
        Auto_layout.addWidget(data_widget)

        Auto_layout.addLayout(layout_works)
        # 定义控件#####################################################################################
        # 创建按钮
        self.run_button = QPushButton("开始运行")
        self.end_button = QPushButton("结束检测")
        self.run_button.clicked.connect(self.auto_run)
        self.end_button.clicked.connect(self.auto_end)
        self.run_button.setFont(font_big)
        self.end_button.setFont(font_big)
        self.end_button.setStyleSheet(
            "QPushButton{color:white}"
            "QPushButton:hover{background-color: rgb(130,90,90);}"
            "QPushButton{background-color:rgb(210,90,90)}"
            "QPushButton{border:2px}"
            "QPushButton{border-radius:5px}"
            "QPushButton{padding:5px 5px}"
            "QPushButton{margin:5px 5px}"
            "QPushButton{width: 100px}"     # 设置按钮的宽度
            "QPushButton{height: 40px}"     # 设置按钮的高度
        )
        self.run_button.setStyleSheet(
            "QPushButton{color:white}"
            "QPushButton:hover{background-color: rgb(46,200,87);}"
            "QPushButton{background-color:rgb(46,146,87)}"
            "QPushButton{border:2px}"
            "QPushButton{border-radius:5px}"
            "QPushButton{padding:5px 5px}"
            "QPushButton{margin:5px 5px}"
            "QPushButton{width: 100px}"  # 设置按钮的宽度
            "QPushButton{height: 40px}"  # 设置按钮的高度
        )
        # 创建日志窗口的滚动区域
        self.auto_log_widget = QTextEdit()
        self.auto_log_widget.setReadOnly(True)
        scroll_area = QScrollArea()
        scroll_area.setWidget(self.auto_log_widget)
        scroll_area.setWidgetResizable(True)

        # 控件进布局###########################################################################
        # 布局（小窗口）进（大）窗口##############################################################
        Auto_up_layout.addWidget(scroll_area)
        Auto_up_widget.setLayout(Auto_up_layout)

        Auto_run_layout.addWidget(self.run_button)
        Auto_run_layout.addWidget(self.end_button)
        Auto_Run_widget.setLayout(Auto_run_layout)

        Auto_down_layout.addWidget(Auto_Run_widget)
        Auto_down_widget.setLayout(Auto_down_layout)

        Auto_layout.addWidget(Auto_up_widget)
        Auto_layout.addWidget(Auto_down_widget)
        Auto_widget.setLayout(Auto_layout)

        self.addTab(Auto_widget, '自动模式')
        self.setTabIcon(0, QIcon('images/UI/R.png'))
    def half_auto(self):
        # 创建中央窗口和布局
        M_widget = QWidget(self)        # 主窗口
        self.addTab(M_widget, '单检一周')
        self.setTabIcon(1, QIcon('images/UI/R.png'))

        # data_widget = QWidget(self)  # 数据窗口（幅值、相角）
        # layout_data = QFormLayout(data_widget)
        # up_widget = QWidget(self)
        # layout_up = QHBoxLayout(up_widget)
        # layout_up.addWidget(data_widget)
        # 创建QLabel控件
        # self.ss0 = QLabel("幅值      相角", self)
        # layout_data.addRow("", self.ss0)
        # self.sensors = []
        # for i in range(7):
        #     spacer = QSpacerItem(20, 10, QSizePolicy.Minimum, QSizePolicy.Expanding)
        #     layout_data.addItem(spacer)
        #     label = QLabel(f"0.00      0.00", self)
        #     layout_data.addRow(f"传感器{i+1}：", label)
        #     self.sensors.append(label)


        data_widget = QWidget(self)     # 数据窗口（幅值、相角）
        ss1 = QWidget(self)  # 传感器
        ss2 = QWidget(self)  # 传感器
        ss3 = QWidget(self)  # 传感器
        ss4 = QWidget(self)  # 传感器
        ss5 = QWidget(self)  # 传感器
        ss6 = QWidget(self)  # 传感器
        ss7 = QWidget(self)  # 传感器

        layout_data = QHBoxLayout(data_widget)
        layout_ss1 = QVBoxLayout(ss1)
        layout_ss2 = QVBoxLayout(ss2)
        layout_ss3 = QVBoxLayout(ss3)
        layout_ss4 = QVBoxLayout(ss4)
        layout_ss5 = QVBoxLayout(ss5)
        layout_ss6 = QVBoxLayout(ss6)
        layout_ss7 = QVBoxLayout(ss7)
        layout_M = QVBoxLayout(M_widget)
        # layout_M.addWidget(up_widget)

        layout_M.addWidget(data_widget)
        layout_data.addWidget(ss1)
        layout_data.addWidget(ss2)
        layout_data.addWidget(ss3)
        layout_data.addWidget(ss4)
        layout_data.addWidget(ss5)
        layout_data.addWidget(ss6)
        layout_data.addWidget(ss7)

        ss1.setFixedSize(130, 500)  # 设置固定大小
        ss2.setFixedSize(130, 500)  # 设置固定大小
        ss3.setFixedSize(130, 500)  # 设置固定大小
        ss4.setFixedSize(130, 500)  # 设置固定大小
        ss5.setFixedSize(130, 500)  # 设置固定大小
        ss6.setFixedSize(130, 500)  # 设置固定大小
        ss7.setFixedSize(130, 500)  # 设置固定大小

        # 创建柱状图控件
        self.figure1, self.ax1 = plt.subplots(figsize=(1.8, 3.65))
        self.figure2, self.ax2 = plt.subplots(figsize=(1.8, 3.65))
        self.figure3, self.ax3 = plt.subplots(figsize=(1.8, 3.65))
        self.figure4, self.ax4 = plt.subplots(figsize=(1.8, 3.65))
        self.figure5, self.ax5 = plt.subplots(figsize=(1.8, 3.65))
        self.figure6, self.ax6 = plt.subplots(figsize=(1.8, 3.65))
        self.figure7, self.ax7 = plt.subplots(figsize=(1.8, 3.65))
        self.canvas1 = FigureCanvas(self.figure1)
        self.canvas2 = FigureCanvas(self.figure2)
        self.canvas3 = FigureCanvas(self.figure3)
        self.canvas4 = FigureCanvas(self.figure4)
        self.canvas5 = FigureCanvas(self.figure5)
        self.canvas6 = FigureCanvas(self.figure6)
        self.canvas7 = FigureCanvas(self.figure7)
        layout_ss1.addWidget(self.canvas1)
        layout_ss2.addWidget(self.canvas2)
        layout_ss3.addWidget(self.canvas3)
        layout_ss4.addWidget(self.canvas4)
        layout_ss5.addWidget(self.canvas5)
        layout_ss6.addWidget(self.canvas6)
        layout_ss7.addWidget(self.canvas7)
        # layout_zzt.addStretch()
        self.cs_widget1 = CircleWidget(angle=90)
        self.cs_widget1.setMinimumSize(115, 115)
        layout_ss1.addWidget(self.cs_widget1)
        self.cs_widget2 = CircleWidget(angle=90)
        self.cs_widget2.setMinimumSize(115, 115)
        layout_ss2.addWidget(self.cs_widget2)
        self.cs_widget3 = SqrtWidget(angle=90)
        self.cs_widget3.setMinimumSize(115, 115)
        layout_ss3.addWidget(self.cs_widget3)
        self.cs_widget4 = SqrtWidget(angle=90)
        self.cs_widget4.setMinimumSize(115, 115)
        layout_ss4.addWidget(self.cs_widget4)
        self.cs_widget5 = SqrtWidget(angle=90)
        self.cs_widget5.setMinimumSize(115, 115)
        layout_ss5.addWidget(self.cs_widget5)
        self.cs_widget6 = CircleWidget(angle=90)
        self.cs_widget6.setMinimumSize(115, 115)
        layout_ss6.addWidget(self.cs_widget6)
        self.cs_widget7 = CircleWidget(angle=90)
        self.cs_widget7.setMinimumSize(115, 115)
        layout_ss7.addWidget(self.cs_widget7)
        # data_widget.setFixedSize(2040, 600)  # 设置固定大小

        for i, figure in enumerate([self.figure1, self.figure2, self.figure3, self.figure4, self.figure5, self.figure6, self.figure7]):
            figure.tight_layout(pad=1.0)
        self.cs_widget7.setAngle(10)

        # 创建按钮
        self.ks_button = QPushButton("开始采集")
        self.ks_button.clicked.connect(self.get_ai)
        self.js_button = QPushButton("结束采集")
        self.js_button.clicked.connect(self.stop)
        self.nh_button = QPushButton("自动拟合")
        self.nh_button.clicked.connect(self.half_auto_run)
        self.zd_button = QPushButton("转动")
        self.zd_button.clicked.connect(self.zhouka_zd)
        self.tz_button = QPushButton("停止")
        self.tz_button.clicked.connect(self.zhouka_tz)
        self.hl_button = QPushButton("回原点")
        self.hl_button.clicked.connect(self.zhouka_hl)
        # 创建输入框
        self.input_mc = QLineEdit()
        self.input_mc.setPlaceholderText(str(self.mc_num))
        self.input_mc.setAlignment(Qt.AlignCenter)
        int_validator = QIntValidator()
        self.input_mc.setValidator(int_validator)
        # 创建日志窗口的滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidget(self.log_widget)
        scroll_area.setWidgetResizable(True)
        # layout_up.addWidget(scroll_area)
        layout_M.addWidget(scroll_area)

        button_widget1 = QWidget(self)
        layout_button1 = QHBoxLayout(button_widget1)
        layout_button1.addWidget(self.ks_button)
        layout_button1.addWidget(self.js_button)
        layout_button1.addWidget(self.input_mc)
        layout_button1.addWidget(self.nh_button)
        layout_M.addWidget(button_widget1)

        button_widget2 = QWidget(self)
        layout_button2 = QHBoxLayout(button_widget2)
        layout_button2.addWidget(self.zd_button)
        layout_button2.addWidget(self.tz_button)
        layout_button2.addWidget(self.hl_button)
        layout_M.addWidget(button_widget2)
    def hand(self):
        # 创建中央窗口和布局
        M_widget = QWidget(self)        # 主窗口
        self.addTab(M_widget, '手动模式')
        self.setTabIcon(2, QIcon('images/UI/R.png'))
        layout_M = QVBoxLayout(M_widget)

        self.hand_log_widget = QTextEdit()
        self.hand_log_widget.setReadOnly(True)
        scroll_area = QScrollArea()
        # scroll_area.setFixedSize(990, 150)  # 设置固定大小
        scroll_area.setWidget(self.hand_log_widget)
        scroll_area.setWidgetResizable(True)
        # 创建按钮
        self.jz_stop = QPushButton('夹爪停止')
        # self.jz_stop.setFixedSize(200, 50)
        # self.jz_stop.setCheckable(True)  # 使按钮可以保持按下状态
        # self.jz_stop.pressed.connect(self.on_button_pressed)  # 上升沿
        # self.jz_stop.released.connect(self.on_button_released)  # 下降沿
        # 绑定鼠标按下和松开事件
        # self.button1.mousePressEvent = lambda event: self.on_mouse_press(event, self.button1)
        # self.button1.mouseReleaseEvent = lambda event: self.on_mouse_release(event, self.button1)
        # self.jz_stop.setChecked(False)  # 设置按钮为未按下状态
        self.jz_stop.clicked.connect(lambda: (
                                     self.fa_shuju(db_num=1, bit_ads=5, bool_value=True, txt="夹爪停止"),
                                     self.fa_shuju(db_num=1, bit_ads=1, bool_value=False),
                                     self.fa_shuju(db_num=1, bit_ads=2, bool_value=False),
                                     self.fa_shuju(db_num=1, bit_ads=3, bool_value=False),
                                     self.fa_shuju(db_num=1, bit_ads=4, bool_value=False),
                                     self.fa_shuju(db_num=1, bit_ads=6, bool_value=False),
                                     self.fa_shuju(db_num=1, bit_ads=7, bool_value=False),
                                     self.fa_shuju(db_num=1, bit_ads=8, bool_value=False),
                                     self.fa_shuju(db_num=1, bit_ads=9, bool_value=False),
                                     self.fa_shuju(db_num=1, bit_ads=85, bool_value=False),
                                     self.fa_shuju(db_num=1, bit_ads=52, bool_value=False),
                                     self.fa_shuju(db_num=1, bit_ads=53, bool_value=False),
                                     self.fa_shuju(db_num=1, bit_ads=77, bool_value=False),
                                     sudden_stop(self.axis)
                                     ))
        self.jz_up = QPushButton('夹爪上升')
        # self.jz_up.setFixedSize(200, 50)
        self.jz_up.clicked.connect(lambda: (
                                            self.fa_shuju(db_num=1, bit_ads=85, bool_value=False),
                                            self.fa_shuju(db_num=1, bit_ads=2, bool_value=True, txt="夹爪上升"),
                                            self.fa_shuju(db_num=1, bit_ads=5, bool_value=False),
                                            self.fa_shuju(db_num=1, bit_ads=8, bool_value=False),
                                            self.fa_shuju(db_num=1, bit_ads=82, bool_value=True),
                                            self.fa_shuju(db_num=1, bit_ads=52, bool_value=False),
                                            self.fa_shuju(db_num=1, bit_ads=77, bool_value=False),
                                            self.fa_shuju(db_num=1, bit_ads=53, bool_value=False)
                                            ))
        self.jz_down = QPushButton('夹爪下降')
        self.jz_down.clicked.connect(lambda: (
                                            self.fa_shuju(db_num=1, bit_ads=85, bool_value=False),
                                            self.fa_shuju(db_num=1, bit_ads=8, bool_value=True, txt="夹爪下降"),
                                            self.fa_shuju(db_num=1, bit_ads=5, bool_value=False),
                                            self.fa_shuju(db_num=1, bit_ads=2, bool_value=False),
                                            self.fa_shuju(db_num=1, bit_ads=82, bool_value=True),
                                            self.fa_shuju(db_num=1, bit_ads=52, bool_value=False),
                                            self.fa_shuju(db_num=1, bit_ads=77, bool_value=False),
                                            self.fa_shuju(db_num=1, bit_ads=53, bool_value=False)
                                            ))
        # self.jz_zz = QPushButton('夹爪正转')
        # self.jz_zz.clicked.connect(lambda: (self.fa_shuju(db_num=1, bit_ads=1, bool_value=True, txt="夹爪正转"),
        #                              self.fa_shuju(db_num=1, bit_ads=5, bool_value=False),
        #                              self.fa_shuju(db_num=1, bit_ads=3, bool_value=False)
        #                              ))
        # self.jz_fz = QPushButton('夹爪反转')
        # self.jz_fz.clicked.connect(lambda: (self.fa_shuju(db_num=1, bit_ads=3, bool_value=True, txt="夹爪反转"),
        #                              self.fa_shuju(db_num=1, bit_ads=5, bool_value=False),
        #                              self.fa_shuju(db_num=1, bit_ads=1, bool_value=False)
        #                              ))
        self.jz_zz = QPushButton('夹爪正转')
        self.jz_zz.mousePressEvent = lambda event: self.on_mouse_press(event, self.jz_zz)
        self.jz_zz.mouseReleaseEvent = lambda event: self.on_mouse_release(event, self.jz_zz)
        self.jz_fz = QPushButton('夹爪反转')
        self.jz_fz.mousePressEvent = lambda event: self.on_mouse_press(event, self.jz_fz)
        self.jz_fz.mouseReleaseEvent = lambda event: self.on_mouse_release(event, self.jz_fz)
        self.jz_qj = QPushButton('夹爪前进')
        self.jz_qj.clicked.connect(lambda: (self.fa_shuju(db_num=1, bit_ads=85, bool_value=False),
                                            self.fa_shuju(db_num=1, bit_ads=6, bool_value=True, txt="夹爪前进"),
                                            self.fa_shuju(db_num=1, bit_ads=5, bool_value=False),
                                            self.fa_shuju(db_num=1, bit_ads=4, bool_value=False),
                                            self.fa_shuju(db_num=1, bit_ads=82, bool_value=True),
                                            self.fa_shuju(db_num=1, bit_ads=52, bool_value=False),
                                            self.fa_shuju(db_num=1, bit_ads=77, bool_value=False),
                                            self.fa_shuju(db_num=1, bit_ads=53, bool_value=False)
                                            ))
        self.jz_ht = QPushButton('夹爪后退')
        self.jz_ht.clicked.connect(lambda: (self.fa_shuju(db_num=1, bit_ads=85, bool_value=False),
                                            self.fa_shuju(db_num=1, bit_ads=4, bool_value=True, txt="夹爪后退"),
                                            self.fa_shuju(db_num=1, bit_ads=5, bool_value=False),
                                            self.fa_shuju(db_num=1, bit_ads=6, bool_value=False),
                                            self.fa_shuju(db_num=1, bit_ads=82, bool_value=True),
                                            self.fa_shuju(db_num=1, bit_ads=52, bool_value=False),
                                            self.fa_shuju(db_num=1, bit_ads=77, bool_value=False),
                                            self.fa_shuju(db_num=1, bit_ads=53, bool_value=False)
                                            ))
        self.jz_jj = QPushButton('夹爪夹紧')
        self.jz_jj.clicked.connect(lambda: (self.fa_shuju(db_num=1, bit_ads=85, bool_value=False),
                                            self.fa_shuju(db_num=1, bit_ads=7, bool_value=True, txt="夹爪夹紧"),
                                            self.fa_shuju(db_num=1, bit_ads=5, bool_value=False),
                                            self.fa_shuju(db_num=1, bit_ads=9, bool_value=False),
                                            self.fa_shuju(db_num=1, bit_ads=82, bool_value=True),
                                            self.fa_shuju(db_num=1, bit_ads=52, bool_value=False),
                                            self.fa_shuju(db_num=1, bit_ads=77, bool_value=False),
                                            self.fa_shuju(db_num=1, bit_ads=53, bool_value=False)
                                            ))
        self.jz_fs = QPushButton('夹爪放松')
        self.jz_fs.clicked.connect(lambda: (self.fa_shuju(db_num=1, bit_ads=85, bool_value=False),
                                            self.fa_shuju(db_num=1, bit_ads=9, bool_value=True, txt="夹爪放松"),
                                            self.fa_shuju(db_num=1, bit_ads=5, bool_value=False),
                                            self.fa_shuju(db_num=1, bit_ads=7, bool_value=False),
                                            self.fa_shuju(db_num=1, bit_ads=82, bool_value=True),
                                            self.fa_shuju(db_num=1, bit_ads=52, bool_value=False),
                                            self.fa_shuju(db_num=1, bit_ads=77, bool_value=False),
                                            self.fa_shuju(db_num=1, bit_ads=53, bool_value=False)
                                            ))
        # 红色按钮
        self.jz_stop.setStyleSheet(
            "QPushButton{"
            "color:white;"
            "background-color:rgb(210,90,90);"
            "}"
            "QPushButton:hover{"
            "background-color: rgb(130,90,90);"
            "}"
            "QPushButton:pressed{"  # 当按钮被按下时的样式
            "background-color: rgb(210,90,90);"  # 按下时的背景颜色
            "}"
        )
        self.bj_stop = QPushButton('步进停止')
        self.bj_stop.clicked.connect(lambda: (self.fa_shuju(db_num=1, bit_ads=15, bool_value=True, txt="步进停止"),
                                            self.fa_shuju(db_num=1, bit_ads=11, bool_value=False),
                                            self.fa_shuju(db_num=1, bit_ads=12, bool_value=False),
                                            self.fa_shuju(db_num=1, bit_ads=13, bool_value=False),
                                            self.fa_shuju(db_num=1, bit_ads=14, bool_value=False),
                                            self.fa_shuju(db_num=1, bit_ads=16, bool_value=False),
                                            self.fa_shuju(db_num=1, bit_ads=17, bool_value=False),
                                            self.fa_shuju(db_num=1, bit_ads=18, bool_value=False),
                                            self.fa_shuju(db_num=1, bit_ads=84, bool_value=False)
                                            # self.fa_shuju(db_num=1, bit_ads=82, bool_value=False)
                                            ))
        self.bj_up = QPushButton('步进上升')
        self.bj_up.clicked.connect(lambda: (self.fa_shuju(db_num=1, bit_ads=17, bool_value=True, txt="步进上升"),
                                            self.fa_shuju(db_num=1, bit_ads=15, bool_value=False),
                                            self.fa_shuju(db_num=1, bit_ads=18, bool_value=False),
                                            self.fa_shuju(db_num=1, bit_ads=12, bool_value=False),
                                            self.fa_shuju(db_num=1, bit_ads=84, bool_value=False),
                                            self.fa_shuju(db_num=1, bit_ads=82, bool_value=True)
                                            ))
        self.bj_down = QPushButton('步进下降')
        self.bj_down.clicked.connect(lambda: (self.fa_shuju(db_num=1, bit_ads=18, bool_value=True, txt="步进下降"),
                                            self.fa_shuju(db_num=1, bit_ads=15, bool_value=False),
                                            self.fa_shuju(db_num=1, bit_ads=17, bool_value=False),
                                            self.fa_shuju(db_num=1, bit_ads=12, bool_value=False),
                                            self.fa_shuju(db_num=1, bit_ads=84, bool_value=False),
                                            self.fa_shuju(db_num=1, bit_ads=82, bool_value=True)
                                            ))
        self.bj_zq = QPushButton('步进最前')
        self.bj_zq.clicked.connect(lambda: (self.fa_shuju(db_num=1, bit_ads=13, bool_value=True, txt="步进最前"),
                                            self.fa_shuju(db_num=1, bit_ads=15, bool_value=False),
                                            self.fa_shuju(db_num=1, bit_ads=11, bool_value=False),
                                            self.fa_shuju(db_num=1, bit_ads=12, bool_value=False),
                                            self.fa_shuju(db_num=1, bit_ads=84, bool_value=False),
                                            self.fa_shuju(db_num=1, bit_ads=82, bool_value=True)
                                            ))
        self.bj_zh = QPushButton('步进最后')
        self.bj_zh.clicked.connect(lambda: (self.fa_shuju(db_num=1, bit_ads=11, bool_value=True, txt="步进最后"),
                                            self.fa_shuju(db_num=1, bit_ads=15, bool_value=False),
                                            self.fa_shuju(db_num=1, bit_ads=13, bool_value=False),
                                            self.fa_shuju(db_num=1, bit_ads=12, bool_value=False),
                                            self.fa_shuju(db_num=1, bit_ads=84, bool_value=False),
                                            self.fa_shuju(db_num=1, bit_ads=82, bool_value=True)
                                            ))
        self.bj_qj = QPushButton('步进前进')
        self.bj_qj.mousePressEvent = lambda event: self.on_mouse_press(event, self.bj_qj)
        self.bj_qj.mouseReleaseEvent = lambda event: self.on_mouse_release(event, self.bj_qj)
        self.bj_ht = QPushButton('步进后退')
        self.bj_ht.mousePressEvent = lambda event: self.on_mouse_press(event, self.bj_ht)
        self.bj_ht.mouseReleaseEvent = lambda event: self.on_mouse_release(event, self.bj_ht)
        self.bj_hl = QPushButton('步进回零')
        self.bj_hl.clicked.connect(lambda: (self.fa_shuju(db_num=1, bit_ads=12, bool_value=True, txt="步进回零"),
                                            self.fa_shuju(db_num=1, bit_ads=11, bool_value=False),
                                            self.fa_shuju(db_num=1, bit_ads=15, bool_value=False),
                                            self.fa_shuju(db_num=1, bit_ads=13, bool_value=False),
                                            self.fa_shuju(db_num=1, bit_ads=14, bool_value=False),
                                            self.fa_shuju(db_num=1, bit_ads=16, bool_value=False),
                                            self.fa_shuju(db_num=1, bit_ads=17, bool_value=False),
                                            self.fa_shuju(db_num=1, bit_ads=18, bool_value=False),
                                            self.fa_shuju(db_num=1, bit_ads=84, bool_value=True),
                                            self.fa_shuju(db_num=1, bit_ads=82, bool_value=True)
                                            ))
        # 红色按钮
        self.bj_stop.setStyleSheet(
            "QPushButton{"
            "color:white;"
            "background-color:rgb(210,90,90);"
            "}" 
            "QPushButton:hover{"
            "background-color: rgb(130,90,90);"
            "}"
            "QPushButton:pressed{"  # 当按钮被按下时的样式
            "background-color: rgb(210,90,90);"  # 按下时的背景颜色
            "}"
        )
        # 绿色按钮
        self.bj_hl.setStyleSheet(
                "QPushButton {"
                "color: white;"  # 字体颜色
                "background-color: rgb(46, 146, 87);"  # 默认背景颜色
                "}"
                "QPushButton:hover {"
                "background-color: rgb(46, 200, 87);}"  # 悬停时背景颜色
                "QPushButton:pressed{"  # 当按钮被按下时的样式
                "background-color: rgb(46,146,87);"  # 按下时的背景颜色
                "}"
        )
        self.yt_j1 = QPushButton('1#压头进')
        self.yt_j1.clicked.connect(lambda: (self.fa_shuju(db_num=1, bit_ads=20, bool_value=True, txt="1#压头进"),
                                     self.fa_shuju(db_num=1, bit_ads=21, bool_value=False),
                                     self.fa_shuju(db_num=1, bit_ads=32, bool_value=False),
                                     self.fa_shuju(db_num=1, bit_ads=33, bool_value=False)
                                     ))
        self.yt_c1 = QPushButton('1#压头出')
        self.yt_c1.clicked.connect(lambda: (self.fa_shuju(db_num=1, bit_ads=21, bool_value=True, txt="1#压头出"),
                                     self.fa_shuju(db_num=1, bit_ads=20, bool_value=False),
                                     self.fa_shuju(db_num=1, bit_ads=32, bool_value=False)
                                     ))
        self.yt_j2 = QPushButton('2#压头进')
        self.yt_j2.clicked.connect(lambda: (self.fa_shuju(db_num=1, bit_ads=22, bool_value=True, txt="2#压头进"),
                                     self.fa_shuju(db_num=1, bit_ads=23, bool_value=False),
                                     self.fa_shuju(db_num=1, bit_ads=32, bool_value=False),
                                     self.fa_shuju(db_num=1, bit_ads=33, bool_value=False)
                                     ))
        self.yt_c2 = QPushButton('2#压头出')
        self.yt_c2.clicked.connect(lambda: (self.fa_shuju(db_num=1, bit_ads=23, bool_value=True, txt="2#压头出"),
                                     self.fa_shuju(db_num=1, bit_ads=22, bool_value=False),
                                     self.fa_shuju(db_num=1, bit_ads=32, bool_value=False)
                                     ))
        self.yt_j3 = QPushButton('3#压头进')
        self.yt_j3.clicked.connect(lambda: (self.fa_shuju(db_num=1, bit_ads=24, bool_value=True, txt="3#压头进"),
                                     self.fa_shuju(db_num=1, bit_ads=25, bool_value=False),
                                     self.fa_shuju(db_num=1, bit_ads=32, bool_value=False),
                                     self.fa_shuju(db_num=1, bit_ads=33, bool_value=False)
                                     ))
        self.yt_c3 = QPushButton('3#压头出')
        self.yt_c3.clicked.connect(lambda: (self.fa_shuju(db_num=1, bit_ads=25, bool_value=True, txt="3#压头出"),
                                     self.fa_shuju(db_num=1, bit_ads=24, bool_value=False),
                                     self.fa_shuju(db_num=1, bit_ads=32, bool_value=False)
                                     ))
        self.yt_j4 = QPushButton('4#压头进')
        self.yt_j4.clicked.connect(lambda: (self.fa_shuju(db_num=1, bit_ads=26, bool_value=True, txt="4#压头进"),
                                     self.fa_shuju(db_num=1, bit_ads=27, bool_value=False),
                                     self.fa_shuju(db_num=1, bit_ads=32, bool_value=False),
                                     self.fa_shuju(db_num=1, bit_ads=33, bool_value=False)
                                     ))
        self.yt_c4 = QPushButton('4#压头出')
        self.yt_c4.clicked.connect(lambda: (self.fa_shuju(db_num=1, bit_ads=27, bool_value=True, txt="4#压头出"),
                                     self.fa_shuju(db_num=1, bit_ads=26, bool_value=False),
                                     self.fa_shuju(db_num=1, bit_ads=32, bool_value=False)
                                     ))
        self.yt_j5 = QPushButton('5#压头进')
        self.yt_j5.clicked.connect(lambda: (self.fa_shuju(db_num=1, bit_ads=28, bool_value=True, txt="5#压头进"),
                                     self.fa_shuju(db_num=1, bit_ads=29, bool_value=False),
                                     self.fa_shuju(db_num=1, bit_ads=32, bool_value=False),
                                     self.fa_shuju(db_num=1, bit_ads=33, bool_value=False)
                                     ))
        self.yt_c5 = QPushButton('5#压头出')
        self.yt_c5.clicked.connect(lambda: (self.fa_shuju(db_num=1, bit_ads=29, bool_value=True, txt="5#压头出"),
                                     self.fa_shuju(db_num=1, bit_ads=28, bool_value=False),
                                     self.fa_shuju(db_num=1, bit_ads=32, bool_value=False)
                                     ))
        self.yt_up = QPushButton('压头抬起')
        self.yt_up.mousePressEvent = lambda event: self.on_mouse_press(event, self.yt_up)
        self.yt_up.mouseReleaseEvent = lambda event: self.on_mouse_release(event, self.yt_up)
        # self.yt_up.clicked.connect(lambda: (self.fa_shuju(db_num=1, bit_ads=30, bool_value=True, txt="压头抬起"),
        #                              self.fa_shuju(db_num=1, bit_ads=31, bool_value=False),
        #                              self.fa_shuju(db_num=1, bit_ads=32, bool_value=False)
        #                              ))
        self.yt_down = QPushButton('压头下压')
        self.yt_down.mousePressEvent = lambda event: self.on_mouse_press(event, self.yt_down)
        self.yt_down.mouseReleaseEvent = lambda event: self.on_mouse_release(event, self.yt_down)
        # self.yt_down.clicked.connect(lambda: (self.fa_shuju(db_num=1, bit_ads=31, bool_value=True, txt="压头下压"),
        #                              self.fa_shuju(db_num=1, bit_ads=30, bool_value=False),
        #                              self.fa_shuju(db_num=1, bit_ads=32, bool_value=False),
        #                              self.fa_shuju(db_num=1, bit_ads=33, bool_value=False)
        #                              ))
        self.yt_stop = QPushButton('压头停止')
        self.yt_stop.clicked.connect(lambda: (self.fa_shuju(db_num=1, bit_ads=32, bool_value=True, txt="压头停止"),
                                            self.fa_shuju(db_num=1, bit_ads=30, bool_value=False),
                                            self.fa_shuju(db_num=1, bit_ads=31, bool_value=False),
                                            self.fa_shuju(db_num=1, bit_ads=33, bool_value=False),
                                            self.fa_shuju(db_num=1, bit_ads=20, bool_value=False),
                                            self.fa_shuju(db_num=1, bit_ads=21, bool_value=False),
                                            self.fa_shuju(db_num=1, bit_ads=22, bool_value=False),
                                            self.fa_shuju(db_num=1, bit_ads=23, bool_value=False),
                                            self.fa_shuju(db_num=1, bit_ads=24, bool_value=False),
                                            self.fa_shuju(db_num=1, bit_ads=25, bool_value=False),
                                            self.fa_shuju(db_num=1, bit_ads=26, bool_value=False),
                                            self.fa_shuju(db_num=1, bit_ads=27, bool_value=False),
                                            self.fa_shuju(db_num=1, bit_ads=28, bool_value=False),
                                            self.fa_shuju(db_num=1, bit_ads=29, bool_value=False),
                                            self.fa_shuju(db_num=1, bit_ads=81, bool_value=False)
                                     ))
        self.yt_hl = QPushButton('压头回零')
        self.yt_hl.clicked.connect(lambda: (self.fa_shuju(db_num=1, bit_ads=33, bool_value=True, txt="压头回零"),
                                     self.fa_shuju(db_num=1, bit_ads=30, bool_value=False),
                                     self.fa_shuju(db_num=1, bit_ads=31, bool_value=False),
                                     self.fa_shuju(db_num=1, bit_ads=32, bool_value=False),
                                     self.fa_shuju(db_num=1, bit_ads=20, bool_value=False),
                                     self.fa_shuju(db_num=1, bit_ads=21, bool_value=True),
                                     self.fa_shuju(db_num=1, bit_ads=22, bool_value=False),
                                     self.fa_shuju(db_num=1, bit_ads=23, bool_value=True),
                                     self.fa_shuju(db_num=1, bit_ads=24, bool_value=False),
                                     self.fa_shuju(db_num=1, bit_ads=25, bool_value=True),
                                     self.fa_shuju(db_num=1, bit_ads=26, bool_value=False),
                                     self.fa_shuju(db_num=1, bit_ads=27, bool_value=True),
                                     self.fa_shuju(db_num=1, bit_ads=28, bool_value=False),
                                     self.fa_shuju(db_num=1, bit_ads=29, bool_value=True),
                                     self.fa_shuju(db_num=1, bit_ads=81, bool_value=True)
                                     ))
        # 红色按钮
        self.yt_stop.setStyleSheet(
            "QPushButton{"
            "color:white;"
            "background-color:rgb(210,90,90);"
            "}"
            "QPushButton:hover{"
            "background-color: rgb(130,90,90);"
            "}"
            "QPushButton:pressed{"  # 当按钮被按下时的样式
            "background-color: rgb(210,90,90);"  # 按下时的背景颜色
            "}"
        )
        # 绿色按钮
        self.yt_hl.setStyleSheet(
                "QPushButton {"
                "color: white;"  # 字体颜色
                "background-color: rgb(46, 146, 87);"  # 默认背景颜色
                "}"
                "QPushButton:hover {"
                "background-color: rgb(46, 200, 87);}"  # 悬停时背景颜色
                "QPushButton:pressed{"  # 当按钮被按下时的样式
                "background-color: rgb(46,146,87);"  # 按下时的背景颜色
                "}"
        )
        self.qn_stop = QPushButton('气囊停止')
        self.qn_stop.clicked.connect(lambda: (self.fa_shuju(db_num=1, bit_ads=35, bool_value=True, txt="气囊停止"),
                                              self.fa_shuju(db_num=1, bit_ads=34, bool_value=False),
                                              self.fa_shuju(db_num=1, bit_ads=36, bool_value=False)
                                              ))
        self.qn_on = QPushButton('气囊充气')
        self.qn_on.clicked.connect(lambda: (self.fa_shuju(db_num=1, bit_ads=34, bool_value=True, txt="气囊充气"),
                                            self.fa_shuju(db_num=1, bit_ads=35, bool_value=False),
                                            self.fa_shuju(db_num=1, bit_ads=36, bool_value=False)
                                            ))
        self.qn_off = QPushButton('气囊放气')
        self.qn_off.clicked.connect(lambda: (self.fa_shuju(db_num=1, bit_ads=36, bool_value=True, txt="气囊放气"),
                                             self.fa_shuju(db_num=1, bit_ads=35, bool_value=False),
                                             self.fa_shuju(db_num=1, bit_ads=34, bool_value=False)
                                             ))
        # 红色按钮
        self.qn_stop.setStyleSheet(
            "QPushButton{"
            "color:white;"
            "background-color:rgb(210,90,90);"
            "}"
            "QPushButton:hover{"
            "background-color: rgb(130,90,90);"
            "}"
            "QPushButton:pressed{"  # 当按钮被按下时的样式
            "background-color: rgb(210,90,90);"  # 按下时的背景颜色
            "}"
        )
        self.zp_stop = QPushButton('找平停止')
        self.zp_stop.clicked.connect(lambda: (self.fa_shuju(db_num=1, bit_ads=38, bool_value=True, txt="找平停止"),
                                              self.fa_shuju(db_num=1, bit_ads=37, bool_value=False),
                                              self.fa_shuju(db_num=1, bit_ads=39, bool_value=False)
                                              ))
        self.zp_up = QPushButton('找平上升')
        self.zp_up.clicked.connect(lambda: (self.fa_shuju(db_num=1, bit_ads=37, bool_value=True, txt="找平上升"),
                                            self.fa_shuju(db_num=1, bit_ads=38, bool_value=False),
                                            self.fa_shuju(db_num=1, bit_ads=39, bool_value=False)
                                            ))
        self.zp_down = QPushButton('找平下降')
        self.zp_down.clicked.connect(lambda: (self.fa_shuju(db_num=1, bit_ads=39, bool_value=True, txt="找平下降"),
                                              self.fa_shuju(db_num=1, bit_ads=37, bool_value=False),
                                              self.fa_shuju(db_num=1, bit_ads=38, bool_value=False)
                                              ))
        # 红色按钮
        self.zp_stop.setStyleSheet(
            "QPushButton{"
            "color:white;"
            "background-color:rgb(210,90,90);"
            "}"
            "QPushButton:hover{"
            "background-color: rgb(130,90,90);"
            "}"
            "QPushButton:pressed{"  # 当按钮被按下时的样式
            "background-color: rgb(210,90,90);"  # 按下时的背景颜色
            "}"
        )
        self.zc1_up = QPushButton('1#支撑进')
        self.zc1_up.clicked.connect(lambda: (self.fa_shuju(db_num=1, bit_ads=40, bool_value=True, txt="1#支撑进"),
                                              self.fa_shuju(db_num=1, bit_ads=41, bool_value=False),
                                              self.fa_shuju(db_num=1, bit_ads=42, bool_value=False)
                                              ))
        self.zc1_stop = QPushButton('1#支撑停')
        self.zc1_stop.clicked.connect(lambda: (self.fa_shuju(db_num=1, bit_ads=41, bool_value=True, txt="1#支撑停"),
                                              self.fa_shuju(db_num=1, bit_ads=42, bool_value=False),
                                              self.fa_shuju(db_num=1, bit_ads=40, bool_value=False)
                                              ))
        self.zc1_down = QPushButton('1#支撑退')
        self.zc1_down.clicked.connect(lambda: (self.fa_shuju(db_num=1, bit_ads=42, bool_value=True, txt="1#支撑退"),
                                              self.fa_shuju(db_num=1, bit_ads=40, bool_value=False),
                                              self.fa_shuju(db_num=1, bit_ads=41, bool_value=False)
                                              ))
        # 红色按钮
        self.zc1_stop.setStyleSheet(
            "QPushButton{"
            "color:white;"
            "background-color:rgb(210,90,90);"
            "}"
            "QPushButton:hover{"
            "background-color: rgb(130,90,90);"
            "}"
            "QPushButton:pressed{"  # 当按钮被按下时的样式
            "background-color: rgb(210,90,90);"  # 按下时的背景颜色
            "}"
        )
        self.zc2_up = QPushButton('2#支撑进')
        self.zc2_up.clicked.connect(lambda: (self.fa_shuju(db_num=1, bit_ads=43, bool_value=True, txt="2#支撑进"),
                                              self.fa_shuju(db_num=1, bit_ads=44, bool_value=False),
                                              self.fa_shuju(db_num=1, bit_ads=45, bool_value=False)
                                              ))
        self.zc2_stop = QPushButton('2#支撑停')
        self.zc2_stop.clicked.connect(lambda: (self.fa_shuju(db_num=1, bit_ads=44, bool_value=True, txt="2#支撑停"),
                                              self.fa_shuju(db_num=1, bit_ads=43, bool_value=False),
                                              self.fa_shuju(db_num=1, bit_ads=45, bool_value=False)
                                              ))
        self.zc2_down = QPushButton('2#支撑退')
        self.zc2_down.clicked.connect(lambda: (self.fa_shuju(db_num=1, bit_ads=45, bool_value=True, txt="2#支撑退"),
                                              self.fa_shuju(db_num=1, bit_ads=43, bool_value=False),
                                              self.fa_shuju(db_num=1, bit_ads=44, bool_value=False)
                                              ))
        # 红色按钮
        self.zc2_stop.setStyleSheet(
            "QPushButton{"
            "color:white;"
            "background-color:rgb(210,90,90);"
            "}"
            "QPushButton:hover{"
            "background-color: rgb(130,90,90);"
            "}"
            "QPushButton:pressed{"  # 当按钮被按下时的样式
            "background-color: rgb(210,90,90);"  # 按下时的背景颜色
            "}"
        )
        self.zc3_up = QPushButton('3#支撑进')
        self.zc3_up.clicked.connect(lambda: (self.fa_shuju(db_num=1, bit_ads=46, bool_value=True, txt="3#支撑进"),
                                               self.fa_shuju(db_num=1, bit_ads=47, bool_value=False),
                                               self.fa_shuju(db_num=1, bit_ads=48, bool_value=False)
                                               ))
        self.zc3_stop = QPushButton('3#支撑停')
        self.zc3_stop.clicked.connect(lambda: (self.fa_shuju(db_num=1, bit_ads=47, bool_value=True, txt="3#支撑停"),
                                               self.fa_shuju(db_num=1, bit_ads=46, bool_value=False),
                                               self.fa_shuju(db_num=1, bit_ads=48, bool_value=False)
                                               ))
        self.zc3_down = QPushButton('3#支撑退')
        self.zc3_down.clicked.connect(lambda: (self.fa_shuju(db_num=1, bit_ads=48, bool_value=True, txt="3#支撑退"),
                                               self.fa_shuju(db_num=1, bit_ads=47, bool_value=False),
                                               self.fa_shuju(db_num=1, bit_ads=46, bool_value=False)
                                               ))
        # 红色按钮
        self.zc3_stop.setStyleSheet(
            "QPushButton{"
            "color:white;"
            "background-color:rgb(210,90,90);"
            "}"
            "QPushButton:hover{"
            "background-color: rgb(130,90,90);"
            "}"
            "QPushButton:pressed{"  # 当按钮被按下时的样式
            "background-color: rgb(210,90,90);"  # 按下时的背景颜色
            "}"
        )
        self.zc4_up = QPushButton('4#支撑进')
        self.zc4_up.clicked.connect(lambda: (self.fa_shuju(db_num=1, bit_ads=49, bool_value=True, txt="4#支撑进"),
                                               self.fa_shuju(db_num=1, bit_ads=50, bool_value=False),
                                               self.fa_shuju(db_num=1, bit_ads=51, bool_value=False)
                                               ))
        self.zc4_stop = QPushButton('4#支撑停')
        self.zc4_stop.clicked.connect(lambda: (self.fa_shuju(db_num=1, bit_ads=50, bool_value=True, txt="4#支撑停"),
                                               self.fa_shuju(db_num=1, bit_ads=49, bool_value=False),
                                               self.fa_shuju(db_num=1, bit_ads=51, bool_value=False)
                                               ))
        self.zc4_down = QPushButton('4#支撑退')
        self.zc4_down.clicked.connect(lambda: (self.fa_shuju(db_num=1, bit_ads=51, bool_value=True, txt="4#支撑退"),
                                               self.fa_shuju(db_num=1, bit_ads=50, bool_value=False),
                                               self.fa_shuju(db_num=1, bit_ads=49, bool_value=False)
                                               ))
        # 红色按钮
        self.zc4_stop.setStyleSheet(
            "QPushButton{"
            "color:white;"
            "background-color:rgb(210,90,90);"
            "}"
            "QPushButton:hover{"
            "background-color: rgb(130,90,90);"
            "}"
            "QPushButton:pressed{"  # 当按钮被按下时的样式
            "background-color: rgb(210,90,90);"  # 按下时的背景颜色
            "}"
        )

        self.jcl = QPushButton('进/出料')
        self.jcl.clicked.connect(lambda: (self.fa_shuju(db_num=1, bit_ads=54, bool_value=True, txt="进/出料"),
                                          self.fa_shuju(db_num=1, bit_ads=82, bool_value=True),
                                          self.fa_shuju(db_num=1, bit_ads=84, bool_value=True)
                                           ))
        self.xy_real = QPushButton('下压real')
        self.xy_real.clicked.connect(self.xiaya_real)
        self.jz_zb = QPushButton('夹爪准备')
        self.jz_zb.clicked.connect(lambda: (self.fa_shuju(db_num=1, bit_ads=85, bool_value=True),
                                            self.fa_shuju(db_num=1, bit_ads=52, bool_value=False),
                                            self.fa_shuju(db_num=1, bit_ads=77, bool_value=False),
                                            self.fa_shuju(db_num=1, bit_ads=53, bool_value=True, txt="夹爪准备"),
                                            self.fa_shuju(db_num=1, bit_ads=82, bool_value=True),
                                            self.fa_shuju(db_num=1, bit_ads=5, bool_value=False)
                                            ))
        self.jz_fw = QPushButton('夹爪复位')
        self.jz_fw.clicked.connect(lambda: (self.fa_shuju(db_num=1, bit_ads=85, bool_value=True),
                                            self.fa_shuju(db_num=1, bit_ads=53, bool_value=False),
                                            self.fa_shuju(db_num=1, bit_ads=77, bool_value=False),
                                            self.fa_shuju(db_num=1, bit_ads=52, bool_value=True, txt="夹爪复位"),
                                            self.fa_shuju(db_num=1, bit_ads=82, bool_value=True),
                                            self.fa_shuju(db_num=1, bit_ads=5, bool_value=False)
                                            ))
        # 绿色按钮
        self.jz_fw.setStyleSheet(
                "QPushButton {"
                "color: white;"  # 字体颜色
                "background-color: rgb(46, 146, 87);"  # 默认背景颜色
                "}"
                "QPushButton:hover {"
                "background-color: rgb(46, 200, 87);}"  # 悬停时背景颜色
                "QPushButton:pressed{"  # 当按钮被按下时的样式
                "background-color: rgb(46,146,87);"  # 按下时的背景颜色
                "}"
        )

        u = QWidget(self)
        layout_u = QHBoxLayout(u)
        layout_M.addWidget(scroll_area)
        layout_M.addWidget(u)
        # layout_M.addStretch()

        u1 = QWidget(self)
        layout_u1 = QVBoxLayout(u1)
        layout_u.addWidget(u1)
        u11 = QWidget(self)
        layout_u11 = QHBoxLayout(u11)
        layout_u1.addWidget(u11)
        u12 = QWidget(self)
        layout_u12 = QHBoxLayout(u12)
        layout_u1.addWidget(u12)
        u13 = QWidget(self)
        layout_u13 = QHBoxLayout(u13)
        layout_u1.addWidget(u13)

        # layout_u.addStretch()

        um = QWidget(self)
        layout_u2 = QVBoxLayout(um)
        layout_u.addWidget(um)
        # 创建输入框
        self.input_real = QLineEdit()
        self.input_real.setPlaceholderText("请输入下压量")
        self.input_real.setAlignment(Qt.AlignCenter)
        int_validator = QDoubleValidator()
        self.input_real.setValidator(int_validator)
        layout_u2.addWidget(self.input_real)
        um1 = QWidget(self)
        layout_u21 = QHBoxLayout(um1)
        layout_u2.addWidget(um1)
        um2 = QWidget(self)
        layout_u22 = QHBoxLayout(um2)
        layout_u2.addWidget(um2)
        layout_u21.addWidget(self.jz_zb)
        layout_u22.addWidget(self.jz_fw)
        layout_u21.addWidget(self.xy_real)
        layout_u22.addWidget(self.jcl)

        u2 = QWidget(self)
        layout_u2 = QVBoxLayout(u2)
        layout_u.addWidget(u2)
        u21 = QWidget(self)
        layout_u21 = QHBoxLayout(u21)
        layout_u2.addWidget(u21)
        u22 = QWidget(self)
        layout_u22 = QHBoxLayout(u22)
        layout_u2.addWidget(u22)
        u23 = QWidget(self)
        layout_u23 = QHBoxLayout(u23)
        layout_u2.addWidget(u23)

        m = QWidget(self)
        layout_m = QVBoxLayout(m)
        layout_M.addWidget(m)
        # layout_M.addStretch()
        m1 = QWidget(self)
        layout_m1 = QHBoxLayout(m1)
        layout_m.addWidget(m1)
        m2 = QWidget(self)
        layout_m2 = QHBoxLayout(m2)
        layout_m.addWidget(m2)

        d = QWidget(self)
        layout_d = QVBoxLayout(d)
        layout_M.addWidget(d)
        d1 = QWidget(self)
        layout_d1 = QHBoxLayout(d1)
        layout_d.addWidget(d1)
        d2 = QWidget(self)
        layout_d2 = QHBoxLayout(d2)
        layout_d.addWidget(d2)
        d3 = QWidget(self)
        layout_d3 = QHBoxLayout(d3)
        layout_d.addWidget(d3)

        layout_u11.addWidget(self.jz_zz)
        layout_u11.addWidget(self.jz_up)
        layout_u11.addWidget(self.jz_fz)

        layout_u12.addWidget(self.jz_ht)
        layout_u12.addWidget(self.jz_stop)
        layout_u12.addWidget(self.jz_qj)

        layout_u13.addWidget(self.jz_jj)
        layout_u13.addWidget(self.jz_down)
        layout_u13.addWidget(self.jz_fs)

        layout_u21.addWidget(self.bj_zh)
        layout_u21.addWidget(self.bj_hl)
        layout_u21.addWidget(self.bj_zq)

        layout_u22.addWidget(self.bj_ht)
        layout_u22.addWidget(self.bj_stop)
        layout_u22.addWidget(self.bj_qj)

        layout_u23.addWidget(self.bj_up)
        layout_u23.addWidget(self.bj_down)

        layout_m1.addWidget(self.yt_j1)
        layout_m1.addWidget(self.yt_j2)
        layout_m1.addWidget(self.yt_j3)
        layout_m1.addWidget(self.yt_j4)
        layout_m1.addWidget(self.yt_j5)
        layout_m1.addWidget(self.yt_stop)
        layout_m1.addWidget(self.yt_up)

        layout_m2.addWidget(self.yt_c1)
        layout_m2.addWidget(self.yt_c2)
        layout_m2.addWidget(self.yt_c3)
        layout_m2.addWidget(self.yt_c4)
        layout_m2.addWidget(self.yt_c5)
        layout_m2.addWidget(self.yt_hl)
        layout_m2.addWidget(self.yt_down)

        layout_d1.addWidget(self.qn_on)
        layout_d1.addWidget(self.zp_up)
        layout_d1.addWidget(self.zc1_up)
        layout_d1.addWidget(self.zc2_up)
        layout_d1.addWidget(self.zc3_up)
        layout_d1.addWidget(self.zc4_up)

        layout_d2.addWidget(self.qn_stop)
        layout_d2.addWidget(self.zp_stop)
        layout_d2.addWidget(self.zc1_stop)
        layout_d2.addWidget(self.zc2_stop)
        layout_d2.addWidget(self.zc3_stop)
        layout_d2.addWidget(self.zc4_stop)

        layout_d3.addWidget(self.qn_off)
        layout_d3.addWidget(self.zp_down)
        layout_d3.addWidget(self.zc1_down)
        layout_d3.addWidget(self.zc2_down)
        layout_d3.addWidget(self.zc3_down)
        layout_d3.addWidget(self.zc4_down)
    def param_ui(self):
        # 创建中央窗口和布局
        M_widget = QWidget(self)        # 主窗口
        self.addTab(M_widget, '参数设置')
        self.setTabIcon(3, QIcon('images/UI/R.png'))
        u = QWidget(self)
        ur = QWidget(self)
        d0 = QWidget(self)
        d1 = QWidget(self)
        d2 = QWidget(self)
        d3 = QWidget(self)
        d = QWidget(self)

        # u.setFixedSize(1440, 500)  # 设置固定大小

        layout_M = QVBoxLayout(M_widget)
        layout_u = QHBoxLayout(u)
        layout_ur = QVBoxLayout(ur)
        layout_d = QHBoxLayout(d)
        layout_d0 = QFormLayout(d0)
        layout_d1 = QFormLayout(d1)
        layout_d2 = QFormLayout(d2)
        layout_d3 = QFormLayout(d3)

        layout_M.addWidget(u)
        layout_M.addWidget(d)
        layout_d.addWidget(d0)
        layout_d.addWidget(d1)
        layout_d.addWidget(d2)
        layout_d.addWidget(d3)

        self.param_log_widget = QTextEdit()
        self.param_log_widget.setReadOnly(True)
        scroll_area = QScrollArea()
        scroll_area.setWidget(self.param_log_widget)
        scroll_area.setWidgetResizable(True)
        layout_u.addWidget(scroll_area)
        # 创建输入框和标签
        font_main = QFont('楷体', 14)
        self.labels = ['半径容忍-P1',
                       '半径容忍-P2',
                       '半径容忍-P3',
                       '半径容忍-P4',
                       '半径容忍-P5',
                       '半径容忍-P6',
                       '半径容忍-P7',
                       '压下量系数-P1',
                       '压下量系数-P2',
                       '压下量系数-P3',
                       '压下量系数-P4',
                       '压下量系数-P5',
                       '压下量系数-P6',
                       '压下量系数-P7',
                       '下压补偿值-P1',
                       '下压补偿值-P2',
                       '下压补偿值-P3',
                       '下压补偿值-P4',
                       '下压补偿值-P5',
                       '下压补偿值-P6',
                       '下压补偿值-P7',
                       '连续下压增量-压1',
                       '连续下压增量-压2',
                       '连续下压增量-压3',
                       '连续下压增量-压4',
                       '连续下压增量-压5',
                       '最大校直次数',
                       '工件P1点半径'
                       ]
        self.input_boxes = {}
        self.param = {}         # 调用值：self.param['工件P1点直接输入']
        # 创建控件
        self.button_update = QPushButton('设置并更新')
        self.button_update.clicked.connect(self.update_param)
        self.button_update.setFont(font_main)
        layout_u.addWidget(ur)
        double_validator = QDoubleValidator()
        for label in self.labels:
            input_box = QLineEdit()
            # input_box.setPlaceholderText("")      # str(self.yx_xs1)
            input_box.setAlignment(Qt.AlignCenter)
            input_box.setValidator(double_validator)
            self.input_boxes[label] = input_box  # 存储输入框以便后续使用
        layout_d0.addRow('半径容忍-P1', self.input_boxes['半径容忍-P1'])
        layout_d0.addRow('半径容忍-P2', self.input_boxes['半径容忍-P2'])
        layout_d0.addRow('半径容忍-P3', self.input_boxes['半径容忍-P3'])
        layout_d0.addRow('半径容忍-P4', self.input_boxes['半径容忍-P4'])
        layout_d0.addRow('半径容忍-P5', self.input_boxes['半径容忍-P5'])
        layout_d0.addRow('半径容忍-P6', self.input_boxes['半径容忍-P6'])
        layout_d0.addRow('半径容忍-P7', self.input_boxes['半径容忍-P7'])

        layout_d1.addRow('压下量系数-P1', self.input_boxes['压下量系数-P1'])
        layout_d1.addRow('压下量系数-P2', self.input_boxes['压下量系数-P2'])
        layout_d1.addRow('压下量系数-P3', self.input_boxes['压下量系数-P3'])
        layout_d1.addRow('压下量系数-P4', self.input_boxes['压下量系数-P4'])
        layout_d1.addRow('压下量系数-P5', self.input_boxes['压下量系数-P5'])
        layout_d1.addRow('压下量系数-P6', self.input_boxes['压下量系数-P6'])
        layout_d1.addRow('压下量系数-P7', self.input_boxes['压下量系数-P7'])

        layout_d2.addRow('下压补偿值-P1', self.input_boxes['下压补偿值-P1'])
        layout_d2.addRow('下压补偿值-P2', self.input_boxes['下压补偿值-P2'])
        layout_d2.addRow('下压补偿值-P3', self.input_boxes['下压补偿值-P3'])
        layout_d2.addRow('下压补偿值-P4', self.input_boxes['下压补偿值-P4'])
        layout_d2.addRow('下压补偿值-P5', self.input_boxes['下压补偿值-P5'])
        layout_d2.addRow('下压补偿值-P6', self.input_boxes['下压补偿值-P6'])
        layout_d2.addRow('下压补偿值-P7', self.input_boxes['下压补偿值-P7'])

        layout_d3.addRow('连续下压增量-压1', self.input_boxes['连续下压增量-压1'])
        layout_d3.addRow('连续下压增量-压2', self.input_boxes['连续下压增量-压2'])
        layout_d3.addRow('连续下压增量-压3', self.input_boxes['连续下压增量-压3'])
        layout_d3.addRow('连续下压增量-压4', self.input_boxes['连续下压增量-压4'])
        layout_d3.addRow('连续下压增量-压5', self.input_boxes['连续下压增量-压5'])
        layout_d3.addRow('最大校直次数', self.input_boxes['最大校直次数'])
        layout_d3.addRow('工件P1点半径', self.input_boxes['工件P1点半径'])

        # 创建各级窗口################################################################################
        Auto_Para_widget = QWidget()
        Auto_Para_widget1 = QWidget()
        Auto_Contact_widget = QWidget()
        # # 定义布局####################################################################################
        Auto_Para_layout = QFormLayout(Auto_Para_widget)
        Auto_Para_layout1 = QHBoxLayout(Auto_Para_widget1)
        Auto_contact_layout = QHBoxLayout(Auto_Contact_widget)
        # 定义控件#####################################################################################
        # 创建输入框
        self.input_IP = QLineEdit()
        self.input_IP.setPlaceholderText(str(self.PLC_IP))
        self.input_IP.setAlignment(Qt.AlignCenter)
        self.input_rack = QLineEdit()
        self.input_rack.setPlaceholderText(str(self.PLC_rack))
        self.input_rack.setAlignment(Qt.AlignCenter)
        self.input_slot = QLineEdit()
        self.input_slot.setPlaceholderText(str(self.PLC_slot))
        self.input_slot.setAlignment(Qt.AlignCenter)
        # 创建按钮
        self.lian_plc_button = QPushButton("连接")
        self.duan_plc_button = QPushButton("断开")
        self.lian_plc_button.clicked.connect(self.lian_PLC_auto)
        self.duan_plc_button.clicked.connect(self.duan_PLC_auto)
        self.lian_plc_button.setFont(font_main)
        self.duan_plc_button.setFont(font_main)
        # 创建一个单选按钮组
        self.radio_button_xmz = QRadioButton("西门子")
        self.radio_button_hc = QRadioButton("汇川")
        self.radio_button_xmz.setChecked(True)
        self.button_group_auto = QButtonGroup()
        self.button_group_auto.addButton(self.radio_button_xmz)
        self.button_group_auto.addButton(self.radio_button_hc)
        # 控件进布局###########################################################################
        # 布局（小窗口）进（大）窗口##############################################################
        Auto_Para_layout1.addWidget(self.radio_button_xmz)
        Auto_Para_layout1.addWidget(self.radio_button_hc)
        Auto_Para_layout.addRow("IP地址:", self.input_IP)
        Auto_Para_layout.addRow("机架号:", self.input_rack)
        Auto_Para_layout.addRow("插槽号:", self.input_slot)
        Auto_Para_layout.addRow("PLC厂家:", Auto_Para_widget1)
        Auto_contact_layout.addWidget(self.lian_plc_button)
        Auto_contact_layout.addWidget(self.duan_plc_button)
        layout_ur.addWidget(Auto_Para_widget)
        layout_ur.addWidget(Auto_Contact_widget)
        layout_ur.addWidget(self.button_update)

        aboutme_title = QLabel('参数修改涉及到下压量计算\n非专业人员切勿随意更改！！！')
        aboutme_title.setFont(QFont('楷体', 24))
        aboutme_title.setAlignment(Qt.AlignCenter)

        layout_M.addWidget(aboutme_title)
    def sensor(self):
        M_widget = QWidget()
        self.plot = sensor_Plot("传感器曲线")
        ks_button = QPushButton("开始采集")
        ks_button.clicked.connect(self.get_ai)
        js_button = QPushButton("结束采集")
        js_button.clicked.connect(self.stop)

        layout_m = QVBoxLayout(M_widget)
        layout_m.addWidget(self.plot)
        layout_d = QHBoxLayout()
        layout_m.addLayout(layout_d)

        layout_d.addWidget(ks_button)
        layout_d.addWidget(js_button)

        self.addTab(M_widget, '传感器曲线')
        self.setTabIcon(4, QIcon('images/UI/R.png'))
    def about_me(self):
        M_widget = QWidget()
        aboutme_layout = QVBoxLayout()
        aboutme_title = QLabel('\n\n欢迎使用XXXX自研矫直机系统beta版\n\n 产品处于开发阶段，感谢包容与理解！！！')
        aboutme_title.setFont(QFont('楷体', 24))
        aboutme_title.setAlignment(Qt.AlignCenter)
        aboutme_img = QLabel()
        aboutme_img.setPixmap(QPixmap('images/UI/R.png'))
        aboutme_img.setAlignment(Qt.AlignCenter)
        label_aboutme = QLabel()
        label_aboutme.setText("<a href='https://space.bilibili.com/389544813'>开发者：肖宗朕</a>")
        label_aboutme.setFont(QFont('楷体', 24))
        label_aboutme.setOpenExternalLinks(True)
        label_aboutme.setAlignment(Qt.AlignRight)
        aboutme_layout.addWidget(aboutme_title)
        aboutme_layout.addStretch()
        aboutme_layout.addWidget(aboutme_img)
        aboutme_layout.addStretch()
        aboutme_layout.addWidget(label_aboutme)
        M_widget.setLayout(aboutme_layout)
        self.addTab(M_widget, '操作手册')
        self.setTabIcon(5, QIcon('images/UI/R.png'))

    def updata_chart(self, data):
        current_time = QDateTime.currentDateTime()
        time_ms = current_time.toMSecsSinceEpoch()
        self.plot.update_data(data, time_ms)
    def auto_plot_bar_chart(self, values):
        categories1 = ['# 1 #', '# 2 #', '# 6 #', '# 7 #']
        if hasattr(self, 'param') and isinstance(self.param, dict):
            a1 = float(self.param.get('半径容忍-P1', 1.0))
            a4 = float(self.param.get('半径容忍-P4', 1.0))
        else:
            a1 = 1.0
            a4 = 2.5
        for i, ax in enumerate([self.auto_ax1, self.auto_ax2, self.auto_ax6, self.auto_ax7]):
            # 获取现有的条形图，如果有的话
            bars = ax.patches
            if i > 1:
                value = values[i + 3]
            else:
                value = values[i]
            color = 'red' if value > a1 else 'green'

            if len(bars) == 0:
                # 如果没有条形图，绘制新的条形图
                ax.bar(categories1[i], value, width=0.2, color=color)
            else:
                # 如果已有条形图，更新现有的条形图
                bar = bars[0]  # 因为每个ax只有一个柱状图
                bar.set_height(value)  # 更新条形图的高度
                bar.set_color(color)  # 更新颜色

            # 设置图表的其他参数
            ax.set_ylim(bottom=0.35, top=7.5)
            ax.set_yscale('log', base=np.e)
            ax.yaxis.set_major_formatter(ticker.ScalarFormatter())
            # ax.axhline(y=2.5, color='black', linestyle='--', linewidth=1)
            ax.axhline(y=a1, color='black', linestyle='--', linewidth=1)
            ax.set_title(f'{value}', fontsize=10)
            ax.tick_params(axis='y', labelsize=8)
            ax.tick_params(axis='x', labelsize=8)
            ax.yaxis.set_major_locator(ticker.MaxNLocator(integer=True))
        categories2 = ['# 3 #', '# 4 #', '# 5 #']
        for i, ax in enumerate([self.auto_ax3, self.auto_ax4, self.auto_ax5]):
            # 获取现有的条形图，如果有的话
            bars = ax.patches
            value = values[i+2]
            color = 'red' if value > a4 else 'green'

            if len(bars) == 0:
                # 如果没有条形图，绘制新的条形图
                ax.bar(categories2[i], value, width=0.2, color=color)
            else:
                # 如果已有条形图，更新现有的条形图
                bar = bars[0]  # 因为每个ax只有一个柱状图
                bar.set_height(value)  # 更新条形图的高度
                bar.set_color(color)  # 更新颜色

            # 设置图表的其他参数
            ax.set_ylim(bottom=0.35, top=7.5)
            ax.set_yscale('log', base=np.e)
            ax.yaxis.set_major_formatter(ticker.ScalarFormatter())
            ax.axhline(y=a4, color='black', linestyle='--', linewidth=1)
            # ax.axhline(y=1, color='black', linestyle='--', linewidth=1)
            ax.set_title(f'{value}', fontsize=10)
            ax.tick_params(axis='y', labelsize=8)
            ax.tick_params(axis='x', labelsize=8)
            ax.yaxis.set_major_locator(ticker.MaxNLocator(integer=True))
        # 使用blit优化更新
        self.auto_canvas1.draw_idle()
        self.auto_canvas2.draw_idle()
        self.auto_canvas3.draw_idle()
        self.auto_canvas4.draw_idle()
        self.auto_canvas5.draw_idle()
        self.auto_canvas6.draw_idle()
        self.auto_canvas7.draw_idle()
        QCoreApplication.processEvents()
    def plot_bar_chart(self, values):
        categories1 = ['# 1 #', '# 2 #', '# 6 #', '# 7 #']
        if hasattr(self, 'param') and isinstance(self.param, dict):
            a1 = float(self.param.get('半径容忍-P1', 1.0))
            a4 = float(self.param.get('半径容忍-P4', 1.0))
        else:
            a1 = 1.0
            a4 = 2.5
        for i, ax in enumerate([self.ax1, self.ax2, self.ax6, self.ax7]):
            # 获取现有的条形图，如果有的话
            bars = ax.patches
            if i > 1:
                value = values[i+3]
            else:
                value = values[i]
            color = 'red' if value > a1 else 'green'

            if len(bars) == 0:
                # 如果没有条形图，绘制新的条形图
                ax.bar(categories1[i], value, width=0.2, color=color)
            else:
                # 如果已有条形图，更新现有的条形图
                bar = bars[0]  # 因为每个ax只有一个柱状图
                bar.set_height(value)  # 更新条形图的高度
                bar.set_color(color)  # 更新颜色

            # 设置图表的其他参数
            ax.set_ylim(bottom=0.35, top=7.5)
            ax.set_yscale('log', base=np.e)
            ax.yaxis.set_major_formatter(ticker.ScalarFormatter())
            ax.axhline(y=a1, color='black', linestyle='--', linewidth=1)
            # ax.axhline(y=1, color='black', linestyle='--', linewidth=1)
            ax.set_title(f'{value}', fontsize=10)
            ax.tick_params(axis='y', labelsize=8)
            ax.tick_params(axis='x', labelsize=8)
            ax.yaxis.set_major_locator(ticker.MaxNLocator(integer=True))
        categories2 = ['# 3 #', '# 4 #', '# 5 #']
        for i, ax in enumerate([self.ax3, self.ax4, self.ax5]):
            # 获取现有的条形图，如果有的话
            bars = ax.patches
            value = values[i+2]
            color = 'red' if value > a4 else 'green'

            if len(bars) == 0:
                # 如果没有条形图，绘制新的条形图
                ax.bar(categories2[i], value, width=0.2, color=color)
            else:
                # 如果已有条形图，更新现有的条形图
                bar = bars[0]  # 因为每个ax只有一个柱状图
                bar.set_height(value)  # 更新条形图的高度
                bar.set_color(color)  # 更新颜色

            # 设置图表的其他参数
            ax.set_ylim(bottom=0.35, top=7.5)
            ax.set_yscale('log', base=np.e)
            ax.yaxis.set_major_formatter(ticker.ScalarFormatter())
            ax.axhline(y=a4, color='black', linestyle='--', linewidth=1)
            # ax.axhline(y=1, color='black', linestyle='--', linewidth=1)
            ax.set_title(f'{value}', fontsize=10)
            ax.tick_params(axis='y', labelsize=8)
            ax.tick_params(axis='x', labelsize=8)
            ax.yaxis.set_major_locator(ticker.MaxNLocator(integer=True))
        # 使用blit优化更新
        self.canvas1.draw_idle()
        self.canvas2.draw_idle()
        self.canvas3.draw_idle()
        self.canvas4.draw_idle()
        self.canvas5.draw_idle()
        self.canvas6.draw_idle()
        self.canvas7.draw_idle()
        QCoreApplication.processEvents()
    def half_auto_run(self):
        self.circle_mode = "手动"
        self.worker_thread_auto.start()
    def new_data_hand_ui(self, bar_mo, bar_xj, list_kesai):
        if self.worker_thread_auto == self.yyfffyy:
            # print(list_kesai)
            # self.kesai3, self.kesai4, self.kesai5 = list_kesai
            self.bar_xj = bar_xj
            self.bar_mo = bar_mo
            if abs((sorted(list_kesai)[1] - 45)) < 10:
                self.list_kesai = list_kesai
            else:
                for i in range(3):
                    if list_kesai[i] >= 45:
                        self.list_kesai[i] = list_kesai[i] - 90
                        self.bar_xj[2 + i] = bar_xj[2 + i] + 90
                    else:
                        self.list_kesai[i] = list_kesai[i]
            self.kesai = sorted(self.list_kesai)[1]
            # 对其他kesai进行补偿
            for i in range(3):
                self.bar_xj[2 + i] = self.bar_xj[2 + i] + (self.list_kesai[i] - self.kesai)
            print(self.kesai, "    kesai    ",self.list_kesai)
            # 找平
            # fast_pmove(self.axis, int((self.kesai / 360) * self.mc_circle))
            if self.circle_mode == "自动":
                print("已接收到信号，准备更新界面柱状")
                self.auto_plot_bar_chart(self.bar_mo)
                print("界面柱状图更新完毕，准备更新饼状图")
                self.auto_cs_widget1.setAngle(-90 + self.bar_xj[0] + self.kesai)
                self.auto_cs_widget2.setAngle(-90 + self.bar_xj[1] + self.kesai)
                self.auto_cs_widget3.setAngle(-90 + self.bar_xj[2])
                self.auto_cs_widget4.setAngle(-90 + self.bar_xj[3])
                self.auto_cs_widget5.setAngle(-90 + self.bar_xj[4])
                self.auto_cs_widget6.setAngle(-90 + self.bar_xj[5] + self.kesai)
                self.auto_cs_widget7.setAngle(-90 + self.bar_xj[6] + self.kesai)
                # QCoreApplication.processEvents()
            if self.circle_mode == "手动":
                print("已接收到信号，准备更新界面柱状")
                self.plot_bar_chart(self.bar_mo)
                print("界面柱状图更新完毕，准备更新饼状图")
                self.cs_widget1.setAngle(-90 + self.bar_xj[0] + self.kesai)
                self.cs_widget2.setAngle(-90 + self.bar_xj[1] + self.kesai)
                self.cs_widget3.setAngle(-90 + self.bar_xj[2])
                self.cs_widget4.setAngle(-90 + self.bar_xj[3])
                self.cs_widget5.setAngle(-90 + self.bar_xj[4])
                self.cs_widget6.setAngle(-90 + self.bar_xj[5] + self.kesai)
                self.cs_widget7.setAngle(-90 + self.bar_xj[6] + self.kesai)
                # QCoreApplication.processEvents()
            print("全部更新完毕，返回用户界面")
            # 将要压的部位凸面朝上
            # thita = (self.kesai) % 360
            # if 180 < thita:
            #     thita -= 360
            # fast_pmove(self.axis, int((thita + 2) / 360 * self.mc_circle))
            self.work_isrun = False
        elif self.worker_thread_auto == self.yyyyyyy:
            self.bar_xj = bar_xj
            self.bar_mo = bar_mo
            if self.circle_mode == "自动":
                print("已接收到信号，准备更新界面柱状")
                self.auto_plot_bar_chart(self.bar_mo)
                print("界面柱状图更新完毕，准备更新饼状图")
                self.auto_cs_widget1.setAngle(-90 + self.bar_xj[0])
                self.auto_cs_widget2.setAngle(-90 + self.bar_xj[1])
                self.auto_cs_widget3.setAngle(-90 + self.bar_xj[2])
                self.auto_cs_widget4.setAngle(-90 + self.bar_xj[3])
                self.auto_cs_widget5.setAngle(-90 + self.bar_xj[4])
                self.auto_cs_widget6.setAngle(-90 + self.bar_xj[5])
                self.auto_cs_widget7.setAngle(-90 + self.bar_xj[6])
                # QCoreApplication.processEvents()
            if self.circle_mode == "手动":
                print("已接收到信号，准备更新界面柱状")
                self.plot_bar_chart(self.bar_mo)
                print("界面柱状图更新完毕，准备更新饼状图")
                self.cs_widget1.setAngle(-90 + self.bar_xj[0])
                self.cs_widget2.setAngle(-90 + self.bar_xj[1])
                self.cs_widget3.setAngle(-90 + self.bar_xj[2])
                self.cs_widget4.setAngle(-90 + self.bar_xj[3])
                self.cs_widget5.setAngle(-90 + self.bar_xj[4])
                self.cs_widget6.setAngle(-90 + self.bar_xj[5])
                self.cs_widget7.setAngle(-90 + self.bar_xj[6])
            print("全部更新完毕，返回用户界面")
            self.work_isrun = False
        elif self.worker_thread_auto == self.yfffffy:
            self.bar_xj = bar_xj
            self.bar_mo = bar_mo
            if abs((sorted(list_kesai)[2] - 45)) < 10:
                self.list_kesai = list_kesai
            else:
                for i in range(5):
                    if list_kesai[i] >= 45:
                        self.list_kesai[i] = list_kesai[i] - 90
                        self.bar_xj[1 + i] = bar_xj[1 + i] + 90
                    else:
                        self.list_kesai[i] = list_kesai[i]
            self.kesai = sorted(self.list_kesai)[2]
            # 对其他kesai进行补偿
            for i in range(5):
                self.bar_xj[1 + i] = self.bar_xj[1 + i] + (self.list_kesai[i] - self.kesai)
            print(self.kesai, "    kesai    ",self.list_kesai)
            # 找平
            # fast_pmove(self.axis, int((self.kesai / 360) * self.mc_circle))
            if self.circle_mode == "自动":
                print("已接收到信号，准备更新界面柱状")
                self.auto_plot_bar_chart(self.bar_mo)
                print("界面柱状图更新完毕，准备更新饼状图")
                self.auto_cs_widget1.setAngle(-90 + self.bar_xj[0] + self.kesai)
                self.auto_cs_widget2.setAngle(-90 + self.bar_xj[1])
                self.auto_cs_widget3.setAngle(-90 + self.bar_xj[2])
                self.auto_cs_widget4.setAngle(-90 + self.bar_xj[3])
                self.auto_cs_widget5.setAngle(-90 + self.bar_xj[4])
                self.auto_cs_widget6.setAngle(-90 + self.bar_xj[5])
                self.auto_cs_widget7.setAngle(-90 + self.bar_xj[6] + self.kesai)
            if self.circle_mode == "手动":
                print("已接收到信号，准备更新界面柱状")
                self.plot_bar_chart(self.bar_mo)
                print("界面柱状图更新完毕，准备更新饼状图")
                self.cs_widget1.setAngle(-90 + self.bar_xj[0] + self.kesai)
                self.cs_widget2.setAngle(-90 + self.bar_xj[1])
                self.cs_widget3.setAngle(-90 + self.bar_xj[2])
                self.cs_widget4.setAngle(-90 + self.bar_xj[3])
                self.cs_widget5.setAngle(-90 + self.bar_xj[4])
                self.cs_widget6.setAngle(-90 + self.bar_xj[5])
                self.cs_widget7.setAngle(-90 + self.bar_xj[6] + self.kesai)
                # QCoreApplication.processEvents()
            print("全部更新完毕，返回用户界面")
            # 将要压的部位凸面朝上
            # thita = (self.kesai) % 360
            # if 180 < thita:
            #     thita -= 360
            # fast_pmove(self.axis, int((thita + 2) / 360 * self.mc_circle))
            self.work_isrun = False
        else:
            return
    def get_ai(self):
        self.plot.clear_chart()
        self.worker_thread.start()
    def new_data_info_ui(self, html_message):
        self.log_widget.append(html_message)
        self.log_widget.ensureCursorVisible()
    def stop(self):
        self.worker_thread.stop()
        self.worker_thread.wait()
        self.worker_thread.stop_init()

        self.worker_thread_auto.stop()
        self.worker_thread_auto.wait()
        self.worker_thread_auto.stop_init()

        color = 'green'
        message = f"成功停止采集"
        html_message = f'<span style="color: {color};">{message}</span>'
        self.log_widget.append(html_message)
        self.log_widget.ensureCursorVisible()
    def end_Thread(self, en):
        if en:
            color = 'red'
            message = f"发生意外"
            html_message = f'<span style="color: {color};">{message}</span>'
            self.log_widget.append(html_message)
            self.log_widget.ensureCursorVisible()
    def fa_shuju(self, db_num, bit_ads, bool_value, txt=""):
        try:
            success = write_bool(self.client_xmz, db_num, bit_ads, bool_value)  # 写入布尔值 True
            if txt != "":
                if success != True:
                    color = 'red'
                    message = f"{txt}失败"
                    html_message = f'<span style="color: {color};">{message}</span>'
                    self.hand_log_widget.append(html_message)
                    self.hand_log_widget.ensureCursorVisible()
                else:
                    color = 'green'
                    message = f"{txt}成功"
                    html_message = f'<span style="color: {color};">{message}</span>'
                    self.hand_log_widget.append(html_message)
                    self.hand_log_widget.ensureCursorVisible()
        except Exception as e:
            color = 'red'
            message = "PLC连接失败\n请重新启动软件"
            html_message = f'<span style="color: {color};">{message}</span>'
            self.hand_log_widget.append(html_message)
            self.hand_log_widget.ensureCursorVisible()
    def zhouka_zd(self):
        try:
            mc_num = self.input_mc.text()
            if not mc_num:
                mc_num = self.mc_num
            else:
                mc_num = int(mc_num)
            result = fast_pmove(self.axis, mc_num)
            # result = con_vmove(self.axis)
            if result == 0:
                color = 'green'
            else:
                color = 'red'
            message = f"轴卡输出：：转动{mc_num}个脉冲"
            html_message = f'<span style="color: {color};">{message}</span>'
            self.log_widget.append(html_message)
            self.log_widget.ensureCursorVisible()
        except Exception as e:
            self.log_widget.append("轴卡连接失败")
            self.log_widget.ensureCursorVisible()
    def zhouka_tz(self):
        try:
            result = sudden_stop(self.axis)
            if result == 0:
                color = 'green'
            else:
                color = 'red'
            message = f"停止转动"
            html_message = f'<span style="color: {color};">{message}</span>'
            self.log_widget.append(html_message)
            self.log_widget.ensureCursorVisible()
        except Exception as e:
            color = 'red'
            message = "轴卡连接失败"
            html_message = f'<span style="color: {color};">{message}</span>'
            self.log_widget.append(html_message)
            self.log_widget.ensureCursorVisible()
    def zhouka_hl(self):
        try:
            result = fast_hmove(self.axis, 1)
            if result == 0:
                color = 'green'
            else:
                color = 'red'
            message = f"轴卡回原点转动"
            html_message = f'<span style="color: {color};">{message}</span>'
            self.log_widget.append(html_message)
            self.log_widget.ensureCursorVisible()
        except Exception as e:
            color = 'red'
            message = "轴卡连接失败"
            html_message = f'<span style="color: {color};">{message}</span>'
            self.log_widget.append(html_message)
            self.log_widget.ensureCursorVisible()
    def on_tab_changed(self, index):
        # 检查当前选中的标签索引
        if index == 0:
            color = 'green'
            message = "启动自动模式"
            html_message = f'<span style="color: {color};">{message}</span>'
            self.auto_log_widget.append(html_message)
            self.auto_log_widget.ensureCursorVisible()
        if index == 1:
            color = 'green'
            message = "启动半自动模式"
            html_message = f'<span style="color: {color};">{message}</span>'
            self.log_widget.append(html_message)
            self.log_widget.ensureCursorVisible()
        if index == 2:
            color = 'green'
            message = "启动手动模式"
            html_message = f'<span style="color: {color};">{message}</span>'
            self.hand_log_widget.append(html_message)
            self.hand_log_widget.ensureCursorVisible()
        if index == 3:
            color = 'green'
            message = "启动参数修改界面"
            html_message = f'<span style="color: {color};">{message}</span>'
            self.param_log_widget.append(html_message)
            self.param_log_widget.ensureCursorVisible()
    def works_changed(self, index):
        if index == 0:
            self.worker_thread_auto = self.yyfffyy
            # 更新自动页面
            layout1 = self.auto_cs_widget1.parent().layout()
            layout2 = self.auto_cs_widget2.parent().layout()
            layout3 = self.auto_cs_widget3.parent().layout()
            layout4 = self.auto_cs_widget4.parent().layout()
            layout5 = self.auto_cs_widget5.parent().layout()
            layout6 = self.auto_cs_widget6.parent().layout()
            layout7 = self.auto_cs_widget7.parent().layout()
            layout1.removeWidget(self.auto_cs_widget1)
            layout2.removeWidget(self.auto_cs_widget2)
            layout3.removeWidget(self.auto_cs_widget3)
            layout4.removeWidget(self.auto_cs_widget4)
            layout5.removeWidget(self.auto_cs_widget5)
            layout6.removeWidget(self.auto_cs_widget6)
            layout7.removeWidget(self.auto_cs_widget7)
            self.auto_cs_widget1.deleteLater()
            self.auto_cs_widget2.deleteLater()
            self.auto_cs_widget3.deleteLater()
            self.auto_cs_widget4.deleteLater()
            self.auto_cs_widget5.deleteLater()
            self.auto_cs_widget6.deleteLater()
            self.auto_cs_widget7.deleteLater()
            self.auto_cs_widget1 = CircleWidget(angle=90)
            self.auto_cs_widget2 = CircleWidget(angle=90)
            self.auto_cs_widget3 = SqrtWidget(angle=90)
            self.auto_cs_widget4 = SqrtWidget(angle=90)
            self.auto_cs_widget5 = SqrtWidget(angle=90)
            self.auto_cs_widget6 = CircleWidget(angle=90)
            self.auto_cs_widget7 = CircleWidget(angle=90)
            self.auto_cs_widget1.setMinimumSize(115, 115)
            self.auto_cs_widget2.setMinimumSize(115, 115)
            self.auto_cs_widget3.setMinimumSize(115, 115)
            self.auto_cs_widget4.setMinimumSize(115, 115)
            self.auto_cs_widget5.setMinimumSize(115, 115)
            self.auto_cs_widget6.setMinimumSize(115, 115)
            self.auto_cs_widget7.setMinimumSize(115, 115)
            layout1.addWidget(self.auto_cs_widget1)
            layout2.addWidget(self.auto_cs_widget2)
            layout3.addWidget(self.auto_cs_widget3)
            layout4.addWidget(self.auto_cs_widget4)
            layout5.addWidget(self.auto_cs_widget5)
            layout6.addWidget(self.auto_cs_widget6)
            layout7.addWidget(self.auto_cs_widget7)
            layout1.update()
            layout2.update()
            layout3.update()
            layout4.update()
            layout5.update()
            layout6.update()
            layout7.update()
            # 更新半自动页面
            _layout1 = self.cs_widget1.parent().layout()
            _layout2 = self.cs_widget2.parent().layout()
            _layout3 = self.cs_widget3.parent().layout()
            _layout4 = self.cs_widget4.parent().layout()
            _layout5 = self.cs_widget5.parent().layout()
            _layout6 = self.cs_widget6.parent().layout()
            _layout7 = self.cs_widget7.parent().layout()
            _layout1.removeWidget(self.cs_widget1)
            _layout2.removeWidget(self.cs_widget2)
            _layout3.removeWidget(self.cs_widget3)
            _layout4.removeWidget(self.cs_widget4)
            _layout5.removeWidget(self.cs_widget5)
            _layout6.removeWidget(self.cs_widget6)
            _layout7.removeWidget(self.cs_widget7)
            self.cs_widget1.deleteLater()
            self.cs_widget2.deleteLater()
            self.cs_widget3.deleteLater()
            self.cs_widget4.deleteLater()
            self.cs_widget5.deleteLater()
            self.cs_widget6.deleteLater()
            self.cs_widget7.deleteLater()
            self.cs_widget1 = CircleWidget(angle=90)
            self.cs_widget2 = CircleWidget(angle=90)
            self.cs_widget3 = SqrtWidget(angle=90)
            self.cs_widget4 = SqrtWidget(angle=90)
            self.cs_widget5 = SqrtWidget(angle=90)
            self.cs_widget6 = CircleWidget(angle=90)
            self.cs_widget7 = CircleWidget(angle=90)
            self.cs_widget1.setMinimumSize(115, 115)
            self.cs_widget2.setMinimumSize(115, 115)
            self.cs_widget3.setMinimumSize(115, 115)
            self.cs_widget4.setMinimumSize(115, 115)
            self.cs_widget5.setMinimumSize(115, 115)
            self.cs_widget6.setMinimumSize(115, 115)
            self.cs_widget7.setMinimumSize(115, 115)
            _layout1.addWidget(self.cs_widget1)
            _layout2.addWidget(self.cs_widget2)
            _layout3.addWidget(self.cs_widget3)
            _layout4.addWidget(self.cs_widget4)
            _layout5.addWidget(self.cs_widget5)
            _layout6.addWidget(self.cs_widget6)
            _layout7.addWidget(self.cs_widget7)
            _layout1.update()
            _layout2.update()
            _layout3.update()
            _layout4.update()
            _layout5.update()
            _layout6.update()
            _layout7.update()
        elif index == 1:
            self.worker_thread_auto = self.yyyyyyy
            # 更新自动页面
            layout1 = self.auto_cs_widget1.parent().layout()
            layout2 = self.auto_cs_widget2.parent().layout()
            layout3 = self.auto_cs_widget3.parent().layout()
            layout4 = self.auto_cs_widget4.parent().layout()
            layout5 = self.auto_cs_widget5.parent().layout()
            layout6 = self.auto_cs_widget6.parent().layout()
            layout7 = self.auto_cs_widget7.parent().layout()
            layout1.removeWidget(self.auto_cs_widget1)
            layout2.removeWidget(self.auto_cs_widget2)
            layout3.removeWidget(self.auto_cs_widget3)
            layout4.removeWidget(self.auto_cs_widget4)
            layout5.removeWidget(self.auto_cs_widget5)
            layout6.removeWidget(self.auto_cs_widget6)
            layout7.removeWidget(self.auto_cs_widget7)
            self.auto_cs_widget1.deleteLater()
            self.auto_cs_widget2.deleteLater()
            self.auto_cs_widget3.deleteLater()
            self.auto_cs_widget4.deleteLater()
            self.auto_cs_widget5.deleteLater()
            self.auto_cs_widget6.deleteLater()
            self.auto_cs_widget7.deleteLater()
            self.auto_cs_widget1 = CircleWidget(angle=90)
            self.auto_cs_widget2 = CircleWidget(angle=90)
            self.auto_cs_widget3 = CircleWidget(angle=90)
            self.auto_cs_widget4 = CircleWidget(angle=90)
            self.auto_cs_widget5 = CircleWidget(angle=90)
            self.auto_cs_widget6 = CircleWidget(angle=90)
            self.auto_cs_widget7 = CircleWidget(angle=90)
            self.auto_cs_widget1.setMinimumSize(115, 115)
            self.auto_cs_widget2.setMinimumSize(115, 115)
            self.auto_cs_widget3.setMinimumSize(115, 115)
            self.auto_cs_widget4.setMinimumSize(115, 115)
            self.auto_cs_widget5.setMinimumSize(115, 115)
            self.auto_cs_widget6.setMinimumSize(115, 115)
            self.auto_cs_widget7.setMinimumSize(115, 115)
            layout1.addWidget(self.auto_cs_widget1)
            layout2.addWidget(self.auto_cs_widget2)
            layout3.addWidget(self.auto_cs_widget3)
            layout4.addWidget(self.auto_cs_widget4)
            layout5.addWidget(self.auto_cs_widget5)
            layout6.addWidget(self.auto_cs_widget6)
            layout7.addWidget(self.auto_cs_widget7)
            layout1.update()
            layout2.update()
            layout3.update()
            layout4.update()
            layout5.update()
            layout6.update()
            layout7.update()
            # 更新半自动页面
            _layout1 = self.cs_widget1.parent().layout()
            _layout2 = self.cs_widget2.parent().layout()
            _layout3 = self.cs_widget3.parent().layout()
            _layout4 = self.cs_widget4.parent().layout()
            _layout5 = self.cs_widget5.parent().layout()
            _layout6 = self.cs_widget6.parent().layout()
            _layout7 = self.cs_widget7.parent().layout()
            _layout1.removeWidget(self.cs_widget1)
            _layout2.removeWidget(self.cs_widget2)
            _layout3.removeWidget(self.cs_widget3)
            _layout4.removeWidget(self.cs_widget4)
            _layout5.removeWidget(self.cs_widget5)
            _layout6.removeWidget(self.cs_widget6)
            _layout7.removeWidget(self.cs_widget7)
            self.cs_widget1.deleteLater()
            self.cs_widget2.deleteLater()
            self.cs_widget3.deleteLater()
            self.cs_widget4.deleteLater()
            self.cs_widget5.deleteLater()
            self.cs_widget6.deleteLater()
            self.cs_widget7.deleteLater()
            self.cs_widget1 = CircleWidget(angle=90)
            self.cs_widget2 = CircleWidget(angle=90)
            self.cs_widget3 = CircleWidget(angle=90)
            self.cs_widget4 = CircleWidget(angle=90)
            self.cs_widget5 = CircleWidget(angle=90)
            self.cs_widget6 = CircleWidget(angle=90)
            self.cs_widget7 = CircleWidget(angle=90)
            self.cs_widget1.setMinimumSize(115, 115)
            self.cs_widget2.setMinimumSize(115, 115)
            self.cs_widget3.setMinimumSize(115, 115)
            self.cs_widget4.setMinimumSize(115, 115)
            self.cs_widget5.setMinimumSize(115, 115)
            self.cs_widget6.setMinimumSize(115, 115)
            self.cs_widget7.setMinimumSize(115, 115)
            _layout1.addWidget(self.cs_widget1)
            _layout2.addWidget(self.cs_widget2)
            _layout3.addWidget(self.cs_widget3)
            _layout4.addWidget(self.cs_widget4)
            _layout5.addWidget(self.cs_widget5)
            _layout6.addWidget(self.cs_widget6)
            _layout7.addWidget(self.cs_widget7)
            _layout1.update()
            _layout2.update()
            _layout3.update()
            _layout4.update()
            _layout5.update()
            _layout6.update()
            _layout7.update()
        elif index == 2:
            self.worker_thread_auto = self.yfffffy
            # 更新自动页面
            layout1 = self.auto_cs_widget1.parent().layout()
            layout2 = self.auto_cs_widget2.parent().layout()
            layout3 = self.auto_cs_widget3.parent().layout()
            layout4 = self.auto_cs_widget4.parent().layout()
            layout5 = self.auto_cs_widget5.parent().layout()
            layout6 = self.auto_cs_widget6.parent().layout()
            layout7 = self.auto_cs_widget7.parent().layout()
            layout1.removeWidget(self.auto_cs_widget1)
            layout2.removeWidget(self.auto_cs_widget2)
            layout3.removeWidget(self.auto_cs_widget3)
            layout4.removeWidget(self.auto_cs_widget4)
            layout5.removeWidget(self.auto_cs_widget5)
            layout6.removeWidget(self.auto_cs_widget6)
            layout7.removeWidget(self.auto_cs_widget7)
            self.auto_cs_widget1.deleteLater()
            self.auto_cs_widget2.deleteLater()
            self.auto_cs_widget3.deleteLater()
            self.auto_cs_widget4.deleteLater()
            self.auto_cs_widget5.deleteLater()
            self.auto_cs_widget6.deleteLater()
            self.auto_cs_widget7.deleteLater()
            self.auto_cs_widget1 = CircleWidget(angle=90)
            self.auto_cs_widget2 = SqrtWidget(angle=90)
            self.auto_cs_widget3 = SqrtWidget(angle=90)
            self.auto_cs_widget4 = SqrtWidget(angle=90)
            self.auto_cs_widget5 = SqrtWidget(angle=90)
            self.auto_cs_widget6 = SqrtWidget(angle=90)
            self.auto_cs_widget7 = CircleWidget(angle=90)
            self.auto_cs_widget1.setMinimumSize(115, 115)
            self.auto_cs_widget2.setMinimumSize(115, 115)
            self.auto_cs_widget3.setMinimumSize(115, 115)
            self.auto_cs_widget4.setMinimumSize(115, 115)
            self.auto_cs_widget5.setMinimumSize(115, 115)
            self.auto_cs_widget6.setMinimumSize(115, 115)
            self.auto_cs_widget7.setMinimumSize(115, 115)
            layout1.addWidget(self.auto_cs_widget1)
            layout2.addWidget(self.auto_cs_widget2)
            layout3.addWidget(self.auto_cs_widget3)
            layout4.addWidget(self.auto_cs_widget4)
            layout5.addWidget(self.auto_cs_widget5)
            layout6.addWidget(self.auto_cs_widget6)
            layout7.addWidget(self.auto_cs_widget7)
            layout1.update()
            layout2.update()
            layout3.update()
            layout4.update()
            layout5.update()
            layout6.update()
            layout7.update()
            # 更新半自动页面
            _layout1 = self.cs_widget1.parent().layout()
            _layout2 = self.cs_widget2.parent().layout()
            _layout3 = self.cs_widget3.parent().layout()
            _layout4 = self.cs_widget4.parent().layout()
            _layout5 = self.cs_widget5.parent().layout()
            _layout6 = self.cs_widget6.parent().layout()
            _layout7 = self.cs_widget7.parent().layout()
            _layout1.removeWidget(self.cs_widget1)
            _layout2.removeWidget(self.cs_widget2)
            _layout3.removeWidget(self.cs_widget3)
            _layout4.removeWidget(self.cs_widget4)
            _layout5.removeWidget(self.cs_widget5)
            _layout6.removeWidget(self.cs_widget6)
            _layout7.removeWidget(self.cs_widget7)
            self.cs_widget1.deleteLater()
            self.cs_widget2.deleteLater()
            self.cs_widget3.deleteLater()
            self.cs_widget4.deleteLater()
            self.cs_widget5.deleteLater()
            self.cs_widget6.deleteLater()
            self.cs_widget7.deleteLater()
            self.cs_widget1 = CircleWidget(angle=90)
            self.cs_widget2 = SqrtWidget(angle=90)
            self.cs_widget3 = SqrtWidget(angle=90)
            self.cs_widget4 = SqrtWidget(angle=90)
            self.cs_widget5 = SqrtWidget(angle=90)
            self.cs_widget6 = SqrtWidget(angle=90)
            self.cs_widget7 = CircleWidget(angle=90)
            self.cs_widget1.setMinimumSize(115, 115)
            self.cs_widget2.setMinimumSize(115, 115)
            self.cs_widget3.setMinimumSize(115, 115)
            self.cs_widget4.setMinimumSize(115, 115)
            self.cs_widget5.setMinimumSize(115, 115)
            self.cs_widget6.setMinimumSize(115, 115)
            self.cs_widget7.setMinimumSize(115, 115)
            _layout1.addWidget(self.cs_widget1)
            _layout2.addWidget(self.cs_widget2)
            _layout3.addWidget(self.cs_widget3)
            _layout4.addWidget(self.cs_widget4)
            _layout5.addWidget(self.cs_widget5)
            _layout6.addWidget(self.cs_widget6)
            _layout7.addWidget(self.cs_widget7)
            _layout1.update()
            _layout2.update()
            _layout3.update()
            _layout4.update()
            _layout5.update()
            _layout6.update()
            _layout7.update()
        else:
            self.worker_thread_auto = self.yyfffyy
            # 更新自动页面
            layout1 = self.auto_cs_widget1.parent().layout()
            layout2 = self.auto_cs_widget2.parent().layout()
            layout3 = self.auto_cs_widget3.parent().layout()
            layout4 = self.auto_cs_widget4.parent().layout()
            layout5 = self.auto_cs_widget5.parent().layout()
            layout6 = self.auto_cs_widget6.parent().layout()
            layout7 = self.auto_cs_widget7.parent().layout()
            layout1.removeWidget(self.auto_cs_widget1)
            layout2.removeWidget(self.auto_cs_widget2)
            layout3.removeWidget(self.auto_cs_widget3)
            layout4.removeWidget(self.auto_cs_widget4)
            layout5.removeWidget(self.auto_cs_widget5)
            layout6.removeWidget(self.auto_cs_widget6)
            layout7.removeWidget(self.auto_cs_widget7)
            self.auto_cs_widget1.deleteLater()
            self.auto_cs_widget2.deleteLater()
            self.auto_cs_widget3.deleteLater()
            self.auto_cs_widget4.deleteLater()
            self.auto_cs_widget5.deleteLater()
            self.auto_cs_widget6.deleteLater()
            self.auto_cs_widget7.deleteLater()
            self.auto_cs_widget1 = CircleWidget(angle=90)
            self.auto_cs_widget2 = CircleWidget(angle=90)
            self.auto_cs_widget3 = SqrtWidget(angle=90)
            self.auto_cs_widget4 = SqrtWidget(angle=90)
            self.auto_cs_widget5 = SqrtWidget(angle=90)
            self.auto_cs_widget6 = CircleWidget(angle=90)
            self.auto_cs_widget7 = CircleWidget(angle=90)
            self.auto_cs_widget1.setMinimumSize(115, 115)
            self.auto_cs_widget2.setMinimumSize(115, 115)
            self.auto_cs_widget3.setMinimumSize(115, 115)
            self.auto_cs_widget4.setMinimumSize(115, 115)
            self.auto_cs_widget5.setMinimumSize(115, 115)
            self.auto_cs_widget6.setMinimumSize(115, 115)
            self.auto_cs_widget7.setMinimumSize(115, 115)
            layout1.addWidget(self.auto_cs_widget1)
            layout2.addWidget(self.auto_cs_widget2)
            layout3.addWidget(self.auto_cs_widget3)
            layout4.addWidget(self.auto_cs_widget4)
            layout5.addWidget(self.auto_cs_widget5)
            layout6.addWidget(self.auto_cs_widget6)
            layout7.addWidget(self.auto_cs_widget7)
            layout1.update()
            layout2.update()
            layout3.update()
            layout4.update()
            layout5.update()
            layout6.update()
            layout7.update()
            # 更新半自动页面
            _layout1 = self.cs_widget1.parent().layout()
            _layout2 = self.cs_widget2.parent().layout()
            _layout3 = self.cs_widget3.parent().layout()
            _layout4 = self.cs_widget4.parent().layout()
            _layout5 = self.cs_widget5.parent().layout()
            _layout6 = self.cs_widget6.parent().layout()
            _layout7 = self.cs_widget7.parent().layout()
            _layout1.removeWidget(self.cs_widget1)
            _layout2.removeWidget(self.cs_widget2)
            _layout3.removeWidget(self.cs_widget3)
            _layout4.removeWidget(self.cs_widget4)
            _layout5.removeWidget(self.cs_widget5)
            _layout6.removeWidget(self.cs_widget6)
            _layout7.removeWidget(self.cs_widget7)
            self.cs_widget1.deleteLater()
            self.cs_widget2.deleteLater()
            self.cs_widget3.deleteLater()
            self.cs_widget4.deleteLater()
            self.cs_widget5.deleteLater()
            self.cs_widget6.deleteLater()
            self.cs_widget7.deleteLater()
            self.cs_widget1 = CircleWidget(angle=90)
            self.cs_widget2 = CircleWidget(angle=90)
            self.cs_widget3 = SqrtWidget(angle=90)
            self.cs_widget4 = SqrtWidget(angle=90)
            self.cs_widget5 = SqrtWidget(angle=90)
            self.cs_widget6 = CircleWidget(angle=90)
            self.cs_widget7 = CircleWidget(angle=90)
            self.cs_widget1.setMinimumSize(115, 115)
            self.cs_widget2.setMinimumSize(115, 115)
            self.cs_widget3.setMinimumSize(115, 115)
            self.cs_widget4.setMinimumSize(115, 115)
            self.cs_widget5.setMinimumSize(115, 115)
            self.cs_widget6.setMinimumSize(115, 115)
            self.cs_widget7.setMinimumSize(115, 115)
            _layout1.addWidget(self.cs_widget1)
            _layout2.addWidget(self.cs_widget2)
            _layout3.addWidget(self.cs_widget3)
            _layout4.addWidget(self.cs_widget4)
            _layout5.addWidget(self.cs_widget5)
            _layout6.addWidget(self.cs_widget6)
            _layout7.addWidget(self.cs_widget7)
            _layout1.update()
            _layout2.update()
            _layout3.update()
            _layout4.update()
            _layout5.update()
            _layout6.update()
            _layout7.update()
    def on_mouse_press(self, event, button):
        # 按下时，按钮状态设置为按下
        button.setChecked(True)
        if button.text() == "夹爪正转":
            try:
                sudden_stop(self.axis)
                con_vmove(self.axis, 1)
            except Exception as e:
                # 捕获并打印错误信息
                print(f"Error writing to PLC: {e}")
                return
            self.fa_shuju(db_num=1, bit_ads=1, bool_value=True, txt="夹爪正转")
            self.fa_shuju(db_num=1, bit_ads=5, bool_value=False)
            self.fa_shuju(db_num=1, bit_ads=3, bool_value=False)
        if button.text() == "夹爪反转":
            try:
                sudden_stop(self.axis)
                con_vmove(self.axis, -1)
            except Exception as e:
                # 捕获并打印错误信息
                print(f"Error writing to PLC: {e}")
                return
            self.fa_shuju(db_num=1, bit_ads=3, bool_value=True, txt="夹爪反转")
            self.fa_shuju(db_num=1, bit_ads=5, bool_value=False)
            self.fa_shuju(db_num=1, bit_ads=1, bool_value=False)
        if button.text() == "步进前进":
            self.fa_shuju(db_num=1, bit_ads=16, bool_value=True, txt="步进前进")
            self.fa_shuju(db_num=1, bit_ads=15, bool_value=False)
            self.fa_shuju(db_num=1, bit_ads=14, bool_value=False)
            self.fa_shuju(db_num=1, bit_ads=12, bool_value=False)
            self.fa_shuju(db_num=1, bit_ads=84, bool_value=False)
            self.fa_shuju(db_num=1, bit_ads=82, bool_value=True)
        if button.text() == "步进后退":
            self.fa_shuju(db_num=1, bit_ads=14, bool_value=True, txt="步进后退")
            self.fa_shuju(db_num=1, bit_ads=15, bool_value=False)
            self.fa_shuju(db_num=1, bit_ads=16, bool_value=False)
            self.fa_shuju(db_num=1, bit_ads=12, bool_value=False)
            self.fa_shuju(db_num=1, bit_ads=84, bool_value=False)
            self.fa_shuju(db_num=1, bit_ads=82, bool_value=True)
        if button.text() == "压头抬起":
            self.fa_shuju(db_num=1, bit_ads=30, bool_value=True, txt="压头抬起")
            self.fa_shuju(db_num=1, bit_ads=31, bool_value=False)
            self.fa_shuju(db_num=1, bit_ads=32, bool_value=False)
            self.fa_shuju(db_num=1, bit_ads=33, bool_value=False)
            self.fa_shuju(db_num=1, bit_ads=81, bool_value=False)
            self.fa_shuju(db_num=1, bit_ads=82, bool_value=True)
        if button.text() == "压头下压":
            self.fa_shuju(db_num=1, bit_ads=31, bool_value=True, txt="压头下压")
            self.fa_shuju(db_num=1, bit_ads=30, bool_value=False)
            self.fa_shuju(db_num=1, bit_ads=32, bool_value=False)
            self.fa_shuju(db_num=1, bit_ads=33, bool_value=False)
            self.fa_shuju(db_num=1, bit_ads=81, bool_value=False)
            self.fa_shuju(db_num=1, bit_ads=82, bool_value=True)
        super(QPushButton, button).mousePressEvent(event)
    def on_mouse_release(self, event, button):
        # 松开时，按钮状态设置为未按下
        button.setChecked(False)
        if button.text() == "夹爪正转":
            try:
                sudden_stop(self.axis)
            except Exception as e:
                # 捕获并打印错误信息
                print(f"Error writing to PLC: {e}")
                return
            self.fa_shuju(db_num=1, bit_ads=1, bool_value=False, txt="夹爪正转停止"),
        if button.text() == "夹爪反转":
            try:
                sudden_stop(self.axis)
            except Exception as e:
                # 捕获并打印错误信息
                print(f"Error writing to PLC: {e}")
                return
            self.fa_shuju(db_num=1, bit_ads=3, bool_value=False, txt="夹爪反转停止")
        if button.text() == "步进前进":
            self.fa_shuju(db_num=1, bit_ads=16, bool_value=False, txt="步进前进停止")
        if button.text() == "步进后退":
            self.fa_shuju(db_num=1, bit_ads=14, bool_value=False, txt="步进后退停止")
        if button.text() == "压头下压":
            self.fa_shuju(db_num=1, bit_ads=31, bool_value=False, txt="压头下压停止")
        if button.text() == "压头抬起":
            self.fa_shuju(db_num=1, bit_ads=30, bool_value=False, txt="压头抬起停止")
        super(QPushButton, button).mouseReleaseEvent(event)
    def load_param(self):
        """从 txt 文件加载参数并设置为输入框的默认值"""
        try:
            with open('parameters.txt', 'r') as file:
                for line in file:
                    line = line.strip()  # 去掉前后空白
                    if '：' in line:
                        name, value = line.split('：', 1)  # 按冒号分隔
                        name = name.strip()
                        value = value.strip()
                        if name in self.input_boxes:  # 检查名称是否在输入框字典中
                            self.input_boxes[name].setText(value)  # 设置输入框的默认值
                            self.param[name] = value
                # print(self.param['压下量系数-P1'])
            self.param_log_widget.append("已恢复上次关闭应用时，对应各项参数")
            self.param_log_widget.ensureCursorVisible()
            # print(self.param)
        except FileNotFoundError:
            print("未找到参数文件，使用默认值")  # 如果文件未找到，可以考虑设置一个默认值
            self.param_log_widget.append("未找到参数文件，使用默认值")
            self.param_log_widget.ensureCursorVisible()

            self.input_boxes['半径容忍-P1'].setText("1.0")
            self.input_boxes['半径容忍-P2'].setText("1.0")
            self.input_boxes['半径容忍-P3'].setText("2.5")
            self.input_boxes['半径容忍-P4'].setText("2.5")
            self.input_boxes['半径容忍-P5'].setText("2.5")
            self.input_boxes['半径容忍-P6'].setText("1.0")
            self.input_boxes['半径容忍-P7'].setText("1.0")
            self.input_boxes['压下量系数-P1'].setText("0.3")
            self.input_boxes['压下量系数-P2'].setText("0.3")
            self.input_boxes['压下量系数-P3'].setText("0.5")
            self.input_boxes['压下量系数-P4'].setText("0.5")
            self.input_boxes['压下量系数-P5'].setText("0.5")
            self.input_boxes['压下量系数-P6'].setText("0.3")
            self.input_boxes['压下量系数-P7'].setText("0.3")
            self.input_boxes['下压补偿值-P1'].setText("0.0")
            self.input_boxes['下压补偿值-P2'].setText("0.0")
            self.input_boxes['下压补偿值-P3'].setText("0.0")
            self.input_boxes['下压补偿值-P4'].setText("0.0")
            self.input_boxes['下压补偿值-P5'].setText("0.0")
            self.input_boxes['下压补偿值-P6'].setText("0.0")
            self.input_boxes['下压补偿值-P7'].setText("0.0")
            self.input_boxes['连续下压增量-压1'].setText("1.0")
            self.input_boxes['连续下压增量-压2'].setText("1.0")
            self.input_boxes['连续下压增量-压3'].setText("1.0")
            self.input_boxes['连续下压增量-压4'].setText("1.0")
            self.input_boxes['连续下压增量-压5'].setText("1.0")
            self.input_boxes['最大校直次数'].setText("15.0")
            self.input_boxes['工件P1点半径'].setText("50.0")

            self.param['半径容忍-P1'] = 1.0
            self.param['半径容忍-P2'] = 1.0
            self.param['半径容忍-P3'] = 2.5
            self.param['半径容忍-P4'] = 2.5
            self.param['半径容忍-P5'] = 2.5
            self.param['半径容忍-P6'] = 1.0
            self.param['半径容忍-P7'] = 1.0
            self.param['压下量系数-P1'] = 0.3
            self.param['压下量系数-P2'] = 0.3
            self.param['压下量系数-P3'] = 0.5
            self.param['压下量系数-P4'] = 0.5
            self.param['压下量系数-P5'] = 0.5
            self.param['压下量系数-P6'] = 0.3
            self.param['压下量系数-P7'] = 0.3
            self.param['下压补偿值-P1'] = 0.0
            self.param['下压补偿值-P2'] = 0.0
            self.param['下压补偿值-P3'] = 0.0
            self.param['下压补偿值-P4'] = 0.0
            self.param['下压补偿值-P5'] = 0.0
            self.param['下压补偿值-P6'] = 0.0
            self.param['下压补偿值-P7'] = 0.0
            self.param['连续下压增量-压1'] = 1.0
            self.param['连续下压增量-压2'] = 1.0
            self.param['连续下压增量-压3'] = 1.0
            self.param['连续下压增量-压4'] = 1.0
            self.param['连续下压增量-压5'] = 1.0
            self.param['最大校直次数'] = 15.0
            self.param['工件P1点半径'] = 50.0
        except Exception as e:
            print(f"读取参数时出错: {e}")
    def update_param(self):
        """保存当前参数值到 txt 文件"""
        with open('parameters.txt', 'w') as file:
            for label in self.labels:
                param_value = self.input_boxes[label].text()  # 获取输入框的当前值
                if not param_value:
                    print(self.param[label])
                    param_value = float(self.param[label])
                else:
                    param_value = float(param_value)
                file.write(f"{label}：{param_value}\n")  # 按格式写入参数值
                self.input_boxes[label].setText(str(param_value))  # 设置输入框的默认值
                self.param[label] = param_value
        ff = {label: self.input_boxes[label].text() for label in self.labels}
        print("参数已保存:\n", ff)
        self.param_log_widget.append(f"参数已保存:\n{ff}")
        self.param_log_widget.ensureCursorVisible()
    def closeEvent(self, event):
        """在关闭窗口时保存参数"""
        self.update_param()  # 关闭时保存参数
        event.accept()  # 继续关闭窗口
    def update_log(self, text):
        self.auto_log_widget.append(text)
        self.auto_log_widget.ensureCursorVisible()
    def lian_PLC_auto(self):
        # 更新 PLC_address 的值
        PLC_IP = self.input_IP.text()
        PLC_rack = self.input_rack.text()
        PLC_slot = self.input_slot.text()
        # print(type(PLC_IP))
        if not PLC_IP:
            PLC_IP = self.PLC_IP
        self.PLC_IP = PLC_IP
        if not PLC_rack:
            PLC_rack = self.PLC_rack
        PLC_rack = int(PLC_rack)
        self.PLC_rack = PLC_rack
        if not PLC_slot:
            PLC_slot = self.PLC_slot
        PLC_slot = int(PLC_slot)
        self.PLC_slot = PLC_slot
        print("尝试连接PLC：：", "\n", "设备IP：", self.PLC_IP)
        self.param_log_widget.append(f"尝试连接PLC：：\n 设备IP： {self.PLC_IP}")
        self.param_log_widget.ensureCursorVisible()
        # 汇川
        if self.radio_button_hc.isChecked():
            color = 'red'
            message = f"请选择西门子！！！"
            html_message = f'<span style="color: {color};">{message}</span>'
            try:
                self.param_log_widget.append(html_message)
                self.param_log_widget.ensureCursorVisible()
            except Exception as e:
                self.param_log_widget.append(html_message)
                self.param_log_widget.ensureCursorVisible()
        # 西门子
        if self.radio_button_xmz.isChecked():
            try:
                self.client_xmz.connect(self.PLC_IP, self.PLC_rack, self.PLC_slot)
                color = 'green'
                message = f"成功连接PLC：：\n设备IP：{self.PLC_IP}"
                html_message = f'<span style="color: {color};">{message}</span>'
                self.param_log_widget.append(html_message)
                self.param_log_widget.ensureCursorVisible()
                # # 获取PLC的状态
                # status = self.client_xmz.get_cpu_state()
                # print(f"当前PLC状态: {status}")
                # # 如果PLC不在运行状态，则将其设置为运行状态
                # if status != snap7.types.CpuStatus.Run:
                #     self.client_xmz.plc_control(snap7.types.PlcControlCommand.Run)
                #     new_status = self.client_xmz.get_cpu_state()
                #     print(f"已尝试将PLC设置为运行状态，新状态: {new_status}")
            except Exception as e:
                color = 'red'
                message = f"连接失败: {e}"
                html_message = f'<span style="color: {color};">{message}</span>'
                self.param_log_widget.append(html_message)
                self.param_log_widget.ensureCursorVisible()
    def duan_PLC_auto(self):
        if self.radio_button_xmz.isChecked():
            try:
                self.client_xmz.disconnect()
                color = 'orange'
                message = "success 断开"
                html_message = f'<span style="color: {color};">{message}</span>'
                self.param_log_widget.append(html_message)
                self.param_log_widget.ensureCursorVisible()
            except Exception as e:
                color = 'red'
                message = f"连接失败: {e}"
                html_message = f'<span style="color: {color};">{message}</span>'
                self.param_log_widget.append(html_message)
                self.param_log_widget.ensureCursorVisible()
        elif self.radio_button_hc.isChecked():
            color = 'red'
            message = f"请选择西门子！！！"
            html_message = f'<span style="color: {color};">{message}</span>'
            try:
                self.param_log_widget.append(html_message)
                self.param_log_widget.ensureCursorVisible()
            except Exception as e:
                self.param_log_widget.append(html_message)
                self.param_log_widget.ensureCursorVisible()
    def xiaya_real(self):
        real_value = self.input_real.text()
        if not real_value:
            QMessageBox.warning(window, "错啦", "请先输入要下压的距离哦！！！", QMessageBox.Ok)
            return
        else:
            try:
                real_value = float(real_value)
            except ValueError:
                real_value = 0.0
        try:
            if real_value > 40:
                real_value = 40
            real_value *= -1
            self.fa_shuju(db_num=1, bit_ads=55, bool_value=True, txt="下压real")
            self.fa_shuju(db_num=1, bit_ads=82, bool_value=True)
            self.fa_shuju(db_num=1, bit_ads=81, bool_value=True)
            time.sleep(0.1)
            write_real(self.client_xmz, 20, real_value)
        except Exception as e:
            print(f"Error writing to PLC: {e}")
            return
    def ya_strategy(self, n):
        if self.worker_thread_auto == self.yyfffyy:
            if n > float(self.param['最大校直次数']):
                return -1, 0, 0, 0
            # ############# 压头1、5 ########################################################################################
            if self.bar_mo[0] > float(self.param['半径容忍-P1']) or self.bar_mo[1] > float(self.param['半径容忍-P2']) or self.bar_mo[5] > float(self.param['半径容忍-P6']) or self.bar_mo[6] > float(self.param['半径容忍-P7']):
                ya_n = self.bar_mo.index(max(self.bar_mo[0], self.bar_mo[1], self.bar_mo[5], self.bar_mo[6]))
                loss = float(self.bar_mo[ya_n])
                thita = (180 + self.kesai + self.bar_xj[ya_n]) % 360
                # if ya_n == 0:       # 279.42
                #     ya_real = 292.74 + float(self.param['压下量系数-P1']) * loss + float(self.param['下压补偿值-P1']) # - float(self.param['工件P1点半径'])
                # elif ya_n == 1:
                #     ya_real = 292.74 + float(self.param['压下量系数-P2']) * loss + float(self.param['下压补偿值-P2']) # - float(self.param['工件P1点半径'])
                # elif ya_n == 5:     # 279.48
                #     ya_real = 291.75 + float(self.param['压下量系数-P6']) * loss + float(self.param['下压补偿值-P6']) # - float(self.param['工件P1点半径'])
                # else:
                #     ya_real = 291.75 + float(self.param['压下量系数-P7']) * loss + float(self.param['下压补偿值-P7']) # - float(self.param['工件P1点半径'])

                if ya_n == 0:
                    z1 = self.bar_mo[1] * np.cos(np.radians(abs(self.bar_xj[0] - self.bar_xj[1]) % 360))
                    z2 = self.bar_mo[2] * np.cos(np.radians(abs(self.bar_xj[0] - self.bar_xj[2]) % 360))
                    ya_real = 292.24 - 0.2 - 0.1 + \
                              float(self.param['压下量系数-P1']) * (2.8 - np.exp(1 - loss)) + float(self.param['下压补偿值-P1']) + \
                              0.2 / (np.exp(-2.8 * z1) + 1) + 0.1 / (np.exp(-1 * z2) + 1)
                elif ya_n == 1:
                    z0 = self.bar_mo[0] * np.cos(np.radians(abs(self.bar_xj[1] - self.bar_xj[0]) % 360))
                    z2 = self.bar_mo[2] * np.cos(np.radians(abs(self.bar_xj[1] - self.bar_xj[2]) % 360))
                    ya_real = 292.24 - 0.15 - 0.15 + \
                              float(self.param['压下量系数-P2']) * (2.8 - np.exp(1 - loss)) + float(self.param['下压补偿值-P2'])+ \
                              0.3 / (np.exp(-3 * z0) + 2) + 0.3 / (np.exp(-1.6 * z2) + 2)
                elif ya_n == 5:
                    z4 = self.bar_mo[4] * np.cos(np.radians(abs(self.bar_xj[5] - self.bar_xj[4]) % 360))
                    z6 = self.bar_mo[6] * np.cos(np.radians(abs(self.bar_xj[5] - self.bar_xj[6]) % 360))
                    ya_real = 291.25 - 0.15 - 0.15 + \
                              float(self.param['压下量系数-P6']) * (2.8 - np.exp(1 - loss)) + float(self.param['下压补偿值-P6'])+ \
                              0.3 / (np.exp(-3 * z6) + 2) + 0.3 / (np.exp(-1.6 * z4) + 2)
                else:
                    z4 = self.bar_mo[4] * np.cos(np.radians(abs(self.bar_xj[6] - self.bar_xj[4]) % 360))
                    z5 = self.bar_mo[5] * np.cos(np.radians(abs(self.bar_xj[6] - self.bar_xj[5]) % 360))
                    ya_real = 291.25  - 0.2 - 0.1 + \
                              float(self.param['压下量系数-P7']) * (2.8 - np.exp(1 - loss)) + float(self.param['下压补偿值-P7']) + \
                              0.2 / (np.exp(-2.8 * z5) + 1) + 0.1 / (np.exp(-1 * z4) + 1)

                if ya_n <= 1:
                    ya_n = 1
                else:
                    ya_n = 5
            # ############# 压头2、3、4 #####################################################################################
            elif self.bar_mo[2] > float(self.param['半径容忍-P3']) or self.bar_mo[3] > float(self.param['半径容忍-P4']) or self.bar_mo[4] > float(self.param['半径容忍-P5']):
                ya_n = self.bar_mo.index(max(self.bar_mo[2], self.bar_mo[3], self.bar_mo[4]))
                thita = (180 + round(self.bar_xj[ya_n] / 90) * 90 + self.kesai) % 360
                i = round(self.bar_xj[ya_n] % 90)
                if i > 45:
                    loss = float(self.bar_mo[ya_n]) * numpy.sin(i * numpy.pi / 180)
                else:
                    loss = float(self.bar_mo[ya_n]) * numpy.cos(i * numpy.pi / 180)

                # if ya_n == 2:   # 276.75
                #     ya_real = 289.68 + float(self.param['压下量系数-P3']) * loss + float(self.param['下压补偿值-P3']) # - float(self.param['工件P1点半径'])
                # elif ya_n == 3: # 275.74
                #     ya_real = 295.68 + float(self.param['压下量系数-P4']) * loss + float(self.param['下压补偿值-P4']) # - float(self.param['工件P1点半径'])
                # else:           # 276.54
                #     ya_real = 289.18 + float(self.param['压下量系数-P5']) * loss + float(self.param['下压补偿值-P5']) # - float(self.param['工件P1点半径'])

                if ya_n == 2:
                    ya_real = 293.38 + float(self.param['压下量系数-P3']) * (3 - np.exp(2 - loss)) + float(self.param['下压补偿值-P3'])
                elif ya_n == 3:
                    ya_real = 294.68 + float(self.param['压下量系数-P4']) * (3 - np.exp(2 - loss)) + float(self.param['下压补偿值-P4'])
                else:
                    ya_real = 293.08 + float(self.param['压下量系数-P5']) * (3 - np.exp(2 - loss)) + float(self.param['下压补偿值-P5'])

            else:
                return 1, 0, 0, 0

            if thita > 180:
                thita -= 360

            if n > 1 and self.ya_n == ya_n and abs(thita) < 30:
                if ya_n == 1:
                    ya_real = float(self.param['连续下压增量-压1']) * float(self.param['压下量系数-P2']) + self.ya_real
                elif ya_n == 2:
                    ya_real = float(self.param['连续下压增量-压2']) * float(self.param['压下量系数-P3']) + self.ya_real
                elif ya_n == 3:
                    ya_real = float(self.param['连续下压增量-压3']) * float(self.param['压下量系数-P4']) + self.ya_real
                elif ya_n == 4:
                    ya_real = float(self.param['连续下压增量-压4']) * float(self.param['压下量系数-P5']) + self.ya_real
                else:
                    ya_real = float(self.param['连续下压增量-压5']) * float(self.param['压下量系数-P6']) + self.ya_real
            self.ya_n = ya_n
            self.thita = thita
            self.ya_real = ya_real
            return 0, ya_n, ya_real, thita
        elif self.worker_thread_auto == self.yfffffy:
            if n > float(self.param['最大校直次数']):
                return -1, 0, 0, 0
            # ############# 压头1、5 ########################################################################################
            if self.bar_mo[0] > float(self.param['半径容忍-P1']) or self.bar_mo[1] > float(self.param['半径容忍-P2']) or \
                    self.bar_mo[5] > float(self.param['半径容忍-P6']) or self.bar_mo[6] > float(
                    self.param['半径容忍-P7']):
                ya_n = self.bar_mo.index(max(self.bar_mo[0], self.bar_mo[1], self.bar_mo[5], self.bar_mo[6]))

                i = round(self.bar_xj[ya_n] % 90)
                if i > 45:
                    loss = float(self.bar_mo[ya_n]) * numpy.sin(i * numpy.pi / 180)
                else:
                    loss = float(self.bar_mo[ya_n]) * numpy.cos(i * numpy.pi / 180)

                thita = (180 + round(self.bar_xj[ya_n] / 90) * 90 + self.kesai) % 360

                if ya_n == 0:
                    ya_real = 292.24 + float(self.param['压下量系数-P1']) * (2.8 - np.exp(1 - loss)) + float(
                        self.param['下压补偿值-P1'])
                elif ya_n == 1:
                    ya_real = 292.24 + float(self.param['压下量系数-P2']) * (2.8 - np.exp(1 - loss)) + float(
                        self.param['下压补偿值-P2'])
                elif ya_n == 5:
                    ya_real = 291.25 + float(self.param['压下量系数-P6']) * (2.8 - np.exp(1 - loss)) + float(
                        self.param['下压补偿值-P6'])
                else:
                    ya_real = 291.25 + float(self.param['压下量系数-P7']) * (2.8 - np.exp(1 - loss)) + float(
                        self.param['下压补偿值-P7'])

                if ya_n <= 1:
                    ya_n = 1
                else:
                    ya_n = 5
            # ############# 压头2、3、4 #####################################################################################
            elif self.bar_mo[2] > float(self.param['半径容忍-P3']) or self.bar_mo[3] > float(
                    self.param['半径容忍-P4']) or self.bar_mo[4] > float(self.param['半径容忍-P5']):
                ya_n = self.bar_mo.index(max(self.bar_mo[2], self.bar_mo[3], self.bar_mo[4]))
                thita = (180 + round(self.bar_xj[ya_n] / 90) * 90 + self.kesai) % 360
                i = round(self.bar_xj[ya_n] % 90)
                if i > 45:
                    loss = float(self.bar_mo[ya_n]) * numpy.sin(i * numpy.pi / 180)
                else:
                    loss = float(self.bar_mo[ya_n]) * numpy.cos(i * numpy.pi / 180)

                if ya_n == 2:
                    ya_real = 293.38 + float(self.param['压下量系数-P3']) * (3 - np.exp(2 - loss)) + float(
                        self.param['下压补偿值-P3'])
                elif ya_n == 3:
                    ya_real = 294.68 + float(self.param['压下量系数-P4']) * (3 - np.exp(2 - loss)) + float(
                        self.param['下压补偿值-P4'])
                else:
                    ya_real = 293.08 + float(self.param['压下量系数-P5']) * (3 - np.exp(2 - loss)) + float(
                        self.param['下压补偿值-P5'])

            else:
                return 1, 0, 0, 0

            if thita > 180:
                thita -= 360

            if n > 1 and self.ya_n == ya_n and abs(thita) < 30:
                if ya_n == 1:
                    ya_real = float(self.param['连续下压增量-压1']) * float(self.param['压下量系数-P2']) + self.ya_real
                elif ya_n == 2:
                    ya_real = float(self.param['连续下压增量-压2']) * float(self.param['压下量系数-P3']) + self.ya_real
                elif ya_n == 3:
                    ya_real = float(self.param['连续下压增量-压3']) * float(self.param['压下量系数-P4']) + self.ya_real
                elif ya_n == 4:
                    ya_real = float(self.param['连续下压增量-压4']) * float(self.param['压下量系数-P5']) + self.ya_real
                else:
                    ya_real = float(self.param['连续下压增量-压5']) * float(self.param['压下量系数-P6']) + self.ya_real
            self.ya_n = ya_n
            self.thita = thita
            self.ya_real = ya_real
            return 0, ya_n, ya_real, thita
        elif self.worker_thread_auto == self.yyyyyyy:
            if n > float(self.param['最大校直次数']):
                return -1, 0, 0, 0
            # ############# 压头1、5 ########################################################################################
            if self.bar_mo[0] > float(self.param['半径容忍-P1']) or self.bar_mo[1] > float(self.param['半径容忍-P2']) or \
                    self.bar_mo[5] > float(self.param['半径容忍-P6']) or self.bar_mo[6] > float(
                    self.param['半径容忍-P7']):
                ya_n = self.bar_mo.index(max(self.bar_mo[0], self.bar_mo[1], self.bar_mo[5], self.bar_mo[6]))
                loss = float(self.bar_mo[ya_n])
                thita = (180 + self.kesai + self.bar_xj[ya_n]) % 360

                if ya_n == 0:
                    ya_real = 292.24 + float(self.param['压下量系数-P1']) * (2.8 - np.exp(1 - loss)) + float(
                        self.param['下压补偿值-P1'])
                elif ya_n == 1:
                    ya_real = 292.24 + float(self.param['压下量系数-P2']) * (2.8 - np.exp(1 - loss)) + float(
                        self.param['下压补偿值-P2'])
                elif ya_n == 5:
                    ya_real = 291.25 + float(self.param['压下量系数-P6']) * (2.8 - np.exp(1 - loss)) + float(
                        self.param['下压补偿值-P6'])
                else:
                    ya_real = 291.25 + float(self.param['压下量系数-P7']) * (2.8 - np.exp(1 - loss)) + float(
                        self.param['下压补偿值-P7'])

                if ya_n <= 1:
                    ya_n = 1
                else:
                    ya_n = 5
            # ############# 压头2、3、4 #####################################################################################
            elif self.bar_mo[2] > float(self.param['半径容忍-P3']) or self.bar_mo[3] > float(
                    self.param['半径容忍-P4']) or self.bar_mo[4] > float(self.param['半径容忍-P5']):

                ya_n = self.bar_mo.index(max(self.bar_mo[2], self.bar_mo[3], self.bar_mo[4]))
                loss = float(self.bar_mo[ya_n])
                thita = (180 + self.kesai + self.bar_xj[ya_n]) % 360

                if ya_n == 2:
                    ya_real = 293.38 + float(self.param['压下量系数-P3']) * (3 - np.exp(2 - loss)) + float(
                        self.param['下压补偿值-P3'])
                elif ya_n == 3:
                    ya_real = 294.68 + float(self.param['压下量系数-P4']) * (3 - np.exp(2 - loss)) + float(
                        self.param['下压补偿值-P4'])
                else:
                    ya_real = 293.08 + float(self.param['压下量系数-P5']) * (3 - np.exp(2 - loss)) + float(
                        self.param['下压补偿值-P5'])

            else:
                return 1, 0, 0, 0

            if thita > 180:
                thita -= 360

            if n > 1 and self.ya_n == ya_n and abs(thita) < 30:
                if ya_n == 1:
                    ya_real = float(self.param['连续下压增量-压1']) * float(self.param['压下量系数-P2']) + self.ya_real
                elif ya_n == 2:
                    ya_real = float(self.param['连续下压增量-压2']) * float(self.param['压下量系数-P3']) + self.ya_real
                elif ya_n == 3:
                    ya_real = float(self.param['连续下压增量-压3']) * float(self.param['压下量系数-P4']) + self.ya_real
                elif ya_n == 4:
                    ya_real = float(self.param['连续下压增量-压4']) * float(self.param['压下量系数-P5']) + self.ya_real
                else:
                    ya_real = float(self.param['连续下压增量-压5']) * float(self.param['压下量系数-P6']) + self.ya_real
            self.ya_n = ya_n
            self.thita = thita
            self.ya_real = ya_real
            return 0, ya_n, ya_real, thita
        else:
            return -1, 0, 0, 0
    def auto_run(self):
        # 禁用标签页切换
        self.setTabEnabled(4, False)  # 禁用第一个标签页
        self.setTabEnabled(1, False)  # 禁用第二个标签页
        self.setTabEnabled(2, False)  # 禁用第三个标签页
        self.setTabEnabled(3, False)  # 禁用第四个标签页
        self.works.setEnabled(False)
        self.EN = True
        self.fa_shuju(db_num=1, bit_ads=80, bool_value=False)
        # 下压、步进、夹爪isrun、init_isrun
        self.fa_shuju(db_num=1, bit_ads=81, bool_value=True)
        self.fa_shuju(db_num=1, bit_ads=84, bool_value=True)
        self.fa_shuju(db_num=1, bit_ads=85, bool_value=True)
        self.fa_shuju(db_num=1, bit_ads=58, bool_value=True)
        # PLC的EN
        self.fa_shuju(db_num=1, bit_ads=57, bool_value=True)
        self.fa_shuju(db_num=1, bit_ads=82, bool_value=True)
        color = 'green'
        message = "开始检测"
        html_message = f'<span style="color: {color};">{message}</span>'
        self.auto_log_widget.append(html_message)
        self.auto_log_widget.ensureCursorVisible()
        # 创建并启动新线程
        thread = threading.Thread(target=self.xun_huan)
        thread.daemon = True  # 设置为守护线程，程序退出时自动结束
        thread.start()
    def xun_huan(self):
        urgent = 1
        while self.EN:
            # # 启动初始化
            self.fa_shuju(db_num=1, bit_ads=37, bool_value=False)
            self.fa_shuju(db_num=1, bit_ads=52, bool_value=False)
            self.fa_shuju(db_num=1, bit_ads=77, bool_value=False)
            self.fa_shuju(db_num=1, bit_ads=53, bool_value=False)
            self.fa_shuju(db_num=1, bit_ads=5, bool_value=False)
            self.fa_shuju(db_num=1, bit_ads=15, bool_value=False)
            self.fa_shuju(db_num=1, bit_ads=32, bool_value=False)

            self.fa_shuju(db_num=1, bit_ads=20, bool_value=False)
            self.fa_shuju(db_num=1, bit_ads=22, bool_value=False)
            self.fa_shuju(db_num=1, bit_ads=24, bool_value=False)
            self.fa_shuju(db_num=1, bit_ads=26, bool_value=False)
            self.fa_shuju(db_num=1, bit_ads=28, bool_value=False)
            self.signals.log_update.emit('新的轴管，启动初始化')
            # 判断PLC是否在执行初始化
            try:
                init_isrun = read_bool(self.client_xmz, 58)
            except Exception as e:
                init_isrun = True
            while init_isrun:
                try:
                    init_isrun = read_bool(self.client_xmz, 58)
                    urgent = read_bool(self.client_xmz, 62)
                except:
                    init_isrun = True
                    urgent = True
                if not self.EN or not urgent:
                    sudden_stop(self.axis)
                    return
                else:
                    time.sleep(0.2)
            # 判断PLC是否在动作
            xy_isrun = read_bool(self.client_xmz, 81)
            bj_isrun = read_bool(self.client_xmz, 84)
            jz_isrun = read_bool(self.client_xmz, 85)
            while xy_isrun or bj_isrun or jz_isrun:
                xy_isrun = read_bool(self.client_xmz, 81)
                bj_isrun = read_bool(self.client_xmz, 84)
                jz_isrun = read_bool(self.client_xmz, 85)
                urgent = read_bool(self.client_xmz, 62)
                if not self.EN or not urgent:
                    sudden_stop(self.axis)
                    return
                else:
                    time.sleep(0.2)
            print("机械准备完毕")
            # self.init_param   # 日志放在子函数中
            # 判断传感器是否有料
            self.youliao = read_bool(self.client_xmz, 79)
            if not self.youliao:
                # 通知PLC请求上料
                self.fa_shuju(db_num=1, bit_ads=86, bool_value=True)
                self.fa_shuju(db_num=1, bit_ads=84, bool_value=True)
                self.fa_shuju(db_num=1, bit_ads=80, bool_value=False)
                self.youliao = read_bool(self.client_xmz, 80)
                self.signals.log_update.emit('等待检验位有料')
                while not self.youliao:
                    self.youliao = read_bool(self.client_xmz, 80)
                    urgent = read_bool(self.client_xmz, 62)
                    if not self.EN or not urgent:
                        sudden_stop(self.axis)
                        return
                    else:
                        time.sleep(0.2)
            print("当前有料，可以开始准备")
            self.jiaozhi = 1
            nn = 0
            while self.jiaozhi and self.EN:
                nn += 1
                # 单检一周准备
                self.fa_shuju(db_num=1, bit_ads=52, bool_value=False)
                self.fa_shuju(db_num=1, bit_ads=77, bool_value=False)
                self.fa_shuju(db_num=1, bit_ads=53, bool_value=True)
                self.fa_shuju(db_num=1, bit_ads=82, bool_value=True)
                self.fa_shuju(db_num=1, bit_ads=5, bool_value=False)
                self.fa_shuju(db_num=1, bit_ads=85, bool_value=True)
                self.plc_isrun = read_bool(self.client_xmz, 85)
                self.signals.log_update.emit('单检一周准备')
                while self.plc_isrun:
                    self.plc_isrun = read_bool(self.client_xmz, 85)
                    urgent = read_bool(self.client_xmz, 62)
                    if not self.EN or not urgent:
                        sudden_stop(self.axis)
                        return
                    else:
                        time.sleep(0.2)
                # 等待夹爪准备好启动PC单检一周
                self.work_isrun = True
                self.circle_mode = "自动"
                self.worker_thread_auto.start()
                self.signals.log_update.emit('单周拟合')
                while self.work_isrun:
                    urgent = read_bool(self.client_xmz, 62)
                    if not self.EN or not urgent:
                        sudden_stop(self.axis)
                        return
                    else:
                        time.sleep(0.2)

                # 在这里进行下压策略
                ok, ya_n, ya_real, thita = self.ya_strategy(nn)     # 下压量

                urgent = read_bool(self.client_xmz, 62)
                if not self.EN or not urgent:
                    return

                ya_real = 274.4 if ya_real < 274.4 else ya_real
                ya_real = 323 if ya_real > 323 else ya_real
                ya_th = self.Tulun.get_th(ya_real)                  # 角度量
                ya_th *= -0.201552                                  # 下压轴动作量
                self.signals.log_update.emit(f"合格：{ok}, 压头：{ya_n},下压工程量:{-1 * ya_th}")
                if ok == 1 or ok == -1:
                    fast_pmove(self.axis, int((self.kesai-42) / 360 * self.mc_circle))
                    if ok == 1:
                        self.signals.log_update.emit('ok了，出料准备！！！！！！')
                        self.fa_shuju(db_num=1, bit_ads=73, bool_value=False)
                        self.fa_shuju(db_num=1, bit_ads=75, bool_value=True)
                    if ok == -1:
                        self.signals.log_update.emit('下压超时，被判NG！！！')
                        self.fa_shuju(db_num=1, bit_ads=75, bool_value=False)
                        self.fa_shuju(db_num=1, bit_ads=73, bool_value=True)

                        self.EN = False
                        self.work_isrun = False
                        sudden_stop(self.axis)
                        # PLC的EN
                        self.fa_shuju(db_num=1, bit_ads=55, bool_value=True, txt="下压real")
                        self.fa_shuju(db_num=1, bit_ads=82, bool_value=True)
                        self.fa_shuju(db_num=1, bit_ads=81, bool_value=True)
                        time.sleep(0.1)
                        write_real(self.client_xmz, 20, 0.1)
                        self.fa_shuju(db_num=1, bit_ads=82, bool_value=False)
                        # 禁用标签页切换
                        self.setTabEnabled(4, True)
                        self.setTabEnabled(1, True)
                        self.setTabEnabled(2, True)
                        self.setTabEnabled(3, True)
                        self.signals.log_update.emit('人工核验')
                        return

                    while (check_done(self.axis)):
                        time.sleep(0.2)
                    # 单检一周复位
                    self.fa_shuju(db_num=1, bit_ads=53, bool_value=False)
                    self.fa_shuju(db_num=1, bit_ads=77, bool_value=False)
                    self.fa_shuju(db_num=1, bit_ads=52, bool_value=True)
                    self.fa_shuju(db_num=1, bit_ads=82, bool_value=True)
                    self.fa_shuju(db_num=1, bit_ads=5, bool_value=False)
                    self.fa_shuju(db_num=1, bit_ads=85, bool_value=True)
                    self.plc_isrun = read_bool(self.client_xmz, 85)
                    while self.plc_isrun:
                        self.plc_isrun = read_bool(self.client_xmz, 85)
                        urgent = read_bool(self.client_xmz, 62)
                        if not self.EN or not urgent:
                            sudden_stop(self.axis)
                            return
                        else:
                            time.sleep(0.2)

                    self.fa_shuju(db_num=1, bit_ads=82, bool_value=True)
                    self.fa_shuju(db_num=1, bit_ads=84, bool_value=True)
                    self.fa_shuju(db_num=1, bit_ads=54, bool_value=True)
                    bj_isrun = read_bool(self.client_xmz, 84)
                    self.signals.log_update.emit('出料！！！')
                    while bj_isrun:
                        bj_isrun = read_bool(self.client_xmz, 84)
                        urgent = read_bool(self.client_xmz, 62)
                        if not self.EN or not urgent:
                            sudden_stop(self.axis)
                            return
                        else:
                            time.sleep(0.2)

                    self.jiaozhi = 0

                elif ok == 0:
                    # 将要压的部位凸面朝上
                    fast_pmove(self.axis, int((thita + 3) / 360 * self.mc_circle))
                    self.signals.log_update.emit('下压准备')
                    while (check_done(self.axis)):
                        time.sleep(0.2)
                    # 夹爪复位，压头动作，支撑动作（等待动作完成）
                    # 夹爪复位
                    self.fa_shuju(db_num=1, bit_ads=53, bool_value=False)
                    self.fa_shuju(db_num=1, bit_ads=52, bool_value=False)
                    self.fa_shuju(db_num=1, bit_ads=77, bool_value=True)
                    self.fa_shuju(db_num=1, bit_ads=82, bool_value=True)
                    self.fa_shuju(db_num=1, bit_ads=5, bool_value=False)
                    self.fa_shuju(db_num=1, bit_ads=85, bool_value=True)
                    # 支撑、压头准备   # todo 设置压头和支撑
                    if ya_n == 1:
                        self.fa_shuju(db_num=1, bit_ads=40, bool_value=False)
                        self.fa_shuju(db_num=1, bit_ads=43, bool_value=False)
                        self.fa_shuju(db_num=1, bit_ads=46, bool_value=False)
                        self.fa_shuju(db_num=1, bit_ads=49, bool_value=False)

                        self.fa_shuju(db_num=1, bit_ads=20, bool_value=True)
                        self.fa_shuju(db_num=1, bit_ads=22, bool_value=False)
                        self.fa_shuju(db_num=1, bit_ads=24, bool_value=False)
                        self.fa_shuju(db_num=1, bit_ads=26, bool_value=False)
                        self.fa_shuju(db_num=1, bit_ads=28, bool_value=False)
                    elif ya_n == 2:
                        self.fa_shuju(db_num=1, bit_ads=40, bool_value=False)
                        self.fa_shuju(db_num=1, bit_ads=43, bool_value=False)
                        self.fa_shuju(db_num=1, bit_ads=46, bool_value=False)
                        self.fa_shuju(db_num=1, bit_ads=49, bool_value=False)

                        self.fa_shuju(db_num=1, bit_ads=20, bool_value=False)
                        self.fa_shuju(db_num=1, bit_ads=22, bool_value=True)
                        self.fa_shuju(db_num=1, bit_ads=24, bool_value=False)
                        self.fa_shuju(db_num=1, bit_ads=26, bool_value=False)
                        self.fa_shuju(db_num=1, bit_ads=28, bool_value=False)
                    elif ya_n == 3:
                        self.fa_shuju(db_num=1, bit_ads=40, bool_value=False)
                        self.fa_shuju(db_num=1, bit_ads=43, bool_value=False)
                        self.fa_shuju(db_num=1, bit_ads=46, bool_value=False)
                        self.fa_shuju(db_num=1, bit_ads=49, bool_value=False)

                        self.fa_shuju(db_num=1, bit_ads=20, bool_value=False)
                        self.fa_shuju(db_num=1, bit_ads=22, bool_value=False)
                        self.fa_shuju(db_num=1, bit_ads=24, bool_value=True)
                        self.fa_shuju(db_num=1, bit_ads=26, bool_value=False)
                        self.fa_shuju(db_num=1, bit_ads=28, bool_value=False)
                    elif ya_n == 4:
                        self.fa_shuju(db_num=1, bit_ads=40, bool_value=False)
                        self.fa_shuju(db_num=1, bit_ads=43, bool_value=False)
                        self.fa_shuju(db_num=1, bit_ads=46, bool_value=False)
                        self.fa_shuju(db_num=1, bit_ads=49, bool_value=False)

                        self.fa_shuju(db_num=1, bit_ads=20, bool_value=False)
                        self.fa_shuju(db_num=1, bit_ads=22, bool_value=False)
                        self.fa_shuju(db_num=1, bit_ads=24, bool_value=False)
                        self.fa_shuju(db_num=1, bit_ads=26, bool_value=True)
                        self.fa_shuju(db_num=1, bit_ads=28, bool_value=False)
                    else:
                        self.fa_shuju(db_num=1, bit_ads=40, bool_value=False)
                        self.fa_shuju(db_num=1, bit_ads=43, bool_value=False)
                        self.fa_shuju(db_num=1, bit_ads=46, bool_value=False)
                        self.fa_shuju(db_num=1, bit_ads=49, bool_value=False)

                        self.fa_shuju(db_num=1, bit_ads=20, bool_value=False)
                        self.fa_shuju(db_num=1, bit_ads=22, bool_value=False)
                        self.fa_shuju(db_num=1, bit_ads=24, bool_value=False)
                        self.fa_shuju(db_num=1, bit_ads=26, bool_value=False)
                        self.fa_shuju(db_num=1, bit_ads=28, bool_value=True)
                    # 判断PLC是否在动作
                    xy_isrun = read_bool(self.client_xmz, 81)
                    jz_isrun = read_bool(self.client_xmz, 85)
                    while xy_isrun or bj_isrun or jz_isrun:
                        xy_isrun = read_bool(self.client_xmz, 81)
                        jz_isrun = read_bool(self.client_xmz, 85)
                        urgent = read_bool(self.client_xmz, 62)
                        if not self.EN or not urgent:
                            sudden_stop(self.axis)
                            return
                        else:
                            time.sleep(0.2)
                    if self.worker_thread_auto == self.yfffffy or \
                            (self.worker_thread_auto == self.yyfffyy and (ya_n == 2 or ya_n == 3 or ya_n == 4)):
                        # 找平升
                        self.fa_shuju(db_num=1, bit_ads=38, bool_value=False)
                        self.fa_shuju(db_num=1, bit_ads=37, bool_value=True)
                        time.sleep(1)
                        # 读找平信号
                        ping = read_bool(self.client_xmz, 76)
                        if not ping:
                            QMessageBox.warning(window, "完蛋", "未找平，停止下压，请检查是否跳齿或机械错误！！！", QMessageBox.Ok)
                            return
                        else:
                            # 找平降
                            self.fa_shuju(db_num=1, bit_ads=37, bool_value=False)
                            time.sleep(1)
                    # 判断是否连击：
                    value = ctypes.c_short(0)
                    AI_ReadChannel(self.card_number, ya_n, self.ad_range, ctypes.pointer(value))
                    pre_press = post_press = 32767 - value.value
                    nnn = 0
                    while abs(pre_press - post_press) < 50:
                        urgent = read_bool(self.client_xmz, 62)
                        if not self.EN or not urgent:
                            sudden_stop(self.axis)
                            return
                        nnn += 1
                        if nnn > 1:
                            self.ya_real = self.f_tulun.f_dis_with_th(-1 * ya_th / 0.201552)
                            self.signals.log_update.emit(f"第{nnn}次连击，下压{-1 * ya_th}，前后差{(post_press - pre_press)/300}毫米")
                        else:
                            self.signals.log_update.emit(f"下压{-1 * ya_th}")
                        # 下压轴下压real（等待动作完成）
                        self.fa_shuju(db_num=1, bit_ads=55, bool_value=True, txt="下压real")
                        self.fa_shuju(db_num=1, bit_ads=82, bool_value=True)
                        self.fa_shuju(db_num=1, bit_ads=81, bool_value=True)
                        time.sleep(0.1)
                        write_real(self.client_xmz, 20, ya_th)

                        xy_isrun = read_bool(self.client_xmz, 81)
                        while xy_isrun or bj_isrun or jz_isrun:
                            xy_isrun = read_bool(self.client_xmz, 81)
                            urgent = read_bool(self.client_xmz, 62)
                            if not self.EN or not urgent:
                                sudden_stop(self.axis)
                                return
                            else:
                                time.sleep(0.2)
                        AI_ReadChannel(self.card_number, ya_n, self.ad_range, ctypes.pointer(value))
                        post_press = 32767 - value.value
                        if ya_n == 1:
                            ya_th -= float(self.param['连续下压增量-压1']) * float(
                                self.param['压下量系数-P2'])
                        elif ya_n == 2:
                            ya_th -= float(self.param['连续下压增量-压2']) * float(
                                self.param['压下量系数-P3'])
                        elif ya_n == 3:
                            ya_th -= float(self.param['连续下压增量-压3']) * float(
                                self.param['压下量系数-P4'])
                        elif ya_n == 4:
                            ya_th -= float(self.param['连续下压增量-压4']) * float(
                                self.param['压下量系数-P5'])
                        else:
                            ya_th -= float(self.param['连续下压增量-压5']) * float(
                                self.param['压下量系数-P6'])
                    self.signals.log_update.emit(f"单次下压成功")
    def auto_end(self):
        reply = QMessageBox.question(self, '你确定？', '你真的确定要停止进程吗？',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.EN = False
            self.work_isrun = False
            sudden_stop(self.axis)
            # PLC的EN
            self.fa_shuju(db_num=1, bit_ads=55, bool_value=True, txt="下压real")
            self.fa_shuju(db_num=1, bit_ads=82, bool_value=True)
            self.fa_shuju(db_num=1, bit_ads=81, bool_value=True)
            time.sleep(0.1)
            write_real(self.client_xmz, 20, 0.1)
            self.fa_shuju(db_num=1, bit_ads=82, bool_value=False)
            # 禁用标签页切换
            self.setTabEnabled(4, True)
            self.setTabEnabled(1, True)
            self.setTabEnabled(2, True)
            self.setTabEnabled(3, True)
            self.works.setEnabled(True)
            self.signals.log_update.emit('结束检测')
            strError = "已终止自动运行模式"
            QMessageBox.information(window, "恭喜您", strError, QMessageBox.Ok)

if __name__ == '__main__':

    os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'

    app = QApplication(sys.argv)
    # 创建开机加载界面
    splash = SplashScreen()
    # 设置字体大小
    font = QFont("Arial", 16)  # 将字体设置为 Arial，大小为 16
    splash.setFont(font)
    splash.show()
    splash.showMessage(f"加载中...", Qt.AlignBottom | Qt.AlignCenter, Qt.blue)
    # 创建主页面
    window = MainWindow()
    window.setWindowIcon(QIcon("./images/UI/IMUST.ico"))
    splash.finish(window)  # 传递主窗口实例
    window.show()
    sys.exit(app.exec_())
