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
        
        # 显示简化内容
        content_label = QLabel("后续功能，可继续模块化开发")
        content_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                color: #333333;
                padding: 50px 0;
                background-color: transparent;
                border: none;
                text-align: center;
            }
        """)
        content_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(content_label)
        
        # 添加弹性空间
        layout.addStretch()
        
        # 创建简化的控件（保持信号连接）
        self.create_placeholder_controls()
    
    def create_placeholder_controls(self):
        """创建占位控件以保持信号连接"""
        # 发送数据输入框（隐藏）
        self.send_input = QLineEdit()
        self.send_input.hide()
        
        # 发送按钮（隐藏）
        self.send_btn = QPushButton("发送")
        self.send_btn.hide()
        
        # 发送选项（隐藏）
        self.hex_send_check = QCheckBox("十六进制发送")
        self.hex_send_check.hide()
        self.auto_send_check = QCheckBox("自动发送")
        self.auto_send_check.hide()
        
        # 自动发送间隔（隐藏）
        self.auto_send_interval = QSpinBox()
        self.auto_send_interval.hide()
        
        # 接收显示区域（隐藏）
        self.receive_text = QTextEdit()
        self.receive_text.hide()
        
        # 统计信息标签（隐藏）
        self.receive_count_label = QLabel("接收: 0")
        self.receive_count_label.hide()
        self.send_count_label = QLabel("发送: 0")
        self.send_count_label.hide()
        
        # 显示选项（隐藏）
        self.hex_display_check = QCheckBox("十六进制显示")
        self.hex_display_check.hide()
    
    def send_data(self):
        """发送数据（占位方法）"""
        pass
    
    def clear_receive(self):
        """清空接收数据（占位方法）"""
        pass
    
    def update_connection_status(self, connected):
        """更新连接状态（占位方法）"""
        pass
    
    def append_receive_data(self, data):
        """添加接收数据（占位方法）"""
        pass
    
    def update_statistics(self, receive_count, send_count):
        """更新统计信息（占位方法）"""
        pass
    
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