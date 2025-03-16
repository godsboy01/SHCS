from werkzeug.security import generate_password_hash, check_password_hash
# 密码工具 (utils/password.py)
def hash_password(password):
    """生成密码的哈希值"""
    return generate_password_hash(password)

def check_password(hashed_password, password):
    """验证密码是否正确"""
    return check_password_hash(hashed_password, password)

