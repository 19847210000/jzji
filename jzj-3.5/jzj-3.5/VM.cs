using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.ComponentModel;
using System.Linq;
using System.Text;

namespace jzj_3._5
{
    public class MainWindowViewModel : INotifyPropertyChanged
    {
        private Para _para;
        public Para Para
        {
            get
            {
                return _para;
            }
            set
            {
                _para = value;
                OnPropertyChanged(nameof(Para));
            }
        }
        public ObservableCollection<LogEntry> LogEntries { get; set; }
        public MainWindowViewModel()
        {
            LogEntries = new ObservableCollection<LogEntry>();
            _para = new Para();  // 假设 Para 是一个类类型，需要显式实例化
            _para.BarChartValues = new List<double> { 0, 0, 0, 0, 0, 0, 0 };
        }

        // 清空日志
        public void ClearLogs()
        {
            LogEntries.Clear();
        }

        public event Action ScrollToBottomRequested;

        public void AddLog(string message, string logLevel)
        {
            // 如果日志数量超过限制，移除最旧的一条
            if (LogEntries.Count >= 100)
            {
                LogEntries.RemoveAt(0); // 删除最旧的一条
            }

            // 添加新日志
            LogEntries.Add(new LogEntry
            {
                Message = message,
                LogLevel = logLevel,
                Timestamp = DateTime.Now
            });

            // 触发滚动到最底部的事件
            ScrollToBottomRequested?.Invoke();
        }

        // INotifyPropertyChanged 实现
        public event PropertyChangedEventHandler PropertyChanged;

        protected virtual void OnPropertyChanged(string propertyName)
        {
            PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(propertyName));
        }
    }
}
