from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QTextEdit, QPushButton, QLabel, QLineEdit, QCheckBox,
                             QSpinBox, QFrame, QGroupBox, QMessageBox, QGridLayout, QComboBox,
                             QScrollArea)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QTextCursor


class SendDataWindow(QMainWindow):
    """发送数据窗口 - CSIP数据包结构"""
    
    # 定义信号
    send_data_signal = pyqtSignal(str, str, bool, bool, int)  # 发送数据信号
    
    def __init__(self, port_name, parent=None):
        super().__init__(parent)
        self.port_name = port_name
        self.auto_send_timer = None
        self.init_ui()
        
    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle(f"串口 {self.port_name} - 发送CSIP数据包")
        self.setGeometry(300, 300, 800, 600)
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # 标题区域
        title_label = QLabel(f"串口 {self.port_name} - CSIP数据包发送")
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
        
        # CSIP数据包结构说明
        info_label = QLabel("数据包结构: 消息头(2字节) + 长度(2字节) + 消息类(1字节) + 消息ID(1字节) + 有效载荷(N字节) + 校验值(4字节)")
        info_label.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: #666666;
                background-color: transparent;
                border: none;
                padding: 5px;
            }
        """)
        layout.addWidget(info_label)
        
        # 数据包字段输入区域
        packet_frame = QFrame()
        packet_frame.setStyleSheet("""
            QFrame {
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                background-color: #f8f9fa;
            }
        """)
        
        packet_layout = QVBoxLayout(packet_frame)
        packet_layout.setContentsMargins(15, 15, 15, 15)
        
        # 字段标签
        fields_label = QLabel("数据包字段:")
        fields_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: #333333;
                background-color: transparent;
                border: none;
                margin-bottom: 10px;
            }
        """)
        packet_layout.addWidget(fields_label)
        
        # 字段输入网格布局
        fields_grid = QGridLayout()
        fields_grid.setSpacing(10)
        
        # 字段1: 消息头 (固定值)
        header_label = QLabel("消息头:")
        header_label.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: #333333;
                background-color: transparent;
                border: none;
            }
        """)
        fields_grid.addWidget(header_label, 0, 0)
        
        # 消息头显示（固定值，不可编辑）
        self.header_display = QLineEdit("0xBA 0xCE")
        self.header_display.setReadOnly(True)
        self.header_display.setStyleSheet("""
            QLineEdit {
                border: 1px solid #d0d0d0;
                border-radius: 4px;
                padding: 8px;
                background-color: #f0f0f0;
                font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
                font-size: 12px;
                color: #666666;
                min-width: 120px;
            }
        """)
        fields_grid.addWidget(self.header_display, 0, 1)
        
        # 字段2: 有效载荷长度 (自动计算)
        length_label = QLabel("有效载荷长度:")
        length_label.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: #333333;
                background-color: transparent;
                border: none;
            }
        """)
        fields_grid.addWidget(length_label, 1, 0)
        
        self.length_input = QLineEdit("自动计算")
        self.length_input.setReadOnly(True)
        self.length_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #d0d0d0;
                border-radius: 4px;
                padding: 8px;
                background-color: #f0f0f0;
                font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
                font-size: 12px;
                color: #666666;
            }
        """)
        fields_grid.addWidget(self.length_input, 1, 1)
        
        # 字段3: 消息类
        class_label = QLabel("消息类 (1字节):")
        class_label.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: #333333;
                background-color: transparent;
                border: none;
            }
        """)
        fields_grid.addWidget(class_label, 2, 0)
        
        self.class_combo = QComboBox()
        self.class_combo.addItems([
            "0x11 - NAV2 (导航结果:位置、速度、时间)",
            "0x12 - TIM2 (授时产品专有信息:时间脉冲输出,各时间系统信息)",
            "0x13 - RXM2 (接收机输出的测量信息:伪距、载波相位等)",
            "0x05 - ACK (ACK/NAK 消息:对CFG消息的应答消息)",
            "0x06 - CFG (输入配置消息:配置导航模式、波特率等)",
            "0x08 - MSG (作为辅助信息输入的卫星电文信息)",
            "0x0A - MON (监控消息:通信状态、CPU载荷、堆栈利用等)",
            "0x0B - AID (辅助消息:星历、历书和其它A-GPS 数据)",
            "0x14 - INS2 (组合导航产品专有信息)",
            "0x15 - RTCM (RTCM输出信息:实时动态定位数据)"
        ])
        self.class_combo.setCurrentText("0x11 - NAV2 (导航结果:位置、速度、时间)")
        self.class_combo.setStyleSheet("""
            QComboBox {
                border: 1px solid #d0d0d0;
                border-radius: 4px;
                padding: 8px;
                background-color: white;
                font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
                font-size: 12px;
                color: #333333;
                min-width: 300px;
            }
            QComboBox:focus {
                border: 2px solid #2196F3;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #666;
                margin-right: 5px;
            }
        """)
        self.class_combo.currentTextChanged.connect(self.on_class_changed)
        fields_grid.addWidget(self.class_combo, 2, 1)
        
        # 字段4: 消息ID
        id_label = QLabel("消息ID (1字节):")
        id_label.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: #333333;
                background-color: transparent;
                border: none;
            }
        """)
        fields_grid.addWidget(id_label, 3, 0)
        
        self.id_combo = QComboBox()
        # 初始化时不添加默认选项，由on_class_changed来设置
        self.id_combo.setStyleSheet("""
            QComboBox {
                border: 1px solid #d0d0d0;
                border-radius: 4px;
                padding: 8px;
                background-color: white;
                font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
                font-size: 12px;
                color: #333333;
                min-width: 200px;
            }
            QComboBox:focus {
                border: 2px solid #2196F3;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #666;
                margin-right: 5px;
            }
        """)
        self.id_combo.currentTextChanged.connect(self.update_packet_preview)
        fields_grid.addWidget(self.id_combo, 3, 1)
        
        # 字段5: 有效载荷
        payload_label = QLabel("有效载荷 (N字节):")
        payload_label.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: #333333;
                background-color: transparent;
                border: none;
            }
        """)
        fields_grid.addWidget(payload_label, 4, 0)
        
        # 创建有效载荷输入区域
        payload_widget = QWidget()
        payload_layout = QVBoxLayout(payload_widget)
        payload_layout.setContentsMargins(0, 0, 0, 0)
        payload_layout.setSpacing(5)
        
        # 默认的有效载荷输入（文本编辑框）
        self.payload_input = QTextEdit()
        self.payload_input.setPlaceholderText("输入十六进制数据，如: 01 02 03 04\n注意: 长度必须是4的倍数")
        self.payload_input.setStyleSheet("""
            QTextEdit {
                border: 1px solid #d0d0d0;
                border-radius: 4px;
                padding: 8px;
                background-color: white;
                font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
                font-size: 12px;
                color: #333333;
            }
            QTextEdit:focus {
                border: 2px solid #2196F3;
            }
        """)
        self.payload_input.setMaximumHeight(100)
        self.payload_input.textChanged.connect(self.update_packet_preview)
        payload_layout.addWidget(self.payload_input)
        
        # NAV2-DOP消息的专用输入框
        self.nav2_dop_widget = QWidget()
        nav2_dop_layout = QVBoxLayout(self.nav2_dop_widget)
        nav2_dop_layout.setContentsMargins(0, 0, 0, 0)
        nav2_dop_layout.setSpacing(5)
        
        # NAV2-DOP标题
        nav2_dop_title = QLabel("NAV2-DOP 消息有效载荷 (定位精度因子):")
        nav2_dop_title.setStyleSheet("""
            QLabel {
                font-size: 12px;
                font-weight: bold;
                color: #333333;
                background-color: #e3f2fd;
                border: 1px solid #bbdefb;
                border-radius: 4px;
                padding: 5px;
            }
        """)
        nav2_dop_layout.addWidget(nav2_dop_title)
        
        # NAV2-DOP字段网格
        nav2_dop_grid = QGridLayout()
        nav2_dop_grid.setSpacing(8)
        
        # 字段1: pDop (位置 DOP)
        pDop_label = QLabel("pDop (位置 DOP):")
        pDop_label.setStyleSheet("""
            QLabel {
                font-size: 11px;
                color: #333333;
                background-color: transparent;
                border: none;
            }
        """)
        nav2_dop_grid.addWidget(pDop_label, 0, 0)
        
        self.pDop_input = QLineEdit()
        self.pDop_input.setPlaceholderText("输入16进制数，留空默认为0")
        self.pDop_input.setMaxLength(8)  # 限制最大长度为8位
        self.pDop_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #d0d0d0;
                border-radius: 4px;
                padding: 6px;
                background-color: white;
                font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
                font-size: 11px;
                color: #333333;
                min-width: 120px;
            }
            QLineEdit:focus {
                border: 2px solid #2196F3;
            }
        """)
        self.pDop_input.textChanged.connect(self.on_nav2_dop_changed)
        self.pDop_input.textChanged.connect(self.validate_hex_input)
        self.pDop_input.editingFinished.connect(self.auto_pad_hex_input)
        nav2_dop_grid.addWidget(self.pDop_input, 0, 1)
        
        # 字段2: hDop (水平 DOP)
        hDop_label = QLabel("hDop (水平 DOP):")
        hDop_label.setStyleSheet("""
            QLabel {
                font-size: 11px;
                color: #333333;
                background-color: transparent;
                border: none;
            }
        """)
        nav2_dop_grid.addWidget(hDop_label, 1, 0)
        
        self.hDop_input = QLineEdit()
        self.hDop_input.setPlaceholderText("输入16进制数，留空默认为0")
        self.hDop_input.setMaxLength(8)  # 限制最大长度为8位
        self.hDop_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #d0d0d0;
                border-radius: 4px;
                padding: 6px;
                background-color: white;
                font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
                font-size: 11px;
                color: #333333;
                min-width: 120px;
            }
            QLineEdit:focus {
                border: 2px solid #2196F3;
            }
        """)
        self.hDop_input.textChanged.connect(self.on_nav2_dop_changed)
        self.hDop_input.textChanged.connect(self.validate_hex_input)
        self.hDop_input.editingFinished.connect(self.auto_pad_hex_input)
        nav2_dop_grid.addWidget(self.hDop_input, 1, 1)
        
        # 字段3: vDop (垂直 DOP)
        vDop_label = QLabel("vDop (垂直 DOP):")
        vDop_label.setStyleSheet("""
            QLabel {
                font-size: 11px;
                color: #333333;
                background-color: transparent;
                border: none;
            }
        """)
        nav2_dop_grid.addWidget(vDop_label, 2, 0)
        
        self.vDop_input = QLineEdit()
        self.vDop_input.setPlaceholderText("输入16进制数，留空默认为0")
        self.vDop_input.setMaxLength(8)  # 限制最大长度为8位
        self.vDop_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #d0d0d0;
                border-radius: 4px;
                padding: 6px;
                background-color: white;
                font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
                font-size: 11px;
                color: #333333;
                min-width: 120px;
            }
            QLineEdit:focus {
                border: 2px solid #2196F3;
            }
        """)
        self.vDop_input.textChanged.connect(self.on_nav2_dop_changed)
        self.vDop_input.textChanged.connect(self.validate_hex_input)
        self.vDop_input.editingFinished.connect(self.auto_pad_hex_input)
        nav2_dop_grid.addWidget(self.vDop_input, 2, 1)
        
        # 字段4: nDop (北向 DOP)
        nDop_label = QLabel("nDop (北向 DOP):")
        nDop_label.setStyleSheet("""
            QLabel {
                font-size: 11px;
                color: #333333;
                background-color: transparent;
                border: none;
            }
        """)
        nav2_dop_grid.addWidget(nDop_label, 3, 0)
        
        self.nDop_input = QLineEdit()
        self.nDop_input.setPlaceholderText("输入16进制数，留空默认为0")
        self.nDop_input.setMaxLength(8)  # 限制最大长度为8位
        self.nDop_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #d0d0d0;
                border-radius: 4px;
                padding: 6px;
                background-color: white;
                font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
                font-size: 11px;
                color: #333333;
                min-width: 120px;
            }
            QLineEdit:focus {
                border: 2px solid #2196F3;
            }
        """)
        self.nDop_input.textChanged.connect(self.on_nav2_dop_changed)
        self.nDop_input.textChanged.connect(self.validate_hex_input)
        self.nDop_input.editingFinished.connect(self.auto_pad_hex_input)
        nav2_dop_grid.addWidget(self.nDop_input, 3, 1)
        
        # 字段5: eDop (东向 DOP)
        eDop_label = QLabel("eDop (东向 DOP):")
        eDop_label.setStyleSheet("""
            QLabel {
                font-size: 11px;
                color: #333333;
                background-color: transparent;
                border: none;
            }
        """)
        nav2_dop_grid.addWidget(eDop_label, 4, 0)
        
        self.eDop_input = QLineEdit()
        self.eDop_input.setPlaceholderText("输入16进制数，留空默认为0")
        self.eDop_input.setMaxLength(8)  # 限制最大长度为8位
        self.eDop_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #d0d0d0;
                border-radius: 4px;
                padding: 6px;
                background-color: white;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 11px;
                color: #333333;
                min-width: 120px;
            }
            QLineEdit:focus {
                border: 2px solid #2196F3;
            }
        """)
        self.eDop_input.textChanged.connect(self.on_nav2_dop_changed)
        self.eDop_input.textChanged.connect(self.validate_hex_input)
        self.eDop_input.editingFinished.connect(self.auto_pad_hex_input)
        nav2_dop_grid.addWidget(self.eDop_input, 4, 1)
        
        # 字段6: tDop (时间 DOP)
        tDop_label = QLabel("tDop (时间 DOP):")
        tDop_label.setStyleSheet("""
            QLabel {
                font-size: 11px;
                color: #333333;
                background-color: transparent;
                border: none;
            }
        """)
        nav2_dop_grid.addWidget(tDop_label, 5, 0)
        
        self.tDop_input = QLineEdit()
        self.tDop_input.setPlaceholderText("输入16进制数，留空默认为0")
        self.tDop_input.setMaxLength(8)  # 限制最大长度为8位
        self.tDop_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #d0d0d0;
                border-radius: 4px;
                padding: 6px;
                background-color: white;
                font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
                font-size: 11px;
                color: #333333;
                min-width: 120px;
            }
            QLineEdit:focus {
                border: 2px solid #2196F3;
            }
        """)
        self.tDop_input.textChanged.connect(self.on_nav2_dop_changed)
        self.tDop_input.textChanged.connect(self.validate_hex_input)
        self.tDop_input.editingFinished.connect(self.auto_pad_hex_input)
        nav2_dop_grid.addWidget(self.tDop_input, 5, 1)
        
        nav2_dop_layout.addLayout(nav2_dop_grid)
        
        # NAV2-SOL消息的专用输入框
        self.nav2_sol_widget = QWidget()
        nav2_sol_layout = QVBoxLayout(self.nav2_sol_widget)
        nav2_sol_layout.setContentsMargins(0, 0, 0, 0)
        nav2_sol_layout.setSpacing(5)
        
        # NAV2-SOL标题
        nav2_sol_title = QLabel("NAV2-SOL 消息有效载荷 (ECEF坐标系下的PVT导航信息):")
        nav2_sol_title.setStyleSheet("""
            QLabel {
                font-size: 12px;
                font-weight: bold;
                color: #333333;
                background-color: #e8f5e8;
                border: 1px solid #c8e6c9;
                border-radius: 4px;
                padding: 5px;
            }
        """)
        nav2_sol_layout.addWidget(nav2_sol_title)
        
        # 创建滚动区域来容纳所有字段
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setMaximumHeight(300)  # 限制最大高度
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: 1px solid #d0d0d0;
                border-radius: 4px;
                background-color: white;
            }
        """)
        
        # 创建滚动区域的内容部件
        scroll_content = QWidget()
        nav2_sol_grid = QGridLayout(scroll_content)
        nav2_sol_grid.setSpacing(6)
        nav2_sol_grid.setContentsMargins(10, 10, 10, 10)
        
        # 定义NAV2-SOL字段信息
        nav2_sol_fields = [
            # 偏移, 数据类型, 最大长度, 名称, 单位, 描述
            (0, "I4", 8, "tow", "ms", "GPS时间, 周内时"),
            (4, "U2", 4, "wn", "-", "GPS时间, 周数"),
            (6, "U2", 4, "res1", "-", "保留"),
            (8, "U1", 2, "fixflags", "-", "位置有效标志"),
            (9, "U1", 2, "velflags", "-", "速度有效标志"),
            (10, "U1", 2, "res2", "-", "保留"),
            (11, "U1", 2, "fixGnssMask", "-", "参与定位的卫星系统掩码"),
            (12, "U1", 2, "numFixtot", "-", "参与解算的卫星总数"),
            (13, "U1", 2, "numFixGps", "-", "参与解算的GPS卫星数目"),
            (14, "U1", 2, "numFixBds", "-", "参与解算的BDS卫星数目"),
            (15, "U1", 2, "numFixGln", "-", "参与解算的GLONASS卫星数目"),
            (16, "U1", 2, "numFixGal", "-", "参与解算的GALILEO卫星数目"),
            (17, "U1", 2, "numFixQzs", "-", "参与解算的QZSS卫星数目"),
            (18, "U1", 2, "numFixSbs", "-", "参与解算的SBAS卫星数目"),
            (19, "U1", 2, "numFixIrn", "-", "参与解算的IRNSS卫星数目"),
            (20, "U4", 8, "res3", "-", "保留"),
            (24, "R8", 16, "x", "m", "ECEF坐标系中的X坐标"),
            (32, "R8", 16, "y", "m", "ECEF坐标系中的Y坐标"),
            (40, "R8", 16, "z", "m", "ECEF坐标系中的Z坐标"),
            (48, "R4", 8, "pAcc", "m", "3D位置的估计精度误差"),
            (52, "R4", 8, "vx", "m/s", "ECEF坐标系中的X速度"),
            (56, "R4", 8, "vy", "m/s", "ECEF坐标系中的Y速度"),
            (60, "R4", 8, "vz", "m/s", "ECEF坐标系中的Z速度"),
            (64, "R4", 8, "sAcc", "m/s", "3D速度的估计精度误差"),
            (68, "R4", 8, "pDop", "-", "位置DOP")
        ]
        
        # 创建输入框字典
        self.nav2_sol_inputs = {}
        
        # 创建所有字段的输入框
        for i, (offset, data_type, max_length, name, unit, description) in enumerate(nav2_sol_fields):
            row = i // 2  # 每行2个字段
            col = (i % 2) * 2  # 每2列为一组
            
            # 字段标签
            label_text = f"{name} ({description}):"
            label = QLabel(label_text)
            label.setStyleSheet("""
                QLabel {
                    font-size: 10px;
                    color: #333333;
                    background-color: transparent;
                    border: none;
                }
            """)
            label.setWordWrap(True)
            nav2_sol_grid.addWidget(label, row, col)
            
            # 输入框
            input_field = QLineEdit()
            input_field.setPlaceholderText(f"输入{max_length}位16进制数，留空默认为0")
            input_field.setMaxLength(max_length)
            input_field.setStyleSheet("""
                QLineEdit {
                    border: 1px solid #d0d0d0;
                    border-radius: 4px;
                    padding: 4px;
                    background-color: white;
                    font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
                    font-size: 10px;
                    color: #333333;
                    min-width: 100px;
                }
                QLineEdit:focus {
                    border: 2px solid #2196F3;
                }
            """)
            
            # 连接信号
            input_field.textChanged.connect(self.on_nav2_sol_changed)
            input_field.textChanged.connect(self.validate_hex_input)
            input_field.editingFinished.connect(self.auto_pad_hex_input)
            
            nav2_sol_grid.addWidget(input_field, row, col + 1)
            
            # 存储输入框引用
            self.nav2_sol_inputs[name] = input_field
        
        # 设置滚动区域的内容
        scroll_area.setWidget(scroll_content)
        nav2_sol_layout.addWidget(scroll_area)
        
        # NAV2-PVH消息的专用输入框
        self.nav2_pvh_widget = QWidget()
        nav2_pvh_layout = QVBoxLayout(self.nav2_pvh_widget)
        nav2_pvh_layout.setContentsMargins(0, 0, 0, 0)
        nav2_pvh_layout.setSpacing(5)
        
        # NAV2-PVH标题
        nav2_pvh_title = QLabel("NAV2-PVH 消息有效载荷 (LLA格式位置,ENU格式速度):")
        nav2_pvh_title.setStyleSheet("""
            QLabel {
                font-size: 12px;
                font-weight: bold;
                color: #333333;
                background-color: #fff3e0;
                border: 1px solid #ffcc80;
                border-radius: 4px;
                padding: 5px;
            }
        """)
        nav2_pvh_layout.addWidget(nav2_pvh_title)
        
        # 创建滚动区域来容纳所有字段
        pvh_scroll_area = QScrollArea()
        pvh_scroll_area.setWidgetResizable(True)
        pvh_scroll_area.setMaximumHeight(300)  # 限制最大高度
        pvh_scroll_area.setStyleSheet("""
            QScrollArea {
                border: 1px solid #d0d0d0;
                border-radius: 4px;
                background-color: white;
            }
        """)
        
        # 创建滚动区域的内容部件
        pvh_scroll_content = QWidget()
        nav2_pvh_grid = QGridLayout(pvh_scroll_content)
        nav2_pvh_grid.setSpacing(6)
        nav2_pvh_grid.setContentsMargins(10, 10, 10, 10)
        
        # 定义NAV2-PVH字段信息
        nav2_pvh_fields = [
            # 偏移, 数据类型, 最大长度, 名称, 单位, 描述
            (0, "I4", 8, "tow", "ms", "GPS时间, 周内时"),
            (4, "U2", 4, "wn", "-", "GPS时间, 周数"),
            (6, "U2", 4, "res1", "-", "保留"),
            (8, "U1", 2, "fixflags", "-", "位置有效标志"),
            (9, "U1", 2, "velflags", "-", "速度有效标志"),
            (10, "U1", 2, "res2", "-", "保留"),
            (11, "U1", 2, "fixGnssMask", "-", "参与定位的卫星系统掩码"),
            (12, "U1", 2, "numFixtot", "-", "参与解算的卫星总数"),
            (13, "U1", 2, "numFixGps", "-", "参与解算的GPS卫星数目"),
            (14, "U1", 2, "numFixBds", "-", "参与解算的BDS卫星数目"),
            (15, "U1", 2, "numFixGln", "-", "参与解算的GLONASS卫星数目"),
            (16, "U1", 2, "numFixGal", "-", "参与解算的GALILEO卫星数目"),
            (17, "U1", 2, "numFixQzs", "-", "参与解算的QZSS卫星数目"),
            (18, "U1", 2, "numFixSbs", "-", "参与解算的SBAS卫星数目"),
            (19, "U1", 2, "numFixIrn", "-", "参与解算的IRNSS卫星数目"),
            (20, "U4", 8, "res3", "-", "保留"),
            (24, "R8", 16, "lon", "度", "经度"),
            (32, "R8", 16, "lat", "度", "纬度"),
            (40, "R4", 8, "height", "m", "大地高度"),
            (44, "R4", 8, "sepGeoid", "m", "高度异常"),
            (48, "R4", 8, "velE", "m/s", "ENU坐标系中的东向速度"),
            (52, "R4", 8, "velN", "m/s", "ENU坐标系中的北向速度"),
            (56, "R4", 8, "velU", "m/s", "ENU坐标系中的天向速度"),
            (60, "R4", 8, "speed3D", "m/s", "3D速度"),
            (64, "R4", 8, "speed2D", "m/s", "2D对地速度"),
            (68, "R4", 8, "heading", "度", "航向"),
            (72, "R4", 8, "hAcc", "m", "位置的估计水平精度误差"),
            (76, "R4", 8, "vAcc", "m", "位置的估计垂直精度误差"),
            (80, "R4", 8, "sAcc", "m/s", "3D速度的估计精度误差"),
            (84, "R4", 8, "cAcc", "度", "航向的精度误差")
        ]
        
        # 创建输入框字典
        self.nav2_pvh_inputs = {}
        
        # 创建所有字段的输入框
        for i, (offset, data_type, max_length, name, unit, description) in enumerate(nav2_pvh_fields):
            row = i // 2  # 每行2个字段
            col = (i % 2) * 2  # 每2列为一组
            
            # 字段标签
            label_text = f"{name} ({description}):"
            label = QLabel(label_text)
            label.setStyleSheet("""
                QLabel {
                    font-size: 10px;
                    color: #333333;
                    background-color: transparent;
                    border: none;
                }
            """)
            label.setWordWrap(True)
            nav2_pvh_grid.addWidget(label, row, col)
            
            # 输入框
            input_field = QLineEdit()
            input_field.setPlaceholderText(f"输入{max_length}位16进制数，留空默认为0")
            input_field.setMaxLength(max_length)
            input_field.setStyleSheet("""
                QLineEdit {
                    border: 1px solid #d0d0d0;
                    border-radius: 4px;
                    padding: 4px;
                    background-color: white;
                    font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
                    font-size: 10px;
                    color: #333333;
                    min-width: 100px;
                }
                QLineEdit:focus {
                    border: 2px solid #2196F3;
                }
            """)
            
            # 连接信号
            input_field.textChanged.connect(self.on_nav2_pvh_changed)
            input_field.textChanged.connect(self.validate_hex_input)
            input_field.editingFinished.connect(self.auto_pad_hex_input)
            
            nav2_pvh_grid.addWidget(input_field, row, col + 1)
            
            # 存储输入框引用
            self.nav2_pvh_inputs[name] = input_field
        
        # 设置滚动区域的内容
        pvh_scroll_area.setWidget(pvh_scroll_content)
        nav2_pvh_layout.addWidget(pvh_scroll_area)
        
        # NAV2-TIMEUTC消息的专用输入框
        self.nav2_timeutc_widget = QWidget()
        nav2_timeutc_layout = QVBoxLayout(self.nav2_timeutc_widget)
        nav2_timeutc_layout.setContentsMargins(0, 0, 0, 0)
        nav2_timeutc_layout.setSpacing(5)
        
        # NAV2-TIMEUTC标题
        nav2_timeutc_title = QLabel("NAV2-TIMEUTC 消息有效载荷 (UTC时间信息):")
        nav2_timeutc_title.setStyleSheet("""
            QLabel {
                font-size: 12px;
                font-weight: bold;
                color: #333333;
                background-color: #f3e5f5;
                border: 1px solid #ce93d8;
                border-radius: 4px;
                padding: 5px;
            }
        """)
        nav2_timeutc_layout.addWidget(nav2_timeutc_title)
        
        # 创建滚动区域来容纳所有字段
        timeutc_scroll_area = QScrollArea()
        timeutc_scroll_area.setWidgetResizable(True)
        timeutc_scroll_area.setMaximumHeight(300)  # 限制最大高度
        timeutc_scroll_area.setStyleSheet("""
            QScrollArea {
                border: 1px solid #d0d0d0;
                border-radius: 4px;
                background-color: white;
            }
        """)
        
        # 创建滚动区域的内容部件
        timeutc_scroll_content = QWidget()
        nav2_timeutc_grid = QGridLayout(timeutc_scroll_content)
        nav2_timeutc_grid.setSpacing(6)
        nav2_timeutc_grid.setContentsMargins(10, 10, 10, 10)
        
        # 定义NAV2-TIMEUTC字段信息
        nav2_timeutc_fields = [
            # 偏移, 数据类型, 最大长度, 名称, 单位, 描述
            (0, "R4", 8, "tacc", "ns", "接收机的时间误差估计值"),
            (4, "I4", 8, "subms", "ms", "时间的毫秒误差值, 范围: -0.5ms~0.5ms"),
            (8, "I1", 2, "subcs", "ms", "时间的厘秒误差值, 范围: -5ms~5ms"),
            (9, "U1", 2, "cs", "cs", "时间的整数厘秒值, 范围: 0cs~99cs"),
            (10, "U2", 4, "year", "-", "年份"),
            (12, "U1", 2, "month", "-", "月份"),
            (13, "U1", 2, "day", "-", "日期"),
            (14, "U1", 2, "hour", "-", "小时数"),
            (15, "U1", 2, "minute", "-", "分钟数"),
            (16, "U1", 2, "second", "-", "秒数"),
            (17, "U1", 2, "tflagx", "-", "综合时间标志"),
            (18, "U1", 2, "tsrc", "-", "时间的卫星系统来源"),
            (19, "I1", 2, "leapsec", "s", "当前的闰秒值")
        ]
        
        # 创建输入框字典
        self.nav2_timeutc_inputs = {}
        
        # 创建所有字段的输入框
        for i, (offset, data_type, max_length, name, unit, description) in enumerate(nav2_timeutc_fields):
            row = i // 2  # 每行2个字段
            col = (i % 2) * 2  # 每2列为一组
            
            # 字段标签
            label_text = f"{name} ({description}):"
            label = QLabel(label_text)
            label.setStyleSheet("""
                QLabel {
                    font-size: 10px;
                    color: #333333;
                    background-color: transparent;
                    border: none;
                }
            """)
            label.setWordWrap(True)
            nav2_timeutc_grid.addWidget(label, row, col)
            
            # 输入框
            input_field = QLineEdit()
            input_field.setPlaceholderText(f"输入{max_length}位16进制数，留空默认为0")
            input_field.setMaxLength(max_length)
            input_field.setStyleSheet("""
                QLineEdit {
                    border: 1px solid #d0d0d0;
                    border-radius: 4px;
                    padding: 4px;
                    background-color: white;
                    font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
                    font-size: 10px;
                    color: #333333;
                    min-width: 100px;
                }
                QLineEdit:focus {
                    border: 2px solid #2196F3;
                }
            """)
            
            # 连接信号
            input_field.textChanged.connect(self.on_nav2_timeutc_changed)
            input_field.textChanged.connect(self.validate_hex_input)
            input_field.editingFinished.connect(self.auto_pad_hex_input)
            
            nav2_timeutc_grid.addWidget(input_field, row, col + 1)
            
            # 存储输入框引用
            self.nav2_timeutc_inputs[name] = input_field
        
        # 设置滚动区域的内容
        timeutc_scroll_area.setWidget(timeutc_scroll_content)
        nav2_timeutc_layout.addWidget(timeutc_scroll_area)
        
        # NAV2-CLK消息的专用输入框
        self.nav2_clk_widget = QWidget()
        nav2_clk_layout = QVBoxLayout(self.nav2_clk_widget)
        nav2_clk_layout.setContentsMargins(0, 0, 0, 0)
        nav2_clk_layout.setSpacing(5)
        
        # NAV2-CLK标题
        nav2_clk_title = QLabel("NAV2-CLK 消息有效载荷 (接收机时间偏差, 频率偏差):")
        nav2_clk_title.setStyleSheet("""
            QLabel {
                font-size: 12px;
                font-weight: bold;
                color: #333333;
                background-color: #e8f5e8;
                border: 1px solid #81c784;
                border-radius: 4px;
                padding: 5px;
            }
        """)
        nav2_clk_layout.addWidget(nav2_clk_title)
        
        # 创建滚动区域来容纳所有字段
        clk_scroll_area = QScrollArea()
        clk_scroll_area.setWidgetResizable(True)
        clk_scroll_area.setMaximumHeight(300)  # 限制最大高度
        clk_scroll_area.setStyleSheet("""
            QScrollArea {
                border: 1px solid #d0d0d0;
                border-radius: 4px;
                background-color: white;
            }
        """)
        
        # 创建滚动区域的内容部件
        clk_scroll_content = QWidget()
        nav2_clk_grid = QGridLayout(clk_scroll_content)
        nav2_clk_grid.setSpacing(6)
        nav2_clk_grid.setContentsMargins(10, 10, 10, 10)
        
        # 定义NAV2-CLK字段信息
        nav2_clk_fields = [
            # 偏移, 数据类型, 最大长度, 名称, 单位, 描述
            (0, "U1", 2, "tsrc", "-", "卫星系统时间源"),
            (1, "U1", 2, "res1", "-", "保留字段"),
            (2, "U1", 2, "towflag", "-", "接收机时间有效标志"),
            (3, "U1", 2, "frqflag", "-", "接收机频率偏差有效标志"),
            (4, "I4", 8, "clkbias", "ns", "当前接收机时间偏差"),
            (8, "R4", 8, "dfxTcxo", "s/s", "接收机TCXO相对频率偏差"),
            (12, "R4", 8, "tacc", "ns", "接收机时间精度"),
            (16, "R4", 8, "facc", "ppb", "接收机频率精度")
        ]
        
        # 创建输入框字典
        self.nav2_clk_inputs = {}
        
        # 创建所有字段的输入框
        for i, (offset, data_type, max_length, name, unit, description) in enumerate(nav2_clk_fields):
            row = i // 2  # 每行2个字段
            col = (i % 2) * 2  # 每2列为一组
            
            # 字段标签
            label_text = f"{name} ({description}):"
            label = QLabel(label_text)
            label.setStyleSheet("""
                QLabel {
                    font-size: 10px;
                    color: #333333;
                    background-color: transparent;
                    border: none;
                }
            """)
            label.setWordWrap(True)
            nav2_clk_grid.addWidget(label, row, col)
            
            # 输入框
            input_field = QLineEdit()
            input_field.setPlaceholderText(f"输入{max_length}位16进制数，留空默认为0")
            input_field.setMaxLength(max_length)
            input_field.setStyleSheet("""
                QLineEdit {
                    border: 1px solid #d0d0d0;
                    border-radius: 4px;
                    padding: 4px;
                    background-color: white;
                    font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
                    font-size: 10px;
                    color: #333333;
                    min-width: 100px;
                }
                QLineEdit:focus {
                    border: 2px solid #2196F3;
                }
            """)
            
            # 连接信号
            input_field.textChanged.connect(self.on_nav2_clk_changed)
            input_field.textChanged.connect(self.validate_hex_input)
            input_field.editingFinished.connect(self.auto_pad_hex_input)
            
            nav2_clk_grid.addWidget(input_field, row, col + 1)
            
            # 存储输入框引用
            self.nav2_clk_inputs[name] = input_field
        
        # 设置滚动区域的内容
        clk_scroll_area.setWidget(clk_scroll_content)
        nav2_clk_layout.addWidget(clk_scroll_area)
        
        # NAV2-RVT消息的专用输入框
        self.nav2_rvt_widget = QWidget()
        nav2_rvt_layout = QVBoxLayout(self.nav2_rvt_widget)
        nav2_rvt_layout.setContentsMargins(0, 0, 0, 0)
        nav2_rvt_layout.setSpacing(5)
        
        # NAV2-RVT标题
        nav2_rvt_title = QLabel("NAV2-RVT 消息有效载荷 (接收机原始时间信息):")
        nav2_rvt_title.setStyleSheet("""
            QLabel {
                font-size: 12px;
                font-weight: bold;
                color: #333333;
                background-color: #fff8e1;
                border: 1px solid #ffb74d;
                border-radius: 4px;
                padding: 5px;
            }
        """)
        nav2_rvt_layout.addWidget(nav2_rvt_title)
        
        # 创建滚动区域来容纳所有字段
        rvt_scroll_area = QScrollArea()
        rvt_scroll_area.setWidgetResizable(True)
        rvt_scroll_area.setMaximumHeight(300)  # 限制最大高度
        rvt_scroll_area.setStyleSheet("""
            QScrollArea {
                border: 1px solid #d0d0d0;
                border-radius: 4px;
                background-color: white;
            }
        """)
        
        # 创建滚动区域的内容部件
        rvt_scroll_content = QWidget()
        nav2_rvt_grid = QGridLayout(rvt_scroll_content)
        nav2_rvt_grid.setSpacing(6)
        nav2_rvt_grid.setContentsMargins(10, 10, 10, 10)
        
        # 定义NAV2-RVT字段信息
        nav2_rvt_fields = [
            # 偏移, 数据类型, 最大长度, 名称, 单位, 描述
            (0, "I4", 8, "rawTow", "ms", "原始接收机时间, GPS周内时的整毫秒部分"),
            (4, "I4", 8, "rawTowSubms", "ms", "原始接收机时间, GPS周内时的小数毫秒部分"),
            (8, "I4", 8, "dtuTow", "ms", "原始接收机时间误差的整数毫秒"),
            (12, "I4", 8, "dtuTowSubms", "ms", "原始接收机时间误差的小数毫秒"),
            (16, "I2", 4, "wn", "-", "原始接收机时间, GPS 周数"),
            (18, "U1", 2, "towflag", "-", "时间的有效标志"),
            (19, "U1", 2, "wnflag", "-", "周数的有效标志"),
            (20, "U1", 2, "res1", "-", "保留"),
            (21, "U1", 2, "ambflag", "-", "接收机整毫秒模糊度标志"),
            (22, "U1", 2, "dtuflag", "-", "接收机时间误差的有效标志"),
            (23, "U1", 2, "rvtRstTag", "-", "接收机时钟重置计数器"),
            (24, "I4", 8, "rvtRst", "ms", "接收机时钟调整量"),
            (28, "R4", 8, "tacc", "ns", "接收机的时间精度"),
            (32, "I4", 8, "res5", "-", "保留"),
            (36, "I4", 8, "res6", "-", "保留"),
            (40, "R4", 8, "dtmeas", "s", "距上次定位测量的时间间隔"),
            (44, "I1", 2, "res2", "-", "保留"),
            (45, "I1", 2, "dtsBds2Gps", "s", "BDS和GPS 时间的整秒偏差"),
            (46, "I1", 2, "dtsGln2Gps", "s", "GLONASS和GPS 时间的整秒偏差"),
            (47, "I1", 2, "dtsGal2Gps", "s", "GALILEO和GPS 时间的整秒偏差"),
            (48, "I1", 2, "dtsIrn2Gps", "s", "IRNSS和GPS 时间的整秒偏差"),
            (49, "U1", 2, "res3", "-", "保留"),
            (50, "U2", 4, "res4", "-", "保留")
        ]
        
        # 创建输入框字典
        self.nav2_rvt_inputs = {}
        
        # 创建所有字段的输入框
        for i, (offset, data_type, max_length, name, unit, description) in enumerate(nav2_rvt_fields):
            row = i // 2  # 每行2个字段
            col = (i % 2) * 2  # 每2列为一组
            
            # 字段标签
            label_text = f"{name} ({description}):"
            label = QLabel(label_text)
            label.setStyleSheet("""
                QLabel {
                    font-size: 10px;
                    color: #333333;
                    background-color: transparent;
                    border: none;
                }
            """)
            label.setWordWrap(True)
            nav2_rvt_grid.addWidget(label, row, col)
            
            # 输入框
            input_field = QLineEdit()
            input_field.setPlaceholderText(f"输入{max_length}位16进制数，留空默认为0")
            input_field.setMaxLength(max_length)
            input_field.setStyleSheet("""
                QLineEdit {
                    border: 1px solid #d0d0d0;
                    border-radius: 4px;
                    padding: 4px;
                    background-color: white;
                    font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
                    font-size: 10px;
                    color: #333333;
                    min-width: 100px;
                }
                QLineEdit:focus {
                    border: 2px solid #2196F3;
                }
            """)
            
            # 连接信号
            input_field.textChanged.connect(self.on_nav2_rvt_changed)
            input_field.textChanged.connect(self.validate_hex_input)
            input_field.editingFinished.connect(self.auto_pad_hex_input)
            
            nav2_rvt_grid.addWidget(input_field, row, col + 1)
            
            # 存储输入框引用
            self.nav2_rvt_inputs[name] = input_field
        
        # 设置滚动区域的内容
        rvt_scroll_area.setWidget(rvt_scroll_content)
        nav2_rvt_layout.addWidget(rvt_scroll_area)
        
        # NAV2-RTC消息的专用输入框
        self.nav2_rtc_widget = QWidget()
        nav2_rtc_layout = QVBoxLayout(self.nav2_rtc_widget)
        nav2_rtc_layout.setContentsMargins(0, 0, 0, 0)
        nav2_rtc_layout.setSpacing(5)
        
        # NAV2-RTC标题
        nav2_rtc_title = QLabel("NAV2-RTC 消息有效载荷 (接收机 RTC 时间信息):")
        nav2_rtc_title.setStyleSheet("""
            QLabel {
                font-size: 12px;
                font-weight: bold;
                color: #333333;
                background-color: #fce4ec;
                border: 1px solid #f48fb1;
                border-radius: 4px;
                padding: 5px;
            }
        """)
        nav2_rtc_layout.addWidget(nav2_rtc_title)
        
        # 创建滚动区域来容纳所有字段
        rtc_scroll_area = QScrollArea()
        rtc_scroll_area.setWidgetResizable(True)
        rtc_scroll_area.setMaximumHeight(300)  # 限制最大高度
        rtc_scroll_area.setStyleSheet("""
            QScrollArea {
                border: 1px solid #d0d0d0;
                border-radius: 4px;
                background-color: white;
            }
        """)
        
        # 创建滚动区域的内容部件
        rtc_scroll_content = QWidget()
        nav2_rtc_grid = QGridLayout(rtc_scroll_content)
        nav2_rtc_grid.setSpacing(6)
        nav2_rtc_grid.setContentsMargins(10, 10, 10, 10)
        
        # 定义NAV2-RTC字段信息
        nav2_rtc_fields = [
            # 偏移, 数据类型, 最大长度, 名称, 单位, 描述
            (0, "I4", 8, "dtRtcTow", "ms", "RTC 时间误差,整数毫秒部分"),
            (4, "I4", 8, "dtRtcTowSubms", "ms", "RTC 时间误差,小数毫秒部分"),
            (8, "I4", 8, "rtcTow", "ms", "RTC 时间的整数毫秒"),
            (12, "I4", 8, "rtcTowSubms", "ms", "RTC 时间的小数毫秒"),
            (16, "I2", 4, "wn", "-", "RTC 时间,GPS 周数"),
            (18, "U1", 2, "res1", "-", "保留"),
            (19, "I1", 2, "leapSec", "s", "GPS 闰秒"),
            (20, "I4", 8, "dfRtc", "Hz", "RTC 晶振频偏"),
            (24, "U1", 2, "dfRtcFlag", "-", "RTC 晶振频偏的计算有效标志"),
            (25, "U1", 2, "rtcSrc", "-", "RTC 时间校准的数据源"),
            (26, "I2", 4, "res2", "-", "保留"),
            (28, "I4", 8, "res3", "-", "保留")
        ]
        
        # 创建输入框字典
        self.nav2_rtc_inputs = {}
        
        # 创建所有字段的输入框
        for i, (offset, data_type, max_length, name, unit, description) in enumerate(nav2_rtc_fields):
            row = i // 2  # 每行2个字段
            col = (i % 2) * 2  # 每2列为一组
            
            # 字段标签
            label_text = f"{name} ({description}):"
            label = QLabel(label_text)
            label.setStyleSheet("""
                QLabel {
                    font-size: 10px;
                    color: #333333;
                    background-color: transparent;
                    border: none;
                }
            """)
            label.setWordWrap(True)
            nav2_rtc_grid.addWidget(label, row, col)
            
            # 输入框
            input_field = QLineEdit()
            input_field.setPlaceholderText(f"输入{max_length}位16进制数，留空默认为0")
            input_field.setMaxLength(max_length)
            input_field.setStyleSheet("""
                QLineEdit {
                    border: 1px solid #d0d0d0;
                    border-radius: 4px;
                    padding: 4px;
                    background-color: white;
                    font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
                    font-size: 10px;
                    color: #333333;
                    min-width: 100px;
                }
                QLineEdit:focus {
                    border: 2px solid #2196F3;
                }
            """)
            
            # 连接信号
            input_field.textChanged.connect(self.on_nav2_rtc_changed)
            input_field.textChanged.connect(self.validate_hex_input)
            input_field.editingFinished.connect(self.auto_pad_hex_input)
            
            nav2_rtc_grid.addWidget(input_field, row, col + 1)
            
            # 存储输入框引用
            self.nav2_rtc_inputs[name] = input_field
        
        # 设置滚动区域的内容
        rtc_scroll_area.setWidget(rtc_scroll_content)
        nav2_rtc_layout.addWidget(rtc_scroll_area)
        
        # NAV2-SAT消息的专用输入框
        self.nav2_sat_widget = QWidget()
        nav2_sat_layout = QVBoxLayout(self.nav2_sat_widget)
        nav2_sat_layout.setContentsMargins(0, 0, 0, 0)
        nav2_sat_layout.setSpacing(5)
        
        # NAV2-SAT标题
        nav2_sat_title = QLabel("NAV2-SAT 消息有效载荷 (接收机所接收到的卫星信息):")
        nav2_sat_title.setStyleSheet("""
            QLabel {
                font-size: 12px;
                font-weight: bold;
                color: #333333;
                background-color: #e0f2f1;
                border: 1px solid #4db6ac;
                border-radius: 4px;
                padding: 5px;
            }
        """)
        nav2_sat_layout.addWidget(nav2_sat_title)
        
        # 固定部分字段
        fixed_fields_frame = QFrame()
        fixed_fields_frame.setStyleSheet("""
            QFrame {
                border: 2px solid #4db6ac;
                border-radius: 8px;
                background-color: #f8fdfc;
                margin: 4px;
                padding: 8px;
            }
        """)
        fixed_fields_layout = QVBoxLayout(fixed_fields_frame)
        fixed_fields_layout.setSpacing(8)
        fixed_fields_layout.setContentsMargins(8, 8, 8, 8)
        
        fixed_fields_title = QLabel("固定部分 (12字节)")
        fixed_fields_title.setStyleSheet("""
            QLabel {
                font-size: 12px;
                font-weight: bold;
                color: #00695c;
                background-color: #e3f2fd;
                border: 1px solid #4db6ac;
                border-radius: 6px;
                padding: 6px 12px;
                margin: 2px;
            }
        """)
        fixed_fields_layout.addWidget(fixed_fields_title)
        
        # 固定字段网格布局
        fixed_fields_grid = QGridLayout()
        fixed_fields_grid.setSpacing(6)
        fixed_fields_grid.setContentsMargins(10, 5, 10, 10)
        
        # 定义固定字段信息
        nav2_sat_fixed_fields = [
            # 偏移, 数据类型, 最大长度, 名称, 单位, 描述
            (0, "U4", 8, "tow", "ms", "GPS时间, 周内时"),
            (4, "U1", 2, "numViewTot", "-", "可见卫星总数"),
            (5, "U1", 2, "numFixTot", "-", "用于定位的卫星总数"),
            (6, "U1", 2, "res1", "-", "保留"),
            (7, "U1", 2, "res2", "-", "保留"),
            (8, "U4", 8, "res3", "-", "保留")
        ]
        
        # 创建固定字段输入框字典
        self.nav2_sat_fixed_inputs = {}
        
        # 创建固定字段的输入框
        for i, (offset, data_type, max_length, name, unit, description) in enumerate(nav2_sat_fixed_fields):
            row = i // 2  # 每行2个字段
            col = (i % 2) * 2  # 每2列为一组
            
            # 字段标签
            label_text = f"{name} ({description})"
            label = QLabel(label_text)
            label.setStyleSheet("""
            QLabel {
                    font-size: 10px;
                    color: #00695c;
                    background-color: #e8f4fd;
                    border: 1px solid #4db6ac;
                    border-radius: 4px;
                    padding: 4px 8px;
                    margin: 1px;
                    font-weight: 500;
                }
            """)
            label.setWordWrap(True)
            label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            fixed_fields_grid.addWidget(label, row, col)
            
            # 输入框
            input_field = QLineEdit()
            input_field.setPlaceholderText(f"{max_length}位16进制")
            input_field.setMaxLength(max_length)
            input_field.setStyleSheet("""
                QLineEdit {
                    border: 2px solid #4db6ac;
                    border-radius: 6px;
                    padding: 6px 8px;
                    background-color: white;
                    font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
                    font-size: 10px;
                    color: #333333;
                    min-width: 110px;
                    min-height: 20px;
                }
                QLineEdit:focus {
                    border: 2px solid #2196F3;
                    background-color: #fafafa;
                }
                QLineEdit:hover {
                    border: 2px solid #26a69a;
                }
            """)
            
            # 连接信号
            input_field.textChanged.connect(self.on_nav2_sat_changed)
            input_field.textChanged.connect(self.validate_hex_input)
            input_field.editingFinished.connect(self.auto_pad_hex_input)
            
            # 特殊处理numViewTot字段，用于动态控制卫星数量
            if name == "numViewTot":
                input_field.textChanged.connect(self.on_satellite_count_changed)
                input_field.editingFinished.connect(self.on_satellite_count_finished)
            
            fixed_fields_grid.addWidget(input_field, row, col + 1)
            
            # 存储输入框引用
            self.nav2_sat_fixed_inputs[name] = input_field
        
        fixed_fields_layout.addLayout(fixed_fields_grid)
        nav2_sat_layout.addWidget(fixed_fields_frame)
        
        # 卫星信息重复部分
        self.satellite_fields_frame = QFrame()
        self.satellite_fields_frame.setStyleSheet("""
            QFrame {
                border: 2px solid #4db6ac;
                border-radius: 8px;
                background-color: #f8fdfc;
                margin: 4px;
                padding: 8px;
            }
        """)
        self.satellite_fields_layout = QVBoxLayout(self.satellite_fields_frame)
        self.satellite_fields_layout.setSpacing(8)
        self.satellite_fields_layout.setContentsMargins(8, 8, 8, 8)
        
        self.satellite_fields_title = QLabel("卫星信息 (0颗卫星):")
        self.satellite_fields_title.setStyleSheet("""
            QLabel {
                font-size: 12px;
                font-weight: bold;
                color: #00695c;
                background-color: #e3f2fd;
                border: 1px solid #4db6ac;
                border-radius: 6px;
                padding: 6px 12px;
                margin: 2px;
            }
        """)
        self.satellite_fields_layout.addWidget(self.satellite_fields_title)
        
        # 卫星字段的滚动区域
        self.satellite_scroll_area = QScrollArea()
        self.satellite_scroll_area.setWidgetResizable(True)
        self.satellite_scroll_area.setMaximumHeight(300)  # 统一最大高度
        self.satellite_scroll_area.setMinimumHeight(150)  # 统一最小高度
        self.satellite_scroll_area.setStyleSheet("""
            QScrollArea {
                border: 2px solid #4db6ac;
                border-radius: 6px;
                background-color: white;
                margin: 2px;
            }
            QScrollBar:vertical {
                background-color: #f0f0f0;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background-color: #4db6ac;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #26a69a;
            }
        """)
        
        # 卫星字段的内容部件
        self.satellite_scroll_content = QWidget()
        self.satellite_grid = QGridLayout(self.satellite_scroll_content)
        self.satellite_grid.setSpacing(8)
        self.satellite_grid.setContentsMargins(12, 12, 12, 12)
        
        self.satellite_scroll_area.setWidget(self.satellite_scroll_content)
        self.satellite_fields_layout.addWidget(self.satellite_scroll_area)
        
        # 将卫星信息框架添加到主布局
        nav2_sat_layout.addWidget(self.satellite_fields_frame)
        
        # 存储卫星输入框的字典列表
        self.nav2_sat_satellite_inputs = []
        
        # NAV2-SIG 卫星信号信息组件
        self.nav2_sig_widget = QFrame()
        self.nav2_sig_widget.setStyleSheet("""
            QFrame {
                border: 2px solid #ff9800;
                border-radius: 8px;
                background-color: #fff3e0;
                margin: 4px;
                padding: 8px;
            }
        """)
        nav2_sig_layout = QVBoxLayout(self.nav2_sig_widget)
        nav2_sig_layout.setSpacing(8)
        nav2_sig_layout.setContentsMargins(8, 8, 8, 8)
        
        # NAV2-SIG标题
        nav2_sig_title = QLabel("NAV2-SIG 卫星信号信息")
        nav2_sig_title.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: #e65100;
                background-color: #ffcc02;
                border: 1px solid #ff9800;
                border-radius: 6px;
                padding: 8px 16px;
                margin: 2px;
            }
        """)
        nav2_sig_layout.addWidget(nav2_sig_title)
        
        # 固定部分字段
        sig_fixed_fields_frame = QFrame()
        sig_fixed_fields_frame.setStyleSheet("""
            QFrame {
                border: 2px solid #ff9800;
                border-radius: 8px;
                background-color: #fff8e1;
                margin: 4px;
                padding: 8px;
            }
        """)
        sig_fixed_fields_layout = QVBoxLayout(sig_fixed_fields_frame)
        sig_fixed_fields_layout.setSpacing(8)
        sig_fixed_fields_layout.setContentsMargins(8, 8, 8, 8)
        
        sig_fixed_fields_title = QLabel("固定部分 (8字节)")
        sig_fixed_fields_title.setStyleSheet("""
            QLabel {
                font-size: 12px;
                font-weight: bold;
                color: #e65100;
                background-color: #ffcc02;
                border: 1px solid #ff9800;
                border-radius: 6px;
                padding: 6px 12px;
                margin: 2px;
            }
        """)
        sig_fixed_fields_layout.addWidget(sig_fixed_fields_title)
        
        # 固定字段网格布局
        sig_fixed_fields_grid = QGridLayout()
        sig_fixed_fields_grid.setSpacing(6)
        sig_fixed_fields_grid.setContentsMargins(10, 5, 10, 10)
        
        # 定义固定字段信息
        nav2_sig_fixed_fields = [
            # 偏移, 数据类型, 最大长度, 名称, 单位, 描述
            (0, "U4", 8, "tow", "ms", "GPS时间, 周内时"),
            (4, "U1", 2, "res1", "-", "保留"),
            (5, "U1", 2, "numTrkTot", "-", "跟踪信号总数"),
            (6, "U1", 2, "numFixTot", "-", "用于定位的信号总数"),
            (7, "U1", 2, "res2", "-", "保留")
        ]
        
        # 创建固定字段输入框字典
        self.nav2_sig_fixed_inputs = {}
        
        # 创建固定字段的输入框
        for i, (offset, data_type, max_length, name, unit, description) in enumerate(nav2_sig_fixed_fields):
            row = i // 2  # 每行2个字段
            col = (i % 2) * 2  # 每2列为一组
            
            # 字段标签
            label_text = f"{name} ({description})"
            label = QLabel(label_text)
            label.setStyleSheet("""
                QLabel {
                    font-size: 10px;
                    color: #e65100;
                    background-color: #ffecb3;
                    border: 1px solid #ff9800;
                    border-radius: 4px;
                    padding: 4px 8px;
                    margin: 1px;
                    font-weight: 500;
                }
            """)
            label.setWordWrap(True)
            label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            sig_fixed_fields_grid.addWidget(label, row, col)
            
            # 输入框
            input_field = QLineEdit()
            input_field.setPlaceholderText(f"{max_length}位16进制")
            input_field.setMaxLength(max_length)
            input_field.setStyleSheet("""
                QLineEdit {
                    border: 2px solid #ff9800;
                    border-radius: 6px;
                    padding: 6px 8px;
                    background-color: white;
                    font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
                    font-size: 10px;
                    color: #333333;
                    min-width: 110px;
                    min-height: 20px;
                }
                QLineEdit:focus {
                    border: 2px solid #2196F3;
                    background-color: #fafafa;
                }
                QLineEdit:hover {
                    border: 2px solid #ffb74d;
                }
            """)
            
            # 连接信号
            input_field.textChanged.connect(self.on_nav2_sig_changed)
            input_field.textChanged.connect(self.validate_hex_input)
            input_field.editingFinished.connect(self.auto_pad_hex_input)
            
            # 特殊处理numTrkTot字段，用于动态控制信号数量
            if name == "numTrkTot":
                input_field.textChanged.connect(self.on_signal_count_changed)
                input_field.editingFinished.connect(self.on_signal_count_finished)
            
            sig_fixed_fields_grid.addWidget(input_field, row, col + 1)
            
            # 存储输入框引用
            self.nav2_sig_fixed_inputs[name] = input_field
        
        sig_fixed_fields_layout.addLayout(sig_fixed_fields_grid)
        nav2_sig_layout.addWidget(sig_fixed_fields_frame)
        
        # 信号信息重复部分
        self.signal_fields_frame = QFrame()
        self.signal_fields_frame.setStyleSheet("""
            QFrame {
                border: 2px solid #ff9800;
                border-radius: 8px;
                background-color: #fff8e1;
                margin: 4px;
                padding: 8px;
            }
        """)
        self.signal_fields_layout = QVBoxLayout(self.signal_fields_frame)
        self.signal_fields_layout.setSpacing(8)
        self.signal_fields_layout.setContentsMargins(8, 8, 8, 8)
        
        self.signal_fields_title = QLabel("信号信息 (0个信号):")
        self.signal_fields_title.setStyleSheet("""
            QLabel {
                font-size: 12px;
                font-weight: bold;
                color: #e65100;
                background-color: #ffcc02;
                border: 1px solid #ff9800;
                border-radius: 6px;
                padding: 6px 12px;
                margin: 2px;
            }
        """)
        self.signal_fields_layout.addWidget(self.signal_fields_title)
        
        # 信号字段的滚动区域
        self.signal_scroll_area = QScrollArea()
        self.signal_scroll_area.setWidgetResizable(True)
        self.signal_scroll_area.setMaximumHeight(300)  # 统一最大高度
        self.signal_scroll_area.setMinimumHeight(150)  # 统一最小高度
        self.signal_scroll_area.setStyleSheet("""
            QScrollArea {
                border: 2px solid #ff9800;
                border-radius: 6px;
                background-color: white;
                margin: 2px;
            }
            QScrollBar:vertical {
                background-color: #f0f0f0;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background-color: #ff9800;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #f57c00;
            }
        """)
        
        # 信号字段的内容部件
        self.signal_scroll_content = QWidget()
        self.signal_grid = QGridLayout(self.signal_scroll_content)
        self.signal_grid.setSpacing(8)
        self.signal_grid.setContentsMargins(12, 12, 12, 12)
        
        self.signal_scroll_area.setWidget(self.signal_scroll_content)
        self.signal_fields_layout.addWidget(self.signal_scroll_area)
        
        # 将信号信息框架添加到主布局
        nav2_sig_layout.addWidget(self.signal_fields_frame)
        
        # 存储信号输入框的字典列表
        self.nav2_sig_signal_inputs = []
        
        # 初始时隐藏九个专用输入框
        self.nav2_dop_widget.hide()
        self.nav2_sol_widget.hide()
        self.nav2_pvh_widget.hide()
        self.nav2_timeutc_widget.hide()
        self.nav2_clk_widget.hide()
        self.nav2_rvt_widget.hide()
        self.nav2_rtc_widget.hide()
        self.nav2_sat_widget.hide()
        self.nav2_sig_widget.hide()
        
        # 将两个输入方式添加到有效载荷布局中
        payload_layout.addWidget(self.payload_input)
        payload_layout.addWidget(self.nav2_dop_widget)
        payload_layout.addWidget(self.nav2_sol_widget)
        payload_layout.addWidget(self.nav2_pvh_widget)
        payload_layout.addWidget(self.nav2_timeutc_widget)
        payload_layout.addWidget(self.nav2_clk_widget)
        payload_layout.addWidget(self.nav2_rvt_widget)
        payload_layout.addWidget(self.nav2_rtc_widget)
        payload_layout.addWidget(self.nav2_sat_widget)
        payload_layout.addWidget(self.nav2_sig_widget)
        
        fields_grid.addWidget(payload_widget, 4, 1)
        
        # 字段6: 校验值 (自动计算)
        checksum_label = QLabel("校验值 (4字节):")
        checksum_label.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: #333333;
                background-color: transparent;
                border: none;
            }
        """)
        fields_grid.addWidget(checksum_label, 5, 0)
        
        self.checksum_input = QLineEdit("自动计算")
        self.checksum_input.setReadOnly(True)
        self.checksum_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #d0d0d0;
                border-radius: 4px;
                padding: 8px;
                background-color: #f0f0f0;
                font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
                font-size: 12px;
                color: #666666;
            }
        """)
        fields_grid.addWidget(self.checksum_input, 5, 1)
        
        packet_layout.addLayout(fields_grid)
        
        # 帮助提示
        help_label = QLabel("提示: 消息类和消息ID已预设常用选项，如需自定义值请直接输入十六进制格式（如: 0xFF）")
        help_label.setStyleSheet("""
            QLabel {
                font-size: 11px;
                color: #666666;
                background-color: transparent;
                border: none;
                padding: 5px;
                font-style: italic;
            }
        """)
        packet_layout.addWidget(help_label)
        
        layout.addWidget(packet_frame)
        
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
        self.send_btn = QPushButton("发送数据包")
        self.send_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: bold;
                min-width: 100px;
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
        
        # 停止按钮
        self.stop_btn = QPushButton("停止自动发送")
        self.stop_btn.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: bold;
                min-width: 100px;
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
        
        # 清空按钮
        self.clear_btn = QPushButton("清空")
        self.clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 12px 24px;
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
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        # 初始化自动发送定时器
        self.auto_send_timer = QTimer()
        self.auto_send_timer.timeout.connect(self.auto_send_data)
        self.is_auto_sending = False
        
        # 先初始化消息ID选项（根据默认的消息类）
        self.on_class_changed()
        
        # 然后初始化数据包预览（使用静默模式）
        self.update_packet_preview(silent=True)
    
    def send_data(self):
        """发送CSIP数据包"""
        try:
            # 构建CSIP数据包
            packet_data = self.build_csip_packet()
            if not packet_data:
                return
                
            auto_mode = self.auto_send_check.isChecked()
            interval = self.interval_spin.value()
            
            # 发送数据包（十六进制格式）
            self.send_data_signal.emit(self.port_name, packet_data, True, auto_mode, interval)
            
            if auto_mode:
                # 开始自动发送
                self.start_auto_send()
            else:
                QMessageBox.information(self, "提示", "CSIP数据包已发送")
                
        except Exception as e:
            QMessageBox.critical(self, "错误", f"发送数据包失败: {str(e)}")
    
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
        self.class_combo.setCurrentText("0x11 - NAV2 (导航结果:位置、速度、时间)")
        self.payload_input.clear()
        
        # 清空NAV2-DOP输入框
        self.pDop_input.clear()
        self.hDop_input.clear()
        self.vDop_input.clear()
        self.nDop_input.clear()
        self.eDop_input.clear()
        self.tDop_input.clear()
        
        # 清空NAV2-SOL输入框
        for input_field in self.nav2_sol_inputs.values():
            input_field.clear()
        
        # 清空NAV2-PVH输入框
        for input_field in self.nav2_pvh_inputs.values():
            input_field.clear()
        
        # 清空NAV2-TIMEUTC输入框
        for input_field in self.nav2_timeutc_inputs.values():
            input_field.clear()
        
        # 清空NAV2-CLK输入框
        for input_field in self.nav2_clk_inputs.values():
            input_field.clear()
        
        # 清空NAV2-RVT输入框
        for input_field in self.nav2_rvt_inputs.values():
            input_field.clear()
        
        # 清空NAV2-RTC输入框
        for input_field in self.nav2_rtc_inputs.values():
            input_field.clear()
        
        # 清空NAV2-SAT输入框
        for input_field in self.nav2_sat_fixed_inputs.values():
            input_field.clear()
        for satellite_inputs in self.nav2_sat_satellite_inputs:
            for input_field in satellite_inputs.values():
                input_field.clear()
        self.nav2_sat_satellite_inputs.clear()
        self.update_satellite_fields(0)
        
        # 清空NAV2-SIG输入框
        for input_field in self.nav2_sig_fixed_inputs.values():
            input_field.clear()
        for signal_inputs in self.nav2_sig_signal_inputs:
            for input_field in signal_inputs.values():
                input_field.clear()
        self.nav2_sig_signal_inputs.clear()
        self.update_signal_fields(0)
        
        # 重新设置消息ID选项
        self.on_class_changed()
        
        # 清空后也更新预览（使用静默模式）
        self.update_packet_preview(silent=True)
    
    def get_data(self):
        """获取当前数据"""
        return self.payload_input.toPlainText()
    
    def set_data(self, data):
        """设置数据"""
        self.payload_input.setPlainText(data)
        self.update_packet_preview() # 设置后也更新预览
    
    def closeEvent(self, event):
        """窗口关闭事件"""
        self.stop_auto_send()
        event.accept() 

    def build_csip_packet(self, silent=False):
        """构建CSIP数据包"""
        try:
            # 解析用户输入（使用静默模式）
            class_value = self.parse_hex_byte(self.class_combo.currentText().split(' - ')[0], silent)
            id_value = self.parse_hex_byte(self.id_combo.currentText().split(' - ')[0], silent)
            
            # 根据消息类和消息ID设置有效载荷输入框的可见性
            if class_value == 0x11 and id_value == 0x01: # NAV2-DOP
                self.nav2_dop_widget.show()
                self.nav2_sol_widget.hide()
                self.nav2_pvh_widget.hide()
                self.nav2_timeutc_widget.hide()
                self.nav2_clk_widget.hide()
                self.nav2_rvt_widget.hide()
                self.nav2_rtc_widget.hide()
                self.nav2_sat_widget.hide()
                self.payload_input.hide() # 隐藏默认的payload输入框
            elif class_value == 0x11 and id_value == 0x02: # NAV2-SOL
                self.nav2_dop_widget.hide()
                self.nav2_sol_widget.show()
                self.nav2_pvh_widget.hide()
                self.nav2_timeutc_widget.hide()
                self.nav2_clk_widget.hide()
                self.nav2_rvt_widget.hide()
                self.nav2_rtc_widget.hide()
                self.nav2_sat_widget.hide()
                self.payload_input.hide() # 隐藏默认的payload输入框
            elif class_value == 0x11 and id_value == 0x03: # NAV2-PVH
                self.nav2_dop_widget.hide()
                self.nav2_sol_widget.hide()
                self.nav2_pvh_widget.show()
                self.nav2_timeutc_widget.hide()
                self.nav2_clk_widget.hide()
                self.nav2_rvt_widget.hide()
                self.nav2_rtc_widget.hide()
                self.nav2_sat_widget.hide()
                self.payload_input.hide() # 隐藏默认的payload输入框
            elif class_value == 0x11 and id_value == 0x05: # NAV2-TIMEUTC
                self.nav2_dop_widget.hide()
                self.nav2_sol_widget.hide()
                self.nav2_pvh_widget.hide()
                self.nav2_timeutc_widget.show()
                self.nav2_clk_widget.hide()
                self.nav2_rvt_widget.hide()
                self.nav2_rtc_widget.hide()
                self.nav2_sat_widget.hide()
                self.payload_input.hide() # 隐藏默认的payload输入框
            elif class_value == 0x11 and id_value == 0x07: # NAV2-CLK
                self.nav2_dop_widget.hide()
                self.nav2_sol_widget.hide()
                self.nav2_pvh_widget.hide()
                self.nav2_timeutc_widget.hide()
                self.nav2_clk_widget.show()
                self.nav2_rvt_widget.hide()
                self.nav2_rtc_widget.hide()
                self.nav2_sat_widget.hide()
                self.payload_input.hide()
            elif class_value == 0x11 and id_value == 0x08: # NAV2-RVT
                self.nav2_dop_widget.hide()
                self.nav2_sol_widget.hide()
                self.nav2_pvh_widget.hide()
                self.nav2_timeutc_widget.hide()
                self.nav2_clk_widget.hide()
                self.nav2_rvt_widget.show()
                self.nav2_rtc_widget.hide()
                self.nav2_sat_widget.hide()
                self.payload_input.hide()
            elif class_value == 0x11 and id_value == 0x09: # NAV2-RTC
                self.nav2_dop_widget.hide()
                self.nav2_sol_widget.hide()
                self.nav2_pvh_widget.hide()
                self.nav2_timeutc_widget.hide()
                self.nav2_clk_widget.hide()
                self.nav2_rvt_widget.hide()
                self.nav2_rtc_widget.show()
                self.nav2_sat_widget.hide()
                self.payload_input.hide()
            elif class_value == 0x11 and id_value == 0x04: # NAV2-SAT
                self.nav2_dop_widget.hide()
                self.nav2_sol_widget.hide()
                self.nav2_pvh_widget.hide()
                self.nav2_timeutc_widget.hide()
                self.nav2_clk_widget.hide()
                self.nav2_rvt_widget.hide()
                self.nav2_rtc_widget.hide()
                self.nav2_sat_widget.show()
                self.payload_input.hide()
            else:
                self.nav2_dop_widget.hide()
                self.nav2_sol_widget.hide()
                self.nav2_pvh_widget.hide()
                self.nav2_timeutc_widget.hide()
                self.nav2_clk_widget.hide()
                self.nav2_rvt_widget.hide()
                self.nav2_rtc_widget.hide()
                self.nav2_sat_widget.hide()
                self.payload_input.show() # 显示默认的payload输入框

            # 获取有效载荷数据
            if self.nav2_dop_widget.isVisible():
                # NAV2-DOP消息：每个字段4字节，总共6个字段
                nav2_dop_fields = [
                    self.pDop_input.text().strip(),
                    self.hDop_input.text().strip(),
                    self.vDop_input.text().strip(),
                    self.nDop_input.text().strip(),
                    self.eDop_input.text().strip(),
                    self.tDop_input.text().strip()
                ]
                
                # 解析每个字段的16进制值并转换为4字节
                # 空字段会自动处理为全0
                payload_data = []
                for field in nav2_dop_fields:
                    field_bytes = self.parse_nav2_dop_field(field, silent)
                    if field_bytes is None:
                        return None
                    payload_data.extend(field_bytes)
            elif self.nav2_sol_widget.isVisible():
                # NAV2-SOL消息：根据字段类型解析
                payload_data = self.parse_nav2_sol_payload(silent)
                if payload_data is None:
                    return None
            elif self.nav2_pvh_widget.isVisible():
                # NAV2-PVH消息：根据字段类型解析
                payload_data = self.parse_nav2_pvh_payload(silent)
                if payload_data is None:
                    return None
            elif self.nav2_timeutc_widget.isVisible():
                # NAV2-TIMEUTC消息：根据字段类型解析
                payload_data = self.parse_nav2_timeutc_payload(silent)
                if payload_data is None:
                    return None
            elif self.nav2_clk_widget.isVisible():
                # NAV2-CLK消息：根据字段类型解析
                payload_data = self.parse_nav2_clk_payload(silent)
                if payload_data is None:
                    return None
            elif self.nav2_rvt_widget.isVisible():
                # NAV2-RVT消息：根据字段类型解析
                payload_data = self.parse_nav2_rvt_payload(silent)
                if payload_data is None:
                    return None
            elif self.nav2_rtc_widget.isVisible():
                # NAV2-RTC消息：根据字段类型解析
                payload_data = self.parse_nav2_rtc_payload(silent)
                if payload_data is None:
                    return None
            elif self.nav2_sat_widget.isVisible():
                # NAV2-SAT消息：根据字段类型解析
                payload_data = self.parse_nav2_sat_payload(silent)
                if payload_data is None:
                    return None
            elif self.nav2_sig_widget.isVisible():
                # NAV2-SIG消息：根据字段类型解析
                payload_data = self.parse_nav2_sig_payload(silent)
                if payload_data is None:
                    return None
            else:
                # 使用默认的payload输入框
                payload_text = self.payload_input.toPlainText().strip()
            if not payload_text:
                payload_data = []
            else:
                payload_data = self.parse_hex_payload(payload_text, silent)
                if payload_data is None:
                    return None
                
                # 检查有效载荷长度是否为4的倍数
                if len(payload_data) % 4 != 0:
                    if not silent:
                        QMessageBox.warning(self, "警告", "有效载荷长度必须是4的倍数")
                    return None
            
            # 计算有效载荷长度（字节数）
            payload_length = self.calculate_payload_length(class_value, id_value, silent)
            
            # 计算校验值
            checksum = self.calculate_checksum(class_value, id_value, payload_length, payload_data)
            
            # 构建完整数据包
            packet = []
            
            # 字段1: 消息头 (固定值: 0xBA, 0xCE)
            packet.extend([0xBA, 0xCE])
            
            # 字段2: 有效载荷长度 (2字节，小端序)
            packet.extend([payload_length & 0xFF, (payload_length >> 8) & 0xFF])
            
            # 字段3: 消息类 (1字节)
            packet.append(class_value)
            
            # 字段4: 消息ID (1字节)
            packet.append(id_value)
            
            # 字段5: 有效载荷
            packet.extend(payload_data)
            
            # 字段6: 校验值 (4字节，小端序)
            packet.extend([checksum & 0xFF, (checksum >> 8) & 0xFF, 
                          (checksum >> 16) & 0xFF, (checksum >> 24) & 0xFF])
            
            
            
            return packet
            
        except Exception as e:
            # 静默处理错误，不显示警告
            return None
    
    def parse_hex_byte(self, text, silent=False):
        """解析十六进制字节值"""
        try:
            text = text.strip()
            # 处理下拉框格式: "0x11 - NAV2 (导航结果:位置、速度、时间)"
            if ' - ' in text:
                text = text.split(' - ')[0]
            
            if text.startswith('0x') or text.startswith('0X'):
                text = text[2:]
            value = int(text, 16)
            if 0 <= value <= 255:
                return value
            else:
                if not silent:
                    QMessageBox.warning(self, "警告", "字节值必须在0x00到0xFF之间")
                return None
        except ValueError:
            if not silent:
                QMessageBox.warning(self, "警告", "请输入有效的十六进制值")
            return None
    
    def parse_hex_payload(self, text, silent=False):
        """解析十六进制有效载荷"""
        try:
            # 清理输入文本
            text = text.strip()
            if not text:
                return []
            
            # 分割并解析十六进制值
            hex_values = []
            for part in text.split():
                part = part.strip()
                if part.startswith('0x') or part.startswith('0X'):
                    part = part[2:]
                if part:
                    value = int(part, 16)
                    if 0 <= value <= 255:
                        hex_values.append(value)
                    else:
                        if not silent:
                            QMessageBox.warning(self, "警告", f"有效载荷值 {part} 超出范围")
                        return None
            
            return hex_values
            
        except ValueError:
            if not silent:
                QMessageBox.warning(self, "警告", "请输入有效的十六进制有效载荷")
            return None
    
    def parse_nav2_dop_field(self, text, silent=False):
        """解析NAV2-DOP字段的16进制输入，转换为4字节数据"""
        try:
            # 清理输入文本
            text = text.strip()
            
            # 如果为空，默认为全0
            if not text:
                return [0x00, 0x00, 0x00, 0x00]
            
            # 移除0x前缀
            if text.startswith('0x') or text.startswith('0X'):
                text = text[2:]
            
            # 检查长度是否超过8位
            if len(text) > 8:
                if not silent:
                    QMessageBox.warning(self, "警告", f"字段 {text} 不能超过8位16进制数")
                return None
            
            # 在封装时自动补零到8位（不在输入框内显示）
            text = text.zfill(8)
            
            # 解析为32位整数
            value = int(text, 16)
            
            # 转换为4字节（小端序）
            bytes_data = [
                value & 0xFF,           # 最低字节
                (value >> 8) & 0xFF,   # 第二字节
                (value >> 16) & 0xFF,  # 第三字节
                (value >> 24) & 0xFF   # 最高字节
            ]
            
            return bytes_data
            
        except ValueError:
            if not silent:
                QMessageBox.warning(self, "警告", f"字段 {text} 不是有效的16进制数")
            return None
    
    def parse_nav2_sol_field(self, text, silent=False):
        """解析NAV2-SOL字段的16进制输入，转换为4字节数据"""
        try:
            # 清理输入文本
            text = text.strip()
            
            # 如果为空，默认为全0
            if not text:
                return [0x00, 0x00, 0x00, 0x00]
            
            # 移除0x前缀
            if text.startswith('0x') or text.startswith('0X'):
                text = text[2:]
            
            # 检查长度是否超过8位
            if len(text) > 8:
                if not silent:
                    QMessageBox.warning(self, "警告", f"字段 {text} 不能超过8位16进制数")
                return None
            
            # 在封装时自动补零到8位（不在输入框内显示）
            text = text.zfill(8)
            
            # 解析为32位整数
            value = int(text, 16)
            
            # 转换为4字节（小端序）
            bytes_data = [
                value & 0xFF,           # 最低字节
                (value >> 8) & 0xFF,   # 第二字节
                (value >> 16) & 0xFF,  # 第三字节
                (value >> 24) & 0xFF   # 最高字节
            ]
            
            return bytes_data
            
        except ValueError:
            if not silent:
                QMessageBox.warning(self, "警告", f"字段 {text} 不是有效的16进制数")
            return None
    
    def parse_nav2_pvh_field(self, text, silent=False):
        """解析NAV2-PVH字段的16进制输入，转换为4字节数据"""
        try:
            # 清理输入文本
            text = text.strip()
            
            # 如果为空，默认为全0
            if not text:
                return [0x00, 0x00, 0x00, 0x00]
            
            # 移除0x前缀
            if text.startswith('0x') or text.startswith('0X'):
                text = text[2:]
            
            # 检查长度是否超过8位
            if len(text) > 8:
                if not silent:
                    QMessageBox.warning(self, "警告", f"字段 {text} 不能超过8位16进制数")
                return None
            
            # 在封装时自动补零到8位（不在输入框内显示）
            text = text.zfill(8)
            
            # 解析为32位整数
            value = int(text, 16)
            
            # 转换为4字节（小端序）
            bytes_data = [
                value & 0xFF,           # 最低字节
                (value >> 8) & 0xFF,   # 第二字节
                (value >> 16) & 0xFF,  # 第三字节
                (value >> 24) & 0xFF   # 最高字节
            ]
            
            return bytes_data
            
        except ValueError:
            if not silent:
                QMessageBox.warning(self, "警告", f"字段 {text} 不是有效的16进制数")
            return None
    
    def calculate_payload_length(self, class_value, id_value, silent=False):
        """计算有效载荷长度（字节数）"""
        try:
            if class_value == 0x11:  # NAV2消息类
                if id_value == 0x01:  # NAV2-DOP
                    return 24  # 固定长度：24字节
                elif id_value == 0x02:  # NAV2-SOL
                    return 72  # 固定长度：72字节
                elif id_value == 0x03:  # NAV2-PVH
                    return 88  # 固定长度：88字节 (根据技术规范)
                elif id_value == 0x04:  # NAV2-SAT
                    # 动态长度：12 + 12×N字节 (N = numViewTot)
                    if hasattr(self, 'nav2_sat_fixed_inputs') and 'numViewTot' in self.nav2_sat_fixed_inputs:
                        num_view_tot_text = self.nav2_sat_fixed_inputs['numViewTot'].text().strip()
                        if num_view_tot_text:
                            try:
                                num_view_tot = int(num_view_tot_text, 16)
                                return 12 + 12 * num_view_tot
                            except ValueError:
                                if not silent:
                                    print(f"无法解析numViewTot值: {num_view_tot_text}")
                                return 12  # 默认只有固定部分
                        else:
                            return 12  # 默认只有固定部分
                    else:
                        return 12  # 默认只有固定部分
                elif id_value == 0x05:  # NAV2-TIMEUTC
                    return 20  # 固定长度：20字节 (根据技术规范)
                elif id_value == 0x06:  # NAV2-SIG
                    # 动态长度：8 + 16×N字节 (N = numTrkTot)
                    if hasattr(self, 'nav2_sig_fixed_inputs') and 'numTrkTot' in self.nav2_sig_fixed_inputs:
                        num_trk_tot_text = self.nav2_sig_fixed_inputs['numTrkTot'].text().strip()
                        if num_trk_tot_text:
                            try:
                                num_trk_tot = int(num_trk_tot_text, 16)
                                return 8 + 16 * num_trk_tot
                            except ValueError:
                                if not silent:
                                    print(f"无法解析numTrkTot值: {num_trk_tot_text}")
                                return 8  # 默认只有固定部分
                        else:
                            return 8  # 默认只有固定部分
                    else:
                        return 8  # 默认只有固定部分
                elif id_value == 0x07:  # NAV2-CLK
                    return 20  # 固定长度：20字节 (根据技术规范)
                elif id_value == 0x08:  # NAV2-RVT
                    return 52  # 固定长度：52字节 (根据技术规范)
                elif id_value == 0x09:  # NAV2-RTC
                    return 32  # 固定长度：32字节 (根据技术规范)
                else:
                    # 其他NAV2消息ID，使用默认payload输入框
                    if hasattr(self, 'payload_input'):
                        payload_text = self.payload_input.toPlainText().strip()
                        if payload_text:
                            payload_data = self.parse_hex_payload(payload_text, silent)
                            if payload_data is not None:
                                return len(payload_data)
                    return 0
            else:
                # 非NAV2消息类，使用默认payload输入框
                if hasattr(self, 'payload_input'):
                    payload_text = self.payload_input.toPlainText().strip()
                    if payload_text:
                        payload_data = self.parse_hex_payload(payload_text, silent)
                        if payload_data is not None:
                            return len(payload_data)
                return 0
                
        except Exception as e:
            if not silent:
                print(f"计算有效载荷长度失败: {str(e)}")
            return 0
    
    def calculate_checksum(self, class_value, id_value, payload_length, payload_data):
        """计算校验值"""
        # 按照算法: ckSum = (id << 24) + (class << 16) + len
        checksum = (id_value << 24) + (class_value << 16) + payload_length
        
        # 累加有效载荷数据（每4字节一组）
        for i in range(0, len(payload_data), 4):
            if i + 3 < len(payload_data):
                # 4字节组成一个字（小端序）
                word = (payload_data[i] | 
                       (payload_data[i + 1] << 8) | 
                       (payload_data[i + 2] << 16) | 
                       (payload_data[i + 3] << 24))
                checksum += word
            else:
                # 处理不足4字节的情况
                remaining = len(payload_data) - i
                word = 0
                for j in range(remaining):
                    word |= payload_data[i + j] << (j * 8)
                checksum += word
        
        return checksum & 0xFFFFFFFF  # 确保是32位无符号整数
    
    def update_packet_preview(self, silent=False):
        """更新数据包预览"""
        try:
            # 检查UI组件是否已经初始化
            if not hasattr(self, 'class_combo') or not hasattr(self, 'id_combo') or not hasattr(self, 'payload_input'):
                return
                
            # 获取当前输入值（使用静默模式）
            class_value = self.parse_hex_byte(self.class_combo.currentText().split(' - ')[0], silent)
            id_value = self.parse_hex_byte(self.id_combo.currentText().split(' - ')[0], silent)
            
            # 如果消息类或消息ID解析失败，不更新预览
            if class_value is None or id_value is None:
                return
                
            # 根据消息类和消息ID设置有效载荷输入框的可见性
            if class_value == 0x11 and id_value == 0x01: # NAV2-DOP
                self.nav2_dop_widget.show()
                self.nav2_sol_widget.hide()
                self.nav2_pvh_widget.hide()
                self.nav2_timeutc_widget.hide()
                self.nav2_clk_widget.hide()
                self.nav2_rvt_widget.hide()
                self.nav2_rtc_widget.hide()
                self.nav2_sat_widget.hide()
                self.payload_input.hide() # 隐藏默认的payload输入框
            elif class_value == 0x11 and id_value == 0x02: # NAV2-SOL
                self.nav2_dop_widget.hide()
                self.nav2_sol_widget.show()
                self.nav2_pvh_widget.hide()
                self.nav2_timeutc_widget.hide()
                self.nav2_clk_widget.hide()
                self.nav2_rvt_widget.hide()
                self.nav2_rtc_widget.hide()
                self.nav2_sat_widget.hide()
                self.payload_input.hide() # 隐藏默认的payload输入框
            elif class_value == 0x11 and id_value == 0x03: # NAV2-PVH
                self.nav2_dop_widget.hide()
                self.nav2_sol_widget.hide()
                self.nav2_pvh_widget.show()
                self.nav2_timeutc_widget.hide()
                self.nav2_clk_widget.hide()
                self.nav2_rvt_widget.hide()
                self.nav2_rtc_widget.hide()
                self.nav2_sat_widget.hide()
                self.payload_input.hide() # 隐藏默认的payload输入框
            elif class_value == 0x11 and id_value == 0x05: # NAV2-TIMEUTC
                self.nav2_dop_widget.hide()
                self.nav2_sol_widget.hide()
                self.nav2_pvh_widget.hide()
                self.nav2_timeutc_widget.show()
                self.nav2_clk_widget.hide()
                self.nav2_rvt_widget.hide()
                self.nav2_rtc_widget.hide()
                self.nav2_sat_widget.hide()
                self.payload_input.hide() # 隐藏默认的payload输入框
            elif class_value == 0x11 and id_value == 0x07: # NAV2-CLK
                self.nav2_dop_widget.hide()
                self.nav2_sol_widget.hide()
                self.nav2_pvh_widget.hide()
                self.nav2_timeutc_widget.hide()
                self.nav2_clk_widget.show()
                self.nav2_rvt_widget.hide()
                self.nav2_rtc_widget.hide()
                self.nav2_sat_widget.hide()
                self.payload_input.hide()
            elif class_value == 0x11 and id_value == 0x08: # NAV2-RVT
                self.nav2_dop_widget.hide()
                self.nav2_sol_widget.hide()
                self.nav2_pvh_widget.hide()
                self.nav2_timeutc_widget.hide()
                self.nav2_clk_widget.hide()
                self.nav2_rvt_widget.show()
                self.nav2_rtc_widget.hide()
                self.nav2_sat_widget.hide()
                self.payload_input.hide()
            elif class_value == 0x11 and id_value == 0x09: # NAV2-RTC
                self.nav2_dop_widget.hide()
                self.nav2_sol_widget.hide()
                self.nav2_pvh_widget.hide()
                self.nav2_timeutc_widget.hide()
                self.nav2_clk_widget.hide()
                self.nav2_rvt_widget.hide()
                self.nav2_rtc_widget.show()
                self.nav2_sat_widget.hide()
                self.payload_input.hide()
            elif class_value == 0x11 and id_value == 0x04: # NAV2-SAT
                self.nav2_dop_widget.hide()
                self.nav2_sol_widget.hide()
                self.nav2_pvh_widget.hide()
                self.nav2_timeutc_widget.hide()
                self.nav2_clk_widget.hide()
                self.nav2_rvt_widget.hide()
                self.nav2_rtc_widget.hide()
                self.nav2_sat_widget.show()
                self.payload_input.hide()
            else:
                self.nav2_dop_widget.hide()
                self.nav2_sol_widget.hide()
                self.nav2_pvh_widget.hide()
                self.nav2_timeutc_widget.hide()
                self.nav2_clk_widget.hide()
                self.nav2_rvt_widget.hide()
                self.nav2_rtc_widget.hide()
                self.nav2_sat_widget.hide()
                self.payload_input.show() # 显示默认的payload输入框

            # 获取有效载荷数据
            if self.nav2_dop_widget.isVisible():
                # NAV2-DOP消息：每个字段4字节，总共6个字段
                nav2_dop_fields = [
                    self.pDop_input.text().strip(),
                    self.hDop_input.text().strip(),
                    self.vDop_input.text().strip(),
                    self.nDop_input.text().strip(),
                    self.eDop_input.text().strip(),
                    self.tDop_input.text().strip()
                ]
                
                # 解析每个字段的16进制值并转换为4字节
                # 空字段会自动处理为全0
                payload_data = []
                for field in nav2_dop_fields:
                    field_bytes = self.parse_nav2_dop_field(field, silent)
                    if field_bytes is None:
                        return None
                    payload_data.extend(field_bytes)
            elif self.nav2_sol_widget.isVisible():
                # NAV2-SOL消息：根据字段类型解析
                payload_data = self.parse_nav2_sol_payload(silent)
                if payload_data is None:
                    return None
            elif self.nav2_pvh_widget.isVisible():
                # NAV2-PVH消息：根据字段类型解析
                payload_data = self.parse_nav2_pvh_payload(silent)
                if payload_data is None:
                    return None
            elif self.nav2_timeutc_widget.isVisible():
                # NAV2-TIMEUTC消息：根据字段类型解析
                payload_data = self.parse_nav2_timeutc_payload(silent)
                if payload_data is None:
                    return None
            elif self.nav2_clk_widget.isVisible():
                # NAV2-CLK消息：根据字段类型解析
                payload_data = self.parse_nav2_clk_payload(silent)
                if payload_data is None:
                    return None
            elif self.nav2_rvt_widget.isVisible():
                # NAV2-RVT消息：根据字段类型解析
                payload_data = self.parse_nav2_rvt_payload(silent)
                if payload_data is None:
                    return None
            elif self.nav2_rtc_widget.isVisible():
                # NAV2-RTC消息：根据字段类型解析
                payload_data = self.parse_nav2_rtc_payload(silent)
                if payload_data is None:
                    return None
            elif self.nav2_sat_widget.isVisible():
                # NAV2-SAT消息：根据字段类型解析
                payload_data = self.parse_nav2_sat_payload(silent)
                if payload_data is None:
                    return None
            elif self.nav2_sig_widget.isVisible():
                # NAV2-SIG消息：根据字段类型解析
                payload_data = self.parse_nav2_sig_payload(silent)
                if payload_data is None:
                    return None
            else:
                # 使用默认的payload输入框
                payload_text = self.payload_input.toPlainText().strip()
            if not payload_text:
                self.length_input.setText("0 字节 (0x0000)")
                self.checksum_input.setText(f"0x{(id_value << 24) + (class_value << 16):08X}")
                return
            
            payload_data = self.parse_hex_payload(payload_text, silent)
            if payload_data is None:
                    return None
            
            # 构建完整数据包
            packet_data = self.build_csip_packet(silent)
            if packet_data:
                # 更新长度和校验值显示
                payload_length = self.calculate_payload_length(class_value, id_value, silent)
                checksum = self.calculate_checksum(class_value, id_value, payload_length, payload_data)
                
                self.length_input.setText(f"{payload_length} 字节 (0x{payload_length:04X})")
                self.checksum_input.setText(f"0x{checksum:08X}")
            else:
                # 即使构建数据包失败，也要显示载荷长度
                payload_length = self.calculate_payload_length(class_value, id_value, silent)
                self.length_input.setText(f"{payload_length} 字节 (0x{payload_length:04X})")
                # 计算只有头部和长度的校验值
                checksum = (id_value << 24) + (class_value << 16) + payload_length
                self.checksum_input.setText(f"0x{checksum:08X}")

        except Exception as e:
            # 静默处理错误，不显示警告
            pass
    

    
    def on_class_changed(self):
        """当消息类改变时，更新消息ID选项"""
        # 暂时断开信号连接，避免在设置选项时触发预览更新
        self.id_combo.currentTextChanged.disconnect()
        
        selected_class = self.class_combo.currentText()
        
        if "NAV2" in selected_class:
            self.id_combo.clear()
            self.id_combo.addItems([
                "0x01 - 几何精度因子 (Geometric Dilution of Precision)",
                "0x02 - ECEF 格式的位置速度 (ECEF format position and velocity)",
                "0x03 - LLA 格式位置,ENU 格式速度 (LLA format position, ENU format velocity)",
                "0x04 - 接收机所接收到的卫星信息 (Receiver's received satellite information)",
                "0x05 - UTC 时间信息 (UTC time information)",
                "0x06 - 接收机所接收到的卫星信号信息 (Receiver's received satellite signal information)",
                "0x07 - 接收机的时间偏差,频率偏差 (Receiver's time bias, frequency bias)",
                "0x08 - 接收机原始时间信息 (Receiver's raw time information)",
                "0x09 - 接收机的RTC时间信息 (Receiver's RTC time information)"
            ])
            self.id_combo.setCurrentText("0x01 - 几何精度因子 (Geometric Dilution of Precision)")
            
            # 当选择NAV2消息类时，检查是否为DOP或SOL消息
            self.check_nav2_dop_visibility()
            
        elif "TIM2" in selected_class:
            self.id_combo.clear()
            self.id_combo.addItems([
                "0x00 - 授时脉冲信息 (Timing pulse information)",
                "0x01 - GPS的时间信息输出 (GPS time information output)",
                "0x02 - BDS 的时间信息输出 (BDS time information output)",
                "0x03 - GLN 的时间信息输出 (GLONASS time information output)",
                "0x04 - GAL 的时间信息输出 (Galileo time information output)",
                "0x05 - IRN的时间信息输出 (IRN time information output)",
                "0x06 - 授时引擎的位置状态 (Timing engine position status)",
                "0x07 - GNSS 系统 UTC 信息异常告警 (GNSS system UTC information anomaly alarm)",
                "0x08 - GNSS 系统时间跳年告警 (GNSS system leap year alarm)",
                "0x09 - TCXO 晶振频偏信息 (TCXO crystal oscillator frequency offset information)"
            ])
            self.id_combo.setCurrentText("0x00 - 授时脉冲信息 (Timing pulse information)")
            
            # 隐藏NAV2-DOP专用输入框
            self.nav2_dop_widget.hide()
            self.payload_input.show()
            
        elif "RXM2" in selected_class:
            self.id_combo.clear()
            self.id_combo.addItems([
                "0x00 - 伪距、载波相位原始测量信息 (Pseudorange, carrier phase raw measurement information)",
                "0x01 - 卫星位置信息(所有卫星) (Satellite position information (all satellites))",
                "0x06 - 卫星原始电文信息 (Satellite raw ephemeris information)",
                "0x0A - 卫星位置信息(单颗卫星) (Satellite position information (single satellite))"
            ])
            self.id_combo.setCurrentText("0x00 - 伪距、载波相位原始测量信息 (Pseudorange, carrier phase raw measurement information)")
            
            # 隐藏NAV2-DOP专用输入框
            self.nav2_dop_widget.hide()
            self.payload_input.show()
            
        elif "ACK" in selected_class:
            self.id_combo.clear()
            self.id_combo.addItems([
                "0x00 - 回复表示消息未被正确接收 (Reply indicating message not correctly received)",
                "0x01 - 回复表示消息被正确接收 (Reply indicating message correctly received)"
            ])
            self.id_combo.setCurrentText("0x01 - 回复表示消息被正确接收 (Reply indicating message correctly received)")
            
            # 隐藏NAV2-DOP专用输入框
            self.nav2_dop_widget.hide()
            self.payload_input.show()
            
        elif "CFG" in selected_class:
            self.id_combo.clear()
            self.id_combo.addItems([
                "0x00 - CFG-PRT (查询/配置 UART 的工作模式 - Query/Configure UART working mode)",
                "0x01 - CFG-MSG (查询/配置信息发送频率 - Query/Configure message sending frequency)",
                "0x02 - CFG-RST (设置 重启接收机/清除保存的数据结构 - Set Restart receiver/Clear saved data structure)",
                "0x03 - CFG-TP (查询/配置接收机 PPS 的相关参数 - Query/Configure receiver PPS related parameters)",
                "0x04 - CFG-RATE (查询/配置接收机的导航速率 - Query/Configure receiver navigation rate)",
                "0x05 - CFG-CFG (设置 清除、保存和加载配置信息 - Set Clear, save and load configuration information)",
                "0x0A - CFG-NAV-LIMIT (查询/设置对参与导航卫星的筛选规则 - Query/Set filtering rules for participating navigation satellites)",
                "0x0B - CFG-NAV-MODE (查询/设置导航模式信息 - Query/Set navigation mode information)",
                "0x0C - CFG-NAVFLT (查询/设置导航的阈值信息 - Query/Set navigation threshold information)",
                "0x0D - CFG-WNREF (查询/设置 GPS 周数参考值 - Query/Set GPS week number reference value)",
                "0x0E - CFG-INS (查询/设置 INS 安装模式 - Query/Set INS installation mode)",
                "0x0F - CFG-NAV-BAND (查询/设置可用卫星系统与信号 - Query/Set available satellite systems and signals)",
                "0x10 - CFG-JSM (查询/设置当前抗干扰防欺骗模式 - Query/Set current anti-interference anti-spoofing mode)",
                "0x11 - CFG-CWI (查询/设置当前抗干扰模式和射频参数 - Query/Set current anti-interference mode and RF parameters)",
                "0x12 - CFG-NMEA (查询/设置 NMEA 协议语句输出配置 - Query/Set NMEA protocol statement output configuration)",
                "0x14 - CFG-RTCM (查询/设置 RTCM 协议语句输出配置 - Query/Set RTCM protocol statement output configuration)",
                "0x16 - CFG-TMODE2 (查询/设置接收机 PPS 的授时模式 - Query/Set receiver PPS timing mode)",
                "0x21 - CFG-SATMASK (查询/设置卫星是否参与定位 - Query/Set whether satellites participate in positioning)",
                "0x22 - CFG-TGDU (查询/设置各个信号频段的硬件延迟量 - Query/Set hardware delay for each signal frequency band)",
                "0x23 - CFG-SBAS (查询/设置 SBAS 卫星接收配置信息 - Query/Set SBAS satellite reception configuration information)"
            ])
            self.id_combo.setCurrentText("0x00 - CFG-PRT (查询/配置 UART 的工作模式 - Query/Configure UART working mode)")
            
            # 隐藏NAV2-DOP专用输入框
            self.nav2_dop_widget.hide()
            self.payload_input.show()
            
        elif "MSG" in selected_class:
            self.id_combo.clear()
            self.id_combo.addItems([
                "0x00 - MSG-BDSUTC (BDS 系统 UTC 信息 - BDS system UTC information)",
                "0x01 - MSG-BDSION (BDS 系统电离层信息 - BDS system ionosphere information)",
                "0x02 - MSG-BDSEPH (BDS 系统星历信息 - BDS system ephemeris information)",
                "0x03 - MSG-BD3ION (BD3 系统9参数电离层信息 - BD3 system 9-parameter ionosphere information)",
                "0x04 - MSG-BD3EPH (BD3 系统星历信息 - BD3 system ephemeris information)",
                "0x05 - MSG-GPSUTC (GPS 系统 UTC 信息 - GPS system UTC information)",
                "0x06 - MSG-GPSION (GPS 系统电离层信息 - GPS system ionosphere information)",
                "0x07 - MSG-GPSEPH (GPS 系统星历信息 - GPS system ephemeris information)",
                "0x08 - MSG-GLNEPH (GLN 系统星历信息 - GLN system ephemeris information)",
                "0x09 - MSG-GALUTC (GAL 系统 UTC 信息 - GAL system UTC information)",
                "0x0B - MSG-GALEPH (GAL 系统星历信息 - GAL system ephemeris information)",
                "0x0C - MSG-QZSUTC (QZSS 系统 UTC 信息 - QZSS system UTC information)",
                "0x0D - MSG-QZSION (QZSS 系统电离层信息 - QZSS system ionosphere information)",
                "0x0E - MSG-QZSEPH (QZSS 系统星历信息 - QZSS system ephemeris information)",
                "0x11 - MSG-IRNEPH (IRN 系统的星历信息 - IRN system ephemeris information)",
                "0x17 - MSG-IGP (格网电离层数据 - Grid ionosphere data)"
            ])
            self.id_combo.setCurrentText("0x00 - MSG-BDSUTC (BDS 系统 UTC 信息 - BDS system UTC information)")
            
            # 隐藏NAV2-DOP专用输入框
            self.nav2_dop_widget.hide()
            self.payload_input.show()
            
        elif "MON" in selected_class:
            self.id_combo.clear()
            self.id_combo.addItems([
                "0x00 - MON-CWI (干扰信号输出 - Interference signal output)",
                "0x01 - MON-RFE (射频增益查询 - RF gain query)",
                "0x02 - MON-HIST (中频数据的直方图统计 - IF data histogram statistics)",
                "0x04 - MON-VER (输出版本信息 - Output version information)",
                "0x05 - MON-CPU (基带处理器信息 - Baseband processor information)",
                "0x06 - MON-ICV (芯片版本信息 - Chip version information)",
                "0x07 - MON-MOD (模块版本信息 - Module version information)",
                "0x09 - MON-HW (硬件的各种配置状态 - Hardware configuration status)",
                "0x0A - MON-JSM (抗干扰防欺骗信息输出 - Anti-interference anti-spoofing information output)",
                "0x0B - MON-SEC (抗干扰防欺骗的直观信息 - Intuitive anti-interference anti-spoofing information)"
            ])
            self.id_combo.setCurrentText("0x00 - MON-CWI (干扰信号输出 - Interference signal output)")
            
            # 隐藏NAV2-DOP专用输入框
            self.nav2_dop_widget.hide()
            self.payload_input.show()
            
        elif "AID" in selected_class:
            self.id_combo.clear()
            self.id_combo.addItems([
                "0x01 - AID-INI (辅助位置、时间、频率、时钟频偏信息 - Auxiliary position, time, frequency, clock bias information)"
            ])
            self.id_combo.setCurrentText("0x01 - AID-INI (辅助位置、时间、频率、时钟频偏信息 - Auxiliary position, time, frequency, clock bias information)")
            
            # 隐藏NAV2-DOP专用输入框
            self.nav2_dop_widget.hide()
            self.payload_input.show()
            
        elif "INS2" in selected_class:
            self.id_combo.clear()
            self.id_combo.addItems([
                "0x00 - INS2-ATT (IMU 坐标系相对于本地导航坐标系(NED)的姿态 - IMU coordinate system attitude relative to local navigation coordinate system (NED))",
                "0x01 - INS2-IMU (传感器信息 - Sensor information)"
            ])
            self.id_combo.setCurrentText("0x00 - INS2-ATT (IMU 坐标系相对于本地导航坐标系(NED)的姿态 - IMU coordinate system attitude relative to local navigation coordinate system (NED))")
            
            # 隐藏NAV2-DOP专用输入框
            self.nav2_dop_widget.hide()
            self.payload_input.show()
            
        elif "RTCM" in selected_class:
            self.id_combo.clear()
            self.id_combo.addItems([
                "0x00 - RTCM_1005 (RTK 基站信息, ARP 信息 - RTK Base Station Information, ARP Information)",
                "0x02 - RTCM_1019 (GPS L1C/A 定点星历 - GPS L1C/A Fixed Ephemeris)",
                "0x03 - RTCM_1042 (BDS B1I 定点星历 - BDS B1I Fixed Ephemeris)",
                "0x04 - RTCM_1044 (QZSS L1C/A 定点星历 - QZSS L1C/A Fixed Ephemeris)",
                "0x05 - RTCM_1045 (GALILEO FNAV 定点星历 - GALILEO FNAV Fixed Ephemeris)",
                "0x06 - RTCM_1046 (GALILEO INAV 定点星历 - GALILEO INAV Fixed Ephemeris)",
                "0x0D - RTCM_107x (GPS MSM 格式测量值 - GPS MSM Format Measurement Value)",
                "0x11 - RTCM_109x (GALILEO MSM 格式测量值 - GALILEO MSM Format Measurement Value)",
                "0x13 - RTCM_111x (QZSS MSM 格式测量值 - QZSS MSM Format Measurement Value)",
                "0x15 - RTCM_112x (BDS MSM 格式测量值 - BDS MSM Format Measurement Value)"
            ])
            self.id_combo.setCurrentText("0x00 - RTCM_1005 (RTK 基站信息, ARP 信息 - RTK Base Station Information, ARP Information)")
            
            # 隐藏NAV2-DOP专用输入框
            self.nav2_dop_widget.hide()
            self.payload_input.show()
            
        else:
            # 默认选项
            self.id_combo.clear()
            self.id_combo.addItems([
                "0x01 - 默认消息ID (Default Message ID)"
            ])
            self.id_combo.setCurrentText("0x01 - 默认消息ID (Default Message ID)")
            
            # 隐藏NAV2-DOP专用输入框
            self.nav2_dop_widget.hide()
            self.payload_input.show()
        
        # 重新连接信号
        self.id_combo.currentTextChanged.connect(self.update_packet_preview) 
        self.id_combo.currentTextChanged.connect(self.check_nav2_dop_visibility) 
        
        # 检查是否需要显示NAV2-DOP专用输入框
        self.check_nav2_dop_visibility()
    
    def check_nav2_dop_visibility(self):
        """检查是否需要显示NAV2专用输入框"""
        try:
            class_value = self.parse_hex_byte(self.class_combo.currentText().split(' - ')[0], silent=True)
            id_value = self.parse_hex_byte(self.id_combo.currentText().split(' - ')[0], silent=True)
            
            if class_value == 0x11:  # NAV2消息类
                if id_value == 0x01:  # NAV2-DOP
                    self.nav2_dop_widget.show()
                    self.nav2_sol_widget.hide()
                    self.nav2_pvh_widget.hide()
                    self.nav2_timeutc_widget.hide()
                    self.nav2_clk_widget.hide()
                    self.nav2_rvt_widget.hide()
                    self.nav2_rtc_widget.hide()
                    self.nav2_sat_widget.hide()
                    self.nav2_sig_widget.hide()
                    self.payload_input.hide()
                elif id_value == 0x02:  # NAV2-SOL
                    self.nav2_dop_widget.hide()
                    self.nav2_sol_widget.show()
                    self.nav2_pvh_widget.hide()
                    self.nav2_timeutc_widget.hide()
                    self.nav2_clk_widget.hide()
                    self.nav2_rvt_widget.hide()
                    self.nav2_rtc_widget.hide()
                    self.nav2_sat_widget.hide()
                    self.nav2_sig_widget.hide()
                    self.payload_input.hide()
                elif id_value == 0x03:  # NAV2-PVH
                    self.nav2_dop_widget.hide()
                    self.nav2_sol_widget.hide()
                    self.nav2_pvh_widget.show()
                    self.nav2_timeutc_widget.hide()
                    self.nav2_clk_widget.hide()
                    self.nav2_rvt_widget.hide()
                    self.nav2_rtc_widget.hide()
                    self.nav2_sat_widget.hide()
                    self.nav2_sig_widget.hide()
                    self.payload_input.hide()
                elif id_value == 0x05:  # NAV2-TIMEUTC
                    self.nav2_dop_widget.hide()
                    self.nav2_sol_widget.hide()
                    self.nav2_pvh_widget.hide()
                    self.nav2_timeutc_widget.show()
                    self.nav2_clk_widget.hide()
                    self.nav2_rvt_widget.hide()
                    self.nav2_rtc_widget.hide()
                    self.nav2_sat_widget.hide()
                    self.nav2_sig_widget.hide()
                    self.payload_input.hide()
                elif id_value == 0x07:  # NAV2-CLK
                    self.nav2_dop_widget.hide()
                    self.nav2_sol_widget.hide()
                    self.nav2_pvh_widget.hide()
                    self.nav2_timeutc_widget.hide()
                    self.nav2_clk_widget.show()
                    self.nav2_rvt_widget.hide()
                    self.nav2_rtc_widget.hide()
                    self.nav2_sat_widget.hide()
                    self.nav2_sig_widget.hide()
                    self.payload_input.hide()
                elif id_value == 0x08:  # NAV2-RVT
                    self.nav2_dop_widget.hide()
                    self.nav2_sol_widget.hide()
                    self.nav2_pvh_widget.hide()
                    self.nav2_timeutc_widget.hide()
                    self.nav2_clk_widget.hide()
                    self.nav2_rvt_widget.show()
                    self.nav2_rtc_widget.hide()
                    self.nav2_sat_widget.hide()
                    self.nav2_sig_widget.hide()
                    self.payload_input.hide()
                elif id_value == 0x09:  # NAV2-RTC
                    self.nav2_dop_widget.hide()
                    self.nav2_sol_widget.hide()
                    self.nav2_pvh_widget.hide()
                    self.nav2_timeutc_widget.hide()
                    self.nav2_clk_widget.hide()
                    self.nav2_rvt_widget.hide()
                    self.nav2_rtc_widget.show()
                    self.nav2_sat_widget.hide()
                    self.nav2_sig_widget.hide()
                    self.payload_input.hide()
                elif id_value == 0x04:  # NAV2-SAT
                    self.nav2_dop_widget.hide()
                    self.nav2_sol_widget.hide()
                    self.nav2_pvh_widget.hide()
                    self.nav2_timeutc_widget.hide()
                    self.nav2_clk_widget.hide()
                    self.nav2_rvt_widget.hide()
                    self.nav2_rtc_widget.hide()
                    self.nav2_sat_widget.show()
                    self.nav2_sig_widget.hide()
                    self.payload_input.hide()
                elif id_value == 0x06:  # NAV2-SIG
                    self.nav2_dop_widget.hide()
                    self.nav2_sol_widget.hide()
                    self.nav2_pvh_widget.hide()
                    self.nav2_timeutc_widget.hide()
                    self.nav2_clk_widget.hide()
                    self.nav2_rvt_widget.hide()
                    self.nav2_rtc_widget.hide()
                    self.nav2_sat_widget.hide()
                    self.nav2_sig_widget.show()
                    self.payload_input.hide()
                else:
                    # 其他NAV2消息ID
                    self.nav2_dop_widget.hide()
                    self.nav2_sol_widget.hide()
                    self.nav2_pvh_widget.hide()
                    self.nav2_timeutc_widget.hide()
                    self.nav2_clk_widget.hide()
                    self.nav2_rvt_widget.hide()
                    self.nav2_rtc_widget.hide()
                    self.nav2_sat_widget.hide()
                    self.nav2_sig_widget.hide()
                    self.payload_input.show()
            else:
                # 非NAV2消息类
                self.nav2_dop_widget.hide()
                self.nav2_sol_widget.hide()
                self.nav2_pvh_widget.hide()
                self.nav2_timeutc_widget.hide()
                self.nav2_clk_widget.hide()
                self.nav2_rvt_widget.hide()
                self.nav2_rtc_widget.hide()
                self.nav2_sat_widget.hide()
                self.nav2_sig_widget.hide()
                self.payload_input.show()
                
            # 调整窗口大小，确保所有组件都能正确显示
            QTimer.singleShot(50, self.adjust_window_size)
                
        except:
            # 如果解析失败，默认隐藏专用输入框
            self.nav2_dop_widget.hide()
            self.nav2_sol_widget.hide()
            self.nav2_pvh_widget.hide()
            self.nav2_timeutc_widget.hide()
            self.nav2_clk_widget.hide()
            self.nav2_rvt_widget.hide()
            self.nav2_rtc_widget.hide()
            self.nav2_sat_widget.hide()
            self.nav2_sig_widget.hide()
            self.payload_input.show()
            
            # 调整窗口大小
            QTimer.singleShot(50, self.adjust_window_size)
    
    def on_nav2_dop_changed(self):
        """当NAV2-DOP消息的有效载荷输入框内容改变时，更新预览"""
        self.update_packet_preview()
    
    def on_nav2_sol_changed(self):
        """当NAV2-SOL消息的有效载荷输入框内容改变时，更新预览"""
        self.update_packet_preview()
    
    def on_nav2_pvh_changed(self):
        """当NAV2-PVH消息的有效载荷输入框内容改变时，更新预览"""
        self.update_packet_preview()
    
    def on_nav2_timeutc_changed(self):
        """当NAV2-TIMEUTC消息的有效载荷输入框内容改变时，更新预览"""
        self.update_packet_preview()
    
    def on_nav2_clk_changed(self):
        """当NAV2-CLK消息的有效载荷输入框内容改变时，更新预览"""
        self.update_packet_preview()
    
    def on_nav2_rvt_changed(self):
        """当NAV2-RVT消息的有效载荷输入框内容改变时，更新预览"""
        self.update_packet_preview()
    
    def on_nav2_rtc_changed(self):
        """当NAV2-RTC消息的有效载荷输入框内容改变时，更新预览"""
        self.update_packet_preview()
    
    def on_nav2_sat_changed(self):
        """当NAV2-SAT消息的有效载荷输入框内容改变时，更新预览"""
        self.update_packet_preview()
    
    def on_nav2_sig_changed(self):
        """当NAV2-SIG消息的有效载荷输入框内容改变时，更新预览"""
        self.update_packet_preview()

    def validate_hex_input(self):
        """验证输入框中的十六进制字符串，只允许有效字符"""
        sender = self.sender()
        if not sender:
            return
            
        text = sender.text().strip()
        
        # 移除0x前缀
        if text.startswith('0x') or text.startswith('0X'):
            text = text[2:]
        
        # 如果为空，直接返回
        if not text:
            return
        
        # 只保留有效的十六进制字符
        valid_text = ''.join(c for c in text if c in '0123456789ABCDEFabcdef')
        
        # 转换为大写
        valid_text = valid_text.upper()
        
        # 限制最大长度为8位
        if len(valid_text) > 8:
            valid_text = valid_text[:8]
        
        # 如果内容有变化，更新输入框
        if valid_text != text.upper():
            sender.setText(valid_text)

    def auto_pad_hex_input(self):
        """在输入框失去焦点时进行最终验证"""
        sender = self.sender()
        if not sender:
            return
            
        text = sender.text().strip()
        
        # 移除0x前缀
        if text.startswith('0x') or text.startswith('0X'):
            text = text[2:]
            
        # 如果为空，直接返回
        if not text:
            return
            
        # 检查是否只包含有效的十六进制字符
        if not all(c in '0123456789ABCDEFabcdef' for c in text):
            # 移除无效字符
            valid_text = ''.join(c for c in text if c in '0123456789ABCDEFabcdef')
            sender.setText(valid_text.upper())
            return
            
        # 转换为大写
        text = text.upper()
        
        # 限制最大长度为8位
        if len(text) > 8:
            text = text[:8]
            
        # 更新输入框内容（如果需要）
        if text != sender.text().replace('0x', '').replace('0X', '').upper():
            sender.setText(text)
            
        # 更新数据包预览
        self.update_packet_preview() 

    def parse_nav2_sol_payload(self, silent=False):
        """解析NAV2-SOL消息的有效载荷"""
        try:
            # 定义NAV2-SOL字段信息
            nav2_sol_fields = [
                # 偏移, 数据类型, 最大长度, 名称, 单位, 描述
                (0, "I4", 8, "tow", "ms", "GPS时间, 周内时"),
                (4, "U2", 4, "wn", "-", "GPS时间, 周数"),
                (6, "U2", 4, "res1", "-", "保留"),
                (8, "U1", 2, "fixflags", "-", "位置有效标志"),
                (9, "U1", 2, "velflags", "-", "速度有效标志"),
                (10, "U1", 2, "res2", "-", "保留"),
                (11, "U1", 2, "fixGnssMask", "-", "参与定位的卫星系统掩码"),
                (12, "U1", 2, "numFixtot", "-", "参与解算的卫星总数"),
                (13, "U1", 2, "numFixGps", "-", "参与解算的GPS卫星数目"),
                (14, "U1", 2, "numFixBds", "-", "参与解算的BDS卫星数目"),
                (15, "U1", 2, "numFixGln", "-", "参与解算的GLONASS卫星数目"),
                (16, "U1", 2, "numFixGal", "-", "参与解算的GALILEO卫星数目"),
                (17, "U1", 2, "numFixQzs", "-", "参与解算的QZSS卫星数目"),
                (18, "U1", 2, "numFixSbs", "-", "参与解算的SBAS卫星数目"),
                (19, "U1", 2, "numFixIrn", "-", "参与解算的IRNSS卫星数目"),
                (20, "U4", 8, "res3", "-", "保留"),
                (24, "R8", 16, "x", "m", "ECEF坐标系中的X坐标"),
                (32, "R8", 16, "y", "m", "ECEF坐标系中的Y坐标"),
                (40, "R8", 16, "z", "m", "ECEF坐标系中的Z坐标"),
                (48, "R4", 8, "pAcc", "m", "3D位置的估计精度误差"),
                (52, "R4", 8, "vx", "m/s", "ECEF坐标系中的X速度"),
                (56, "R4", 8, "vy", "m/s", "ECEF坐标系中的Y速度"),
                (60, "R4", 8, "vz", "m/s", "ECEF坐标系中的Z速度"),
                (64, "R4", 8, "sAcc", "m/s", "3D速度的估计精度误差"),
                (68, "R4", 8, "pDop", "-", "位置DOP")
            ]
            
            payload_data = []
            
            for offset, data_type, max_length, name, unit, description in nav2_sol_fields:
                # 获取输入框的值
                if name in self.nav2_sol_inputs:
                    field_text = self.nav2_sol_inputs[name].text().strip()
                else:
                    field_text = ""
                
                # 根据数据类型解析字段
                if data_type == "I4":  # 4字节有符号整数
                    field_bytes = self.parse_signed_int_field(field_text, 4, silent)
                elif data_type == "U4":  # 4字节无符号整数
                    field_bytes = self.parse_unsigned_int_field(field_text, 4, silent)
                elif data_type == "U2":  # 2字节无符号整数
                    field_bytes = self.parse_unsigned_int_field(field_text, 2, silent)
                elif data_type == "U1":  # 1字节无符号整数
                    field_bytes = self.parse_unsigned_int_field(field_text, 1, silent)
                elif data_type == "R4":  # 4字节浮点数
                    field_bytes = self.parse_float_field(field_text, 4, silent)
                elif data_type == "R8":  # 8字节浮点数
                    field_bytes = self.parse_float_field(field_text, 8, silent)
                else:
                    # 未知数据类型，使用默认值
                    field_bytes = [0x00] * self.get_data_type_size(data_type)
                
                if field_bytes is None:
                    return None
                
                payload_data.extend(field_bytes)
            
            return payload_data
            
        except Exception as e:
            if not silent:
                QMessageBox.warning(self, "警告", f"解析NAV2-SOL有效载荷失败: {str(e)}")
            return None
    
    def get_data_type_size(self, data_type):
        """获取数据类型的字节大小"""
        size_map = {
            "I4": 4,   # 4字节有符号整数
            "U4": 4,   # 4字节无符号整数
            "U2": 2,   # 2字节无符号整数
            "U1": 1,   # 1字节无符号整数
            "R4": 4,   # 4字节浮点数
            "R8": 8    # 8字节浮点数
        }
        return size_map.get(data_type, 4)  # 默认4字节
    
    def parse_signed_int_field(self, text, size, silent=False):
        """解析有符号整数字段"""
        try:
            if not text:
                return [0x00] * size
            
            # 移除0x前缀
            if text.startswith('0x') or text.startswith('0X'):
                text = text[2:]
            
            # 检查长度
            max_length = size * 2
            if len(text) > max_length:
                if not silent:
                    QMessageBox.warning(self, "警告", f"字段长度不能超过{max_length}位")
                return None
            
            # 补零到指定长度
            text = text.zfill(max_length)
            
            # 解析为整数
            value = int(text, 16)
            
            # 转换为字节数组（小端序）
            bytes_data = []
            for i in range(size):
                bytes_data.append((value >> (i * 8)) & 0xFF)
            
            return bytes_data
            
        except ValueError:
            if not silent:
                QMessageBox.warning(self, "警告", f"字段 {text} 不是有效的16进制数")
            return None
    
    def parse_unsigned_int_field(self, text, size, silent=False):
        """解析无符号整数字段"""
        try:
            if not text:
                return [0x00] * size
            
            # 移除0x前缀
            if text.startswith('0x') or text.startswith('0X'):
                text = text[2:]
            
            # 检查长度
            max_length = size * 2
            if len(text) > max_length:
                if not silent:
                    QMessageBox.warning(self, "警告", f"字段长度不能超过{max_length}位")
                return None
            
            # 补零到指定长度
            text = text.zfill(max_length)
            
            # 解析为整数
            value = int(text, 16)
            
            # 转换为字节数组（小端序）
            bytes_data = []
            for i in range(size):
                bytes_data.append((value >> (i * 8)) & 0xFF)
            
            return bytes_data
            
        except ValueError:
            if not silent:
                QMessageBox.warning(self, "警告", f"字段 {text} 不是有效的16进制数")
            return None
    
    def parse_float_field(self, text, size, silent=False):
        """解析浮点数字段"""
        try:
            if not text:
                return [0x00] * size
            
            # 移除0x前缀
            if text.startswith('0x') or text.startswith('0X'):
                text = text[2:]
            
            # 检查长度
            max_length = size * 2
            if len(text) > max_length:
                if not silent:
                    QMessageBox.warning(self, "警告", f"字段长度不能超过{max_length}位")
                return None
            
            # 补零到指定长度
            text = text.zfill(max_length)
            
            # 解析为整数
            value = int(text, 16)
            
            # 转换为字节数组（小端序）
            bytes_data = []
            for i in range(size):
                bytes_data.append((value >> (i * 8)) & 0xFF)
            
            return bytes_data
            
        except ValueError:
            if not silent:
                QMessageBox.warning(self, "警告", f"字段 {text} 不是有效的16进制数")
            return None
    
    def parse_nav2_pvh_payload(self, silent=False):
        """解析NAV2-PVH消息的有效载荷"""
        try:
            # 定义NAV2-PVH字段信息
            nav2_pvh_fields = [
                # 偏移, 数据类型, 最大长度, 名称, 单位, 描述
                (0, "I4", 8, "tow", "ms", "GPS时间, 周内时"),
                (4, "U2", 4, "wn", "-", "GPS时间, 周数"),
                (6, "U2", 4, "res1", "-", "保留"),
                (8, "U1", 2, "fixflags", "-", "位置有效标志"),
                (9, "U1", 2, "velflags", "-", "速度有效标志"),
                (10, "U1", 2, "res2", "-", "保留"),
                (11, "U1", 2, "fixGnssMask", "-", "参与定位的卫星系统掩码"),
                (12, "U1", 2, "numFixtot", "-", "参与解算的卫星总数"),
                (13, "U1", 2, "numFixGps", "-", "参与解算的GPS卫星数目"),
                (14, "U1", 2, "numFixBds", "-", "参与解算的BDS卫星数目"),
                (15, "U1", 2, "numFixGln", "-", "参与解算的GLONASS卫星数目"),
                (16, "U1", 2, "numFixGal", "-", "参与解算的GALILEO卫星数目"),
                (17, "U1", 2, "numFixQzs", "-", "参与解算的QZSS卫星数目"),
                (18, "U1", 2, "numFixSbs", "-", "参与解算的SBAS卫星数目"),
                (19, "U1", 2, "numFixIrn", "-", "参与解算的IRNSS卫星数目"),
                (20, "U4", 8, "res3", "-", "保留"),
                (24, "R8", 16, "lon", "度", "经度"),
                (32, "R8", 16, "lat", "度", "纬度"),
                (40, "R4", 8, "height", "m", "大地高度"),
                (44, "R4", 8, "sepGeoid", "m", "高度异常"),
                (48, "R4", 8, "velE", "m/s", "ENU坐标系中的东向速度"),
                (52, "R4", 8, "velN", "m/s", "ENU坐标系中的北向速度"),
                (56, "R4", 8, "velU", "m/s", "ENU坐标系中的天向速度"),
                (60, "R4", 8, "speed3D", "m/s", "3D速度"),
                (64, "R4", 8, "speed2D", "m/s", "2D对地速度"),
                (68, "R4", 8, "heading", "度", "航向"),
                (72, "R4", 8, "hAcc", "m", "位置的估计水平精度误差"),
                (76, "R4", 8, "vAcc", "m", "位置的估计垂直精度误差"),
                (80, "R4", 8, "sAcc", "m/s", "3D速度的估计精度误差"),
                (84, "R4", 8, "cAcc", "度", "航向的精度误差")
            ]
            
            payload_data = []
            
            for offset, data_type, max_length, name, unit, description in nav2_pvh_fields:
                # 获取输入框的值
                if name in self.nav2_pvh_inputs:
                    field_text = self.nav2_pvh_inputs[name].text().strip()
                else:
                    field_text = ""
                
                # 根据数据类型解析字段
                if data_type == "I4":  # 4字节有符号整数
                    field_bytes = self.parse_signed_int_field(field_text, 4, silent)
                elif data_type == "U4":  # 4字节无符号整数
                    field_bytes = self.parse_unsigned_int_field(field_text, 4, silent)
                elif data_type == "U2":  # 2字节无符号整数
                    field_bytes = self.parse_unsigned_int_field(field_text, 2, silent)
                elif data_type == "U1":  # 1字节无符号整数
                    field_bytes = self.parse_unsigned_int_field(field_text, 1, silent)
                elif data_type == "R4":  # 4字节浮点数
                    field_bytes = self.parse_float_field(field_text, 4, silent)
                elif data_type == "R8":  # 8字节浮点数
                    field_bytes = self.parse_float_field(field_text, 8, silent)
                else:
                    # 未知数据类型，使用默认值
                    field_bytes = [0x00] * self.get_data_type_size(data_type)
                
                if field_bytes is None:
                    return None
                
                payload_data.extend(field_bytes)
            
            return payload_data
            
        except Exception as e:
            if not silent:
                QMessageBox.warning(self, "警告", f"解析NAV2-PVH有效载荷失败: {str(e)}")
            return None
    
    def parse_nav2_timeutc_payload(self, silent=False):
        """解析NAV2-TIMEUTC消息的有效载荷"""
        try:
            # 定义NAV2-TIMEUTC字段信息
            nav2_timeutc_fields = [
                # 偏移, 数据类型, 最大长度, 名称, 单位, 描述
                (0, "R4", 8, "tacc", "ns", "接收机的时间误差估计值"),
                (4, "I4", 8, "subms", "ms", "时间的毫秒误差值, 范围: -0.5ms~0.5ms"),
                (8, "I1", 2, "subcs", "ms", "时间的厘秒误差值, 范围: -5ms~5ms"),
                (9, "U1", 2, "cs", "cs", "时间的整数厘秒值, 范围: 0cs~99cs"),
                (10, "U2", 4, "year", "-", "年份"),
                (12, "U1", 2, "month", "-", "月份"),
                (13, "U1", 2, "day", "-", "日期"),
                (14, "U1", 2, "hour", "-", "小时数"),
                (15, "U1", 2, "minute", "-", "分钟数"),
                (16, "U1", 2, "second", "-", "秒数"),
                (17, "U1", 2, "tflagx", "-", "综合时间标志"),
                (18, "U1", 2, "tsrc", "-", "时间的卫星系统来源"),
                (19, "I1", 2, "leapsec", "s", "当前的闰秒值")
            ]
            
            payload_data = []
            
            for offset, data_type, max_length, name, unit, description in nav2_timeutc_fields:
                # 获取输入框的值
                if name in self.nav2_timeutc_inputs:
                    field_text = self.nav2_timeutc_inputs[name].text().strip()
                else:
                    field_text = ""
                
                # 根据数据类型解析字段
                if data_type == "I4":  # 4字节有符号整数
                    field_bytes = self.parse_signed_int_field(field_text, 4, silent)
                elif data_type == "U4":  # 4字节无符号整数
                    field_bytes = self.parse_unsigned_int_field(field_text, 4, silent)
                elif data_type == "U2":  # 2字节无符号整数
                    field_bytes = self.parse_unsigned_int_field(field_text, 2, silent)
                elif data_type == "U1":  # 1字节无符号整数
                    field_bytes = self.parse_unsigned_int_field(field_text, 1, silent)
                elif data_type == "R4":  # 4字节浮点数
                    field_bytes = self.parse_float_field(field_text, 4, silent)
                elif data_type == "R8":  # 8字节浮点数
                    field_bytes = self.parse_float_field(field_text, 8, silent)
                else:
                    # 未知数据类型，使用默认值
                    field_bytes = [0x00] * self.get_data_type_size(data_type)
                
                if field_bytes is None:
                    return None
                
                payload_data.extend(field_bytes)
            
            return payload_data
            
        except Exception as e:
            if not silent:
                QMessageBox.warning(self, "警告", f"解析NAV2-TIMEUTC有效载荷失败: {str(e)}")
            return None
    
    def parse_nav2_clk_payload(self, silent=False):
        """解析NAV2-CLK消息的有效载荷"""
        try:
            # 定义NAV2-CLK字段信息
            nav2_clk_fields = [
                # 偏移, 数据类型, 最大长度, 名称, 单位, 描述
                (0, "U1", 2, "tsrc", "-", "卫星系统时间源"),
                (1, "U1", 2, "res1", "-", "保留字段"),
                (2, "U1", 2, "towflag", "-", "接收机时间有效标志"),
                (3, "U1", 2, "frqflag", "-", "接收机频率偏差有效标志"),
                (4, "I4", 8, "clkbias", "ns", "当前接收机时间偏差"),
                (8, "R4", 8, "dfxTcxo", "s/s", "接收机TCXO相对频率偏差"),
                (12, "R4", 8, "tacc", "ns", "接收机时间精度"),
                (16, "R4", 8, "facc", "ppb", "接收机频率精度")
            ]
            
            payload_data = []
            
            for offset, data_type, max_length, name, unit, description in nav2_clk_fields:
                # 获取输入框的值
                if name in self.nav2_clk_inputs:
                    field_text = self.nav2_clk_inputs[name].text().strip()
                else:
                    field_text = ""
                
                # 根据数据类型解析字段
                if data_type == "U1":  # 1字节无符号整数
                    field_bytes = self.parse_unsigned_int_field(field_text, 1, silent)
                elif data_type == "I4":  # 4字节有符号整数
                    field_bytes = self.parse_signed_int_field(field_text, 4, silent)
                elif data_type == "R4":  # 4字节浮点数
                    field_bytes = self.parse_float_field(field_text, 4, silent)
                else:
                    # 未知数据类型，使用默认值
                    field_bytes = [0x00] * self.get_data_type_size(data_type)
                
                if field_bytes is None:
                    return None
                
                payload_data.extend(field_bytes)
            
            return payload_data
            
        except Exception as e:
            if not silent:
                QMessageBox.warning(self, "警告", f"解析NAV2-CLK有效载荷失败: {str(e)}")
            return None
    
    def parse_nav2_rvt_payload(self, silent=False):
        """解析NAV2-RVT消息的有效载荷"""
        try:
            # 定义NAV2-RVT字段信息
            nav2_rvt_fields = [
                # 偏移, 数据类型, 最大长度, 名称, 单位, 描述
                (0, "I4", 8, "rawTow", "ms", "原始接收机时间, GPS周内时的整毫秒部分"),
                (4, "I4", 8, "rawTowSubms", "ms", "原始接收机时间, GPS周内时的小数毫秒部分"),
                (8, "I4", 8, "dtuTow", "ms", "原始接收机时间误差的整数毫秒"),
                (12, "I4", 8, "dtuTowSubms", "ms", "原始接收机时间误差的小数毫秒"),
                (16, "I2", 4, "wn", "-", "原始接收机时间, GPS 周数"),
                (18, "U1", 2, "towflag", "-", "时间的有效标志"),
                (19, "U1", 2, "wnflag", "-", "周数的有效标志"),
                (20, "U1", 2, "res1", "-", "保留"),
                (21, "U1", 2, "ambflag", "-", "接收机整毫秒模糊度标志"),
                (22, "U1", 2, "dtuflag", "-", "接收机时间误差的有效标志"),
                (23, "U1", 2, "rvtRstTag", "-", "接收机时钟重置计数器"),
                (24, "I4", 8, "rvtRst", "ms", "接收机时钟调整量"),
                (28, "R4", 8, "tacc", "ns", "接收机的时间精度"),
                (32, "I4", 8, "res5", "-", "保留"),
                (36, "I4", 8, "res6", "-", "保留"),
                (40, "R4", 8, "dtmeas", "s", "距上次定位测量的时间间隔"),
                (44, "I1", 2, "res2", "-", "保留"),
                (45, "I1", 2, "dtsBds2Gps", "s", "BDS和GPS 时间的整秒偏差"),
                (46, "I1", 2, "dtsGln2Gps", "s", "GLONASS和GPS 时间的整秒偏差"),
                (47, "I1", 2, "dtsGal2Gps", "s", "GALILEO和GPS 时间的整秒偏差"),
                (48, "I1", 2, "dtsIrn2Gps", "s", "IRNSS和GPS 时间的整秒偏差"),
                (49, "U1", 2, "res3", "-", "保留"),
                (50, "U2", 4, "res4", "-", "保留")
            ]
            
            payload_data = []
            
            for offset, data_type, max_length, name, unit, description in nav2_rvt_fields:
                # 获取输入框的值
                if name in self.nav2_rvt_inputs:
                    field_text = self.nav2_rvt_inputs[name].text().strip()
                else:
                    field_text = ""
                
                # 根据数据类型解析字段
                if data_type == "I4":  # 4字节有符号整数
                    field_bytes = self.parse_signed_int_field(field_text, 4, silent)
                elif data_type == "U4":  # 4字节无符号整数
                    field_bytes = self.parse_unsigned_int_field(field_text, 4, silent)
                elif data_type == "U2":  # 2字节无符号整数
                    field_bytes = self.parse_unsigned_int_field(field_text, 2, silent)
                elif data_type == "U1":  # 1字节无符号整数
                    field_bytes = self.parse_unsigned_int_field(field_text, 1, silent)
                elif data_type == "R4":  # 4字节浮点数
                    field_bytes = self.parse_float_field(field_text, 4, silent)
                elif data_type == "R8":  # 8字节浮点数
                    field_bytes = self.parse_float_field(field_text, 8, silent)
                else:
                    # 未知数据类型，使用默认值
                    field_bytes = [0x00] * self.get_data_type_size(data_type)
                
                if field_bytes is None:
                    return None
                
                payload_data.extend(field_bytes)
            
            return payload_data
            
        except Exception as e:
            if not silent:
                QMessageBox.warning(self, "警告", f"解析NAV2-RVT有效载荷失败: {str(e)}")
            return None
    
    def parse_nav2_rtc_payload(self, silent=False):
        """解析NAV2-RTC消息的有效载荷"""
        try:
            # 定义NAV2-RTC字段信息
            nav2_rtc_fields = [
                # 偏移, 数据类型, 最大长度, 名称, 单位, 描述
                (0, "I4", 8, "dtRtcTow", "ms", "RTC 时间误差,整数毫秒部分"),
                (4, "I4", 8, "dtRtcTowSubms", "ms", "RTC 时间误差,小数毫秒部分"),
                (8, "I4", 8, "rtcTow", "ms", "RTC 时间的整数毫秒"),
                (12, "I4", 8, "rtcTowSubms", "ms", "RTC 时间的小数毫秒"),
                (16, "I2", 4, "wn", "-", "RTC 时间,GPS 周数"),
                (18, "U1", 2, "res1", "-", "保留"),
                (19, "I1", 2, "leapSec", "s", "GPS 闰秒"),
                (20, "I4", 8, "dfRtc", "Hz", "RTC 晶振频偏"),
                (24, "U1", 2, "dfRtcFlag", "-", "RTC 晶振频偏的计算有效标志"),
                (25, "U1", 2, "rtcSrc", "-", "RTC 时间校准的数据源"),
                (26, "I2", 4, "res2", "-", "保留"),
                (28, "I4", 8, "res3", "-", "保留")
            ]
            
            payload_data = []
            
            for offset, data_type, max_length, name, unit, description in nav2_rtc_fields:
                # 获取输入框的值
                if name in self.nav2_rtc_inputs:
                    field_text = self.nav2_rtc_inputs[name].text().strip()
                else:
                    field_text = ""
                
                # 根据数据类型解析字段
                if data_type == "I4":  # 4字节有符号整数
                    field_bytes = self.parse_signed_int_field(field_text, 4, silent)
                elif data_type == "U4":  # 4字节无符号整数
                    field_bytes = self.parse_unsigned_int_field(field_text, 4, silent)
                elif data_type == "U2":  # 2字节无符号整数
                    field_bytes = self.parse_unsigned_int_field(field_text, 2, silent)
                elif data_type == "U1":  # 1字节无符号整数
                    field_bytes = self.parse_unsigned_int_field(field_text, 1, silent)
                elif data_type == "R4":  # 4字节浮点数
                    field_bytes = self.parse_float_field(field_text, 4, silent)
                elif data_type == "R8":  # 8字节浮点数
                    field_bytes = self.parse_float_field(field_text, 8, silent)
                else:
                    # 未知数据类型，使用默认值
                    field_bytes = [0x00] * self.get_data_type_size(data_type)
                
                if field_bytes is None:
                    return None
                
                payload_data.extend(field_bytes)
            
            return payload_data
            
        except Exception as e:
            if not silent:
                QMessageBox.warning(self, "警告", f"解析NAV2-RTC有效载荷失败: {str(e)}")
            return None
    
    def parse_nav2_sat_payload(self, silent=False):
        """解析NAV2-SAT消息的有效载荷"""
        try:
            # 定义NAV2-SAT固定字段信息
            nav2_sat_fixed_fields = [
                # 偏移, 数据类型, 最大长度, 名称, 单位, 描述
                (0, "U4", 8, "tow", "ms", "GPS时间, 周内时"),
                (4, "U1", 2, "numViewTot", "-", "可见卫星总数"),
                (5, "U1", 2, "numFixTot", "-", "用于定位的卫星总数"),
                (6, "U1", 2, "res1", "-", "保留"),
                (7, "U1", 2, "res2", "-", "保留"),
                (8, "U4", 8, "res3", "-", "保留")
            ]
            
            payload_data = []
            
            # 解析固定字段
            for offset, data_type, max_length, name, unit, description in nav2_sat_fixed_fields:
                # 获取输入框的值
                if name in self.nav2_sat_fixed_inputs:
                    field_text = self.nav2_sat_fixed_inputs[name].text().strip()
                else:
                    field_text = ""
                
                # 根据数据类型解析字段
                if data_type == "U4":  # 4字节无符号整数
                    field_bytes = self.parse_unsigned_int_field(field_text, 4, silent)
                elif data_type == "U1":  # 1字节无符号整数
                    field_bytes = self.parse_unsigned_int_field(field_text, 1, silent)
                else:
                    # 未知数据类型，使用默认值
                    field_bytes = [0x00] * self.get_data_type_size(data_type)
                
                if field_bytes is None:
                    return None
                
                payload_data.extend(field_bytes)
            
            # 解析卫星数据字段
            for satellite_inputs in self.nav2_sat_satellite_inputs:
                # 定义卫星字段信息
                satellite_field_definitions = [
                    # 名称, 数据类型, 最大长度, 单位, 描述
                    ("chn", "U1", 2, "-", "跟踪通道号"),
                    ("svid", "U1", 2, "-", "卫星编号"),
                    ("gnssid", "U1", 2, "-", "卫星系统标识符"),
                    ("flagx", "U1", 2, "-", "卫星状态标志"),
                    ("quality", "U1", 2, "-", "信号质量"),
                    ("cn0", "U1", 2, "dBHz", "载噪比"),
                    ("sigid", "U1", 2, "-", "卫星信号标识符"),
                    ("elevation", "U1", 2, "度", "卫星仰角"),
                    ("azimuth", "U2", 4, "度", "卫星方位角"),
                    ("prresi", "I2", 4, "dm", "伪距误差")
                ]
                
                for name, data_type, max_length, unit, description in satellite_field_definitions:
                    # 获取输入框的值
                    if name in satellite_inputs:
                        field_text = satellite_inputs[name].text().strip()
                    else:
                        field_text = ""
                    
                    # 根据数据类型解析字段
                    if data_type == "U1":  # 1字节无符号整数
                        field_bytes = self.parse_unsigned_int_field(field_text, 1, silent)
                    elif data_type == "U2":  # 2字节无符号整数
                        field_bytes = self.parse_unsigned_int_field(field_text, 2, silent)
                    elif data_type == "I2":  # 2字节有符号整数
                        field_bytes = self.parse_signed_int_field(field_text, 2, silent)
                    else:
                        # 未知数据类型，使用默认值
                        field_bytes = [0x00] * self.get_data_type_size(data_type)
                    
                    if field_bytes is None:
                        return None
                    
                    payload_data.extend(field_bytes)
            
            return payload_data
            
        except Exception as e:
            if not silent:
                QMessageBox.warning(self, "警告", f"解析NAV2-SAT有效载荷失败: {str(e)}")
            return None
    
    def parse_nav2_sig_payload(self, silent=False):
        """解析NAV2-SIG消息的有效载荷"""
        try:
            # 定义NAV2-SIG固定字段信息
            nav2_sig_fixed_fields = [
                # 偏移, 数据类型, 最大长度, 名称, 单位, 描述
                (0, "U4", 8, "tow", "ms", "GPS时间, 周内时"),
                (4, "U1", 2, "res1", "-", "保留"),
                (5, "U1", 2, "numTrkTot", "-", "跟踪信号总数"),
                (6, "U1", 2, "numFixTot", "-", "用于定位的信号总数"),
                (7, "U1", 2, "res2", "-", "保留")
            ]
            
            payload_data = []
            
            # 解析固定字段
            for offset, data_type, max_length, name, unit, description in nav2_sig_fixed_fields:
                # 获取输入框的值
                if name in self.nav2_sig_fixed_inputs:
                    field_text = self.nav2_sig_fixed_inputs[name].text().strip()
                else:
                    field_text = ""
                
                # 根据数据类型解析字段
                if data_type == "U4":  # 4字节无符号整数
                    field_bytes = self.parse_unsigned_int_field(field_text, 4, silent)
                elif data_type == "U1":  # 1字节无符号整数
                    field_bytes = self.parse_unsigned_int_field(field_text, 1, silent)
                else:
                    # 未知数据类型，使用默认值
                    field_bytes = [0x00] * self.get_data_type_size(data_type)
                
                if field_bytes is None:
                    return None
                
                payload_data.extend(field_bytes)
            
            # 解析重复的信号字段
            for signal_inputs in self.nav2_sig_signal_inputs:
                # 定义信号字段信息
                signal_field_definitions = [
                    # 名称, 数据类型, 最大长度, 单位, 描述
                    ("gnssid", "U1", 2, "-", "卫星系统标识符"),
                    ("svid", "U1", 2, "-", "卫星编号"),
                    ("sigid", "U1", 2, "-", "卫星信号标识符"),
                    ("freqid", "U1", 2, "-", "卫星信号标识符"),
                    ("prResi", "I2", 4, "dm", "伪距误差"),
                    ("cn0", "U1", 2, "dBHz", "载噪比"),
                    ("trkind", "U1", 2, "-", "信号质量"),
                    ("corflagx", "U1", 2, "-", "信号修正标志"),
                    ("solflagx", "U1", 2, "-", "信号解算标志"),
                    ("chn", "U1", 2, "-", "跟踪通道号"),
                    ("eleDeg", "U1", 2, "度", "卫星仰角"),
                    ("aziDeg", "U2", 4, "度", "卫星方位角"),
                    ("ionoDelay", "I2", 4, "dm", "电离层延迟修正量")
                ]
                
                for name, data_type, max_length, unit, description in signal_field_definitions:
                    # 获取输入框的值
                    if name in signal_inputs:
                        field_text = signal_inputs[name].text().strip()
                    else:
                        field_text = ""
                    
                    # 根据数据类型解析字段
                    if data_type == "U1":  # 1字节无符号整数
                        field_bytes = self.parse_unsigned_int_field(field_text, 1, silent)
                    elif data_type == "U2":  # 2字节无符号整数
                        field_bytes = self.parse_unsigned_int_field(field_text, 2, silent)
                    elif data_type == "I2":  # 2字节有符号整数
                        field_bytes = self.parse_signed_int_field(field_text, 2, silent)
                    else:
                        # 未知数据类型，使用默认值
                        field_bytes = [0x00] * self.get_data_type_size(data_type)
                    
                    if field_bytes is None:
                        return None
                    
                    payload_data.extend(field_bytes)
            
            return payload_data
            
        except Exception as e:
            if not silent:
                QMessageBox.warning(self, "警告", f"解析NAV2-SIG有效载荷失败: {str(e)}")
            return None
    
    def update_satellite_fields(self, satellite_count):
        """根据卫星数量动态更新卫星字段"""
        try:
            print(f"开始更新卫星字段，目标数量: {satellite_count}")
            
            # 清空现有的卫星输入框
            current_count = self.satellite_grid.count()
            print(f"当前卫星网格中的部件数量: {current_count}")
            
            for i in reversed(range(self.satellite_grid.count())):
                widget = self.satellite_grid.itemAt(i).widget()
                if widget:
                    print(f"删除部件: {widget}")
                    widget.deleteLater()
            
            self.nav2_sat_satellite_inputs.clear()
            print("已清空现有卫星输入框")
            
            if satellite_count <= 0:
                self.satellite_fields_title.setText("卫星信息 (0颗卫星)")
                print("卫星数量为0，更新完成")
                return
            
            # 更新标题
            self.satellite_fields_title.setText(f"卫星信息 ({satellite_count}颗卫星)")
            
            # 定义卫星字段信息
            satellite_field_definitions = [
                # 名称, 数据类型, 最大长度, 单位, 描述
                ("chn", "U1", 2, "-", "跟踪通道号"),
                ("svid", "U1", 2, "-", "卫星编号"),
                ("gnssid", "U1", 2, "-", "卫星系统标识符"),
                ("flagx", "U1", 2, "-", "卫星状态标志"),
                ("quality", "U1", 2, "-", "信号质量"),
                ("cn0", "U1", 2, "dBHz", "载噪比"),
                ("sigid", "U1", 2, "-", "卫星信号标识符"),
                ("elevation", "U1", 2, "度", "卫星仰角"),
                ("azimuth", "U2", 4, "度", "卫星方位角"),
                ("prresi", "I2", 4, "dm", "伪距误差")
            ]
            
            # 为每颗卫星创建输入框
            for sat_index in range(satellite_count):
                # 创建卫星分组标题
                sat_title = QLabel(f"卫星 {sat_index + 1}")
                sat_title.setStyleSheet("""
                    QLabel {
                        font-size: 12px;
                        font-weight: bold;
                        color: #2e7d32;
                        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                            stop:0 #e8f5e5, stop:1 #c8e6c9);
                        border: 2px solid #81c784;
                        border-radius: 8px;
                        padding: 8px 16px;
                        margin: 4px 2px;
                        text-align: center;
                    }
                """)
                sat_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
                self.satellite_grid.addWidget(sat_title, sat_index * 6, 0, 1, 4)
                
                # 存储这颗卫星的输入框
                satellite_inputs = {}
                
                # 创建这颗卫星的所有字段
                for field_index, (name, data_type, max_length, unit, description) in enumerate(satellite_field_definitions):
                    row = sat_index * 6 + 1 + (field_index // 2)
                    col = (field_index % 2) * 2
                    
                    # 字段标签
                    label_text = f"{name} ({description})"
                    label = QLabel(label_text)
                    label.setStyleSheet("""
                        QLabel {
                            font-size: 10px;
                            color: #2e7d32;
                            background-color: #f1f8e9;
                            border: 1px solid #c8e6c9;
                            border-radius: 4px;
                            padding: 4px 8px;
                            margin: 1px;
                            font-weight: 500;
                        }
                    """)
                    label.setWordWrap(True)
                    label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
                    self.satellite_grid.addWidget(label, row, col)
                    
                    # 输入框
                    input_field = QLineEdit()
                    input_field.setPlaceholderText(f"{max_length}位16进制")
                    input_field.setMaxLength(max_length)
                    input_field.setStyleSheet("""
                        QLineEdit {
                            border: 2px solid #81c784;
                            border-radius: 6px;
                            padding: 6px 8px;
                            background-color: white;
                            font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
                            font-size: 10px;
                            color: #333333;
                            min-width: 90px;
                            min-height: 20px;
                        }
                        QLineEdit:focus {
                            border: 2px solid #2196F3;
                            background-color: #fafafa;
                        }
                        QLineEdit:hover {
                            border: 2px solid #66bb6a;
                        }
                    """)
                    
                    # 连接信号
                    input_field.textChanged.connect(self.on_nav2_sat_changed)
                    input_field.textChanged.connect(self.validate_hex_input)
                    input_field.editingFinished.connect(self.auto_pad_hex_input)
                    
                    self.satellite_grid.addWidget(input_field, row, col + 1)
                    
                    # 存储输入框引用
                    satellite_inputs[name] = input_field
                
                self.nav2_sat_satellite_inputs.append(satellite_inputs)
                
        except Exception as e:
            print(f"更新卫星字段失败: {str(e)}")
    
    def update_signal_fields(self, signal_count):
        """根据信号数量动态更新信号字段"""
        try:
            print(f"开始更新信号字段，目标数量: {signal_count}")
            
            # 清空现有的信号输入框
            current_count = self.signal_grid.count()
            print(f"当前信号网格中的部件数量: {current_count}")
            
            for i in reversed(range(self.signal_grid.count())):
                widget = self.signal_grid.itemAt(i).widget()
                if widget:
                    print(f"删除部件: {widget}")
                    widget.deleteLater()
            
            self.nav2_sig_signal_inputs.clear()
            print("已清空现有信号输入框")
            
            if signal_count <= 0:
                self.signal_fields_title.setText("信号信息 (0个信号)")
                print("信号数量为0，更新完成")
                return
            
            # 更新标题
            self.signal_fields_title.setText(f"信号信息 ({signal_count}个信号)")
            
            # 定义信号字段信息
            signal_field_definitions = [
                # 名称, 数据类型, 最大长度, 单位, 描述
                ("gnssid", "U1", 2, "-", "卫星系统标识符"),
                ("svid", "U1", 2, "-", "卫星编号"),
                ("sigid", "U1", 2, "-", "卫星信号标识符"),
                ("freqid", "U1", 2, "-", "卫星信号标识符"),
                ("prResi", "I2", 4, "dm", "伪距误差"),
                ("cn0", "U1", 2, "dBHz", "载噪比"),
                ("trkind", "U1", 2, "-", "信号质量"),
                ("corflagx", "U1", 2, "-", "信号修正标志"),
                ("solflagx", "U1", 2, "-", "信号解算标志"),
                ("chn", "U1", 2, "-", "跟踪通道号"),
                ("eleDeg", "U1", 2, "度", "卫星仰角"),
                ("aziDeg", "U2", 4, "度", "卫星方位角"),
                ("ionoDelay", "I2", 4, "dm", "电离层延迟修正量")
            ]
            
            # 为每个信号创建输入框
            for sig_index in range(signal_count):
                # 创建信号分组标题
                sig_title = QLabel(f"信号 {sig_index + 1}")
                sig_title.setStyleSheet("""
                    QLabel {
                        font-size: 12px;
                        font-weight: bold;
                        color: #e65100;
                        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                            stop:0 #ffecb3, stop:1 #ffcc02);
                        border: 2px solid #ff9800;
                        border-radius: 8px;
                        padding: 8px 16px;
                        margin: 4px 2px;
                        text-align: center;
                    }
                """)
                sig_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
                self.signal_grid.addWidget(sig_title, sig_index * 7, 0, 1, 4)
                
                # 存储这个信号的输入框
                signal_inputs = {}
                
                # 创建这个信号的所有字段
                for field_index, (name, data_type, max_length, unit, description) in enumerate(signal_field_definitions):
                    row = sig_index * 7 + 1 + (field_index // 2)
                    col = (field_index % 2) * 2
                    
                    # 字段标签
                    label_text = f"{name} ({description})"
                    label = QLabel(label_text)
                    label.setStyleSheet("""
                        QLabel {
                            font-size: 10px;
                            color: #e65100;
                            background-color: #ffecb3;
                            border: 1px solid #ff9800;
                            border-radius: 4px;
                            padding: 4px 8px;
                            margin: 1px;
                            font-weight: 500;
                        }
                    """)
                    label.setWordWrap(True)
                    label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
                    self.signal_grid.addWidget(label, row, col)
                    
                    # 输入框
                    input_field = QLineEdit()
                    input_field.setPlaceholderText(f"{max_length}位16进制")
                    input_field.setMaxLength(max_length)
                    input_field.setStyleSheet("""
                        QLineEdit {
                            border: 2px solid #ff9800;
                            border-radius: 6px;
                            padding: 6px 8px;
                            background-color: white;
                            font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
                            font-size: 10px;
                            color: #333333;
                            min-width: 90px;
                            min-height: 20px;
                        }
                        QLineEdit:focus {
                            border: 2px solid #2196F3;
                            background-color: #fafafa;
                        }
                        QLineEdit:hover {
                            border: 2px solid #ffb74d;
                        }
                    """)
                    
                    # 连接信号
                    input_field.textChanged.connect(self.on_nav2_sig_changed)
                    input_field.textChanged.connect(self.validate_hex_input)
                    input_field.editingFinished.connect(self.auto_pad_hex_input)
                    
                    self.signal_grid.addWidget(input_field, row, col + 1)
                    
                    # 存储输入框引用
                    signal_inputs[name] = input_field
                
                self.nav2_sig_signal_inputs.append(signal_inputs)
                
        except Exception as e:
            print(f"更新信号字段失败: {str(e)}")
    
    def on_satellite_count_changed(self):
        """当卫星数量改变时，动态更新卫星字段"""
        try:
            # 获取numViewTot的值
            num_view_tot_text = self.nav2_sat_fixed_inputs.get("numViewTot", "").text().strip()
            print(f"numViewTot输入变化: '{num_view_tot_text}', 长度: {len(num_view_tot_text)}")
            
            if not num_view_tot_text:
                print("清空卫星字段")
                self.update_satellite_fields(0)
                return
            
            # 检查是否输入了2位16进制数
            if len(num_view_tot_text) == 2:
                print(f"检测到2位输入，准备解析卫星数量")
                # 解析卫星数量
                try:
                    satellite_count = int(num_view_tot_text, 16)
                    if satellite_count < 0:
                        satellite_count = 0
                    elif satellite_count > 32:  # 限制最大卫星数量
                        satellite_count = 32
                    print(f"解析成功，卫星数量: {satellite_count}")
                except ValueError:
                    satellite_count = 0
                    print(f"解析失败，使用默认值: {satellite_count}")
                
                # 立即更新卫星字段
                print(f"开始更新卫星字段，数量: {satellite_count}")
                self.update_satellite_fields(satellite_count)
                self.update_packet_preview()
                print("卫星字段更新完成")
            else:
                print(f"输入长度不足2位，当前长度: {len(num_view_tot_text)}")
            
        except Exception as e:
            print(f"处理卫星数量变化失败: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def on_satellite_count_finished(self):
        """当卫星数量输入完成时，最终确认并更新"""
        try:
            # 获取numViewTot的值
            num_view_tot_text = self.nav2_sat_fixed_inputs.get("numViewTot", "").text().strip()
            if not num_view_tot_text:
                self.update_satellite_fields(0)
                return
            
            # 解析卫星数量
            try:
                satellite_count = int(num_view_tot_text, 16)
                if satellite_count < 0:
                    satellite_count = 0
                elif satellite_count > 32:  # 限制最大卫星数量
                    satellite_count = 32
            except ValueError:
                satellite_count = 0
            
            # 最终更新卫星字段
            self.update_satellite_fields(satellite_count)
            self.update_packet_preview()
            
        except Exception as e:
            print(f"处理卫星数量输入完成失败: {str(e)}")
    
    def on_signal_count_changed(self):
        """当信号数量改变时，动态更新信号字段"""
        try:
            # 获取numTrkTot的值
            num_trk_tot_text = self.nav2_sig_fixed_inputs.get("numTrkTot", "").text().strip()
            print(f"numTrkTot输入变化: '{num_trk_tot_text}', 长度: {len(num_trk_tot_text)}")
            
            if not num_trk_tot_text:
                print("清空信号字段")
                self.update_signal_fields(0)
                return
            
            # 检查是否输入了2位16进制数
            if len(num_trk_tot_text) == 2:
                print(f"检测到2位输入，准备解析信号数量")
                # 解析信号数量
                try:
                    signal_count = int(num_trk_tot_text, 16)
                    if signal_count < 0:
                        signal_count = 0
                    elif signal_count > 32:  # 限制最大信号数量
                        signal_count = 32
                    print(f"解析成功，信号数量: {signal_count}")
                except ValueError:
                    signal_count = 0
                    print(f"解析失败，使用默认值: {signal_count}")
                
                # 立即更新信号字段
                print(f"开始更新信号字段，数量: {signal_count}")
                self.update_signal_fields(signal_count)
                self.update_packet_preview()
                print("信号字段更新完成")
            else:
                print(f"输入长度不足2位，当前长度: {len(num_trk_tot_text)}")
            
        except Exception as e:
            print(f"处理信号数量变化失败: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def on_signal_count_finished(self):
        """当信号数量输入完成时，最终确认并更新"""
        try:
            # 获取numTrkTot的值
            num_trk_tot_text = self.nav2_sig_fixed_inputs.get("numTrkTot", "").text().strip()
            if not num_trk_tot_text:
                self.update_signal_fields(0)
                return
            
            # 解析信号数量
            try:
                signal_count = int(num_trk_tot_text, 16)
                if signal_count < 0:
                    signal_count = 0
                elif signal_count > 32:  # 限制最大信号数量
                    signal_count = 32
            except ValueError:
                signal_count = 0
            
            # 最终更新信号字段
            self.update_signal_fields(signal_count)
            self.update_packet_preview()
            
        except Exception as e:
            print(f"处理信号数量输入完成失败: {str(e)}")
    
    def adjust_window_size(self):
        """调整窗口大小，确保所有组件都能正确显示"""
        try:
            # 获取当前窗口大小
            current_size = self.size()
            
            # 根据当前显示的消息类型调整窗口大小
            if self.nav2_sat_widget.isVisible():
                # NAV2-SAT需要更多空间显示卫星信息
                target_height = 800
            elif self.nav2_sig_widget.isVisible():
                # NAV2-SIG需要更多空间显示信号信息
                target_height = 800
            elif self.nav2_dop_widget.isVisible():
                # NAV2-DOP使用最小窗口大小
                target_height = 600
            elif (self.nav2_sol_widget.isVisible() or 
                  self.nav2_pvh_widget.isVisible() or 
                  self.nav2_timeutc_widget.isVisible() or 
                  self.nav2_clk_widget.isVisible() or 
                  self.nav2_rvt_widget.isVisible() or 
                  self.nav2_rtc_widget.isVisible()):
                # 其他固定长度的NAV2消息类型使用中等窗口大小
                target_height = 700
            else:
                # 默认大小
                target_height = 600
            
            # 如果当前高度与目标高度不同，则调整
            if current_size.height() != target_height:
                self.resize(current_size.width(), target_height)
                # 强制更新布局
                self.updateGeometry()
                self.adjustSize()
                print(f"窗口大小已调整: {current_size.width()}x{current_size.height()} -> {current_size.width()}x{target_height}")
                
        except Exception as e:
            print(f"调整窗口大小失败: {str(e)}")