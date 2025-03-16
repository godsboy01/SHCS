import os
from werkzeug.utils import secure_filename

# 配置文件上传路径
UPLOAD_FOLDER = 'uploads/avatars'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# 确保上传目录存在
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# 检查文件扩展名是否允许
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# 处理文件上传
def handle_upload(file):
    if not file:
        return None, '未上传文件'
    if file.filename == '':
        return None, '未选择文件'
    if not allowed_file(file.filename):
        return None, '文件类型不支持'

    # 保存文件
    filename = secure_filename(file.filename)
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(file_path)

    return file_path, None