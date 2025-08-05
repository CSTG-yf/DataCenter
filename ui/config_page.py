from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, 
                             QGroupBox, QLabel, QComboBox, QPushButton)
from PyQt6.QtCore import pyqtSignal


class ConfigPage(QWidget):
    """串口配置页面"""
    
    # 定义信号
    connect_signal = pyqtSignal(dict)  # 连接信号
    disconnect_signal = pyqtSignal()   # 断开连接信号
    refresh_ports_signal = pyqtSignal()  # 刷新串口信号
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        """初始化UI界面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # 页面标题
        title = QLabel("串口配置")
        title.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 20px;")
        layout.addWidget(title)
        
        # 配置组
        config_group = QGroupBox("连接参数")
        config_layout = QGridLayout(config_group)
        
        # 串口选择
        config_layout.addWidget(QLabel("串口:"), 0, 0)
        self.port_combo = QComboBox()
        self.port_combo.setMinimumWidth(300)
        config_layout.addWidget(self.port_combo, 0, 1)
        
        # 刷新串口按钮
        self.refresh_btn = QPushButton("刷新")
        self.refresh_btn.clicked.connect(self.refresh_ports_signal.emit)
        config_layout.addWidget(self.refresh_btn, 0, 2)
        
        # 波特率选择
        config_layout.addWidget(QLabel("波特率:"), 1, 0)
        self.baud_combo = QComboBox()
        self.baud_combo.addItems(['9600', '19200', '38400', '57600', '115200'])
        self.baud_combo.setCurrentText('9600')
        config_layout.addWidget(self.baud_combo, 1, 1, 1, 2)
        
        # 数据位选择
        config_layout.addWidget(QLabel("数据位:"), 2, 0)
        self.data_bits_combo = QComboBox()
        self.data_bits_combo.addItems(['5', '6', '7', '8'])
        self.data_bits_combo.setCurrentText('8')
        config_layout.addWidget(self.data_bits_combo, 2, 1, 1, 2)
        
        # 停止位选择
        config_layout.addWidget(QLabel("停止位:"), 3, 0)
        self.stop_bits_combo = QComboBox()
        self.stop_bits_combo.addItems(['1', '1.5', '2'])
        self.stop_bits_combo.setCurrentText('1')
        config_layout.addWidget(self.stop_bits_combo, 3, 1, 1, 2)
        
        # 校验位选择
        config_layout.addWidget(QLabel("校验位:"), 4, 0)
        self.parity_combo = QComboBox()
        self.parity_combo.addItems(['无', '奇校验', '偶校验'])
        self.parity_combo.setCurrentText('无')
        config_layout.addWidget(self.parity_combo, 4, 1, 1, 2)
        
        layout.addWidget(config_group)
        
        # 连接控制组
        connect_group = QGroupBox("连接控制")
        connect_layout = QHBoxLayout(connect_group)
        
        # 连接按钮
        self.connect_btn = QPushButton("连接")
        self.connect_btn.clicked.connect(self.connect_serial)
        self.connect_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 15px 30px;
                border-radius: 8px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        connect_layout.addWidget(self.connect_btn)
        
        # 断开连接按钮
        self.disconnect_btn = QPushButton("断开连接")
        self.disconnect_btn.clicked.connect(self.disconnect_signal.emit)
        self.disconnect_btn.setEnabled(False)
        self.disconnect_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                padding: 15px 30px;
                border-radius: 8px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        connect_layout.addWidget(self.disconnect_btn)
        
        connect_layout.addStretch()
        layout.addWidget(connect_group)
        
        layout.addStretch()
    
    def connect_serial(self):
        """连接串口"""
        config = {
            'port': self.port_combo.currentText(),
            'baudrate': int(self.baud_combo.currentText()),
            'bytesize': int(self.data_bits_combo.currentText()),
            'stopbits': float(self.stop_bits_combo.currentText()),
            'parity': self.get_parity_value()
        }
        self.connect_signal.emit(config)
    
    def get_parity_value(self):
        """获取校验位值"""
        parity_map = {
            '无': 'N',
            '奇校验': 'O', 
            '偶校验': 'E'
        }
        return parity_map.get(self.parity_combo.currentText(), 'N')
    
    def update_connection_status(self, connected):
        """更新连接状态"""
        self.connect_btn.setEnabled(not connected)
        self.disconnect_btn.setEnabled(connected)
        self.port_combo.setEnabled(not connected)
        self.baud_combo.setEnabled(not connected)
        self.data_bits_combo.setEnabled(not connected)
        self.stop_bits_combo.setEnabled(not connected)
        self.parity_combo.setEnabled(not connected)
    
    def update_port_list(self, ports):
        """更新串口列表"""
        self.port_combo.clear()
        self.port_combo.addItems(ports) 