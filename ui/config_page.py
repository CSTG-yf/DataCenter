from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, 
                             QGroupBox, QLabel, QComboBox, QPushButton, QFrame,
                             QCheckBox, QLineEdit, QDialog, QMessageBox)
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QFont
import serial.tools.list_ports


class SerialConnectionDialog(QDialog):
    """串口连接对话框"""
    
    connection_requested = pyqtSignal(dict)  # 连接请求信号
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("连接新串口")
        self.setFixedSize(400, 300)
        self.setModal(True)
        self.init_ui()
        self.refresh_ports()
        
    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # 标题
        title = QLabel("连接新串口")
        title.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #333333;
                padding: 10px 0;
            }
        """)
        layout.addWidget(title)
        
        # 串口选择
        port_layout = QHBoxLayout()
        port_label = QLabel("串口:")
        port_label.setStyleSheet("font-size: 14px; color: #333333; min-width: 60px;")
        port_layout.addWidget(port_label)
        
        self.port_combo = QComboBox()
        self.port_combo.setStyleSheet("""
            QComboBox {
                border: 1px solid #d0d0d0;
                border-radius: 4px;
                padding: 8px 12px;
                background-color: white;
                font-size: 14px;
                min-width: 200px;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #666666;
            }
        """)
        port_layout.addWidget(self.port_combo)
        
        self.refresh_btn = QPushButton("刷新")
        self.refresh_btn.clicked.connect(self.refresh_ports)
        self.refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        port_layout.addWidget(self.refresh_btn)
        port_layout.addStretch()
        layout.addLayout(port_layout)
        
        # 波特率选择
        baud_layout = QHBoxLayout()
        baud_label = QLabel("波特率:")
        baud_label.setStyleSheet("font-size: 14px; color: #333333; min-width: 60px;")
        baud_layout.addWidget(baud_label)
        
        self.baud_combo = QComboBox()
        self.baud_combo.addItems(['9600', '19200', '38400', '57600', '115200'])
        self.baud_combo.setCurrentText('115200')
        self.baud_combo.setStyleSheet("""
            QComboBox {
                border: 1px solid #d0d0d0;
                border-radius: 4px;
                padding: 8px 12px;
                background-color: white;
                font-size: 14px;
                min-width: 200px;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #666666;
            }
        """)
        baud_layout.addWidget(self.baud_combo)
        baud_layout.addStretch()
        layout.addLayout(baud_layout)
        
        # 添加弹性空间
        layout.addStretch()
        
        # 按钮区域
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.cancel_btn = QPushButton("取消")
        self.cancel_btn.clicked.connect(self.reject)
        self.cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #f5f5f5;
                color: #333333;
                border: 1px solid #d0d0d0;
                padding: 10px 20px;
                border-radius: 4px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
        """)
        button_layout.addWidget(self.cancel_btn)
        
        self.connect_btn = QPushButton("连接")
        self.connect_btn.clicked.connect(self.connect_serial)
        self.connect_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 4px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        button_layout.addWidget(self.connect_btn)
        
        layout.addLayout(button_layout)
    
    def refresh_ports(self):
        """刷新串口列表"""
        self.port_combo.clear()
        ports = [port.device for port in serial.tools.list_ports.comports()]
        self.port_combo.addItems(ports)
    
    def connect_serial(self):
        """连接串口"""
        port = self.port_combo.currentText()
        if not port:
            QMessageBox.warning(self, "警告", "请选择串口")
            return
            
        config = {
            'port': port,
            'baudrate': int(self.baud_combo.currentText())
        }
        self.connection_requested.emit(config)
        self.accept()


