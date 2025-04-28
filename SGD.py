import bisect
def find_closest_index(target, float_list):
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
float_list = [0.0, 5.5, 10.1, 15.8, 20.2, 30.0, 40.7, 50.1, 60.0, 70.9, 80.5, 90.3, 100.0]
target_value = 12.0
closest_index = find_closest_index(target_value, float_list)
print(closest_index)