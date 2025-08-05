from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, 
                             QLabel, QPushButton, QTextEdit, QLineEdit, 
                             QSpinBox, QCheckBox, QSplitter, QFrame)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QTextCursor


class DataPage(QWidget):
    """数据收发页面"""
    
    # 定义信号
    send_data_signal = pyqtSignal(str)  # 发送数据信号
    clear_signal = pyqtSignal()         # 清空信号
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        """初始化UI界面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # 页面标题
        title = QLabel("数据收发")
        title.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 20px;")
        layout.addWidget(title)
        
        # 创建分割器
        splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(splitter)
        
        # 左侧发送控制
        send_panel = self.create_send_panel()
        splitter.addWidget(send_panel)
        
        # 右侧接收显示
        receive_panel = self.create_receive_panel()
        splitter.addWidget(receive_panel)
        
        # 设置分割器比例
        splitter.setSizes([500, 800])
    
    def create_send_panel(self):
        """创建发送控制面板"""
        panel = QFrame()
        panel.setFrameStyle(QFrame.Shape.StyledPanel)
        layout = QVBoxLayout(panel)
        
        # 发送控制组
        send_group = QGroupBox("发送控制")
        send_layout = QVBoxLayout(send_group)
        
        # 发送数据输入框
        self.send_input = QLineEdit()
        self.send_input.setPlaceholderText("输入要发送的数据")
        self.send_input.returnPressed.connect(self.send_data)
        send_layout.addWidget(self.send_input)
        
        # 发送按钮
        self.send_btn = QPushButton("发送")
        self.send_btn.clicked.connect(self.send_data)
        self.send_btn.setEnabled(False)
        self.send_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 6px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        send_layout.addWidget(self.send_btn)
        
        # 发送选项
        send_options_layout = QHBoxLayout()
        self.hex_send_check = QCheckBox("十六进制发送")
        self.auto_send_check = QCheckBox("自动发送")
        send_options_layout.addWidget(self.hex_send_check)
        send_options_layout.addWidget(self.auto_send_check)
        send_layout.addLayout(send_options_layout)
        
        # 自动发送间隔
        auto_send_layout = QHBoxLayout()
        auto_send_layout.addWidget(QLabel("间隔(ms):"))
        self.auto_send_interval = QSpinBox()
        self.auto_send_interval.setRange(100, 10000)
        self.auto_send_interval.setValue(1000)
        auto_send_layout.addWidget(self.auto_send_interval)
        send_layout.addLayout(auto_send_layout)
        
        layout.addWidget(send_group)
        layout.addStretch()
        
        return panel
    
    def create_receive_panel(self):
        """创建接收显示面板"""
        panel = QFrame()
        panel.setFrameStyle(QFrame.Shape.StyledPanel)
        layout = QVBoxLayout(panel)
        
        # 数据显示组
        data_group = QGroupBox("接收数据")
        data_layout = QVBoxLayout(data_group)
        
        # 接收数据显示
        self.receive_text = QTextEdit()
        self.receive_text.setFont(QFont("Consolas", 12))
        self.receive_text.setReadOnly(True)
        data_layout.addWidget(self.receive_text)
        
        # 接收控制按钮
        receive_control_layout = QHBoxLayout()
        self.clear_receive_btn = QPushButton("清空接收")
        self.clear_receive_btn.clicked.connect(self.clear_receive)
        self.clear_receive_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF9800;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #F57C00;
            }
        """)
        receive_control_layout.addWidget(self.clear_receive_btn)
        
        self.hex_display_check = QCheckBox("十六进制显示")
        receive_control_layout.addWidget(self.hex_display_check)
        
        self.auto_scroll_check = QCheckBox("自动滚动")
        self.auto_scroll_check.setChecked(True)
        receive_control_layout.addWidget(self.auto_scroll_check)
        
        receive_control_layout.addStretch()
        data_layout.addLayout(receive_control_layout)
        
        layout.addWidget(data_group)
        
        # 统计信息
        stats_layout = QHBoxLayout()
        self.receive_count_label = QLabel("接收: 0 字节")
        self.send_count_label = QLabel("发送: 0 字节")
        stats_layout.addWidget(self.receive_count_label)
        stats_layout.addWidget(self.send_count_label)
        stats_layout.addStretch()
        layout.addLayout(stats_layout)
        
        return panel
    
    def send_data(self):
        """发送数据"""
        data = self.send_input.text()
        if data:
            self.send_data_signal.emit(data)
            self.send_input.clear()
    
    def clear_receive(self):
        """清空接收数据"""
        self.receive_text.clear()
        self.clear_signal.emit()
    
    def update_connection_status(self, connected):
        """更新连接状态"""
        self.send_btn.setEnabled(connected)
    
    def append_receive_data(self, data):
        """添加接收数据到显示区域"""
        cursor = self.receive_text.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.receive_text.setTextCursor(cursor)
        self.receive_text.insertPlainText(data)
        
        if self.auto_scroll_check.isChecked():
            self.receive_text.ensureCursorVisible()
    
    def update_statistics(self, receive_count, send_count):
        """更新统计信息"""
        self.receive_count_label.setText(f"接收: {receive_count} 字节")
        self.send_count_label.setText(f"发送: {send_count} 字节")
    
    def is_hex_send(self):
        """是否十六进制发送"""
        return self.hex_send_check.isChecked()
    
    def is_auto_send(self):
        """是否自动发送"""
        return self.auto_send_check.isChecked()
    
    def get_auto_send_interval(self):
        """获取自动发送间隔"""
        return self.auto_send_interval.value()
    
    def is_hex_display(self):
        """是否十六进制显示"""
        return self.hex_display_check.isChecked() 