class ConfigPage(QWidget):
    """串口配置页面 - 重新设计为Data sources面板"""
    
    # 定义信号
    connect_signal = pyqtSignal(dict)  # 连接信号
    disconnect_signal = pyqtSignal()   # 断开连接信号
    refresh_ports_signal = pyqtSignal()  # 刷新串口信号
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        """初始化UI界面 - 按照图片设计"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # 创建标题栏
        self.create_title_bar(layout)
        
        # 创建内容区域
        self.create_content_area(layout)
        
    def create_title_bar(self, parent_layout):
        """创建标题栏 - 与图片一致"""
        title_frame = QFrame()
        title_frame.setFixedHeight(45)
        title_frame.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border-bottom: 1px solid #d0d0d0;
            }
        """)
        
        title_layout = QHBoxLayout(title_frame)
        title_layout.setContentsMargins(12, 0, 12, 0)
        
        # 标题
        self.title_label = QLabel("Data sources")
        self.title_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: #333333;
            }
        """)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        button_layout.setSpacing(8)
        
        # + 按钮
        self.add_btn = QPushButton("+")
        self.add_btn.setFixedSize(28, 28)
        self.add_btn.clicked.connect(self.show_connection_dialog)
        self.add_btn.setStyleSheet("""
            QPushButton {
                border: none;
                background-color: transparent;
                font-size: 16px;
                color: #666666;
                border-radius: 14px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
                color: #333333;
            }
        """)
        
        # 设置按钮
        self.settings_btn = QPushButton("⚙")
        self.settings_btn.setFixedSize(28, 28)
        self.settings_btn.clicked.connect(self.show_settings)
        self.settings_btn.setStyleSheet("""
            QPushButton {
                border: none;
                background-color: transparent;
                font-size: 16px;
                color: #666666;
                border-radius: 14px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
                color: #333333;
            }
        """)
        
        # X 按钮
        self.close_btn = QPushButton("×")
        self.close_btn.setFixedSize(28, 28)
        self.close_btn.clicked.connect(self.close_panel)
        self.close_btn.setStyleSheet("""
            QPushButton {
                border: none;
                background-color: transparent;
                font-size: 16px;
                color: #666666;
                border-radius: 14px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
                color: #333333;
            }
        """)
        
        button_layout.addWidget(self.add_btn)
        button_layout.addWidget(self.settings_btn)
        button_layout.addWidget(self.close_btn)
        
        title_layout.addWidget(self.title_label)
        title_layout.addStretch()
        title_layout.addLayout(button_layout)
        
        parent_layout.addWidget(title_frame)
        
    def create_content_area(self, parent_layout):
        """创建内容区域 - 与图片一致"""
        content_frame = QFrame()
        content_frame.setStyleSheet("""
            QFrame {
                background-color: white;
            }
        """)
        
        content_layout = QVBoxLayout(content_frame)
        content_layout.setContentsMargins(20, 40, 20, 20)
        content_layout.setSpacing(10)
        
        # 提示文本
        self.hint_label = QLabel("You haven't added any data sources yet.")
        self.hint_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #666666;
                text-align: center;
            }
        """)
        self.hint_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.action_label = QLabel("To add a data source click <b>+</b> above.")
        self.action_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #666666;
                text-align: center;
            }
        """)
        self.action_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        content_layout.addWidget(self.hint_label)
        content_layout.addWidget(self.action_label)
        content_layout.addStretch()
        
        parent_layout.addWidget(content_frame)
    
    def show_connection_dialog(self):
        """显示串口连接对话框"""
        dialog = SerialConnectionDialog(self)
        dialog.connection_requested.connect(self.handle_connection_request)
        dialog.exec()
    
    def handle_connection_request(self, config):
        """处理连接请求"""
        self.connect_signal.emit(config)
        # 更新界面显示
        self.update_connection_status(True)
        self.hint_label.setText(f"Connected to {config['port']} at {config['baudrate']} baud")
        self.action_label.setText("Click ⚙ to configure or × to disconnect")
    
    def show_settings(self):
        """显示设置"""
        QMessageBox.information(self, "设置", "串口设置功能")
    
    def close_panel(self):
        """关闭面板"""
        # 隐藏右侧菜单
        if hasattr(self.parent(), 'right_menu'):
            self.parent().right_menu.hide_menu()
    
    def update_connection_status(self, connected):
        """更新连接状态"""
        if connected:
            self.add_btn.setEnabled(False)
        else:
            self.add_btn.setEnabled(True)
            self.hint_label.setText("You haven't added any data sources yet.")
            self.action_label.setText("To add a data source click <b>+</b> above.")
    
    def update_port_list(self, ports):
        """更新串口列表 - 保留接口兼容性"""
        pass 