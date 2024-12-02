using System;
using System.Collections.Generic;
using System.Linq;
using System.Runtime.InteropServices;
using System.Text;

namespace jzj_3._5
{
    internal class cjk_9114
    {
        // 定义常量对应类型
        public const short I16 = 16; // short
        public const ushort U16 = 16; // ushort
        public const uint U32 = 32; // uint
        public const double F64 = 64.0;

        // 导入 PCI-Dask64.dll 中的函数
        [DllImport("PCI-Dask64.dll", CallingConvention = CallingConvention.Cdecl)]
        public static extern short Register_Card(ushort cardType, ushort cardNumber);

        [DllImport("PCI-Dask64.dll", CallingConvention = CallingConvention.Cdecl)]
        public static extern short AI_9114_Config(ushort cardHandle, ushort triggerSource);

        [DllImport("PCI-Dask64.dll", CallingConvention = CallingConvention.Cdecl)]
        public static extern short AI_ContReadChannel(ushort cardNumber, ushort channel, ushort adRange,
                                                     ref ushort buffer, uint readCount, double sampleRate, ushort syncMode);

        [DllImport("PCI-Dask64.dll", CallingConvention = CallingConvention.StdCall)]
        public static extern short AI_ContScanChannels(
        ushort cardNumber,       // 设备卡号
        ushort channels,         // 通道号
        ushort adRange,          // 模拟输入范围
        ushort[] buffer,         // 数据缓冲区（数组）
        uint readCount,          // 读取样本数
        double sampleRate,       // 采样率
        ushort syncMode          // 同步模式
                                                        );
        [DllImport("PCI-Dask64.dll", CallingConvention = CallingConvention.StdCall)]
            public static extern short AI_ReadChannel(
            ushort CardNumber,
            ushort Channel,
            ushort AdRange,
            ref ushort Value
            );
        [DllImport("PCI-Dask64.dll", CallingConvention = CallingConvention.Cdecl)]
        public static extern short Release_Card(ushort cardNumber);

        // 包装函数，处理对 DLL 的调用和参数
        public static void AiContReadChannel(int cardNumber, int channel, int adRange,
                                      ushort[] buffer, uint readCount, double sampleRate, ushort syncMode,
                                      out short result, out ushort[] filledBuffer)
        {
            ushort[] bufferArray = new ushort[buffer.Length];
            result = AI_ContReadChannel((ushort)cardNumber, (ushort)channel, (ushort)adRange,
                                        ref bufferArray[0], readCount, sampleRate, syncMode);
            filledBuffer = bufferArray;
        }

        //public static void AiContScanChannels(ushort cardNumber, ushort channels, ushort adRange,
        //                                ushort[] buffer, uint readCount, double sampleRate, ushort syncMode,
        //                                out short result, ref ushort[] bufferArray)
        //{
        //    if (bufferArray == null || bufferArray.Length != buffer.Length)
        //    {
        //        // 如果数组为 null 或长度不匹配，重新分配内存
        //        bufferArray = new ushort[buffer.Length];
        //    }
        //    result = AI_ContScanChannels((ushort)cardNumber, (ushort)channels, (ushort)adRange,
        //                                 bufferArray, readCount, sampleRate, syncMode);
        //}
    }
}
