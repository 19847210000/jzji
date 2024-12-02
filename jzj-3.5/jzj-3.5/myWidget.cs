using System;
using System.Collections.Generic;
using System.Globalization;
using System.Linq;
using System.Text;
using System.Windows.Controls;
using System.Windows.Data;
using System.Windows.Media;
using System.Windows;

namespace jzj_3._5
{
    public class CircleWidget : Control
    {
        // 依赖属性 - 用于角度
        public static readonly DependencyProperty AngleProperty =
            DependencyProperty.Register("Angle", typeof(double), typeof(CircleWidget),
            new FrameworkPropertyMetadata(0.0, FrameworkPropertyMetadataOptions.AffectsRender));

        // 公共属性 - 角度
        public double Angle
        {
            get => (double)GetValue(AngleProperty);
            set => SetValue(AngleProperty, value);
        }

        static CircleWidget()
        {
            // 注册默认样式
            DefaultStyleKeyProperty.OverrideMetadata(typeof(CircleWidget), new FrameworkPropertyMetadata(typeof(CircleWidget)));
        }

        // 重写 OnRender 方法来绘制控件
        protected override void OnRender(DrawingContext drawingContext)
        {
            base.OnRender(drawingContext);

            // 计算圆心和半径
            double centerX = ActualWidth / 2;
            double centerY = ActualHeight / 2;
            double radius = 42;

            // 绘制圆
            drawingContext.DrawEllipse(new SolidColorBrush(Color.FromRgb(58, 128, 12)),
                new Pen(Brushes.Black, 3), new Point(centerX, centerY), radius, radius);

            // 计算半径线的终点坐标
            double endX = centerX + radius * Math.Cos(Math.PI * Angle / 180.0);
            double endY = centerY - radius * Math.Sin(Math.PI * Angle / 180.0);

            // 绘制半径线
            drawingContext.DrawLine(new Pen(Brushes.Red, 5), new Point(centerX, centerY), new Point(endX, endY));
        }
    }
    public class SqrtWidget : Control
    {
        // 角度属性
        public static readonly DependencyProperty AngleProperty =
            DependencyProperty.Register("Angle", typeof(double), typeof(SqrtWidget),
                new FrameworkPropertyMetadata(0.0, FrameworkPropertyMetadataOptions.AffectsRender));

        public double Angle
        {
            get => (double)GetValue(AngleProperty);
            set => SetValue(AngleProperty, value);
        }

        // 构造函数
        public SqrtWidget()
        {
            // 默认角度为 0
            Angle = 0;
            SizeChanged += (sender, args) => InvalidateVisual(); // 当大小改变时重新绘制
        }

        // 设置角度的方法
        public void SetAngle(double newAngle)
        {
            Angle = (360 + newAngle) % 360; // 角度归一化到 0-360 范围内
            InvalidateVisual(); // 重新绘制
        }

        // 重写 OnRender 方法来绘制图形
        protected override void OnRender(DrawingContext drawingContext)
        {
            base.OnRender(drawingContext);

            // 设置画笔
            Brush squareBrush = new SolidColorBrush(Color.FromRgb(128, 58, 12)); // 正方形颜色
            Pen blackPen = new Pen(Brushes.Black, 3); // 边框笔刷，宽度为7

            // 计算正方形的边长和左上角坐标
            double sideLength = 85;
            double topLeftX = (ActualWidth - sideLength) / 2;
            double topLeftY = (ActualHeight - sideLength) / 2;

            // 绘制正方形
            drawingContext.DrawRectangle(squareBrush, blackPen, new Rect(topLeftX, topLeftY, sideLength, sideLength));

            // 计算中心点坐标
            double centerX = topLeftX + sideLength / 2;
            double centerY = topLeftY + sideLength / 2;

            // 根据角度计算半径的终点坐标
            double endX = centerX;
            double endY = centerY;
            Angle = (360 + Angle) % 360; // 角度归一化到 0-360 范围内
            // 判断角度的范围并计算线的终点坐标
            if (315 <= Angle || Angle < 45)  // 向右
            {
                endX = topLeftX + sideLength;
                endY = centerY - sideLength / 2 * Math.Sin(Math.PI * Angle / 180);
            }
            else if (45 <= Angle && Angle < 135)  // 向上
            {
                endX = centerX + sideLength / 2 * Math.Cos(Math.PI * Angle / 180);
                endY = topLeftY;
            }
            else if (135 <= Angle && Angle < 225)  // 向左
            {
                endX = topLeftX;
                endY = centerY - sideLength / 2 * Math.Sin(Math.PI * Angle / 180);
            }
            else if (225 <= Angle && Angle < 315)  // 向下
            {
                endX = centerX + sideLength / 2 * Math.Cos(Math.PI * Angle / 180);
                endY = topLeftY + sideLength;
            }

            // 设置半径线的画笔颜色为绿色
            Pen greenPen = new Pen(Brushes.Green, 5); // 半径线的颜色和宽度

            // 绘制半径线
            drawingContext.DrawLine(greenPen, new Point(centerX, centerY), new Point(endX, endY));
        }
    }
    public class BarChartWidget : Control
    {
        // 构造函数
        public BarChartWidget()
        {
            SizeChanged += (sender, args) => InvalidateVisual(); // 当控件尺寸变化时重新绘制
        }

