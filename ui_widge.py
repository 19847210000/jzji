import math
import sys
import tulun
from PyQt5.QtWidgets import QWidget, QSplashScreen, QLabel, QVBoxLayout, QToolTip
from PyQt5.QtGui import QPainter, QColor, QIcon, QFont, QPen, QPixmap
from PyQt5.QtCore import Qt, QDateTime, QTimer, QPointF, QRect, QEvent
from PyQt5.QtChart import QChart, QChartView, QLineSeries, QDateTimeAxis, QValueAxis


class CircleWidget(QWidget):
    def __init__(self, angle=0):
        super().__init__()
        self.angle = angle % 360  # 角度数据，单位是度

    def setAngle(self, new_angle):
        self.angle = new_angle  # 更新角度
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        # 设置圆的颜色
        painter.setBrush(QColor(58, 128, 12))
        pen = QPen(QColor(0, 0, 0))  # 黑色边框
        pen.setWidth(4)  # 设置边框宽度为3像素
        painter.setPen(pen)

        # 计算圆心和半径
        center_x = self.width() // 2
        center_y = self.height() // 2
        # radius = min(center_x, center_y) - 10  # 留出边距
        radius = 30  # 绘制圆形
        painter.drawEllipse(center_x - radius, center_y - radius, radius * 2, radius * 2)
        # 计算半径线的终点坐标
        end_x = center_x + radius * math.cos(math.radians(self.angle))
        end_y = center_y - radius * math.sin(math.radians(self.angle))  # Y坐标方向向上
        # 绘制半径
        pen = QPen(QColor(255, 0, 0))  # 黑色边框
        pen.setWidth(4)  # 设置边框宽度为3像素
        painter.setPen(pen)
        painter.drawLine(center_x, center_y, end_x, end_y)


