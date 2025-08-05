from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, QPushButton, QGroupBox
from PyQt6.QtCore import pyqtSignal


class HistoryPage(QWidget):
    """历史记录页面"""
    
    # 定义信号
    clear_history_signal = pyqtSignal()  # 清空历史记录信号
    save_history_signal = pyqtSignal()   # 保存历史记录信号
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        """初始化UI界面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 页面标题
        title = QLabel("历史记录")
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title)
        
        # 历史记录控制组
        control_group = QGroupBox("历史记录控制")
        control_layout = QHBoxLayout(control_group)
        
        # 清空历史记录按钮
        self.clear_history_btn = QPushButton("清空历史记录")
        self.clear_history_btn.clicked.connect(self.clear_history_signal.emit)
        control_layout.addWidget(self.clear_history_btn)
        
        # 保存历史记录按钮
        self.save_history_btn = QPushButton("保存历史记录")
        self.save_history_btn.clicked.connect(self.save_history_signal.emit)
        control_layout.addWidget(self.save_history_btn)
        
        control_layout.addStretch()
        layout.addWidget(control_group)
        
        # 历史记录文本区域
        self.history_text = QTextEdit()
        self.history_text.setReadOnly(True)
        self.history_text.setPlaceholderText("历史记录将在这里显示...")
        layout.addWidget(self.history_text)
        
        # 统计信息
        stats_layout = QHBoxLayout()
        self.history_count_label = QLabel("记录条数: 0")
        self.history_size_label = QLabel("文件大小: 0 KB")
        stats_layout.addWidget(self.history_count_label)
        stats_layout.addWidget(self.history_size_label)
        stats_layout.addStretch()
        layout.addLayout(stats_layout)
    
    def append_history(self, text):
        """添加历史记录"""
        self.history_text.append(text)
    
    def clear_history(self):
        """清空历史记录"""
        self.history_text.clear()
    
    def set_history_content(self, content):
        """设置历史记录内容"""
        self.history_text.setPlainText(content)
    
    def get_history_content(self):
        """获取历史记录内容"""
        return self.history_text.toPlainText()
    
    def update_statistics(self, count, size_kb):
        """更新统计信息"""
        self.history_count_label.setText(f"记录条数: {count}")
        self.history_size_label.setText(f"文件大小: {size_kb} KB") 