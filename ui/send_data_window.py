from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QTextEdit, QPushButton, QLabel, QLineEdit, QCheckBox,
                             QSpinBox, QFrame, QGroupBox, QMessageBox, QGridLayout, QComboBox)
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
        fields_grid.addWidget(self.payload_input, 4, 1)
        
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
        
        # 数据包预览区域
        preview_frame = QFrame()
        preview_frame.setStyleSheet("""
            QFrame {
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                background-color: #f8f9fa;
            }
        """)
        
        preview_layout = QVBoxLayout(preview_frame)
        preview_layout.setContentsMargins(15, 15, 15, 15)
        
        # 预览标签
        preview_label = QLabel("完整数据包预览:")
        preview_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: #333333;
                background-color: transparent;
                border: none;
                margin-bottom: 10px;
            }
        """)
        preview_layout.addWidget(preview_label)
        
        # 预览文本框
        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        self.preview_text.setStyleSheet("""
            QTextEdit {
                border: 1px solid #d0d0d0;
                border-radius: 4px;
                padding: 10px;
                background-color: #f5f5f5;
                font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
                font-size: 12px;
                color: #333333;
            }
        """)
        self.preview_text.setMaximumHeight(120)
        preview_layout.addWidget(self.preview_text)
        
        layout.addWidget(preview_frame)
        
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
            payload_text = self.payload_input.toPlainText().strip()
            
            if class_value is None or id_value is None:
                return None
            
            # 处理空有效载荷的情况
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
            payload_length = len(payload_data)
            
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
            
            # 转换为十六进制字符串
            hex_packet = ' '.join([f"{b:02X}" for b in packet])
            
            # 更新预览
            self.preview_text.setPlainText(hex_packet)
            
            return hex_packet
            
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
                
            payload_text = self.payload_input.toPlainText().strip()
            
            # 如果没有有效载荷，显示基本信息
            if not payload_text:
                self.length_input.setText("0 字节 (0x0000)")
                self.checksum_input.setText(f"0x{(id_value << 24) + (class_value << 16):08X}")
                self.preview_text.setPlainText("请输入有效载荷数据")
                return
            
            # 解析有效载荷（使用静默模式）
            payload_data = self.parse_hex_payload(payload_text, silent)
            if payload_data is None:
                return
            
            # 构建完整数据包
            packet_data = self.build_csip_packet(silent)
            if packet_data:
                # 更新长度和校验值显示
                payload_length = len(payload_data)
                checksum = self.calculate_checksum(class_value, id_value, payload_length, payload_data)
                
                self.length_input.setText(f"{payload_length} 字节 (0x{payload_length:04X})")
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
            
        elif "RXM2" in selected_class:
            self.id_combo.clear()
            self.id_combo.addItems([
                "0x00 - 伪距、载波相位原始测量信息 (Pseudorange, carrier phase raw measurement information)",
                "0x01 - 卫星位置信息(所有卫星) (Satellite position information (all satellites))",
                "0x06 - 卫星原始电文信息 (Satellite raw ephemeris information)",
                "0x0A - 卫星位置信息(单颗卫星) (Satellite position information (single satellite))"
            ])
            self.id_combo.setCurrentText("0x00 - 伪距、载波相位原始测量信息 (Pseudorange, carrier phase raw measurement information)")
            
        elif "ACK" in selected_class:
            self.id_combo.clear()
            self.id_combo.addItems([
                "0x00 - 回复表示消息未被正确接收 (Reply indicating message not correctly received)",
                "0x01 - 回复表示消息被正确接收 (Reply indicating message correctly received)"
            ])
            self.id_combo.setCurrentText("0x01 - 回复表示消息被正确接收 (Reply indicating message correctly received)")
            
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
            
        elif "AID" in selected_class:
            self.id_combo.clear()
            self.id_combo.addItems([
                "0x01 - AID-INI (辅助位置、时间、频率、时钟频偏信息 - Auxiliary position, time, frequency, clock bias information)"
            ])
            self.id_combo.setCurrentText("0x01 - AID-INI (辅助位置、时间、频率、时钟频偏信息 - Auxiliary position, time, frequency, clock bias information)")
            
        elif "INS2" in selected_class:
            self.id_combo.clear()
            self.id_combo.addItems([
                "0x00 - INS2-ATT (IMU 坐标系相对于本地导航坐标系(NED)的姿态 - IMU coordinate system attitude relative to local navigation coordinate system (NED))",
                "0x01 - INS2-IMU (传感器信息 - Sensor information)"
            ])
            self.id_combo.setCurrentText("0x00 - INS2-ATT (IMU 坐标系相对于本地导航坐标系(NED)的姿态 - IMU coordinate system attitude relative to local navigation coordinate system (NED))")
            
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
            
        else:
            # 默认选项
            self.id_combo.clear()
            self.id_combo.addItems([
                "0x01 - 默认消息ID (Default Message ID)"
            ])
            self.id_combo.setCurrentText("0x01 - 默认消息ID (Default Message ID)")
        
        # 重新连接信号
        self.id_combo.currentTextChanged.connect(self.update_packet_preview) 