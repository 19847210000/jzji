这是我的一个小项目，配合PLC与机械结构进行通讯，通过旋转一周采集散点进行拟合计算，实现检测一个轴体（圆轴或方轴）的中心偏移量的角度和方向。

目前正在着手准备下一步的下压量计算和整个工程的闭环逻辑设计，重心放在python平台，是否后期会跟进C#+WPF部分，作者在此不做保证

jzj3.5文件内的是软件的部分实现，在dotnet3.5上进行的，该部分内容还不完整，但是可以在你的电脑上直接运行，只需要在Windows操作系统上安装.NET3.5之后。

相关conda环境还没有打包，因为我是在我之前的深度学习pytorch环境上直接进行的，主要使用的环境也就是PyQt5，主要使用的一些环境版本简单放一下，后期是否会回来填坑也不好说。


![1733099220385](https://github.com/user-attachments/assets/06e19d09-f004-4d67-9886-32a903633e95)


这个项目能干哈？

可以为你提供一个简单的PYQT、WDF界面，并在这个基础上可以修改为你的专属界面，在这个项目中有多种UI实现，

包括button和鼠标事件的绑定、日志的不同颜色输出、子窗口的创建和管理、多种布局的嵌套、单选按钮的创建和管理、输入框的非数字输入限制、信号与槽的应用 and so on。