class SqrtWidget(QWidget):
    def __init__(self, angle=0):
        super().__init__()

        self.angle = angle % 360

    def setAngle(self, new_angle):
        # if new_angle < 0 or new_angle > 360:
        #     new_angle = new_angle % 360
        self.angle = new_angle % 360  # 更新角度
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)

        # 设置正方形的颜色
        painter.setBrush(QColor(128, 58, 12))
        pen = QPen(QColor(0, 0, 0))  # 黑色边框
        pen.setWidth(4)  # 设置边框宽度为3像素
        painter.setPen(pen)

        # 计算正方形的边长和左上角坐标
        # side_length = min(self.width(), self.height()) - 10  # 留出边距
        side_length = 60
        top_left_x = (self.width() - side_length) // 2
        top_left_y = (self.height() - side_length) // 2

        # 绘制正方形
        painter.drawRect(top_left_x, top_left_y, side_length, side_length)

        # 计算半径线的终点坐标
        center_x = top_left_x + side_length // 2
        center_y = top_left_y + side_length // 2

        if 315 <= self.angle or self.angle < 45:  # 向右
            end_x = top_left_x + side_length
            end_y = center_y - (side_length // 2) * math.sin(math.radians(self.angle))
        elif 45 <= self.angle < 135:  # 向上
            end_x = center_x + (side_length // 2) * math.cos(math.radians(self.angle))
            end_y = top_left_y
        elif 135 <= self.angle < 225:  # 向左
            end_x = top_left_x
            end_y = center_y - (side_length // 2) * math.sin(math.radians(self.angle))
        elif 225 <= self.angle < 315:  # 向下
            end_x = center_x + (side_length // 2) * math.cos(math.radians(self.angle))
            end_y = top_left_y + side_length
        else:
            # 可以处理其他角度或插值，简化为正方形的四条边
            end_x = center_x + (side_length // 2) * math.cos(math.radians(self.angle))
            end_y = center_y - (side_length // 2) * math.sin(math.radians(self.angle))

        # 绘制半径
        pen = QPen(QColor(0, 255, 0))  # 黑色边框
        pen.setWidth(4)  # 设置边框宽度为3像素
        painter.setPen(pen)
        painter.drawLine(center_x, center_y, end_x, end_y)


class SplashScreen(QSplashScreen):
    def __init__(self):
        super().__init__(QPixmap("images/UI/R.png"))  # 替换为你的图片路径
        self.setWindowFlag(Qt.WindowStaysOnTopHint)


class sensor_Plot(QWidget):
    def __init__(self, name):
        super().__init__()
        self.cc_line = 0
        # 创建图表对象
        self.chart = QChart()
        # self.chart_view = QChartView(self.chart)
        self.chart_view = CustomChartView(self.chart, self)
        # 颜色列表：红橙黄绿青蓝紫
        colors = ['#FF0000', '#FFA500', '#FFFF00', '#008000', '#00FFFF', '#0000FF', '#800080']
        # 创建七个数据系列，每个系列都有不同的颜色
        self.series_list = []
        for i in range(7):
            series = QLineSeries()
            series.setName(f"传感器 {i + 1}    ")  # 设置图例名称
            # series.setColor(Qt.GlobalColor(i + 1))  # 默认颜色
            color = QColor(colors[i])
            series.setColor(color)
            self.chart.addSeries(series)
            self.series_list.append(series)
        # 设置X轴：时间轴
        self.axis_x = QDateTimeAxis()
        self.axis_x.setFormat("hh:mm:ss:zzz")  # 设置时间格式
        self.chart.addAxis(self.axis_x, Qt.AlignBottom)
        # 设置Y轴：值轴
        self.axis_y = QValueAxis()
        self.axis_y.setRange(0, 100)
        self.chart.addAxis(self.axis_y, Qt.AlignLeft)
        # 将每个数据系列附加到X轴和Y轴
        for series in self.series_list:
            series.attachAxis(self.axis_x)
            series.attachAxis(self.axis_y)
        # 设置图表标题
        self.chart.setTitle(name)
        self.chart_view.setRenderHint(QPainter.Antialiasing)  # 启用抗锯齿
        # 布局设置
        layout = QVBoxLayout()
        layout.addWidget(self.chart_view)
        self.setLayout(layout)

        # 设置X轴的最大显示点数
        self.max_points = 500
        self.axis_y.setTickCount(9)
        self.axis_x.setTickCount(5)

        # limited
        # 创建上限线
        self.upper_limit = QLineSeries()
        self.upper_limit.setName("上限")
        # 创建下限线
        self.lower_limit = QLineSeries()
        self.lower_limit.setName("下限")

    def update_data(self, new_values, current_time):
        if self.cc_line == 0:
            self.add_limit_lines(current_time - 10000, current_time)
        # 遍历所有系列并更新数据
        for i, series in enumerate(self.series_list):
            # 删除最早的点，保持系列点数不超过最大限制
            if series.count() > self.max_points:
                series.remove(0)
            # 添加新的数据点
            series.append(current_time, new_values[i])
        if current_time > int(self.cc_line + 10000):
            self.add_limit_lines(current_time, current_time + 10000)
            self.cc_line = current_time

        # 更新X轴范围为当前时间前30秒 到当前时间
        start_time = QDateTime.fromMSecsSinceEpoch(current_time - 10000)  # 当前时间的30秒前
        current_time = QDateTime.fromMSecsSinceEpoch(current_time)  # 当前时间
        self.axis_x.setRange(start_time, current_time)
        # 更新图表
        self.chart_view.repaint()

    def clear_chart(self):
        """
        清空所有数据系列的点。
        """
        for series in self.series_list:
            series.clear()
        self.chart_view.repaint()

    def add_limit_lines(self, start_time, current_time):
        self.upper_limit.append(QPointF(start_time, 77.5))
        self.upper_limit.append(QPointF(current_time, 77.5))
        self.upper_limit.setColor(QColor(0, 0, 0))
        # 创建 QPen 并设置虚线样式
        pen = QPen(QColor(0, 0, 0))
        pen.setStyle(Qt.DashLine)  # 设置为虚线
        self.upper_limit.setPen(pen)
        self.chart.addSeries(self.upper_limit)
        self.upper_limit.attachAxis(self.axis_x)
        self.upper_limit.attachAxis(self.axis_y)

        self.lower_limit.append(QPointF(start_time, 16.5))
        self.lower_limit.append(QPointF(current_time, 16.5))  # 设置另一点
        self.lower_limit.setColor(QColor(0, 0, 0))  # 蓝色
        # 创建 QPen 并设置虚线样式
        pen = QPen(QColor(0, 0, 0))  # 设置蓝色
        pen.setStyle(Qt.DashLine)  # 设置为虚线
        self.lower_limit.setPen(pen)
        self.chart.addSeries(self.lower_limit)
        self.lower_limit.attachAxis(self.axis_x)
        self.lower_limit.attachAxis(self.axis_y)

class CustomChartView(QChartView):
    def __init__(self, chart, parent=None):
        super().__init__(chart, parent)
        self.parent = parent
        self.mouse_x = -1

    def mouseMoveEvent(self, event):
        pos = event.pos()
        if self.chart().plotArea().contains(pos):
            point = self.chart().mapToValue(pos)
            tooltip_text = ""
            self.mouse_x = pos.x()
            for series in self.parent.series_list:
                min_distance = float('inf')
                closest_point = None
                for i in range(series.count()):
                    data_point = series.at(i)
                    distance = abs(data_point.x() - point.x())
                    if distance < min_distance:
                        min_distance = distance
                        closest_point = data_point
                if closest_point:
                    tooltip_text += f"{series.name()}: x={QDateTime.fromMSecsSinceEpoch(int(closest_point.x())).toString('hh:mm:ss:zzz')}, y={closest_point.y()}\n"
            if tooltip_text:
                QToolTip.showText(self.mapToGlobal(pos), tooltip_text, self)
            else:
                QToolTip.hideText()
        else:
            self.mouse_x = -1
            QToolTip.hideText()
        self.update()
        super().mouseMoveEvent(event)

    def leaveEvent(self, event):
        self.mouse_x = -1
        QToolTip.hideText()
        self.update()
        super().leaveEvent(event)

    def paintEvent(self, event):
        super().paintEvent(event)
        if self.mouse_x >= 0:
            painter = QPainter(self.viewport())
            pen = QPen(QColor(255, 0, 0))
            pen.setStyle(Qt.SolidLine)
            painter.setPen(pen)
            y_min = self.chart().plotArea().top()
            y_max = self.chart().plotArea().bottom()
            painter.drawLine(self.mouse_x, y_min, self.mouse_x, y_max)