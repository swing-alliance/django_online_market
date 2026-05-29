

def checkwords(content):
    """检查敏感词"""
    # 这里可以使用一个敏感词列表，或者调用一个第三方的敏感词检测服务
    sensitive_words = ["badword1", "badword2", "badword3"]  # 示例敏感词列表
    for word in sensitive_words:
        if word in content:
            return False  # 如果发现敏感词，返回False
    return True  # 如果没有发现敏感词，返回True