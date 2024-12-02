using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Linq;
using System.Text;

namespace jzj_3._5
{
    public class Para : INotifyPropertyChanged
    {
        public event PropertyChangedEventHandler PropertyChanged;
        protected virtual void OnPropertyChanged(string propertyName)
        {
            PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(propertyName));
        }
        private string _ip;
        public string IP
        {
            get { return _ip; }
            set
            {
                if (_ip != value)  // 确保值有变化
                {
                    _ip = value;
                    OnPropertyChanged(nameof(IP));  // 触发 PropertyChanged 事件
                }
            }
        }
        // Param1 属性
        private string _Num_mc;
        public string Num_mc
        {
            get { return _Num_mc; }
            set
            {
                if (_Num_mc != value)  // 确保值有变化
                {
                    _Num_mc = value;
                    OnPropertyChanged(nameof(Num_mc));  // 触发 PropertyChanged 事件
                }
            }
        }

        private string _Compensation1;
        public string Compensation1
        {
            get { return _Compensation1; }
            set
            {
                if (_Compensation1 != value)  // 确保值有变化
                {
                    _Compensation1 = value;
                    OnPropertyChanged(nameof(Compensation1));  // 触发 PropertyChanged 事件
                }
            }
        }
        private string _Compensation2;
        public string Compensation2
        {
            get { return _Compensation2; }
            set
            {
                if (_Compensation2 != value)  // 确保值有变化
                {
                    _Compensation2 = value;
                    OnPropertyChanged(nameof(Compensation2));  // 触发 PropertyChanged 事件
                }
            }
        }
        private string _Compensation3;
        public string Compensation3
        {
            get { return _Compensation3; }
            set
            {
                if (_Compensation3 != value)  // 确保值有变化
                {
                    _Compensation3 = value;
                    OnPropertyChanged(nameof(Compensation3));  // 触发 PropertyChanged 事件
                }
            }
        }
        private string _Compensation4;
        public string Compensation4
        {
            get { return _Compensation4; }
            set
            {
                if (_Compensation4 != value)  // 确保值有变化
                {
                    _Compensation4 = value;
                    OnPropertyChanged(nameof(Compensation4));  // 触发 PropertyChanged 事件
                }
            }
        }
        private string _Compensation5;
        public string Compensation5
        {
            get { return _Compensation5; }
            set
            {
                if (_Compensation5 != value)  // 确保值有变化
                {
                    _Compensation5 = value;
                    OnPropertyChanged(nameof(Compensation5));  // 触发 PropertyChanged 事件
                }
            }
        }
        private string _Compensation6;
        public string Compensation6
        {
            get { return _Compensation6; }
            set
            {
                if (_Compensation6 != value)  // 确保值有变化
                {
                    _Compensation6 = value;
                    OnPropertyChanged(nameof(Compensation6));  // 触发 PropertyChanged 事件
                }
            }
        }
        private string _Compensation7;
        public string Compensation7
        {
            get { return _Compensation7; }
            set
            {
                if (_Compensation7 != value)  // 确保值有变化
                {
                    _Compensation7 = value;
                    OnPropertyChanged(nameof(Compensation7));  // 触发 PropertyChanged 事件
                }
            }
        }
        private string _Press1;
        public string Press1
        {
            get { return _Press1; }
            set
            {
                if (_Press1 != value)  // 确保值有变化
                {
                    _Press1 = value;
                    OnPropertyChanged(nameof(Press1));  // 触发 PropertyChanged 事件
                }
            }
        }
        private string _Press2;
        public string Press2
        {
            get { return _Press2; }
            set
            {
                if (_Press2 != value)  // 确保值有变化
                {
                    _Press2 = value;
                    OnPropertyChanged(nameof(Press2));  // 触发 PropertyChanged 事件
                }
            }
        }
        private string _Press3;
        public string Press3
        {
            get { return _Press3; }
            set
            {
                if (_Press3 != value)  // 确保值有变化
                {
                    _Press3 = value;
                    OnPropertyChanged(nameof(Press3));  // 触发 PropertyChanged 事件
                }
            }
        }
        private string _Press4;
        public string Press4
        {
            get { return _Press4; }
            set
            {
                if (_Press4 != value)  // 确保值有变化
                {
                    _Press4 = value;
                    OnPropertyChanged(nameof(Press4));  // 触发 PropertyChanged 事件
                }
            }
        }
        private string _Press5;
        public string Press5
        {
            get { return _Press5; }
            set
            {
                if (_Press5 != value)  // 确保值有变化
                {
                    _Press5 = value;
                    OnPropertyChanged(nameof(Press5));  // 触发 PropertyChanged 事件
                }
            }
        }
        private string _Press6;
        public string Press6
        {
            get { return _Press6; }
            set
            {
                if (_Press6 != value)  // 确保值有变化
                {
                    _Press6 = value;
                    OnPropertyChanged(nameof(Press6));  // 触发 PropertyChanged 事件
                }
            }
        }
        private string _Press7;
        public string Press7
        {
            get { return _Press7; }
            set
            {
                if (_Press7 != value)  // 确保值有变化
                {
                    _Press7 = value;
                    OnPropertyChanged(nameof(Press7));  // 触发 PropertyChanged 事件
                }
            }
        }
        private string _Add1;
        public string Add1
        {
            get { return _Add1; }
            set
            {
                if (_Add1 != value)  // 确保值有变化
                {
                    _Add1 = value;
                    OnPropertyChanged(nameof(Add1));  // 触发 PropertyChanged 事件
                }
            }
        }
        private string _Add2;
        public string Add2
        {
            get { return _Add2; }
            set
            {
                if (_Add2 != value)  // 确保值有变化
                {
                    _Add2 = value;
                    OnPropertyChanged(nameof(Add2));  // 触发 PropertyChanged 事件
                }
            }
        }
        private string _Add3;
        public string Add3
        {
            get { return _Add3; }
            set
            {
                if (_Add3 != value)  // 确保值有变化
                {
                    _Add3 = value;
                    OnPropertyChanged(nameof(Add3));  // 触发 PropertyChanged 事件
                }
            }
        }
        private string _Add4;
        public string Add4
        {
            get { return _Add4; }
            set
            {
                if (_Add4 != value)  // 确保值有变化
                {
                    _Add4 = value;
                    OnPropertyChanged(nameof(Add4));  // 触发 PropertyChanged 事件
                }
            }
        }
        private string _Add5;
        public string Add5
        {
            get { return _Add5; }
            set
            {
                if (_Add5 != value)  // 确保值有变化
                {
                    _Add5 = value;
                    OnPropertyChanged(nameof(Add5));  // 触发 PropertyChanged 事件
                }
            }
        }
        private string _Max_num;
        public string Max_num
        {
            get { return _Max_num; }
            set
            {
                if (_Max_num != value)  // 确保值有变化
                {
                    _Max_num = value;
                    OnPropertyChanged(nameof(Max_num));  // 触发 PropertyChanged 事件
                }
            }
        }
        private string _Direct_P1;
        public string Direct_P1
        {
            get { return _Direct_P1; }
            set
            {
                if (_Direct_P1 != value)  // 确保值有变化
                {
                    _Direct_P1 = value;
                    OnPropertyChanged(nameof(Direct_P1));  // 触发 PropertyChanged 事件
                }
            }
        }
        private bool _EN;
        public bool EN
        {
            get { return _EN; }
            set
            {
                if (_EN != value)  // 确保值有变化
                {
                    _EN = value;
                    OnPropertyChanged(nameof(EN));  // 触发 PropertyChanged 事件
                }
            }
        }
        private double _angle1;
        public double Angle1
        {
            get { return _angle1; }
            set
            {
                if (_angle1 != value)
                {
                    _angle1 = value;
                    OnPropertyChanged(nameof(Angle1));
                }
            }
        }
        private double _angle2;
        public double Angle2
        {
            get { return _angle2; }
            set
            {
                if (_angle2 != value)
                {
                    _angle2 = value;
                    OnPropertyChanged(nameof(Angle2));
                }
            }
        }
        private double _angle3;
        public double Angle3
        {
            get { return _angle3; }
            set
            {
                if (_angle3 != value)
                {
                    _angle3 = value;
                    OnPropertyChanged(nameof(Angle3));
                }
            }
        }
        private double _angle4;
        public double Angle4
        {
            get { return _angle4; }
            set
            {
                if (_angle4 != value)
                {
                    _angle4 = value;
                    OnPropertyChanged(nameof(Angle4));
                }
            }
        }
        private double _angle5;
        public double Angle5
        {
            get { return _angle5; }
            set
            {
                if (_angle5 != value)
                {
                    _angle5 = value;
                    OnPropertyChanged(nameof(Angle5));
                }
            }
        }
        private double _angle6;
        public double Angle6
        {
            get { return _angle6; }
            set
            {
                if (_angle6 != value)
                {
                    _angle6 = value;
                    OnPropertyChanged(nameof(Angle6));
                }
            }
        }
        private double _angle7;
        public double Angle7
        {
            get { return _angle7; }
            set
            {
                if (_angle7 != value)
                {
                    _angle7 = value;
                    OnPropertyChanged(nameof(Angle7));
                }
            }
        }
        private List<double> _barChartValues;
        public List<double> BarChartValues
        {
            get => _barChartValues;
            set
            {
                if (_barChartValues != value)
                {
                    _barChartValues = value;
                    OnPropertyChanged(nameof(BarChartValues));
                }
            }
        }
    }
}
