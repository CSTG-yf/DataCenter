import serial
import serial.tools.list_ports
import threading
import time
from PyQt6.QtCore import QObject, pyqtSignal, QTimer


class SerialHandler(QObject):
    """串口通信处理器，负责串口连接和数据收发"""
    
    # 定义信号
    data_received = pyqtSignal(str)  # 接收到数据信号
    connection_changed = pyqtSignal(bool)  # 连接状态改变信号
    error_occurred = pyqtSignal(str)  # 错误信号
    port_list_updated = pyqtSignal(list)  # 串口列表更新信号
    statistics_updated = pyqtSignal(int, int)  # 统计信息更新信号
    
    def __init__(self):
        super().__init__()
        self.serial_port = None
        self.is_connected = False
        self.receive_thread = None
        self.auto_send_timer = None
        self.auto_send_data = ""
        
        # 统计信息
        self.receive_count = 0
        self.send_count = 0
        
        # 创建自动发送定时器
        self.auto_send_timer = QTimer()
        self.auto_send_timer.timeout.connect(self.auto_send_data_func)
        
    def get_available_ports(self):
        """获取可用串口列表"""
        try:
            ports = [port.device for port in serial.tools.list_ports.comports()]
            self.port_list_updated.emit(ports)
            return ports
        except Exception as e:
            self.error_occurred.emit(f"获取串口列表失败: {str(e)}")
            return []
    
    def connect_serial(self, config):
        """连接串口"""
        try:
            if self.is_connected:
                self.disconnect_serial()
            
            # 设置默认参数（如果配置中没有提供）
            port = config.get('port')
            baudrate = config.get('baudrate', 115200)
            bytesize = config.get('bytesize', 8)
            stopbits = config.get('stopbits', 1)
            parity = config.get('parity', 'N')
            
            # 创建串口对象
            self.serial_port = serial.Serial(
                port=port,
                baudrate=baudrate,
                bytesize=bytesize,
                stopbits=stopbits,
                parity=parity,
                timeout=1
            )
            
            if self.serial_port.is_open:
                self.is_connected = True
                self.connection_changed.emit(True)
                
                # 启动接收线程
                self.receive_thread = threading.Thread(target=self.receive_data_loop, daemon=True)
                self.receive_thread.start()
                
                return True
            else:
                self.error_occurred.emit("串口打开失败")
                return False
                
        except serial.SerialException as e:
            self.error_occurred.emit(f"串口连接失败: {str(e)}")
            return False
        except Exception as e:
            self.error_occurred.emit(f"连接错误: {str(e)}")
            return False
    
    def disconnect_serial(self):
        """断开串口连接"""
        try:
            # 停止自动发送
            if self.auto_send_timer.isActive():
                self.auto_send_timer.stop()
            
            # 关闭串口
            if self.serial_port and self.serial_port.is_open:
                self.serial_port.close()
            
            self.is_connected = False
            self.connection_changed.emit(False)
            
        except Exception as e:
            self.error_occurred.emit(f"断开连接错误: {str(e)}")
    
    def send_data(self, data, hex_mode=False):
        """发送数据"""
        if not self.is_connected or not self.serial_port:
            self.error_occurred.emit("串口未连接")
            return False
        
        try:
            if hex_mode:
                # 十六进制发送
                data_bytes = self.hex_string_to_bytes(data)
            else:
                # 普通文本发送
                data_bytes = data.encode('utf-8')
            
            # 发送数据
            bytes_sent = self.serial_port.write(data_bytes)
            self.send_count += bytes_sent
            
            # 更新统计信息
            self.statistics_updated.emit(self.receive_count, self.send_count)
            
            return True
            
        except Exception as e:
            self.error_occurred.emit(f"发送数据失败: {str(e)}")
            return False
    
    def receive_data_loop(self):
        """接收数据循环"""
        while self.is_connected and self.serial_port and self.serial_port.is_open:
            try:
                if self.serial_port.in_waiting > 0:
                    # 读取数据
                    data = self.serial_port.read(self.serial_port.in_waiting)
                    if data:
                        # 转换为字符串
                        data_str = data.decode('utf-8', errors='ignore')
                        self.receive_count += len(data)
                        
                        # 发送接收数据信号
                        self.data_received.emit(data_str)
                        
                        # 更新统计信息
                        self.statistics_updated.emit(self.receive_count, self.send_count)
                
                time.sleep(0.01)  # 短暂休眠，避免CPU占用过高
                
            except Exception as e:
                self.error_occurred.emit(f"接收数据错误: {str(e)}")
                break
        
        # 接收循环结束，更新连接状态
        if self.is_connected:
            self.is_connected = False
            self.connection_changed.emit(False)
    
    def start_auto_send(self, data, interval_ms, hex_mode=False):
        """开始自动发送"""
        if not self.is_connected:
            self.error_occurred.emit("串口未连接")
            return False
        
        try:
            self.auto_send_data = data
            self.auto_send_hex_mode = hex_mode
            self.auto_send_timer.start(interval_ms)
            return True
        except Exception as e:
            self.error_occurred.emit(f"启动自动发送失败: {str(e)}")
            return False
    
    def stop_auto_send(self):
        """停止自动发送"""
        if self.auto_send_timer.isActive():
            self.auto_send_timer.stop()
    
    def auto_send_data_func(self):
        """自动发送数据函数"""
        if self.is_connected and self.auto_send_data:
            self.send_data(self.auto_send_data, self.auto_send_hex_mode)
    
    def clear_statistics(self):
        """清空统计信息"""
        self.receive_count = 0
        self.send_count = 0
        self.statistics_updated.emit(self.receive_count, self.send_count)
    
    def hex_string_to_bytes(self, hex_string):
        """将十六进制字符串转换为字节"""
        try:
            # 移除空格和换行符
            hex_string = hex_string.replace(' ', '').replace('\n', '').replace('\r', '')
            
            # 确保字符串长度为偶数
            if len(hex_string) % 2 != 0:
                hex_string = '0' + hex_string
            
            # 转换为字节
            return bytes.fromhex(hex_string)
        except ValueError as e:
            raise ValueError(f"无效的十六进制字符串: {str(e)}")
    
    def bytes_to_hex_string(self, data_bytes):
        """将字节转换为十六进制字符串"""
        return ' '.join([f'{b:02X}' for b in data_bytes])
    
    def get_connection_status(self):
        """获取连接状态"""
        return self.is_connected
    
    def get_statistics(self):
        """获取统计信息"""
        return self.receive_count, self.send_count
