import serial
import serial.tools.list_ports
import threading
import time
from PyQt6.QtCore import QObject, pyqtSignal, QTimer


class MultiSerialManager(QObject):
    """多串口管理器，负责管理多个串口连接"""
    
    # 定义信号
    data_received = pyqtSignal(str, str)  # 接收到数据信号 (port_name, data)
    connection_changed = pyqtSignal(str, bool)  # 连接状态改变信号 (port_name, connected)
    error_occurred = pyqtSignal(str, str)  # 错误信号 (port_name, error_message)
    port_list_updated = pyqtSignal(list)  # 串口列表更新信号
    statistics_updated = pyqtSignal(str, int, int)  # 统计信息更新信号 (port_name, receive_count, send_count)
    
    def __init__(self):
        super().__init__()
        self.serial_ports = {}  # 存储串口对象 {port_name: serial_object}
        self.receive_threads = {}  # 存储接收线程 {port_name: thread}
        self.auto_send_timers = {}  # 存储自动发送定时器 {port_name: timer}
        self.auto_send_data = {}  # 存储自动发送数据 {port_name: data}
        
        # 统计信息 {port_name: {'receive_count': 0, 'send_count': 0}}
        self.statistics = {}
        
    def get_available_ports(self):
        """获取可用串口列表"""
        try:
            ports = [port.device for port in serial.tools.list_ports.comports()]
            self.port_list_updated.emit(ports)
            return ports
        except Exception as e:
            self.error_occurred.emit("", f"获取串口列表失败: {str(e)}")
            return []
    
    def connect_serial(self, config):
        """连接串口"""
        try:
            port_name = config['port']
            
            # 检查是否已经连接
            if port_name in self.serial_ports:
                self.error_occurred.emit(port_name, f"串口 {port_name} 已经连接")
                return False
            
            # 设置默认参数
            baudrate = config.get('baudrate', 115200)
            bytesize = config.get('bytesize', 8)
            stopbits = config.get('stopbits', 1)
            parity = config.get('parity', 'N')
            
            # 创建串口对象
            serial_port = serial.Serial(
                port=port_name,
                baudrate=baudrate,
                bytesize=bytesize,
                stopbits=stopbits,
                parity=parity,
                timeout=1
            )
            
            if serial_port.is_open:
                # 存储串口对象
                self.serial_ports[port_name] = serial_port
                
                # 初始化统计信息
                self.statistics[port_name] = {'receive_count': 0, 'send_count': 0}
                
                # 创建自动发送定时器
                auto_send_timer = QTimer()
                auto_send_timer.timeout.connect(lambda: self.auto_send_data_func(port_name))
                self.auto_send_timers[port_name] = auto_send_timer
                
                # 启动接收线程
                receive_thread = threading.Thread(
                    target=self.receive_data_loop, 
                    args=(port_name,), 
                    daemon=True
                )
                self.receive_threads[port_name] = receive_thread
                receive_thread.start()
                
                # 等待线程启动
                import time
                time.sleep(0.05)
                
                # 发送连接状态信号
                self.connection_changed.emit(port_name, True)
                
                return True
            else:
                self.error_occurred.emit(port_name, "串口打开失败")
                return False
                
        except serial.SerialException as e:
            self.error_occurred.emit(port_name, f"串口连接失败: {str(e)}")
            return False
        except Exception as e:
            self.error_occurred.emit(port_name, f"连接错误: {str(e)}")
            return False
    
    def disconnect_serial(self, port_name):
        """断开指定串口连接"""
        try:
            if port_name in self.serial_ports:
                # 停止自动发送
                if port_name in self.auto_send_timers:
                    self.auto_send_timers[port_name].stop()
                
                # 关闭串口
                serial_port = self.serial_ports[port_name]
                if serial_port.is_open:
                    serial_port.close()
                
                # 清理资源
                del self.serial_ports[port_name]
                if port_name in self.auto_send_timers:
                    del self.auto_send_timers[port_name]
                if port_name in self.statistics:
                    del self.statistics[port_name]
                
                # 等待接收线程自然结束
                import time
                time.sleep(0.1)
                
                # 发送连接状态信号
                self.connection_changed.emit(port_name, False)
                
                return True
            else:
                self.error_occurred.emit(port_name, f"串口 {port_name} 未连接")
                return False
                
        except Exception as e:
            self.error_occurred.emit(port_name, f"断开连接错误: {str(e)}")
            return False
    
    def send_data(self, port_name, data, hex_mode=False):
        """向指定串口发送数据"""
        try:
            if port_name not in self.serial_ports:
                self.error_occurred.emit(port_name, f"串口 {port_name} 未连接")
                return False
            
            serial_port = self.serial_ports[port_name]
            
            if hex_mode:
                # 十六进制发送
                try:
                    # 移除空格和换行符
                    hex_string = data.replace(' ', '').replace('\n', '').replace('\r', '')
                    # 转换为字节
                    data_bytes = bytes.fromhex(hex_string)
                except ValueError:
                    self.error_occurred.emit(port_name, "十六进制数据格式错误")
                    return False
            else:
                # 普通文本发送
                data_bytes = data.encode('utf-8')
            
            # 发送数据
            serial_port.write(data_bytes)
            serial_port.flush()
            
            # 更新统计信息
            if port_name in self.statistics:
                self.statistics[port_name]['send_count'] += len(data_bytes)
                self.statistics_updated.emit(
                    port_name, 
                    self.statistics[port_name]['receive_count'],
                    self.statistics[port_name]['send_count']
                )
            
            return True
            
        except Exception as e:
            self.error_occurred.emit(port_name, f"发送数据失败: {str(e)}")
            return False
    
    def receive_data_loop(self, port_name):
        """接收数据循环"""
        try:
            serial_port = self.serial_ports[port_name]
            
            while port_name in self.serial_ports and serial_port.is_open:
                try:
                    # 检查串口是否仍然有效
                    if not serial_port.is_open:
                        break
                    
                    # 读取数据
                    data = serial_port.readline()
                    if data is not None and len(data) > 0:
                        # 转换为字符串
                        data_str = data.decode('utf-8', errors='ignore')
                        
                        # 更新统计信息
                        if port_name in self.statistics:
                            self.statistics[port_name]['receive_count'] += len(data)
                            self.statistics_updated.emit(
                                port_name,
                                self.statistics[port_name]['receive_count'],
                                self.statistics[port_name]['send_count']
                            )
                        
                        # 发送接收数据信号
                        self.data_received.emit(port_name, data_str)
                    
                    # 添加短暂延时避免CPU占用过高
                    import time
                    time.sleep(0.01)
                        
                except Exception as e:
                    if port_name in self.serial_ports:
                        # 检查是否是串口关闭导致的错误
                        if "Port is closed" in str(e) or "Access denied" in str(e):
                            # 串口已关闭，正常退出
                            break
                        else:
                            self.error_occurred.emit(port_name, f"接收数据错误: {str(e)}")
                    break
                    
        except Exception as e:
            self.error_occurred.emit(port_name, f"接收线程错误: {str(e)}")
    
    def start_auto_send(self, port_name, data, interval_ms, hex_mode=False):
        """开始自动发送"""
        try:
            if port_name not in self.serial_ports:
                self.error_occurred.emit(port_name, f"串口 {port_name} 未连接")
                return False
            
            # 存储自动发送数据
            self.auto_send_data[port_name] = {
                'data': data,
                'hex_mode': hex_mode
            }
            
            # 启动定时器
            if port_name in self.auto_send_timers:
                self.auto_send_timers[port_name].start(interval_ms)
            
            return True
            
        except Exception as e:
            self.error_occurred.emit(port_name, f"启动自动发送失败: {str(e)}")
            return False
    
    def stop_auto_send(self, port_name):
        """停止自动发送"""
        try:
            if port_name in self.auto_send_timers:
                self.auto_send_timers[port_name].stop()
            
            if port_name in self.auto_send_data:
                del self.auto_send_data[port_name]
            
            return True
            
        except Exception as e:
            self.error_occurred.emit(port_name, f"停止自动发送失败: {str(e)}")
            return False
    
    def auto_send_data_func(self, port_name):
        """自动发送数据函数"""
        try:
            if port_name in self.auto_send_data:
                auto_data = self.auto_send_data[port_name]
                self.send_data(port_name, auto_data['data'], auto_data['hex_mode'])
        except Exception as e:
            self.error_occurred.emit(port_name, f"自动发送数据失败: {str(e)}")
    
    def clear_statistics(self, port_name=None):
        """清空统计信息"""
        if port_name:
            if port_name in self.statistics:
                self.statistics[port_name] = {'receive_count': 0, 'send_count': 0}
                self.statistics_updated.emit(port_name, 0, 0)
        else:
            # 清空所有统计信息
            for port in self.statistics:
                self.statistics[port] = {'receive_count': 0, 'send_count': 0}
                self.statistics_updated.emit(port, 0, 0)
    
    def get_connection_status(self, port_name):
        """获取连接状态"""
        return port_name in self.serial_ports and self.serial_ports[port_name].is_open
    
    def get_statistics(self, port_name):
        """获取统计信息"""
        if port_name in self.statistics:
            return self.statistics[port_name]
        return {'receive_count': 0, 'send_count': 0}
    
    def get_all_connected_ports(self):
        """获取所有已连接的串口"""
        return list(self.serial_ports.keys())
    
    def disconnect_all(self):
        """断开所有串口连接"""
        for port_name in list(self.serial_ports.keys()):
            self.disconnect_serial(port_name) 