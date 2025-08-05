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
        
        # 页面标题
        title = QLabel("设置")
        title.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 20px;")
        layout.addWidget(title)
        
        # 应用程序设置组
        app_settings_group = QGroupBox("应用程序设置")
        app_settings_layout = QVBoxLayout(app_settings_group)
        
        # 自动刷新串口列表
        self.auto_refresh_check = QCheckBox("自动刷新串口列表")
        self.auto_refresh_check.setChecked(True)
        self.auto_refresh_check.toggled.connect(self.on_setting_changed)
        app_settings_layout.addWidget(self.auto_refresh_check)
        
        # 保存历史记录
        self.save_history_check = QCheckBox("保存历史记录")
        self.save_history_check.setChecked(True)
        self.save_history_check.toggled.connect(self.on_setting_changed)
        app_settings_layout.addWidget(self.save_history_check)
        
        # 自动保存间隔
        auto_save_layout = QHBoxLayout()
        auto_save_layout.addWidget(QLabel("自动保存间隔(分钟):"))
        self.auto_save_interval = QSpinBox()
        self.auto_save_interval.setRange(1, 60)
        self.auto_save_interval.setValue(5)
        self.auto_save_interval.valueChanged.connect(self.on_setting_changed)
        auto_save_layout.addWidget(self.auto_save_interval)
        auto_save_layout.addStretch()
        app_settings_layout.addLayout(auto_save_layout)
        
        layout.addWidget(app_settings_group)
        
        # 显示设置组
        display_settings_group = QGroupBox("显示设置")
        display_settings_layout = QVBoxLayout(display_settings_group)
        
        # 默认字体大小
        font_size_layout = QHBoxLayout()
        font_size_layout.addWidget(QLabel("默认字体大小:"))
        self.font_size_combo = QComboBox()
        self.font_size_combo.addItems(['8', '9', '10', '11', '12', '14', '16'])
        self.font_size_combo.setCurrentText('10')
        self.font_size_combo.currentTextChanged.connect(self.on_setting_changed)
        font_size_layout.addWidget(self.font_size_combo)
        font_size_layout.addStretch()
        display_settings_layout.addLayout(font_size_layout)
        
        # 显示时间戳
        self.show_timestamp_check = QCheckBox("显示时间戳")
        self.show_timestamp_check.setChecked(True)
        self.show_timestamp_check.toggled.connect(self.on_setting_changed)
        display_settings_layout.addWidget(self.show_timestamp_check)
        
        # 显示发送/接收标识
        self.show_direction_check = QCheckBox("显示发送/接收标识")
        self.show_direction_check.setChecked(True)
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
                background-color: #FF9800;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 6px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #F57C00;
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
        
        if 'auto_save_interval' in settings:
            self.auto_save_interval.setValue(settings['auto_save_interval'])
        
        if 'font_size' in settings:
            self.font_size_combo.setCurrentText(str(settings['font_size']))
        
        if 'show_timestamp' in settings:
            self.show_timestamp_check.setChecked(settings['show_timestamp'])
        
        if 'show_direction' in settings:
            self.show_direction_check.setChecked(settings['show_direction']) 