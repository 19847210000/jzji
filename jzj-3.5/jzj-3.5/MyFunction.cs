using System;
using System.Collections.Generic;
using System.Linq;
using System.Windows;

namespace jzj_3._5
{
    public class CircleResult
    {
        public double X { get; set; }
        public double Y { get; set; }
        public double Z { get; set; }

        public CircleResult(double x, double y, double z)
        {
            X = x;
            Y = y;
            Z = z;
        }
    }
    public class CirclePointsResult
    {
        public double[] R { get; set; }
        public double[] Theta { get; set; }

        public CirclePointsResult(double[] r, double[] theta)
        {
            R = r;
            Theta = theta;
        }
    }
    public class Circle_EC
    {
        public static CircleResult GetCircle(double[] r, double[] theta)
        {
            // 转换为数组
            r = r.Select(x => (double)x).ToArray();
            theta = theta.Select(x => (double)x).ToArray();

            // 将角度转换为弧度
            theta = theta.Select(x => Math.PI * x / 180).ToArray();

            // 计算 b = r^2
            var b = r.Select(x => x * x).ToArray();

            // 构造矩阵 A
            int len = r.Length;
            double[,] A = new double[len, 3];

            for (int i = 0; i < len; i++)
            {
                A[i, 0] = 2 * r[i] * Math.Cos(theta[i]);
                A[i, 1] = 2 * r[i] * Math.Sin(theta[i]);
                A[i, 2] = 1; // 追加 1
            }

            // 计算 A^T * A
            double[,] AT = TransposeMatrix(A);
            double[,] ATA = MultiplyMatrices(AT, A);

            // 计算 ATA 的逆
            double[,] ATAInv = InverseMatrix(ATA);

            // 计算 BcA, BsA, C
            double[] result = MultiplyMatrixVector(MultiplyMatrices(ATAInv, AT),  b);

            // 解压结果
            double BcA = result[0];
            double BsA = result[1];
            double C = result[2];

            // 计算 B 和 thta
            double B = Math.Sqrt(BcA * BcA + BsA * BsA);
            double thta = Math.Atan2(BsA, BcA) * 180 / Math.PI;

            if (thta < 0) thta += 360;

            // 返回结果
            double cosThta = Math.Cos(thta * Math.PI / 180);
            double sinThta = Math.Sin(thta * Math.PI / 180);

            return new CircleResult(B * cosThta, B * sinThta, Math.Sqrt(B * B + C));
        }
        // 矩阵转置
        public static double[,] TransposeMatrix(double[,] matrix)
        {
            int rows = matrix.GetLength(0);
            int cols = matrix.GetLength(1);
            double[,] transposed = new double[cols, rows];

            for (int i = 0; i < rows; i++)
                for (int j = 0; j < cols; j++)
                    transposed[j, i] = matrix[i, j];

            return transposed;
        }
        // 矩阵乘法
        public static double[,] MultiplyMatrices(double[,] A, double[,] B)
        {
            int rowsA = A.GetLength(0);
            int colsA = A.GetLength(1);
            int rowsB = B.GetLength(0);
            int colsB = B.GetLength(1);

            if (colsA != rowsB)
                throw new InvalidOperationException("Matrices cannot be multiplied");

            double[,] result = new double[rowsA, colsB];

            for (int i = 0; i < rowsA; i++)
                for (int j = 0; j < colsB; j++)
                    for (int k = 0; k < colsA; k++)
                        result[i, j] += A[i, k] * B[k, j];

            return result;
        }
        // 计算矩阵的逆
        public static double[,] InverseMatrix(double[,] matrix)
        {
            int n = matrix.GetLength(0);
            double[,] augmented = new double[n, 2 * n];
            double[,] inverse = new double[n, n];

            // 创建增广矩阵 [matrix | I]
            for (int i = 0; i < n; i++)
                for (int j = 0; j < n; j++)
                    augmented[i, j] = matrix[i, j];

            for (int i = 0; i < n; i++)
                augmented[i, n + i] = 1;

            // 进行高斯-约旦消元法
            for (int i = 0; i < n; i++)
            {
                double pivot = augmented[i, i];
                for (int j = 0; j < 2 * n; j++)
                    augmented[i, j] /= pivot;

                for (int j = 0; j < n; j++)
                {
                    if (j != i)
                    {
                        double factor = augmented[j, i];
                        for (int k = 0; k < 2 * n; k++)
                            augmented[j, k] -= factor * augmented[i, k];
                    }
                }
            }

            // 取出右半部分作为逆矩阵
            for (int i = 0; i < n; i++)
                for (int j = 0; j < n; j++)
                    inverse[i, j] = augmented[i, n + j];

            return inverse;
        }
        // 矩阵乘以列向量
        public static double[] MultiplyMatrixVector(double[,] matrix, double[] vector)
        {
            int rows = matrix.GetLength(0);
            int cols = matrix.GetLength(1);

            if (cols != vector.Length)
                throw new InvalidOperationException("Matrix and vector sizes do not match");

            double[] result = new double[rows];

            for (int i = 0; i < rows; i++)
            {
                result[i] = 0;
                for (int j = 0; j < cols; j++)
                    result[i] += matrix[i, j] * vector[j];
            }

            return result;
        }
        // 转换一维数组为列向量（矩阵）
        public static double[,] ToColumnMatrix(double[] array)
        {
            int len = array.Length;
            double[,] matrix = new double[len, 1];

            for (int i = 0; i < len; i++)
                matrix[i, 0] = array[i];

            return matrix;
        }
        // 随机生成散点
        public static Random yigeyongyuanbuhuiyongdezhi = new Random();
        public static CirclePointsResult GenerateCirclePoints(int num, double[] center, double radius, double n)
        {
            // 生成均匀的角度
            double[] angles = new double[num];
            for (int i = 0; i < num; i++)
                angles[i] = 2 * Math.PI * i / num;

            // 随机生成半径
            double[] R = new double[num];
            for (int i = 0; i < num; i++)
                R[i] = radius + (yigeyongyuanbuhuiyongdezhi.NextDouble() * 2 * n - n); // 半径范围 [radius-n, radius+n]

            // 计算圆周坐标 (x, y)
            double[] x = new double[num];
            double[] y = new double[num];

            for (int i = 0; i < num; i++)
            {
                x[i] = center[0] + R[i] * Math.Cos(angles[i]);
                y[i] = center[1] + R[i] * Math.Sin(angles[i]);
            }

            // 计算半径 r 和角度 theta
            double[] r = new double[num];
            double[] theta = new double[num];

            for (int i = 0; i < num; i++)
            {
                r[i] = Math.Sqrt(x[i] * x[i] + y[i] * y[i]);
                theta[i] = Math.Atan2(y[i], x[i]) * 180 / Math.PI;
            }

            return new CirclePointsResult(r, theta);
        }
    }
    public class Filter
    {
        public static double[] MedianFilter(double[] inputArray)
        {
            int windowSize = 7; // 中位数窗口大小
            int halfWindow = windowSize / 2;
            int length = inputArray.Length;
            // 输出数组
            double[] outputArray = new double[length];
            for (int i = 0; i < length; i++)
            {
                // 计算前后共7个值的窗口范围
                int start = Math.Max(0, i - halfWindow);  // 窗口左边界
                int end = Math.Min(length - 1, i + halfWindow);  // 窗口右边界
                if (i - halfWindow < 0)
                {
                    // 将左边缺失的部分填充为第一个元素
                    start = 0;
                    end = 6;
                }
                // 如果右边界不足（后面不足3个值），填充后面的值为倒数第四个元素
                if (i + halfWindow >= length)
                {
                    end = length - 1;
                    start = length - 7;
                }
                // 获取窗口内的所有值
                double[] window = new double[end - start + 1];
                Array.Copy(inputArray, start, window, 0, window.Length);
                // 对窗口进行排序，取中位值
                Array.Sort(window);
                outputArray[i] = window[window.Length / 2]; // 中位数
            }
            return outputArray;
        }
    }
    public class MyFunction
    {
        private MainWindowViewModel _VM;
        int axis = 1;
        ushort card_number;
        ushort channel;
        ushort ad_range;
        uint read_count;
        double sample_rate;
        ushort sync_mode;
        short card_handle;
        ushort triggerSource;
        private int r;
        long num_pulses;
        long circle_pulses;
        public MyFunction(MainWindowViewModel VM)
        {
            _VM = VM;

            //初始化采集卡
            card_number = 0;
            channel = 5;
            ad_range = 1;
            read_count = 12;
            sample_rate = 10000.0;
            sync_mode = 1;
            triggerSource = 1;
            num_pulses = 21125;
            circle_pulses = 84500;

            card_handle = cjk_9114.Register_Card(24, card_number);
            Application.Current.Dispatcher.Invoke((Action)(() =>
            {
                if (card_handle < 0) { _VM.AddLog($"采集卡初始化失败:{card_handle}", "Error"); }
                else { _VM.AddLog($"采集卡初始化成功，句柄：{card_handle}", "Info"); }
            }));
            short result = cjk_9114.AI_9114_Config(card_number, triggerSource);
            Application.Current.Dispatcher.Invoke((Action)(() =>
            {
                if (result != 0) { _VM.AddLog($"采集卡配置失败:{result}", "Error"); }
                else { _VM.AddLog($"采集卡配置成功，句柄：{result}", "Info"); }
            }));

            string _para = _VM.Para.Press1;
        }
        private bool en;
        public void Caiji()
        {
            //int c = 0;
            
            Application.Current.Dispatcher.Invoke((Action)(() =>
            {
                _VM.Para.EN = true;
            }));
            en = true;
            //// 创建一个缓冲区来存储数据
            ushort[] bufferArray = new ushort[read_count];
            //short r = 0;
            int result = 0;
            int dir;
            long encoderValue = -1;
            ushort Value1 = 0;
            ushort Value2 = 0;
            ushort Value3 = 0;
            ushort Value4 = 0;
            ushort Value5 = 0;
            ushort Value6 = 0;
            ushort Value7 = 0;
            while (en)
            {
                //c += 1;
                //c %= 3;
                en = _VM.Para.EN;

                cjk_9114.AI_ReadChannel(card_number, 0, ad_range, ref Value1);
                cjk_9114.AI_ReadChannel(card_number, 1, ad_range, ref Value2);
                cjk_9114.AI_ReadChannel(card_number, 2, ad_range, ref Value3);
                cjk_9114.AI_ReadChannel(card_number, 3, ad_range, ref Value4);
                cjk_9114.AI_ReadChannel(card_number, 4, ad_range, ref Value5);
                cjk_9114.AI_ReadChannel(card_number, 5, ad_range, ref Value6);
                cjk_9114.AI_ReadChannel(card_number, 5, ad_range, ref Value7);

                // 获取编码器值和当前方向
                result = MPC08E.get_encoder(axis, ref encoderValue);
                dir = MPC08E.get_cur_dir(axis);
                //string color;
                //if (c == 0)
                //{
                //    color = "rgba(214, 134, 232, 1)";
                //}
                //else if (c == 1)
                //{
                //    color = "rgba(214, 134, 232, 0.6)";
                //}
                //else
                //{
                //    color = "rgba(214, 134, 232, 0.4)";
                //}
                //string message = $"轴卡：{Math.Round((double)encoderValue)}，采集卡：{Math.Round(ai_0_avg)}, {Math.Round(ai_0_avg)} 方向：{dir}";
                //string htmlMessage = $"<span style=\"color: {color};\">{message}</span>";
                Application.Current.Dispatcher.Invoke((Action)(() =>
                {
                    _VM.AddLog($"轴卡：{Math.Round((double)encoderValue)}，方向：{dir}\n" +
                        $"采集卡：{Value1},{Value7} ", "Info");
                }));
                // 控制循环速率，类似于 Python 中的 time.sleep(0.333)
                System.Threading.Thread.Sleep(500);
            }
        }
        public void ni_he()
        {
            int i = 0;
            List<double> AI_0 = new List<double>();
            List<double> AI_1 = new List<double>();
            List<double> AI_2 = new List<double>();
            List<double> AI_3 = new List<double>();
            List<double> AI_4 = new List<double>();
            List<double> AI_5 = new List<double>();
            List<double> AI_6 = new List<double>();
            List<double> axis_data = new List<double>();
            try
            {
                int err = 0;
                MPC08E.fast_pmove(axis, circle_pulses);
                // 数据采集
                en = _VM.Para.EN;
                // 创建一个缓冲区来存储数据
                ushort[] bufferArray = new ushort[read_count];
                short r;
                double angle;
                long encoderValue = -1;
                int result;
                ushort Value1 = 0;
                ushort Value2 = 0;
                ushort Value3 = 0;
                ushort Value4 = 0;
                ushort Value5 = 0;
                ushort Value6 = 0;
                ushort Value7 = 0;
                //en = false;
                while (en)
                {
                    if (MPC08E.check_done(axis) == 0)
                    {
                        break;
                    }
                    i++;
                    cjk_9114.AI_ReadChannel(card_number, 0, ad_range, ref Value1);
                    cjk_9114.AI_ReadChannel(card_number, 1, ad_range, ref Value2);
                    cjk_9114.AI_ReadChannel(card_number, 2, ad_range, ref Value3);
                    cjk_9114.AI_ReadChannel(card_number, 3, ad_range, ref Value4);
                    cjk_9114.AI_ReadChannel(card_number, 4, ad_range, ref Value5);
                    cjk_9114.AI_ReadChannel(card_number, 5, ad_range, ref Value6);
                    cjk_9114.AI_ReadChannel(card_number, 5, ad_range, ref Value7);
                    // 获取编码器值
                    result = MPC08E.get_encoder(axis, ref encoderValue);
                    AI_0.Add((double)Value1);
                    AI_1.Add((double)Value2);
                    AI_2.Add((double)Value3);
                    AI_3.Add((double)Value4);
                    AI_4.Add((double)Value5);
                    AI_5.Add((double)Value6);
                    AI_6.Add((double)Value7);
                    angle = ((encoderValue % num_pulses) * 360 / num_pulses);
                    axis_data.Add(angle);
                }
            }
            catch (Exception ex)
            {
                Application.Current.Dispatcher.Invoke((Action)(() =>
                {
                    _VM.AddLog($"get_ai异常发生: {ex.Message}", "Error");
                }));
            }
            if (AI_0.Count <= 500)
            {
                Application.Current.Dispatcher.Invoke((Action)(() =>
                {
                    _VM.AddLog($"采集的数据不足，{AI_0.Count} ", "Error");
                }));
                return;
            }
            Application.Current.Dispatcher.Invoke((Action)(() =>
            {
                _VM.AddLog($"数据采集完成:{AI_0.Count}", "Info");
            }));
            double[] axisDataArray = axis_data.ToArray();
            double[] AI_0_DataArray = AI_0.ToArray();
            double[] AI_1_DataArray = AI_1.ToArray();
            double[] AI_2_DataArray = AI_2.ToArray();
            double[] AI_3_DataArray = AI_3.ToArray();
            double[] AI_4_DataArray = AI_4.ToArray();
            double[] AI_5_DataArray = AI_5.ToArray();
            double[] AI_6_DataArray = AI_6.ToArray();
            AI_0_DataArray = Filter.MedianFilter(AI_0_DataArray);
            AI_1_DataArray = Filter.MedianFilter(AI_1_DataArray);
            AI_2_DataArray = Filter.MedianFilter(AI_2_DataArray);
            AI_3_DataArray = Filter.MedianFilter(AI_3_DataArray);
            AI_4_DataArray = Filter.MedianFilter(AI_4_DataArray);
            AI_5_DataArray = Filter.MedianFilter(AI_5_DataArray);
            AI_6_DataArray = Filter.MedianFilter(AI_6_DataArray);
            CircleResult SS1 = Circle_EC.GetCircle(AI_0_DataArray, axisDataArray);
            CircleResult SS2 = Circle_EC.GetCircle(AI_1_DataArray, axisDataArray);
            CircleResult SS3 = Circle_EC.GetCircle(AI_2_DataArray, axisDataArray);
            CircleResult SS4 = Circle_EC.GetCircle(AI_3_DataArray, axisDataArray);
            CircleResult SS5 = Circle_EC.GetCircle(AI_4_DataArray, axisDataArray);
            CircleResult SS6 = Circle_EC.GetCircle(AI_5_DataArray, axisDataArray);
            CircleResult SS7 = Circle_EC.GetCircle(AI_6_DataArray, axisDataArray);
            double mo1 = Math.Round(Math.Sqrt(SS1.X * SS1.X + SS1.Y * SS1.Y), 2);
            double mo2 = Math.Round(Math.Sqrt(SS2.X * SS2.X + SS2.Y * SS2.Y), 2);
            double mo3 = Math.Round(Math.Sqrt(SS3.X * SS3.X + SS3.Y * SS3.Y), 2);
            double mo4 = Math.Round(Math.Sqrt(SS4.X * SS4.X + SS4.Y * SS4.Y), 2);
            double mo5 = Math.Round(Math.Sqrt(SS5.X * SS5.X + SS5.Y * SS5.Y), 2);
            double mo6 = Math.Round(Math.Sqrt(SS6.X * SS6.X + SS6.Y * SS6.Y), 2);
            double mo7 = Math.Round(Math.Sqrt(SS7.X * SS7.X + SS7.Y * SS7.Y), 2);
            double xj1 = -90 - Math.Round(Math.Atan2(SS1.Y, SS1.X) * 180 / Math.PI, 2);
            double xj2 = -90 - Math.Round(Math.Atan2(SS2.Y, SS2.X) * 180 / Math.PI, 2);
            double xj3 = -90 - Math.Round(Math.Atan2(SS3.Y, SS3.X) * 180 / Math.PI, 2);
            double xj4 = -90 - Math.Round(Math.Atan2(SS4.Y, SS4.X) * 180 / Math.PI, 2);
            double xj5 = -90 - Math.Round(Math.Atan2(SS5.Y, SS5.X) * 180 / Math.PI, 2);
            double xj6 = -90 - Math.Round(Math.Atan2(SS6.Y, SS6.X) * 180 / Math.PI, 2);
            double xj7 = -90 - Math.Round(Math.Atan2(SS7.Y, SS7.X) * 180 / Math.PI, 2);
            Application.Current.Dispatcher.Invoke((Action)(() =>
            {
                _VM.AddLog($"1号传感器：：拟合圆圆心: ({SS1.X}, {SS1.Y}), 半径: {SS1.Z}", "Info");
                _VM.AddLog($"2号传感器：：拟合圆圆心: ({SS2.X}, {SS2.Y}), 半径: {SS2.Z}", "Info");
                _VM.AddLog($"3号传感器：：拟合圆圆心: ({SS3.X}, {SS3.Y}), 半径: {SS3.Z}", "Info");
                _VM.AddLog($"4号传感器：：拟合圆圆心: ({SS4.X}, {SS4.Y}), 半径: {SS4.Z}", "Info");
                _VM.AddLog($"5号传感器：：拟合圆圆心: ({SS5.X}, {SS5.Y}), 半径: {SS5.Z}", "Info");
                _VM.AddLog($"6号传感器：：拟合圆圆心: ({SS6.X}, {SS6.Y}), 半径: {SS6.Z}", "Info");
                _VM.AddLog($"7号传感器：：拟合圆圆心: ({SS7.X}, {SS7.Y}), 半径: {SS7.Z}", "Info");
                _VM.Para.Angle1 = xj1;
                _VM.Para.Angle2 = xj2;
                _VM.Para.Angle3 = xj3;
                _VM.Para.Angle4 = xj4;
                _VM.Para.Angle5 = xj5;
                _VM.Para.Angle6 = xj6;
                _VM.Para.Angle7 = xj7;
                _VM.Para.BarChartValues = new List<double> { mo1, mo2, mo3, mo4, mo5, mo6, mo7 };
            }));
            //测试专用
            //double[] center = new double[] { -465, 56 };
            //int num = 10000;
            //double radius = 10;
            //double n = 0.1;
            //CirclePointsResult circlePoints = Circle_EC.GenerateCirclePoints(num, center, radius, n);
            //circlePoints.R = Filter.MedianFilter(circlePoints.R);
            //CircleResult SS1 = Circle_EC.GetCircle(circlePoints.R, circlePoints.Theta);
            //Application.Current.Dispatcher.Invoke((Action)(() =>
            //{
            //    _VM.AddLog($"Fitted Circle Center: ({SS1.X}, {SS1.Y}), Radius: {SS1.Z}", "Info");
            //    _VM.Para.Angle1 = -90 - Math.Round(Math.Atan2(SS1.Y, SS1.X) * 180 / Math.PI, 2);
            //    _VM.Para.Angle2 = -90 - Math.Round(Math.Atan2(SS1.Y, SS1.X) * 180 / Math.PI, 2);
            //    _VM.Para.Angle3 = -90 - Math.Round(Math.Atan2(SS1.Y, SS1.X) * 180 / Math.PI, 2);
            //    _VM.Para.Angle4 = -90 - Math.Round(Math.Atan2(SS1.Y, SS1.X) * 180 / Math.PI, 2);
            //    _VM.Para.Angle5 = -90 - Math.Round(Math.Atan2(SS1.Y, SS1.X) * 180 / Math.PI, 2);
            //    _VM.Para.Angle6 = -90 - Math.Round(Math.Atan2(SS1.Y, SS1.X) * 180 / Math.PI, 2);
            //    _VM.Para.Angle7 = -90 - Math.Round(Math.Atan2(SS1.Y, SS1.X) * 180 / Math.PI, 2);
            //    _VM.Para.BarChartValues = new List<double> { Math.Round(Math.Sqrt(SS1.X * SS1.X + SS1.Y * SS1.Y), 2),
            //        Math.Round(Math.Sqrt(SS1.X * SS1.X + SS1.Y * SS1.Y), 2),
            //        Math.Round(Math.Sqrt(SS1.X * SS1.X + SS1.Y * SS1.Y), 2),
            //        Math.Round(Math.Sqrt(SS1.X * SS1.X + SS1.Y * SS1.Y), 2),
            //        Math.Round(Math.Sqrt(SS1.X * SS1.X + SS1.Y * SS1.Y), 2),
            //        Math.Round(Math.Sqrt(SS1.X * SS1.X + SS1.Y * SS1.Y), 2),
            //        Math.Round(Math.Sqrt(SS1.X * SS1.X + SS1.Y * SS1.Y), 2)};
            //}));
        }
    }
}
