import ctypes
import time

I16 = ctypes.c_short
U16 = ctypes.c_ushort
U32 = ctypes.c_uint
F64 = ctypes.c_double

# 加载 DLL
dask_dll = ctypes.CDLL('./PCI-Dask64.dll')

# 定义函数参数类型和返回类型
# 定义初始化函数
# dask_dll.Register_Card.argtypes = [U16, U16]
# dask_dll.Register_Card.restype = I16
# 定义配置9114函数
AI_9114_Config = dask_dll.AI_9114_Config
AI_9114_Config.argtypes = [U16, U16]  # 参数类型
AI_9114_Config.restype = I16  # 返回类型
# 读指定通道函数
AI_ReadChannel = dask_dll.AI_ReadChannel
AI_ReadChannel.argtypes = [U16, U16, U16, ctypes.POINTER(I16)]  # card_number;channel;ad_range;value
AI_ReadChannel.restype = I16  # 返回类型
# 扫描各通道函数
AI_ContScanChannels = dask_dll.AI_ContScanChannels
AI_ContScanChannels.argtypes = [U16, U16, U16, ctypes.POINTER(U16), U32, F64, U16]  # 参数类型
AI_ContScanChannels.restype = I16  # 返回类型
# 释放采集卡
dask_dll.Release_Card.argtypes = [U16]
dask_dll.Release_Card.restype = I16

if __name__ == "__main__":
    # 初始化采集卡
    card_number = 0             # 卡号
    card_handle = dask_dll.Register_Card(24, card_number)   # 24=>ad_range(1,2,3,4),25=>ad_range(1,10,11,12)
    # 配置采集卡
    trigger_source = 1          # 触发源
    AI_9114_Config(card_handle, trigger_source)
    # 采集卡参数
    channel = 5                 # 传感器位置
    ad_range = 2                # 1=>正负10；2=>正负5；3=>正负2.5；4=>正负1.25；10=>正负1；11=>正负0.1；12=>正负0.01
    read_count = 48
    sample_rate = 100000.0      # 最高100000.0
    sync_mode = 1               # 1=>SYNCH_OP同步;2=>ASYNCH_OP异步;

    i = 30
    while(i>0):
        i-=1

        value1 = ctypes.c_short(0)
        value2 = ctypes.c_short(0)
        AI_ReadChannel(card_number, 0, ad_range, ctypes.pointer(value1))
        AI_ReadChannel(card_number, 5, ad_range, ctypes.pointer(value2))
        print(value1.value,value2.value)
        time.sleep(1)

        # sync_mode = 2  # 1=>SYNCH_OP同步;2=>ASYNCH_OP异步;
        # buffer_array = (U16 * read_count)()
        # result = AI_ContScanChannels(card_number, channel, ad_range, buffer_array, read_count, sample_rate, sync_mode)
        # print(list(buffer_array[:read_count]))
        # time.sleep(1)

    # 释放采集卡资源
    result = dask_dll.Release_Card(card_number)