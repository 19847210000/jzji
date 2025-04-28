from matplotlib import pyplot as plt
from scipy.optimize import minimize
import math
import numpy


class Thita_with_Dis():
    def __init__(self):
        self.dis = 0
        self.theta = 0
    def f_dis_with_th(self, th):
        th_radians = math.radians(th)
        if 0 <= th < 60:
            return 135 / numpy.cos(th_radians)
        elif 60 <= th < 83:
            return 159 * numpy.cos(math.radians(83 - th)) + (114**2 - (159 * numpy.sin(math.radians(83 - th)))**2) ** 0.5
        elif 83 <= th < 215.6:
            return 16.39 * numpy.cos(math.radians(245 - th)) + (290**2 - (16.39 * numpy.sin(math.radians(245 - th)))**2) ** 0.5
        elif 215.6 <= th < 221:
            return ((th - 215.6) / 6270.967545270072) + 304.16755786250786
        else:
            return 13.24 * numpy.cos(math.radians(336 - th)) + (310**2 - (13.24 * numpy.sin(math.radians(336 - th)))**2) ** 0.5
    def objective(self, th):
        dis = self.f_dis_with_th(th)
        return (dis - self.dis) ** 2
    def get_th(self, dis):
        self.dis = dis
        result = minimize(self.objective, x0 = 150, bounds=[(83, 330)])
        return result.x[0]

    def plot(self):
        # 生成 theta 值，从 0 到 67 * np.pi / 180
        theta_values = numpy.linspace(0, 330, 6000)
        dis_values = []

        # 计算每个 theta 对应的体积
        for theta in theta_values:
            dis = self.f_dis_with_th(theta)
            dis_values.append(dis)

        # 绘制变化曲线
        plt.figure(figsize=(10, 6))
        plt.plot(theta_values, dis_values, label='Distance vs. Angle', color='blue')
        plt.title('Distance Change with Angle')
        plt.xlabel('Angle (degree)')
        plt.ylabel('Distance')
        plt.grid(True)
        plt.legend()
        plt.show()

if __name__ == "__main__":
    f_th_with_dis = Thita_with_Dis()    # 有效Dis：  274.4 ~ 323 mm
    thita = f_th_with_dis.get_th(323)   # 有效Thita：   83 ~ 330 °
    dis = f_th_with_dis.f_dis_with_th(182)
    # print(thita)
    print(dis)

    f_th_with_dis.plot()