"""
设置工具模块
用于处理各种设置的解析和应用
"""

def parse_update_interval(interval_text):
    """
    解析更新间隔设置文本，返回毫秒数
    
    Args:
        interval_text (str): 更新间隔设置文本，如 "标准更新 (100ms)"
    
    Returns:
        int: 更新间隔的毫秒数
    """
    interval_map = {
        "实时更新 (0ms)": 0,
        "快速更新 (50ms)": 50,
        "标准更新 (100ms)": 100,
        "慢速更新 (200ms)": 200,
        "极慢更新 (500ms)": 500
    }
    
    return interval_map.get(interval_text, 100)  # 默认返回100ms


def get_update_interval_options():
    """
    获取更新间隔选项列表
    
    Returns:
        list: 更新间隔选项列表
    """
    return [
        "实时更新 (0ms)",
        "快速更新 (50ms)", 
        "标准更新 (100ms)",
        "慢速更新 (200ms)",
        "极慢更新 (500ms)"
    ]
