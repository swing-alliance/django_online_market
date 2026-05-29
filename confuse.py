import base64
import urllib.parse

def restore_string_by_salt(encoded_str: str, salt: int) -> str:

    try:
        base64_decoded = base64.b64decode(encoded_str).decode('utf-8')
        url_decoded = urllib.parse.unquote(base64_decoded)
        shifted_chars = []
        for ch in url_decoded:
            original_char = chr(ord(ch) - salt)
            shifted_chars.append(original_char)
        decrypted = ''.join(reversed(shifted_chars))
        return decrypted
    except Exception as e:
        return f"还原失败: {e}"


def decrypt_confusion_data(encoded_str1: str, encoded_str2: str, salt: int):
    """
    批量解密两个混淆后的字符串
    """
    decrypted1 = restore_string_by_salt(encoded_str1, salt)
    decrypted2 = restore_string_by_salt(encoded_str2, salt)
    return {
        'decrypted1': decrypted1,
        'decrypted2': decrypted2
    }




# 使用示例
if __name__ == "__main__":
    # 假设从JS调试中获取到的混淆结果和盐值
    # 例如JS中输出: salt=42, data=["YWJjZGVmZw==", "MTIzNDU2Nzg="]
    # 这里的值需要替换为实际从页面获取的混淆数据
    
    confused_str1 = "JTVCJTIyZWNibyUyMiUyQyUyMmhxc2IlMjIlNUQ="   # 示例值，请替换为实际值
    confused_str2 = "JTIyZWNib3RyYWNlJTIy"                       # 示例值，请替换为实际值
    salt = 42  # 从JS中获取或通过其他方式获取
    
    result = decrypt_confusion_data(confused_str1, confused_str2, salt)
    print(f"解密结果1: {result['decrypted1']}")
    print(f"解密结果2: {result['decrypted2']}")