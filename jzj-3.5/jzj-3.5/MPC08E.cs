using System;
using System.Collections.Generic;
using System.Linq;
using System.Runtime.InteropServices;
using System.Text;

namespace jzj_3._5
{
    internal class MPC08E
    {
        // 导入 MPC08E.dll 中的函数
        // 导入 mpc_lib.dll 中的函数
        [DllImport("MPC08.dll", CallingConvention = CallingConvention.Cdecl)]
        public static extern int auto_set();  // 轴数设置

        [DllImport("MPC08.dll", CallingConvention = CallingConvention.Cdecl)]
        public static extern int init_board();  // 初始化卡

        [DllImport("MPC08.dll", CallingConvention = CallingConvention.Cdecl)]
        public static extern int get_board_num();  // 获取卡数
        [DllImport("MPC08.dll", CallingConvention = CallingConvention.Cdecl)]
        public static extern int con_pmove(int ch, long pulses);

        [DllImport("MPC08.dll", CallingConvention = CallingConvention.Cdecl)]
        public static extern int fast_pmove(int ch, long pulses);

        [DllImport("MPC08.dll", CallingConvention = CallingConvention.Cdecl)]
        public static extern int set_home_mode(int ch, int origin_mode);

        [DllImport("MPC08.dll", CallingConvention = CallingConvention.Cdecl)]
        public static extern int con_hmove(int ch, int direction);

        [DllImport("MPC08.dll", CallingConvention = CallingConvention.Cdecl)]
        public static extern int fast_hmove(int ch, int direction);

        [DllImport("MPC08.dll", CallingConvention = CallingConvention.Cdecl)]
        public static extern int con_vmove(int ch, int direction);

        [DllImport("MPC08.dll", CallingConvention = CallingConvention.Cdecl)]
        public static extern int fast_vmove(int ch, int direction);

        [DllImport("MPC08.dll", CallingConvention = CallingConvention.Cdecl)]
        public static extern int check_done(int ch);

        [DllImport("MPC08.dll", CallingConvention = CallingConvention.Cdecl)]
        public static extern int sudden_stop(int ch);

        [DllImport("MPC08.dll", CallingConvention = CallingConvention.Cdecl)]
        public static extern int reset_pos(int ch);

        [DllImport("MPC08.dll", CallingConvention = CallingConvention.Cdecl)]
        public static extern int get_abs_pos(int ch, ref long pos);

        [DllImport("MPC08.dll", CallingConvention = CallingConvention.Cdecl)]
        public static extern int get_rel_pos(int ch, out long pos);

        [DllImport("MPC08.dll", CallingConvention = CallingConvention.Cdecl)]
        public static extern int get_encoder(int ch, ref long pos);

        [DllImport("MPC08.dll", CallingConvention = CallingConvention.Cdecl)]
        public static extern int set_maxspeed(int ch, double speed);

        [DllImport("MPC08.dll", CallingConvention = CallingConvention.Cdecl)]
        public static extern int set_conspeed(int ch, double speed);

        [DllImport("MPC08.dll", CallingConvention = CallingConvention.Cdecl)]
        public static extern int set_outmode(int ch, int mode, int speed);

        [DllImport("MPC08.dll", CallingConvention = CallingConvention.Cdecl)]
        public static extern int get_cur_dir(int ch);

        [DllImport("MPC08.dll", CallingConvention = CallingConvention.Cdecl)]
        public static extern int set_getpos_mode(int ch, int mode);
    }
}
