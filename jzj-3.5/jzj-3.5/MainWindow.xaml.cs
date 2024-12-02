using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Data;
using System.Windows.Documents;
using System.Windows.Input;
using System.Windows.Media;
using System.Windows.Media.Imaging;
using System.Windows.Navigation;
using System.Windows.Shapes;

namespace jzj_3._5
{
    /// <summary>
    /// Interaction logic for MainWindow.xaml
    /// </summary>
    public partial class MainWindow : Window
    {
        public MainWindowViewModel VM;
        public MyFunction Func;
        private bool is_run;
        private bool is_run_cj;
        private bool is_run_nh;
        private int axis = 1;
        int r;
        public MainWindow()
        {
            InitializeComponent();
            VM = new MainWindowViewModel();
            //初始化轴卡
            r = MPC08E.auto_set();
            VM.AddLog($"轴卡auto_set:{r}", "Info");
            r = MPC08E.init_board();
            VM.AddLog($"轴卡init_board:{r}", "Info");
            MPC08E.set_outmode(axis, 1, 1);
            MPC08E.set_conspeed(axis, 4000);
            MPC08E.set_maxspeed(axis, 8000);
            MPC08E.reset_pos(axis);
            MPC08E.set_getpos_mode(axis, 1);
            VM.Para.Num_mc = "2000";
            Func = new MyFunction(VM);
            is_run = false;
            is_run_cj = false;
            is_run_nh = false;
            VM.ScrollToBottomRequested += OnScrollToBottomRequested;
            DataContext = VM;

            VM.Para.IP = "192.168.1.14";
            // 初始化时调用 Lian_PLC
            Lian_PLC(this, null);

            VM.Para.BarChartValues = new List<double> { 1.5, 4, 2.5, 0.8, 10, 2.0, 1.2 };
            //barChart_auto.MaxValue = 5;  // 设置 Y 轴最大值
            //barChart_auto.MinValue = 0;  // 设置 Y 轴最小值
            //barChart_hand.MaxValue = 5;  // 设置 Y 轴最大值
            //barChart_hand.MinValue = 0;  // 设置 Y 轴最小值

            // 可以根据需要指定日志级别和消息
            //VM.AddLog("这是一个信息日志", "Info");
            //VM.AddLog("这是一个警告日志", "Warning");
            //VM.AddLog("这是一个错误日志", "Error");
            //viewModel.ClearLogs();

            VM.Para.Press1 = "0";
            VM.Para.Press2 = "0";
            VM.Para.Press3 = "0";
            VM.Para.Press4 = "0";
            VM.Para.Press5 = "0";
            VM.Para.Press6 = "0";
            VM.Para.Press7 = "0";
            VM.Para.Compensation1 = "0";
            VM.Para.Compensation2 = "0";
            VM.Para.Compensation3 = "0";
            VM.Para.Compensation4 = "0";
            VM.Para.Compensation5 = "0";
            VM.Para.Compensation6 = "0";
            VM.Para.Compensation7 = "0";
            VM.Para.Add1 = "0";
            VM.Para.Add2 = "0";
            VM.Para.Add3 = "0";
            VM.Para.Add4 = "0";
            VM.Para.Add5 = "0";
            VM.Para.Max_num = "0";
            VM.Para.Direct_P1 = "0";

        }
        private void OnScrollToBottomRequested()
        {
            LogListBox_auto.ScrollIntoView(LogListBox_auto.Items[LogListBox_auto.Items.Count - 1]);
            LogListBox_halfauto.ScrollIntoView(LogListBox_halfauto.Items[LogListBox_halfauto.Items.Count - 1]);
            LogListBox_hand.ScrollIntoView(LogListBox_hand.Items[LogListBox_hand.Items.Count - 1]);
            LogListBox_para.ScrollIntoView(LogListBox_para.Items[LogListBox_para.Items.Count - 1]);
        }
        private void Lian_PLC(object sender, RoutedEventArgs e)
        {
            // 如果你需要在后台代码中操作按钮，可以通过其 Name 属性进行引用
            if (radioButtonXmz.IsChecked == true)
            {
                // "西门子" 被选中时执行的代码
                VM.Para.IP = "192.168.1.10";
                Application.Current.Dispatcher.Invoke((Action)(() =>
                {
                    VM.AddLog("运行LianPLC！！！", "Info");
                }));
            };
            if (radioButtonHc.IsChecked == true)

            {
                // "汇川" 被选中时执行的代码
                Application.Current.Dispatcher.Invoke((Action)(() =>
                {
                    VM.AddLog("请选择西门子！！！", "Warning");
                }));
            };
        }
        private void Duan_PLC(object sender, RoutedEventArgs e)
        {

        }
        private void Set_Para(object sender, RoutedEventArgs e)
        {

        }
        private void B_End_Click(object sender, RoutedEventArgs e)
        {
            VM.Para.EN = false;
            Application.Current.Dispatcher.Invoke((Action)(() =>
            {
                VM.AddLog("结束自动模式！！！", "Info");
            }));
        }
        private void B_Run_Click(object sender, RoutedEventArgs e)
        {
            if (is_run) { return; }
            is_run = true;
            Application.Current.Dispatcher.Invoke((Action)(() =>
            {
                VM.AddLog("开始自动模式！！！", "Info");
            }));
            VM.Para.EN = true;

            // 创建一个新的线程来执行长时间运行的任务
            Thread workerThread = new Thread(RunTask);
            workerThread.Start();
        }
        private void RunTask()
        {
            int i = 0;
            while (VM.Para.EN)
            {
                // 模拟延迟 1000 毫秒
                Thread.Sleep(1000);

                //VM.AddLog($"运行中 {i}", "Info");
                Application.Current.Dispatcher.Invoke((Action)(() =>
                {
                    VM.AddLog($"运行中 {i}", "Info");
                }));

                i++;
            }

            is_run = false;
        }
        private void B_End_cj(object sender, RoutedEventArgs e)
        {
            VM.Para.EN = false;
            Application.Current.Dispatcher.Invoke((Action)(() =>
            {
                VM.AddLog("结束数据采集！！！", "Info");
            }));
        }
        private void B_Run_zd(object sender, RoutedEventArgs e)
        {
            long num_mc;
            if (long.TryParse(VM.Para.Num_mc, out num_mc))
            {
                MPC08E.fast_pmove(axis, num_mc);
                Application.Current.Dispatcher.Invoke((Action)(() =>
                {
                    VM.AddLog($"成功启动夹爪，转动{num_mc}", "Info");
                }));
            }
            else
            {
                Application.Current.Dispatcher.Invoke((Action)(() =>
                {
                    VM.AddLog($"输入的{VM.Para.Num_mc}不是有效的启动指令，请输入数字", "Error");
                }));
            }
        }
        private void B_End_zd(object sender, RoutedEventArgs e)
        {
            MPC08E.sudden_stop(axis);
            Application.Current.Dispatcher.Invoke((Action)(() =>
            {
                VM.AddLog($"停转电机", "Info");
            }));
        }
        private void B_hl(object sender, RoutedEventArgs e)
        {
            MPC08E.con_hmove(axis, 1);
            Application.Current.Dispatcher.Invoke((Action)(() =>
            {
                VM.AddLog($"电机回零", "Info");
            }));
        }
        private void B_hand_jzzz(object sender, RoutedEventArgs e)
        {

        }
        private void B_hand_jzht(object sender, RoutedEventArgs e)
        {

        }
        private void B_hand_jzss(object sender, RoutedEventArgs e)
        {

        }
        private void B_hand_jztz(object sender, RoutedEventArgs e)
        {

        }
        private void B_hand_jzjj(object sender, RoutedEventArgs e)
        {

        }
        private void B_hand_jzxj(object sender, RoutedEventArgs e)
        {

        }
        private void B_hand_jzfz(object sender, RoutedEventArgs e)
        {

        }
        private void B_hand_jzqj(object sender, RoutedEventArgs e)
        {

        }
        private void B_hand_jzsk(object sender, RoutedEventArgs e)
        {

        }
        private void B_hand_bjzh(object sender, RoutedEventArgs e)
        {

        }
        private void B_hand_bjht(object sender, RoutedEventArgs e)
        {

        }
        private void B_hand_bjss(object sender, RoutedEventArgs e)
        {

        }
        private void B_hand_bjhl(object sender, RoutedEventArgs e)
        {

        }
        private void B_hand_bjtz(object sender, RoutedEventArgs e)
        {

        }
        private void B_hand_bjzq(object sender, RoutedEventArgs e)
        {

        }
        private void B_hand_bjqj(object sender, RoutedEventArgs e)
        {

        }
        private void B_hand_bjxj(object sender, RoutedEventArgs e)
        {

        }
        private void B_hand_ytj1(object sender, RoutedEventArgs e)
        {

        }
        private void B_hand_ytc1(object sender, RoutedEventArgs e)
        {

        }
        private void B_hand_ytj2(object sender, RoutedEventArgs e)
        {

        }
        private void B_hand_ytc2(object sender, RoutedEventArgs e)
        {

        }
        private void B_hand_ytj3(object sender, RoutedEventArgs e)
        {

        }
        private void B_hand_ytc3(object sender, RoutedEventArgs e)
        {

        }
        private void B_hand_ytj4(object sender, RoutedEventArgs e)
        {

        }
        private void B_hand_ytc4(object sender, RoutedEventArgs e)
        {

        }
        private void B_hand_ytj5(object sender, RoutedEventArgs e)
        {

        }
        private void B_hand_ytc5(object sender, RoutedEventArgs e)
        {

        }
        private void B_hand_yttz(object sender, RoutedEventArgs e)
        {

        }
        private void B_hand_ythl(object sender, RoutedEventArgs e)
        {

        }
        private void B_hand_yttq(object sender, RoutedEventArgs e)
        {

        }
        private void B_hand_ytxy(object sender, RoutedEventArgs e)
        {

        }
        private void B_hand_zcj1(object sender, RoutedEventArgs e)
        {

        }
        private void B_hand_zcting1(object sender, RoutedEventArgs e)
        {

        }
        private void B_hand_zct1(object sender, RoutedEventArgs e)
        {

        }
        private void B_hand_zcj2(object sender, RoutedEventArgs e)
        {

        }
        private void B_hand_zcting2(object sender, RoutedEventArgs e)
        {

        }
        private void B_hand_zct2(object sender, RoutedEventArgs e)
        {

        }
        private void B_hand_zcj3(object sender, RoutedEventArgs e)
        {

        }
        private void B_hand_zcting3(object sender, RoutedEventArgs e)
        {

        }
        private void B_hand_zct3(object sender, RoutedEventArgs e)
        {

        }
        private void B_hand_zcj4(object sender, RoutedEventArgs e)
        {

        }
        private void B_hand_zcting4(object sender, RoutedEventArgs e)
        {

        }
        private void B_hand_zct4(object sender, RoutedEventArgs e)
        {

        }
        private void B_hand_zpss(object sender, RoutedEventArgs e)
        {

        }
        private void B_hand_zpting(object sender, RoutedEventArgs e)
        {

        }
        private void B_hand_zpxj(object sender, RoutedEventArgs e)
        {

        }
        private void B_hand_qncq(object sender, RoutedEventArgs e)
        {

        }
        private void B_hand_qntz(object sender, RoutedEventArgs e)
        {

        }
        private void B_hand_qnfq(object sender, RoutedEventArgs e)
        {

        }
        private void B_ec(object sender, RoutedEventArgs e)
        {
            if (is_run_nh == true) { return; }

            is_run_nh = true;
            VM.Para.EN = true;

            // 使用线程来运行长时间操作
            Thread thread = new Thread(() =>
            {
                Func.ni_he();  // 在后台线程执行长时间的操作
                is_run_nh = false;
            });

            thread.Start();
        }
        private void B_Run_cj(object sender, RoutedEventArgs e)
        {
            if (is_run_cj == true) { return; }
            is_run_cj = true;

            // 使用 Thread 启动一个后台线程来执行采集操作
            Thread thread = new Thread(() =>
            {
                Func.Caiji();  // 在后台线程执行长时间的操作
                is_run_cj = false;
            });
            thread.Start();  // 启动后台线程
        }
    }
}
