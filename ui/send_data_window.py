from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QTextEdit, QPushButton, QLabel, QLineEdit, QCheckBox,
                             QSpinBox, QFrame, QGroupBox, QMessageBox)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QTextCursor


class SendDataWindow(QMainWindow):
    """发送数据窗口"""
    
    # 定义信号
    send_data_signal = pyqtSignal(str, str, bool, bool, int)  # 发送数据信号
    
    def __init__(self, port_name, parent=None):
        super().__init__(parent)
        self.port_name = port_name
        self.auto_send_timer = None
        self.init_ui()
        
    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle(f"串口 {self.port_name} - 发送数据")
        self.setGeometry(300, 300, 700, 500)
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # 标题区域
        title_label = QLabel(f"串口 {self.port_name} 发送数据")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #333333;
                background-color: transparent;
                border: none;
            }
        """)
        layout.addWidget(title_label)
        
        # 数据输入区域
        input_frame = QFrame()
        input_frame.setStyleSheet("""
            QFrame {
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                background-color: #f8f9fa;
            }
        """)
        
        input_layout = QVBoxLayout(input_frame)
        input_layout.setContentsMargins(15, 15, 15, 15)
        
        # 数据标签
        data_label = QLabel("发送数据:")
        data_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: #333333;
                background-color: transparent;
                border: none;
                margin-bottom: 10px;
            }
        """)
        input_layout.addWidget(data_label)
        
        # 文本输入区域
        self.text_input = QTextEdit()
        self.text_input.setStyleSheet("""
            QTextEdit {
                border: 1px solid #d0d0d0;
                border-radius: 6px;
                background-color: white;
                font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
                font-size: 12px;
                padding: 10px;
                color: #333333;
            }
        """)
        self.text_input.setMinimumHeight(200)
        self.text_input.setPlaceholderText("请输入要发送的数据...")
        input_layout.addWidget(self.text_input)
        
        layout.addWidget(input_frame)
        
        # 发送选项区域
        options_frame = QFrame()
        options_frame.setStyleSheet("""
            QFrame {
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                background-color: #f8f9fa;
            }
        """)
        
        options_layout = QVBoxLayout(options_frame)
        options_layout.setContentsMargins(15, 15, 15, 15)
        
        # 选项标签
        options_label = QLabel("发送选项:")
        options_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: #333333;
                background-color: transparent;
                border: none;
                margin-bottom: 10px;
            }
        """)
        options_layout.addWidget(options_label)
        
        # 选项布局
        options_grid = QHBoxLayout()
        
        # 十六进制发送选项
        self.hex_send_check = QCheckBox("十六进制发送")
        self.hex_send_check.setStyleSheet("""
            QCheckBox {
                font-size: 12px;
                color: #333333;
                background-color: transparent;
                border: none;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
            }
        """)
        options_grid.addWidget(self.hex_send_check)
        
        # 自动发送选项
        self.auto_send_check = QCheckBox("自动发送")
        self.auto_send_check.setStyleSheet("""
            QCheckBox {
                font-size: 12px;
                color: #333333;
                background-color: transparent;
                border: none;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
            }
        """)
        self.auto_send_check.toggled.connect(self.toggle_auto_send)
        options_grid.addWidget(self.auto_send_check)
        
        # 自动发送间隔
        interval_label = QLabel("间隔(ms):")
        interval_label.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: #333333;
                background-color: transparent;
                border: none;
            }
        """)
        options_grid.addWidget(interval_label)
        
        self.interval_spin = QSpinBox()
        self.interval_spin.setRange(100, 10000)
        self.interval_spin.setValue(1000)
        self.interval_spin.setSuffix(" ms")
        self.interval_spin.setStyleSheet("""
            QSpinBox {
                border: 1px solid #d0d0d0;
                border-radius: 4px;
                padding: 4px 8px;
                background-color: white;
                font-size: 12px;
                min-width: 80px;
            }
        """)
        options_grid.addWidget(self.interval_spin)
        
        options_grid.addStretch()
        options_layout.addLayout(options_grid)
        
        layout.addWidget(options_frame)
        
        # 控制按钮区域
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        # 发送按钮
        self.send_btn = QPushButton("发送")
        self.send_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #1e7e34;
            }
            QPushButton:pressed {
                background-color: #155724;
            }
        """)
        self.send_btn.clicked.connect(self.send_data)
        button_layout.addWidget(self.send_btn)
        
        # 停止自动发送按钮
        self.stop_btn = QPushButton("停止自动发送")
        self.stop_btn.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
            QPushButton:pressed {
                background-color: #bd2130;
            }
        """)
        self.stop_btn.clicked.connect(self.stop_auto_send)
        self.stop_btn.setEnabled(False)
        button_layout.addWidget(self.stop_btn)
        
        button_layout.addStretch()
        
        # 清空按钮
        self.clear_btn = QPushButton("清空")
        self.clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
            QPushButton:pressed {
                background-color: #545b62;
            }
        """)
        self.clear_btn.clicked.connect(self.clear_data)
        button_layout.addWidget(self.clear_btn)
        
        layout.addLayout(button_layout)
        
        # 初始化自动发送定时器
        self.auto_send_timer = QTimer()
        self.auto_send_timer.timeout.connect(self.auto_send_data)
        self.is_auto_sending = False
        
    def send_data(self):
        """发送数据"""
        data = self.text_input.toPlainText().strip()
        if not data:
            QMessageBox.warning(self, "警告", "请输入要发送的数据")
            return
            
        hex_mode = self.hex_send_check.isChecked()
        auto_mode = self.auto_send_check.isChecked()
        interval = self.interval_spin.value()
        
        self.send_data_signal.emit(self.port_name, data, hex_mode, auto_mode, interval)
        
        if auto_mode:
            # 开始自动发送
            self.start_auto_send()
        else:
            QMessageBox.information(self, "提示", "数据已发送")
    
    def toggle_auto_send(self, checked):
        """切换自动发送"""
        if checked:
            self.interval_spin.setEnabled(True)
        else:
            self.interval_spin.setEnabled(False)
            self.stop_auto_send()
    
    def auto_send_data(self):
        """自动发送数据"""
        if self.is_auto_sending:
            self.send_data()
    
    def start_auto_send(self):
        """开始自动发送"""
        if not self.is_auto_sending:
            interval = self.interval_spin.value()
            self.auto_send_timer.start(interval)
            self.is_auto_sending = True
            self.stop_btn.setEnabled(True)
            self.send_btn.setEnabled(False)
    
    def stop_auto_send(self):
        """停止自动发送"""
        if self.is_auto_sending:
            self.auto_send_timer.stop()
            self.is_auto_sending = False
            self.stop_btn.setEnabled(False)
            self.send_btn.setEnabled(True)
            
            # 通知主程序停止自动发送
            self.send_data_signal.emit(self.port_name, "", False, False, 1000)
    
    def update_auto_send_status(self, is_auto_sending):
        """更新自动发送状态（由外部调用）"""
        self.is_auto_sending = is_auto_sending
        self.stop_btn.setEnabled(is_auto_sending)
        self.send_btn.setEnabled(not is_auto_sending)
    
    def clear_data(self):
        """清空数据"""
        self.text_input.clear()
    
    def get_data(self):
        """获取当前数据"""
        return self.text_input.toPlainText()
    
    def set_data(self, data):
        """设置数据"""
        self.text_input.setPlainText(data)
    
    def closeEvent(self, event):
        """窗口关闭事件"""
        self.stop_auto_send()
        event.accept() 