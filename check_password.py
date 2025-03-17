import sys
sys.path.append('.')  # 添加当前目录到Python路径

from flask import Flask
from SHCS.models.models import User, db
from SHCS.utils.password import check_password

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:123456@localhost:3306/smart_home_care'
db.init_app(app)

def check_user_password(username, password):
    with app.app_context():
        user = User.query.filter_by(username=username).first()
        if not user:
            return "用户不存在"
        print(f"数据库中的密码哈希: {user.password}")
        if check_password(password, user.password):
            return "密码正确"
        return "密码错误"

if __name__ == "__main__":
    result = check_user_password("test4", "Test123!")
    print(result) 