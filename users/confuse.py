import base64
import time

def is_validation_field_valid(encoded_str):
    """校验时间是否超时"""
    try:
        # 1. Base64 解码
        decoded_str = base64.b64decode(encoded_str).decode('utf-8')
        
        # 2. 字符串反转
        reversed_str = decoded_str[::-1]
        
        # 3. ASCII 还原
        original = "".join([chr(ord(c) - 1) for c in reversed_str])
        
        # 4. 分离时间戳和盐 (取前13位)
        timestamp_str = original[:13]
        client_timestamp = int(timestamp_str)
        
        # 5. 计算差值 (单位：毫秒)
        current_timestamp = int(time.time() * 1000)
        time_diff = current_timestamp - client_timestamp
        
        # 6. 校验：差值是否在 0 到 120,000 毫秒（2分钟）之间
        # 我们同时校验是否为负数（防止客户端时间早于服务器太多，或者恶意重放）
        if 0 <= time_diff <= 120000:
            return True, "验证通过"
        else:
            return False, f"请求过期或时间戳异常 (差值: {time_diff}ms)"
            
    except Exception as e:
        return False, f"解析失败: {str(e)}"

