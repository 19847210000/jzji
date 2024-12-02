import ctypes
import time

# 加载 DLL
mpc_lib = ctypes.CDLL('./MPC08.dll')

# 函数定义
# 单轴控制
con_pmove = mpc_lib.con_pmove
con_pmove.argtypes = [ctypes.c_int, ctypes.c_long]
con_pmove.restype = ctypes.c_int
# 单轴快速
fast_pmove = mpc_lib.fast_pmove
fast_pmove.argtypes = [ctypes.c_int, ctypes.c_long]
fast_pmove.restype = ctypes.c_int
# 回原点设置
set_home_mode = mpc_lib.set_home_mode
set_home_mode.argtypes = [ctypes.c_int, ctypes.c_int]       # int ch,int origin_mode 0和1是立即停止，2和3是缓慢停止
set_home_mode.restype = ctypes.c_int
# 单轴回原点
con_hmove = mpc_lib.con_hmove
con_hmove.argtypes = [ctypes.c_int, ctypes.c_int]           # int ch,int 转动方向1和-1
con_hmove.restype = ctypes.c_int
# 单轴快速回原点
fast_hmove = mpc_lib.fast_hmove
fast_hmove.argtypes = [ctypes.c_int, ctypes.c_int]           # int ch,int 转动方向1和-1
fast_hmove.restype = ctypes.c_int
# 单轴连续运行
con_vmove = mpc_lib.con_vmove
con_vmove.argtypes = [ctypes.c_int, ctypes.c_int]          # int ch,int 转动方向1和-1
con_vmove.restype = ctypes.c_int
# 单轴连续运行
fast_vmove = mpc_lib.fast_vmove
fast_vmove.argtypes = [ctypes.c_int, ctypes.c_int]          # int ch,int 转动方向1和-1
fast_vmove.restype = ctypes.c_int
# 检查轴运动状态
check_done = mpc_lib.check_done         # 0静止，1运动，-1错误
check_done.argtypes = [ctypes.c_int]
check_done.restype = ctypes.c_int
# 立即停止
sudden_stop = mpc_lib.sudden_stop
sudden_stop.argtypes = [ctypes.c_int]
sudden_stop.restype = ctypes.c_int
# 位置置零
reset_pos = mpc_lib.reset_pos
reset_pos.argtypes = [ctypes.c_int]
reset_pos.restype = ctypes.c_int
# 获取轴的绝对位置
get_abs_pos = mpc_lib.get_abs_pos
get_abs_pos.argtypes = [ctypes.c_int, ctypes.POINTER(ctypes.c_long)]
get_abs_pos.restype = ctypes.c_int
# 获取轴的绝对位置
get_rel_pos = mpc_lib.get_rel_pos
get_rel_pos.argtypes = [ctypes.c_int, ctypes.POINTER(ctypes.c_long)]
get_rel_pos.restype = ctypes.c_int
# 获取轴的真实位置
get_encoder = mpc_lib.get_encoder
get_encoder.argtypes = [ctypes.c_int, ctypes.POINTER(ctypes.c_long)]
get_encoder.restype = ctypes.c_int
# 设置最大转速
set_maxspeed = mpc_lib.set_maxspeed
set_maxspeed.argtypes = [ctypes.c_int, ctypes.c_double]     # ch, speed
set_maxspeed.restype = ctypes.c_int
# 设置常速转速
set_conspeed = mpc_lib.set_conspeed
set_conspeed.argtypes = [ctypes.c_int, ctypes.c_double]     # ch, speed
set_conspeed.restype = ctypes.c_int
# 脉冲输出模式设置
set_outmode = mpc_lib.set_outmode
set_outmode.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_int]       # int ch,int origin_mode 0和1是立即停止，2和3是缓慢停止
set_outmode.restype = ctypes.c_int
# 获取轴运动方向
get_cur_dir = mpc_lib.get_cur_dir
get_cur_dir.argtypes = [ctypes.c_int]
get_cur_dir.restype = ctypes.c_int
# 设置编码器模式
set_getpos_mode = mpc_lib.set_getpos_mode
set_getpos_mode.argtypes = [ctypes.c_int, ctypes.c_int]
set_getpos_mode.restype = ctypes.c_int

if __name__ == "__main__":
    r1 = mpc_lib.auto_set()
    print("轴数", r1)
    r2 = mpc_lib.init_board()
    print("卡数", r2)
    axis = 1
    pulses = 4000
    r1 = mpc_lib.auto_set()
    r2 = mpc_lib.init_board()
    set_outmode(axis, 1, 1)
    set_conspeed(axis, 4000)
    set_maxspeed(axis, 8000)
    reset_pos(axis)
    set_getpos_mode(axis, 1)

    fast_pmove(axis, pulses)

    for i in range(30):
        wz = ctypes.c_long(0)
        get_encoder(axis, ctypes.byref(wz))
        print(wz.value)
        time.sleep(0.1)