from PyQt5.QtGui import QPen, QPixmap
import math
from PyQt5.QtWidgets import QWidget, QSplashScreen, QLabel, QVBoxLayout
from PyQt5.QtGui import QPainter, QColor, QIcon, QFont
from PyQt5.QtCore import Qt

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
        radius = 30             # 绘制圆形
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
        super().__init__(QPixmap("images/UI/L.jpg"))  # 替换为你的图片路径
        self.setWindowFlag(Qt.WindowStaysOnTopHint)