        // 获取柱状图的值
        public static readonly DependencyProperty ValuesProperty =
            DependencyProperty.Register("Values", typeof(List<double>), typeof(BarChartWidget),
                new FrameworkPropertyMetadata(new List<double>(), FrameworkPropertyMetadataOptions.AffectsRender));

        public List<double> Values
        {
            get => (List<double>)GetValue(ValuesProperty);
            set => SetValue(ValuesProperty, value);
        }

        // 获取最大Y轴值
        public static readonly DependencyProperty MaxValueProperty =
            DependencyProperty.Register("MaxValue", typeof(double), typeof(BarChartWidget),
                new FrameworkPropertyMetadata(5.0, FrameworkPropertyMetadataOptions.AffectsRender));

        public double MaxValue
        {
            get => (double)GetValue(MaxValueProperty);
            set => SetValue(MaxValueProperty, value);
        }

        // 获取最小Y轴值
        public static readonly DependencyProperty MinValueProperty =
            DependencyProperty.Register("MinValue", typeof(double), typeof(BarChartWidget),
                new FrameworkPropertyMetadata(0.0, FrameworkPropertyMetadataOptions.AffectsRender));

        public double MinValue
        {
            get => (double)GetValue(MinValueProperty);
            set => SetValue(MinValueProperty, value);
        }

        // 重写 OnRender 方法进行绘制
        protected override void OnRender(DrawingContext drawingContext)
        {
            base.OnRender(drawingContext);

            double barWidth = ActualWidth / Values.Count * 0.3; // 每个柱子的宽度
            double spacing = ActualWidth / Values.Count * 0.7; // 柱子之间的间距
            double scaleY = ActualHeight / (MaxValue - MinValue); // Y轴的缩放比例

            for (int i = 0; i < Values.Count; i++)
            {
                double value = Values[i];

                // 根据值设置柱子的颜色
                Brush barColor = value >= 2 ? Brushes.Red : Brushes.Green;

                // 计算柱子的位置和高度
                double barHeight = (value - MinValue) * scaleY;
                double x = i * (barWidth + spacing);
                double y = ActualHeight - barHeight;

                // 创建并绘制柱状图
                drawingContext.DrawRectangle(barColor, null, new Rect(x, y, barWidth, barHeight));

                // 绘制柱子上方的文本（当前值）
                FormattedText formattedText = new FormattedText(
                    value.ToString("0.##"),
                    CultureInfo.InvariantCulture,
                    FlowDirection.LeftToRight,
                    new Typeface("Arial"),
                    16, // 字体大小
                    Brushes.Black // 文本颜色
                );

                // 计算文本位置，放在柱子上方
                double textX = x + barWidth / 2 - formattedText.Width / 2;
                double textY = y - formattedText.Height - 5; // 文本距离柱子顶部一些距离

                // 绘制文本
                drawingContext.DrawText(formattedText, new Point(textX, textY));
            }

            // 绘制水平基准线
            //Pen linePen = new Pen(Brushes.Black, 1);
            //drawingContext.DrawLine(linePen, new Point(0, this.ActualHeight - (2 * scaleY)), new Point(this.ActualWidth, this.ActualHeight - (2 * scaleY)));
            //drawingContext.DrawLine(linePen, new Point(0, this.ActualHeight - (1 * scaleY)), new Point(this.ActualWidth, this.ActualHeight - (1 * scaleY)));
        }
    }
    public class LogEntry
    {
        public string Message { get; set; }
        public string LogLevel { get; set; } // 比如 "Info", "Warning", "Error"
        public DateTime Timestamp { get; set; }
    }
    public class LogLevelToColorConverter : IValueConverter
    {
        public object Convert(object value, Type targetType, object parameter, CultureInfo culture)
        {
            string logLevel = value as string;
            switch (logLevel)
            {
                case "Error":
                    return Brushes.Red;
                case "Warning":
                    return Brushes.Orange;
                case "Info":
                    return Brushes.Green;
                default:
                    return Brushes.Black;
            }
        }

        public object ConvertBack(object value, Type targetType, object parameter, CultureInfo culture)
        {
            throw new NotImplementedException();
        }
    }
}
