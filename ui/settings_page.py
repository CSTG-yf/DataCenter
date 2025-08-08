from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, 
                             QLabel, QCheckBox, QPushButton, QSpinBox, QComboBox)
from PyQt6.QtCore import pyqtSignal


class SettingsPage(QWidget):
    """设置页面"""
    
    # 定义信号
    settings_changed_signal = pyqtSignal(dict)  # 设置变更信号
    reset_settings_signal = pyqtSignal()        # 重置设置信号
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        """初始化UI界面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # 页面标题
        title = QLabel("设置")
        title.setStyleSheet("""
            QLabel {
                font-size: 24px; 
                font-weight: bold; 
                color: #333333;
                margin-bottom: 20px;
                background-color: transparent;
                border: none;
            }
        """)
        layout.addWidget(title)
        
        # 应用程序设置组
        app_settings_group = QGroupBox("应用程序设置")
        app_settings_group.setStyleSheet("""
            QGroupBox {
                font-size: 16px;
                font-weight: bold;
                color: #333333;
                border: none;
                background-color: transparent;
                margin-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 0px;
                padding: 0px 0px 0px 0px;
                color: #333333;
                background-color: transparent;
            }
        """)
        app_settings_layout = QVBoxLayout(app_settings_group)
        app_settings_layout.setSpacing(15)
        app_settings_layout.setContentsMargins(0, 20, 0, 0)
        
        # 自动刷新串口列表
        self.auto_refresh_check = QCheckBox("自动刷新串口列表")
        self.auto_refresh_check.setChecked(True)
        self.auto_refresh_check.setStyleSheet("""
            QCheckBox {
                font-size: 14px;
                color: #333333;
                spacing: 8px;
                background-color: transparent;
                border: none;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border: 2px solid #d0d0d0;
                border-radius: 3px;
                background-color: white;
            }
            QCheckBox::indicator:checked {
                background-color: #2196F3;
                border: 2px solid #2196F3;
            }
            QCheckBox::indicator:hover {
                border: 2px solid #2196F3;
            }
        """)
        self.auto_refresh_check.toggled.connect(self.on_setting_changed)
        app_settings_layout.addWidget(self.auto_refresh_check)
        
        # 保存历史记录
        self.save_history_check = QCheckBox("保存历史记录")
        self.save_history_check.setChecked(True)
        self.save_history_check.setStyleSheet("""
            QCheckBox {
                font-size: 14px;
                color: #333333;
                spacing: 8px;
                background-color: transparent;
                border: none;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border: 2px solid #d0d0d0;
                border-radius: 3px;
                background-color: white;
            }
            QCheckBox::indicator:checked {
                background-color: #2196F3;
                border: 2px solid #2196F3;
            }
            QCheckBox::indicator:hover {
                border: 2px solid #2196F3;
            }
        """)
        self.save_history_check.toggled.connect(self.on_setting_changed)
        app_settings_layout.addWidget(self.save_history_check)
        
        # 串口自动保存设置
        serial_save_group = QGroupBox("串口数据保存设置")
        serial_save_group.setStyleSheet("""
            QGroupBox {
                font-size: 16px;
                font-weight: bold;
                color: #333333;
                border: none;
                background-color: transparent;
                margin-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 0px;
                padding: 0px 0px 0px 0px;
                color: #333333;
                background-color: transparent;
            }
        """)
        serial_save_layout = QVBoxLayout(serial_save_group)
        serial_save_layout.setSpacing(15)
        serial_save_layout.setContentsMargins(0, 20, 0, 0)
        
        # 自动保存串口数据
        self.auto_save_serial_check = QCheckBox("自动保存串口数据到文件")
        self.auto_save_serial_check.setChecked(True)  # 默认启用
        self.auto_save_serial_check.setStyleSheet("""
            QCheckBox {
                font-size: 14px;
                color: #333333;
                spacing: 8px;
                background-color: transparent;
                border: none;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border: 2px solid #d0d0d0;
                border-radius: 3px;
                background-color: white;
            }
            QCheckBox::indicator:checked {
                background-color: #2196F3;
                border: 2px solid #2196F3;
            }
            QCheckBox::indicator:hover {
                border: 2px solid #2196F3;
            }
        """)
        self.auto_save_serial_check.toggled.connect(self.on_setting_changed)
        serial_save_layout.addWidget(self.auto_save_serial_check)
        
        # 保存目录说明
        save_dir_label = QLabel("数据将保存到软件目录下的 serial_logs 文件夹中")
        save_dir_label.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: #666666;
                background-color: transparent;
                border: none;
                padding: 0px;
                margin: 0px;
            }
        """)
        serial_save_layout.addWidget(save_dir_label)
        
        # 文件大小限制
        file_size_layout = QHBoxLayout()
        file_size_label = QLabel("单个文件最大大小(MB):")
        file_size_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #333333;
                background-color: transparent;
                border: none;
            }
        """)
        file_size_layout.addWidget(file_size_label)
        
        self.file_size_limit = QSpinBox()
        self.file_size_limit.setRange(100, 1000)
        self.file_size_limit.setValue(500)  # 默认500MB
        self.file_size_limit.setSuffix(" MB")
        self.file_size_limit.setStyleSheet("""
            QSpinBox {
                border: 1px solid #d0d0d0;
                border-radius: 6px;
                padding: 8px 12px;
                background-color: white;
                font-size: 14px;
                color: #333333;
            }
            QSpinBox:hover {
                border: 2px solid #2196F3;
            }
            QSpinBox:focus {
                border: 2px solid #1976D2;
            }
            QSpinBox::up-button, QSpinBox::down-button {
                border: none;
                background-color: transparent;
                width: 20px;
            }
        """)
        self.file_size_limit.valueChanged.connect(self.on_setting_changed)
        file_size_layout.addWidget(self.file_size_limit)
        file_size_layout.addStretch()
        serial_save_layout.addLayout(file_size_layout)
        
        app_settings_layout.addWidget(serial_save_group)
        
        # 自动保存间隔
        auto_save_layout = QHBoxLayout()
        auto_save_label = QLabel("自动保存间隔(分钟):")
        auto_save_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #333333;
                background-color: transparent;
                border: none;
            }
        """)
        auto_save_layout.addWidget(auto_save_label)
        
        self.auto_save_interval = QSpinBox()
        self.auto_save_interval.setRange(1, 60)
        self.auto_save_interval.setValue(5)
        self.auto_save_interval.setStyleSheet("""
            QSpinBox {
                border: 1px solid #d0d0d0;
                border-radius: 6px;
                padding: 8px 12px;
                background-color: white;
                font-size: 14px;
                color: #333333;
            }
            QSpinBox:hover {
                border: 2px solid #2196F3;
            }
            QSpinBox:focus {
                border: 2px solid #1976D2;
            }
            QSpinBox::up-button, QSpinBox::down-button {
                border: none;
                background-color: transparent;
                width: 20px;
            }
        """)
        self.auto_save_interval.valueChanged.connect(self.on_setting_changed)
        auto_save_layout.addWidget(self.auto_save_interval)
        auto_save_layout.addStretch()
        app_settings_layout.addLayout(auto_save_layout)
        
        layout.addWidget(app_settings_group)
        
        # 显示设置组
        display_settings_group = QGroupBox("显示设置")
        display_settings_group.setStyleSheet("""
            QGroupBox {
                font-size: 16px;
                font-weight: bold;
                color: #333333;
                border: none;
                background-color: transparent;
                margin-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 0px;
                padding: 0px 0px 0px 0px;
                color: #333333;
                background-color: transparent;
            }
        """)
        display_settings_layout = QVBoxLayout(display_settings_group)
        display_settings_layout.setSpacing(15)
        display_settings_layout.setContentsMargins(0, 20, 0, 0)
        
        # 默认字体大小
        font_size_layout = QHBoxLayout()
        font_size_label = QLabel("默认字体大小:")
        font_size_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #333333;
                background-color: transparent;
                border: none;
            }
        """)
        font_size_layout.addWidget(font_size_label)
        
        self.font_size_combo = QComboBox()
        self.font_size_combo.addItems(['8', '9', '10', '11', '12', '14', '16'])
        self.font_size_combo.setCurrentText('10')
        self.font_size_combo.setStyleSheet("""
            QComboBox {
                border: 1px solid #d0d0d0;
                border-radius: 6px;
                padding: 8px 12px;
                background-color: white;
                font-size: 14px;
                color: #333333;
            }
            QComboBox:hover {
                border: 2px solid #2196F3;
            }
            QComboBox:focus {
                border: 2px solid #1976D2;
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
        self.font_size_combo.currentTextChanged.connect(self.on_setting_changed)
        font_size_layout.addWidget(self.font_size_combo)
        font_size_layout.addStretch()
        display_settings_layout.addLayout(font_size_layout)
        
        # 显示时间戳
        self.show_timestamp_check = QCheckBox("显示时间戳")
        self.show_timestamp_check.setChecked(True)
        self.show_timestamp_check.setStyleSheet("""
            QCheckBox {
                font-size: 14px;
                color: #333333;
                spacing: 8px;
                background-color: transparent;
                border: none;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border: 2px solid #d0d0d0;
                border-radius: 3px;
                background-color: white;
            }
            QCheckBox::indicator:checked {
                background-color: #2196F3;
                border: 2px solid #2196F3;
            }
            QCheckBox::indicator:hover {
                border: 2px solid #2196F3;
            }
        """)
        self.show_timestamp_check.toggled.connect(self.on_setting_changed)
        display_settings_layout.addWidget(self.show_timestamp_check)
        
        # 显示发送/接收标识
        self.show_direction_check = QCheckBox("显示发送/接收标识")
        self.show_direction_check.setChecked(True)
        self.show_direction_check.setStyleSheet("""
            QCheckBox {
                font-size: 14px;
                color: #333333;
                spacing: 8px;
                background-color: transparent;
                border: none;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border: 2px solid #d0d0d0;
                border-radius: 3px;
                background-color: white;
            }
            QCheckBox::indicator:checked {
                background-color: #2196F3;
                border: 2px solid #2196F3;
            }
            QCheckBox::indicator:hover {
                border: 2px solid #2196F3;
            }
        """)
        self.show_direction_check.toggled.connect(self.on_setting_changed)
        display_settings_layout.addWidget(self.show_direction_check)
        
        layout.addWidget(display_settings_group)
        
        # 控制按钮
        control_layout = QHBoxLayout()
        
        # 重置设置按钮
        self.reset_btn = QPushButton("重置设置")
        self.reset_btn.clicked.connect(self.reset_settings_signal.emit)
        self.reset_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #FF9800;
                border: none;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                color: #F57C00;
            }
        """)
        control_layout.addWidget(self.reset_btn)
        
        control_layout.addStretch()
        layout.addLayout(control_layout)
        
        layout.addStretch()
    
    def on_setting_changed(self):
        """设置变更时的处理"""
        settings = self.get_settings()
        self.settings_changed_signal.emit(settings)
    
    def get_settings(self):
        """获取当前设置"""
        return {
            'auto_refresh_ports': self.auto_refresh_check.isChecked(),
            'save_history': self.save_history_check.isChecked(),
            'auto_save_serial': self.auto_save_serial_check.isChecked(),
            'file_size_limit': self.file_size_limit.value(),
            'auto_save_interval': self.auto_save_interval.value(),
            'font_size': int(self.font_size_combo.currentText()),
            'show_timestamp': self.show_timestamp_check.isChecked(),
            'show_direction': self.show_direction_check.isChecked()
        }
    
    def set_settings(self, settings):
        """设置配置项"""
        if 'auto_refresh_ports' in settings:
            self.auto_refresh_check.setChecked(settings['auto_refresh_ports'])
        
        if 'save_history' in settings:
            self.save_history_check.setChecked(settings['save_history'])
        
        if 'auto_save_serial' in settings:
            self.auto_save_serial_check.setChecked(settings['auto_save_serial'])
        
        if 'file_size_limit' in settings:
            self.file_size_limit.setValue(settings['file_size_limit'])
        
        if 'auto_save_interval' in settings:
            self.auto_save_interval.setValue(settings['auto_save_interval'])
        
        if 'font_size' in settings:
            self.font_size_combo.setCurrentText(str(settings['font_size']))
        
        if 'show_timestamp' in settings:
            self.show_timestamp_check.setChecked(settings['show_timestamp'])
        
        if 'show_direction' in settings:
            self.show_direction_check.setChecked(settings['show_direction']) 