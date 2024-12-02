import time
from PyQt5.QtWidgets import (QLineEdit, QHBoxLayout, QPushButton, QTextEdit, QScrollArea,
                             QFormLayout, QApplication, QTabWidget, QRadioButton, QButtonGroup,
                             QMessageBox, QSpacerItem, QSizePolicy)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtGui import QIntValidator, QDoubleValidator
import matplotlib.ticker as ticker
from my_function import *
from ui_widge import *
from MPC08E import *
import numpy as np
import snap7
import sys

class MainWindow(QTabWidget):
    def __init__(self):
        super().__init__()
        # self.setFixedSize(1440, 1200)  # 设置固定大小
        # 最大化窗口
        self.showMaximized()
        # 禁用调整窗口大小
        self.setFixedSize(self.size())
        # 连接标签切换信号
        self.currentChanged.connect(self.on_tab_changed)
        self.setWindowTitle('矫直机')
        self.setWindowIcon(QIcon('images/UI/L.jpg'))
        self.axis = 1
        self.mc_num = 2000
        self.PLC_IP = '192.168.1.11'  # 替换为PLC的 IP地址、机架和插槽
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
        set_conspeed(self.axis, 4000)
        set_maxspeed(self.axis, 8000)
        reset_pos(self.axis)
        set_getpos_mode(self.axis, 1)
        self.auto()
        self.half_auto()
        self.hand()
        self.param_ui()
        self.about_me()
        self.log_widget.append(f"轴数:{r1}\n卡数:{r2}\n默认控制1轴")
        self.client_xmz = snap7.client.Client()
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
        self.worker_thread_auto = WorkerThread(2)
        self.worker_thread_auto.ec_signal.connect(self.new_data_hand_ui)
        self.worker_thread_auto.end_signal.connect(self.end_Thread)
        self.list_kesai = [0, 0, 0]
        self.kesai = 0

        # # 定义bar_mo和bar_xj的示例值
        # bar_mo = [round(2.5, 2),  # mo1
        #           round(0.0, 2),
        #           round(1.5, 2),
        #           round(0.0, 2),
        #           round(0.0, 2),
        #           round(0.0, 2),
        #           round(3.0, 2)]  # mo7
        # bar_xj = [1.0, 0, 0, 0, 0, 0, 1.5]  # xj1, xj7
        # self.update_labels_hand(bar_mo, bar_xj)

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

        ss1.setFixedSize(115, 255)  # 设置固定大小
        ss2.setFixedSize(115, 255)  # 设置固定大小
        ss3.setFixedSize(115, 255)  # 设置固定大小
        ss4.setFixedSize(115, 255)  # 设置固定大小
        ss5.setFixedSize(115, 255)  # 设置固定大小
        ss6.setFixedSize(115, 255)  # 设置固定大小
        ss7.setFixedSize(115, 255)  # 设置固定大小

        # 创建柱状图控件
        self.auto_figure1, self.auto_ax1 = plt.subplots(figsize=(1, 1.9))
        self.auto_figure2, self.auto_ax2 = plt.subplots(figsize=(1, 1.9))
        self.auto_figure3, self.auto_ax3 = plt.subplots(figsize=(1, 1.9))
        self.auto_figure4, self.auto_ax4 = plt.subplots(figsize=(1, 1.9))
        self.auto_figure5, self.auto_ax5 = plt.subplots(figsize=(1, 1.9))
        self.auto_figure6, self.auto_ax6 = plt.subplots(figsize=(1, 1.9))
        self.auto_figure7, self.auto_ax7 = plt.subplots(figsize=(1, 1.9))
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
        self.auto_circle_widget1 = CircleWidget(angle=90)
        self.auto_circle_widget1.setMinimumSize(115, 115)
        layout_ss1.addWidget(self.auto_circle_widget1)
        self.auto_circle_widget2 = CircleWidget(angle=90)
        self.auto_circle_widget2.setMinimumSize(115, 115)
        layout_ss2.addWidget(self.auto_circle_widget2)
        self.auto_sqrt_widget3 = SqrtWidget(angle=90)
        self.auto_sqrt_widget3.setMinimumSize(115, 115)
        layout_ss3.addWidget(self.auto_sqrt_widget3)
        self.auto_sqrt_widget4 = SqrtWidget(angle=90)
        self.auto_sqrt_widget4.setMinimumSize(115, 115)
        layout_ss4.addWidget(self.auto_sqrt_widget4)
        self.auto_sqrt_widget5 = SqrtWidget(angle=90)
        self.auto_sqrt_widget5.setMinimumSize(115, 115)
        layout_ss5.addWidget(self.auto_sqrt_widget5)
        self.auto_circle_widget6 = CircleWidget(angle=90)
        self.auto_circle_widget6.setMinimumSize(115, 115)
        layout_ss6.addWidget(self.auto_circle_widget6)
        self.auto_circle_widget7 = CircleWidget(angle=90)
        self.auto_circle_widget7.setMinimumSize(115, 115)
        layout_ss7.addWidget(self.auto_circle_widget7)
        # data_widget.setFixedSize(2040, 600)  # 设置固定大小

        # 绘制柱状图
        self.auto_plot_bar_chart([2, 2, 3, 1, 1, 3, 2])
        for i, figure in enumerate([self.auto_figure1, self.auto_figure2,
                                    self.auto_figure3,
                                    self.auto_figure4, self.auto_figure5,
                                    self.auto_figure6, self.auto_figure7]):
            figure.tight_layout(pad=1.0)
        self.auto_circle_widget7.setAngle(10)

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

        ss1.setFixedSize(115, 255)  # 设置固定大小
        ss2.setFixedSize(115, 255)  # 设置固定大小
        ss3.setFixedSize(115, 255)  # 设置固定大小
        ss4.setFixedSize(115, 255)  # 设置固定大小
        ss5.setFixedSize(115, 255)  # 设置固定大小
        ss6.setFixedSize(115, 255)  # 设置固定大小
        ss7.setFixedSize(115, 255)  # 设置固定大小

        # 创建柱状图控件
        self.figure1, self.ax1 = plt.subplots(figsize=(1, 1.9))
        self.figure2, self.ax2 = plt.subplots(figsize=(1, 1.9))
        self.figure3, self.ax3 = plt.subplots(figsize=(1, 1.9))
        self.figure4, self.ax4 = plt.subplots(figsize=(1, 1.9))
        self.figure5, self.ax5 = plt.subplots(figsize=(1, 1.9))
        self.figure6, self.ax6 = plt.subplots(figsize=(1, 1.9))
        self.figure7, self.ax7 = plt.subplots(figsize=(1, 1.9))
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
        self.circle_widget1 = CircleWidget(angle=90)
        self.circle_widget1.setMinimumSize(115, 115)
        layout_ss1.addWidget(self.circle_widget1)
        self.circle_widget2 = CircleWidget(angle=90)
        self.circle_widget2.setMinimumSize(115, 115)
        layout_ss2.addWidget(self.circle_widget2)
        self.sqrt_widget3 = SqrtWidget(angle=90)
        self.sqrt_widget3.setMinimumSize(115, 115)
        layout_ss3.addWidget(self.sqrt_widget3)
        self.sqrt_widget4 = SqrtWidget(angle=90)
        self.sqrt_widget4.setMinimumSize(115, 115)
        layout_ss4.addWidget(self.sqrt_widget4)
        self.sqrt_widget5 = SqrtWidget(angle=90)
        self.sqrt_widget5.setMinimumSize(115, 115)
        layout_ss5.addWidget(self.sqrt_widget5)
        self.circle_widget6 = CircleWidget(angle=90)
        self.circle_widget6.setMinimumSize(115, 115)
        layout_ss6.addWidget(self.circle_widget6)
        self.circle_widget7 = CircleWidget(angle=90)
        self.circle_widget7.setMinimumSize(115, 115)
        layout_ss7.addWidget(self.circle_widget7)
        # data_widget.setFixedSize(2040, 600)  # 设置固定大小

        # 绘制柱状图
        self.plot_bar_chart([1.00, 1.00, 2.00, 2.10, 1.20, 1.40, 1.90])
        for i, figure in enumerate([self.figure1, self.figure2, self.figure3, self.figure4, self.figure5, self.figure6, self.figure7]):
            figure.tight_layout(pad=1.0)
        self.circle_widget7.setAngle(10)

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
        self.jz_stop.clicked.connect(lambda: (self.fa_shuju(db_num=1, bit_ads=5, bool_value=True, txt="夹爪停止"),
                                     self.fa_shuju(db_num=1, bit_ads=1, bool_value=False),
                                     self.fa_shuju(db_num=1, bit_ads=2, bool_value=False),
                                     self.fa_shuju(db_num=1, bit_ads=3, bool_value=False),
                                     self.fa_shuju(db_num=1, bit_ads=4, bool_value=False),
                                     self.fa_shuju(db_num=1, bit_ads=6, bool_value=False),
                                     self.fa_shuju(db_num=1, bit_ads=7, bool_value=False),
                                     self.fa_shuju(db_num=1, bit_ads=8, bool_value=False),
                                     self.fa_shuju(db_num=1, bit_ads=9, bool_value=False)
                                     ))
        self.jz_up = QPushButton('夹爪上升')
        # self.jz_up.setFixedSize(200, 50)
        self.jz_up.clicked.connect(lambda: (self.fa_shuju(db_num=1, bit_ads=2, bool_value=True, txt="夹爪上升"),
                                     self.fa_shuju(db_num=1, bit_ads=5, bool_value=False),
                                     self.fa_shuju(db_num=1, bit_ads=8, bool_value=False)
                                     ))
        self.jz_down = QPushButton('夹爪下降')
        self.jz_down.clicked.connect(lambda: (self.fa_shuju(db_num=1, bit_ads=8, bool_value=True, txt="夹爪下降"),
                                     self.fa_shuju(db_num=1, bit_ads=5, bool_value=False),
                                     self.fa_shuju(db_num=1, bit_ads=2, bool_value=False)
                                     ))
        self.jz_zz = QPushButton('夹爪正转')
        self.jz_zz.clicked.connect(lambda: (self.fa_shuju(db_num=1, bit_ads=1, bool_value=True, txt="夹爪正转"),
                                     self.fa_shuju(db_num=1, bit_ads=5, bool_value=False),
                                     self.fa_shuju(db_num=1, bit_ads=3, bool_value=False)
                                     ))
        self.jz_fz = QPushButton('夹爪反转')
        self.jz_fz.clicked.connect(lambda: (self.fa_shuju(db_num=1, bit_ads=3, bool_value=True, txt="夹爪反转"),
                                     self.fa_shuju(db_num=1, bit_ads=5, bool_value=False),
                                     self.fa_shuju(db_num=1, bit_ads=1, bool_value=False)
                                     ))
        self.jz_qj = QPushButton('夹爪前进')
        self.jz_qj.clicked.connect(lambda: (self.fa_shuju(db_num=1, bit_ads=6, bool_value=True, txt="夹爪前进"),
                                     self.fa_shuju(db_num=1, bit_ads=5, bool_value=False),
                                     self.fa_shuju(db_num=1, bit_ads=4, bool_value=False)
                                     ))
        self.jz_ht = QPushButton('夹爪后退')
        self.jz_ht.clicked.connect(lambda: (self.fa_shuju(db_num=1, bit_ads=4, bool_value=True, txt="夹爪后退"),
                                     self.fa_shuju(db_num=1, bit_ads=5, bool_value=False),
                                     self.fa_shuju(db_num=1, bit_ads=6, bool_value=False)
                                     ))
        self.jz_jj = QPushButton('夹爪夹紧')
        self.jz_jj.clicked.connect(lambda: (self.fa_shuju(db_num=1, bit_ads=7, bool_value=True, txt="夹爪夹紧"),
                                     self.fa_shuju(db_num=1, bit_ads=5, bool_value=False),
                                     self.fa_shuju(db_num=1, bit_ads=9, bool_value=False)
                                     ))
        self.jz_fs = QPushButton('夹爪放松')
        self.jz_fs.clicked.connect(lambda: (self.fa_shuju(db_num=1, bit_ads=9, bool_value=True, txt="夹爪放松"),
                                     self.fa_shuju(db_num=1, bit_ads=5, bool_value=False),
                                     self.fa_shuju(db_num=1, bit_ads=7, bool_value=False)
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
                                     self.fa_shuju(db_num=1, bit_ads=18, bool_value=False)
                                     ))
        self.bj_up = QPushButton('步进上升')
        self.bj_up.clicked.connect(lambda: (self.fa_shuju(db_num=1, bit_ads=17, bool_value=True, txt="步进上升"),
                                     self.fa_shuju(db_num=1, bit_ads=15, bool_value=False),
                                     self.fa_shuju(db_num=1, bit_ads=18, bool_value=False),
                                     self.fa_shuju(db_num=1, bit_ads=12, bool_value=False)
                                     ))
        self.bj_down = QPushButton('步进下降')
        self.bj_down.clicked.connect(lambda: (self.fa_shuju(db_num=1, bit_ads=18, bool_value=True, txt="步进下降"),
                                     self.fa_shuju(db_num=1, bit_ads=15, bool_value=False),
                                     self.fa_shuju(db_num=1, bit_ads=17, bool_value=False)
                                     ))
        self.bj_zq = QPushButton('步进最前')
        self.bj_zq.clicked.connect(lambda: (self.fa_shuju(db_num=1, bit_ads=13, bool_value=True, txt="步进最前"),
                                     self.fa_shuju(db_num=1, bit_ads=15, bool_value=False),
                                     self.fa_shuju(db_num=1, bit_ads=11, bool_value=False),
                                     self.fa_shuju(db_num=1, bit_ads=12, bool_value=False)
                                     ))
        self.bj_zh = QPushButton('步进最后')
        self.bj_zh.clicked.connect(lambda: (self.fa_shuju(db_num=1, bit_ads=11, bool_value=True, txt="步进最后"),
                                     self.fa_shuju(db_num=1, bit_ads=15, bool_value=False),
                                     self.fa_shuju(db_num=1, bit_ads=13, bool_value=False),
                                     self.fa_shuju(db_num=1, bit_ads=12, bool_value=False)
                                     ))
        self.bj_qj = QPushButton('步进前进')
        # 绑定鼠标按下和松开事件
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
                                     self.fa_shuju(db_num=1, bit_ads=18, bool_value=False)
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
        self.yt_up.clicked.connect(lambda: (self.fa_shuju(db_num=1, bit_ads=30, bool_value=True, txt="压头抬起"),
                                     self.fa_shuju(db_num=1, bit_ads=31, bool_value=False),
                                     self.fa_shuju(db_num=1, bit_ads=32, bool_value=False)
                                     ))
        self.yt_down = QPushButton('压头下压')
        self.yt_down.clicked.connect(lambda: (self.fa_shuju(db_num=1, bit_ads=31, bool_value=True, txt="压头下压"),
                                     self.fa_shuju(db_num=1, bit_ads=30, bool_value=False),
                                     self.fa_shuju(db_num=1, bit_ads=32, bool_value=False),
                                     self.fa_shuju(db_num=1, bit_ads=33, bool_value=False)
                                     ))
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
                                     self.fa_shuju(db_num=1, bit_ads=29, bool_value=False)
                                     ))
        self.yt_hl = QPushButton('压头回零')
        self.yt_hl.clicked.connect(lambda: (self.fa_shuju(db_num=1, bit_ads=33, bool_value=True, txt="压头回零"),
                                     self.fa_shuju(db_num=1, bit_ads=30, bool_value=True),
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
                                     self.fa_shuju(db_num=1, bit_ads=29, bool_value=True)
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

        layout_u.addStretch()

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
        d1 = QWidget(self)
        d2 = QWidget(self)
        d3 = QWidget(self)
        d = QWidget(self)

        # u.setFixedSize(1440, 500)  # 设置固定大小

        layout_M = QVBoxLayout(M_widget)
        layout_u = QHBoxLayout(u)
        layout_ur = QVBoxLayout(ur)
        layout_d = QHBoxLayout(d)
        layout_d1 = QFormLayout(d1)
        layout_d2 = QFormLayout(d2)
        layout_d3 = QFormLayout(d3)

        layout_M.addWidget(u)
        layout_M.addWidget(d)
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
        self.labels = ['压下量系数-P1',
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
                       '连续下压增量-压块1',
                       '连续下压增量-压块2',
                       '连续下压增量-压块3',
                       '连续下压增量-压块4',
                       '连续下压增量-压块5',
                       '最大校直次数',
                       '工件P1点直接输入'
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
        self.load_param()
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

        layout_d3.addRow('连续下压增量-压块1', self.input_boxes['连续下压增量-压块1'])
        layout_d3.addRow('连续下压增量-压块2', self.input_boxes['连续下压增量-压块2'])
        layout_d3.addRow('连续下压增量-压块3', self.input_boxes['连续下压增量-压块3'])
        layout_d3.addRow('连续下压增量-压块4', self.input_boxes['连续下压增量-压块4'])
        layout_d3.addRow('连续下压增量-压块5', self.input_boxes['连续下压增量-压块5'])
        layout_d3.addRow('最大校直次数', self.input_boxes['最大校直次数'])
        layout_d3.addRow('工件P1点直接输入', self.input_boxes['工件P1点直接输入'])

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
    def about_me(self):
        M_widget = QWidget()
        aboutme_layout = QVBoxLayout()
        aboutme_title = QLabel('\n\n欢迎使用凤宝重科自研矫直机系统beta版\n\n 产品处于开发阶段，感谢包容与理解！！！')
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
        self.setTabIcon(4, QIcon('images/UI/R.png'))

    def auto_plot_bar_chart(self, values):
        if self.auto_ax1.has_data():
            self.auto_ax1.clear()
        if self.auto_ax2.has_data():
            self.auto_ax2.clear()
        if self.auto_ax3.has_data():
            self.auto_ax3.clear()
        if self.auto_ax4.has_data():
            self.auto_ax4.clear()
        if self.auto_ax5.has_data():
            self.auto_ax5.clear()
        if self.auto_ax6.has_data():
            self.auto_ax6.clear()
        if self.auto_ax7.has_data():
            self.auto_ax7.clear()
        categories = ['Sensor1', 'Sensor2', 'Sensor3', 'Sensor4', 'Sensor5', 'Sensor6', 'Sensor7']
        # 柱1
        if values[0] >= 2:
            self.auto_ax1.bar(categories[0], values[0], width=0.2, color='red')
        else:
            self.auto_ax1.bar(categories[0], values[0], width=0.2, color='green')
        self.auto_ax1.set_ylim(bottom=0.45, top= 5.5)
        self.auto_ax1.set_yscale('log', base=np.e)
        self.auto_ax1.yaxis.set_major_formatter(ticker.ScalarFormatter())
        # self.ax1.set_yticks([0.5, round(1), round(2), round(5)])
        self.auto_ax1.axhline(y=2, color='black', linestyle='--', linewidth=1)
        self.auto_ax1.axhline(y=1, color='black', linestyle='--', linewidth=1)
        self.auto_ax1.set_title(f'{values[0]}', fontsize=10)
        self.auto_ax1.tick_params(axis='y', labelsize=8)
        self.auto_ax1.tick_params(axis='x', labelsize=8)
        self.auto_ax1.yaxis.set_major_locator(ticker.MaxNLocator(integer=True))
        self.auto_canvas1.draw()

        # 柱2
        if values[1] >= 2:
            self.auto_ax2.bar(categories[1], values[1], width=0.2, color='red')
        else:
            self.auto_ax2.bar(categories[1], values[1], width=0.2, color='green')
        self.auto_ax2.set_ylim(bottom=0.45, top= 5.5)
        self.auto_ax2.set_yscale('log', base=np.e)
        self.auto_ax2.yaxis.set_major_formatter(ticker.ScalarFormatter())
        # self.ax2.set_yticks([0.5, 1, 2, 5])
        self.auto_ax2.axhline(y=2, color='black', linestyle='--', linewidth=1)
        self.auto_ax2.axhline(y=1, color='black', linestyle='--', linewidth=1)
        self.auto_ax2.set_title(f'{values[1]}', fontsize=10)
        self.auto_ax2.tick_params(axis='y', labelsize=8)
        self.auto_ax2.tick_params(axis='x', labelsize=8)
        self.auto_ax2.yaxis.set_major_locator(ticker.MaxNLocator(integer=True))
        self.auto_canvas2.draw()

        # 柱3
        if values[2] >= 2:
            self.auto_ax3.bar(categories[2], values[2], width=0.2, color='red')
        else:
            self.auto_ax3.bar(categories[2], values[2], width=0.2, color='green')
        self.auto_ax3.set_ylim(bottom=0.45, top= 5.5)
        self.auto_ax3.set_yscale('log', base=np.e)
        self.auto_ax3.yaxis.set_major_formatter(ticker.ScalarFormatter())
        # self.ax3.set_yticks([0.5, 1, 2, 5])
        self.auto_ax3.axhline(y=2, color='black', linestyle='--', linewidth=1)
        self.auto_ax3.axhline(y=1, color='black', linestyle='--', linewidth=1)
        self.auto_ax3.set_title(f'{values[2]}', fontsize=10)
        self.auto_ax3.tick_params(axis='y', labelsize=8)
        self.auto_ax3.tick_params(axis='x', labelsize=8)
        self.auto_ax3.yaxis.set_major_locator(ticker.MaxNLocator(integer=True))
        self.auto_canvas3.draw()

        # 柱4
        if values[3] >= 2:
            self.auto_ax4.bar(categories[3], values[3], width=0.2, color='red')
        else:
            self.auto_ax4.bar(categories[3], values[3], width=0.2, color='green')
        self.auto_ax4.set_ylim(bottom=0.45, top= 5.5)
        self.auto_ax4.set_yscale('log', base=np.e)
        self.auto_ax4.yaxis.set_major_formatter(ticker.ScalarFormatter())
        # self.ax4.set_yticks([0.5, 1, 2, 5])
        self.auto_ax4.axhline(y=2, color='black', linestyle='--', linewidth=1)
        self.auto_ax4.axhline(y=1, color='black', linestyle='--', linewidth=1)
        self.auto_ax4.set_title(f'{values[3]}', fontsize=10)
        self.auto_ax4.tick_params(axis='y', labelsize=8)
        self.auto_ax4.tick_params(axis='x', labelsize=8)
        self.auto_ax4.yaxis.set_major_locator(ticker.MaxNLocator(integer=True))
        self.auto_canvas4.draw()

        # 柱5
        if values[4] >= 2:
            self.auto_ax5.bar(categories[4], values[4], width=0.2, color='red')
        else:
            self.auto_ax5.bar(categories[4], values[4], width=0.2, color='green')
        self.auto_ax5.set_ylim(bottom=0.45, top= 5.5)
        self.auto_ax5.set_yscale('log', base=np.e)
        self.auto_ax5.yaxis.set_major_formatter(ticker.ScalarFormatter())
        # self.ax5.set_yticks([0.5, 1, 2, 5])
        self.auto_ax5.axhline(y=2, color='black', linestyle='--', linewidth=1)
        self.auto_ax5.axhline(y=1, color='black', linestyle='--', linewidth=1)
        self.auto_ax5.set_title(f'{values[4]}', fontsize=10)
        self.auto_ax5.tick_params(axis='y', labelsize=8)
        self.auto_ax5.tick_params(axis='x', labelsize=8)
        self.auto_ax5.yaxis.set_major_locator(ticker.MaxNLocator(integer=True))
        self.auto_canvas5.draw()

        # 柱6
        if values[5] >= 2:
            self.auto_ax6.bar(categories[5], values[5], width=0.2, color='red')
        else:
            self.auto_ax6.bar(categories[5], values[5], width=0.2, color='green')
        self.auto_ax6.set_ylim(bottom=0.45, top= 5.5)
        self.auto_ax6.set_yscale('log', base=np.e)
        self.auto_ax6.yaxis.set_major_formatter(ticker.ScalarFormatter())
        # self.ax6.set_yticks([0.5, 1, 2, 5])
        self.auto_ax6.axhline(y=2, color='black', linestyle='--', linewidth=1)
        self.auto_ax6.axhline(y=1, color='black', linestyle='--', linewidth=1)
        self.auto_ax6.set_title(f'{values[5]}', fontsize=10)
        self.auto_ax6.tick_params(axis='y', labelsize=8)
        self.auto_ax6.tick_params(axis='x', labelsize=8)
        self.auto_ax6.yaxis.set_major_locator(ticker.MaxNLocator(integer=True))
        self.auto_canvas6.draw()

        # 柱7
        if values[6] >= 2:
            self.auto_ax7.bar(categories[6], values[6], width=0.2, color='red')
        else:
            self.auto_ax7.bar(categories[6], values[6], width=0.2, color='green')
        self.auto_ax7.set_ylim(bottom=0.45, top= 5.5)
        self.auto_ax7.set_yscale('log', base=np.e)
        self.auto_ax7.yaxis.set_major_formatter(ticker.ScalarFormatter())
        # self.ax7.set_yticks([0.5, 1, 2, 5])
        self.auto_ax7.axhline(y=2, color='black', linestyle='--', linewidth=1)
        self.auto_ax7.axhline(y=1, color='black', linestyle='--', linewidth=1)
        self.auto_ax7.set_title(f'{values[6]}', fontsize=10)
        self.auto_ax7.tick_params(axis='y', labelsize=8)
        self.auto_ax7.tick_params(axis='x', labelsize=8)
        self.auto_ax7.yaxis.set_major_locator(ticker.MaxNLocator(integer=True))
        self.auto_canvas7.draw()
    def plot_bar_chart(self, values):
        categories = ['Sensor1', 'Sensor2', 'Sensor3', 'Sensor4', 'Sensor5', 'Sensor6', 'Sensor7']
        for i, ax in enumerate([self.ax1, self.ax2, self.ax3, self.ax4, self.ax5, self.ax6, self.ax7]):
            # 获取现有的条形图，如果有的话
            bars = ax.patches
            value = values[i]
            color = 'red' if value >= 2 else 'green'

            if len(bars) == 0:
                # 如果没有条形图，绘制新的条形图
                ax.bar(categories[i], value, width=0.2, color=color)
            else:
                # 如果已有条形图，更新现有的条形图
                bar = bars[0]  # 因为每个ax只有一个柱状图
                bar.set_height(value)  # 更新条形图的高度
                bar.set_color(color)  # 更新颜色

            # 设置图表的其他参数
            ax.set_ylim(bottom=0.45, top=5.5)
            ax.set_yscale('log', base=np.e)
            ax.yaxis.set_major_formatter(ticker.ScalarFormatter())
            ax.axhline(y=2, color='black', linestyle='--', linewidth=1)
            ax.axhline(y=1, color='black', linestyle='--', linewidth=1)
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
        self.worker_thread_auto.start()
    def new_data_hand_ui(self, bar_mo, bar_xj, list_kesai):
        # print(list_kesai)
        # self.kesai3, self.kesai4, self.kesai5 = list_kesai
        for i in range(3):
            if abs(((list_kesai[0] + list_kesai[1] + list_kesai[2]) / 3) - 45) < 10:
                break
            if list_kesai[i] >= 45:
                self.list_kesai[i] = list_kesai[i] - 90
                bar_xj[2 + i] = bar_xj[2 + i] + 90
        self.kesai = (self.list_kesai[0] - self.list_kesai[1] +self.list_kesai[2]) / 3
        # 对其他kesai进行补偿
        for i in range(3):
            bar_xj[2 + i] = bar_xj[2 + i] + (self.list_kesai[i] - self.kesai)
        print("已接收到信号，准备更新界面柱状")
        self.plot_bar_chart(bar_mo)
        print("界面柱状图更新完毕，准备更新饼状图")
        self.circle_widget1.setAngle(-90 - bar_xj[0])
        self.circle_widget2.setAngle(-90 - bar_xj[1])
        self.sqrt_widget3.setAngle(-90 - bar_xj[2])
        self.sqrt_widget4.setAngle(-90 - bar_xj[3])
        self.sqrt_widget5.setAngle(-90 - bar_xj[4])
        self.circle_widget6.setAngle(-90 - bar_xj[5])
        self.circle_widget7.setAngle(-90 - bar_xj[6])
        # QCoreApplication.processEvents()
        print("全部更新完毕，返回用户界面")
    def get_ai(self):
        self.worker_thread.start()
    def new_data_info_ui(self, html_message):
        self.log_widget.append(html_message)
        self.log_widget.ensureCursorVisible()
    def stop(self):
        self.log_widget.append(f"正在停止采集")
        self.log_widget.ensureCursorVisible()

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
            # 写入布尔值到第一个DB块的第一个字节
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
    def on_mouse_press(self, event, button):
        # 按下时，按钮状态设置为按下
        button.setChecked(True)
        if button.text() == "步进前进":
            self.fa_shuju(db_num=1, bit_ads=16, bool_value=True, txt="步进前进"),
            self.fa_shuju(db_num=1, bit_ads=15, bool_value=False),
            self.fa_shuju(db_num=1, bit_ads=14, bool_value=False),
            self.fa_shuju(db_num=1, bit_ads=12, bool_value=False)
        if button.text() == "步进后退":
            self.fa_shuju(db_num=1, bit_ads=14, bool_value=True, txt="步进后退"),
            self.fa_shuju(db_num=1, bit_ads=15, bool_value=False),
            self.fa_shuju(db_num=1, bit_ads=16, bool_value=False),
            self.fa_shuju(db_num=1, bit_ads=12, bool_value=False)
        super(QPushButton, button).mousePressEvent(event)
    def on_mouse_release(self, event, button):
        # 松开时，按钮状态设置为未按下
        button.setChecked(False)
        if button.text() == "步进前进":
            self.fa_shuju(db_num=1, bit_ads=16, bool_value=False, txt="步进前进停止")
        if button.text() == "步进后退":
            self.fa_shuju(db_num=1, bit_ads=14, bool_value=False, txt="步进后退停止")
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
            for label in self.labels:
                self.input_boxes[label].setText("0.0")  # 设置默认值
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
    def auto_run(self):
        color = 'green'
        message = "开始检测"
        html_message = f'<span style="color: {color};">{message}</span>'
        self.auto_log_widget.append(html_message)
        self.auto_log_widget.ensureCursorVisible()
        # self.duan_plc_button.setEnabled(False)
        # self.lian_plc_button.setEnabled(False)
        # self.run_button.setEnabled(False)
        # self.radio_button_xmz.setEnabled(False)
        # self.radio_button_hc.setEnabled(False)
        # self.input_IP.setEnabled(False)
        # self.input_rack.setEnabled(False)
        # self.input_slot.setEnabled(False)
        # self.worker_thread1.start()
        # self.worker_thread3.start()
    def auto_end(self):
        reply = QMessageBox.question(self, 'Confirmation', '确认停止进程？',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.auto_log_widget.append("正在结束检测")
            self.auto_log_widget.ensureCursorVisible()
            # self.worker_thread3.stop()
            # self.worker_thread2.stop()
            # self.worker_thread1.stop()
            # self.worker_thread3.wait()  # 等待线程结束
            # self.worker_thread2.wait()  # 等待线程结束
            # self.worker_thread1.wait()  # 等待线程结束
            self.auto_log_widget.append("成功结束检测")
            self.auto_log_widget.ensureCursorVisible()
            strError = "成功停止程序"
            # self.worker_thread3.stop_init()
            # self.worker_thread2.stop_init()
            # self.worker_thread1.stop_init()
            QMessageBox.warning(window, "Error", strError, QMessageBox.Ok)

if __name__ == '__main__':
    write_bool(snap7.client.Client(), 1, 100, False)
    try:
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
        splash.finish(window)  # 传递主窗口实例
        window.show()
        sys.exit(app.exec_())
    except Exception as e:
        print("意外退出")
        print(f"Unexpected error: {e}")
        write_bool(snap7.client.Client(), 1, 100, True)
    write_bool(snap7.client.Client(), 1, 100, True)