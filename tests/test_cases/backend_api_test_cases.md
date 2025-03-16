# 后端 API 测试用例

## 1. 用户认证模块

### TC-B001: 用户注册
- **接口**：`POST /api/auth/register`
- **前置条件**：
  - 服务器正常运行
  - 数据库已连接
- **测试数据**：
```json
{
    "username": "testuser",
    "password": "Test123!",
    "email": "test@example.com",
    "phone": "13800138000"
}
```
- **测试步骤**：
  1. 发送注册请求
  2. 检查响应状态码和数据格式
  3. 验证用户是否成功写入数据库
- **预期结果**：
  - 状态码：200
  - 返回格式：
```json
{
    "code": 200,
    "message": "注册成功",
    "data": {
        "userId": "用户ID",
        "username": "testuser"
    }
}
```
- **实际结果**：
  - [ ] 待测试

### TC-B002: 重复用户名注册
- **接口**：`POST /api/auth/register`
- **前置条件**：
  - 已存在用户名为 "testuser" 的用户
- **测试数据**：
```json
{
    "username": "testuser",
    "password": "Test123!",
    "email": "test2@example.com",
    "phone": "13800138001"
}
```
- **预期结果**：
  - 状态码：400
  - 返回信息：用户名已存在
- **实际结果**：
  - [ ] 待测试

### TC-B003: 用户登录
- **接口**：`POST /api/auth/login`
- **前置条件**：
  - 数据库中已存在测试用户
- **测试数据**：
```json
{
    "username": "testuser",
    "password": "Test123!"
}
```
- **预期结果**：
  - 状态码：200
  - 返回格式：
```json
{
    "code": 200,
    "message": "登录成功",
    "data": {
        "token": "JWT令牌",
        "userInfo": {
            "userId": "用户ID",
            "username": "testuser",
            "role": "用户角色"
        }
    }
}
```
- **实际结果**：
  - [ ] 待测试

### TC-B004: 错误密码登录
- **接口**：`POST /api/auth/login`
- **前置条件**：
  - 数据库中已存在测试用户
- **测试数据**：
```json
{
    "username": "testuser",
    "password": "WrongPass123!"
}
```
- **预期结果**：
  - 状态码：401
  - 返回信息：用户名或密码错误
- **实际结果**：
  - [ ] 待测试

## 2. 用户信息模块

### TC-B005: 获取用户信息
- **接口**：`GET /api/user/info`
- **前置条件**：
  - 用户已登录
  - 持有有效 token
- **请求头**：
```
Authorization: Bearer {token}
```
- **预期结果**：
  - 状态码：200
  - 返回用户完整信息
- **实际结果**：
  - [ ] 待测试

### TC-B006: 未授权访问
- **接口**：`GET /api/user/info`
- **前置条件**：
  - 无 token 或 token 无效
- **预期结果**：
  - 状态码：401
  - 返回未授权错误信息
- **实际结果**：
  - [ ] 待测试

## 3. 密码安全测试

### TC-B007: 密码强度验证
- **接口**：`POST /api/auth/register`
- **测试数据集**：
```json
[
    {"password": "short", "expect": "密码长度不足"},
    {"password": "nouppercase123!", "expect": "需要包含大写字母"},
    {"password": "NOLOWERCASE123!", "expect": "需要包含小写字母"},
    {"password": "NoNumbers!", "expect": "需要包含数字"},
    {"password": "NoSpecial123", "expect": "需要包含特殊字符"}
]
```
- **预期结果**：
  - 对应的错误提示
  - 状态码：400
- **实际结果**：
  - [ ] 待测试

## 4. Token 测试

### TC-B008: Token 过期测试
- **前置条件**：
  - 配置短期过期的 token
- **测试步骤**：
  1. 登录获取 token
  2. 等待 token 过期
  3. 使用过期 token 请求
- **预期结果**：
  - 状态码：401
  - 返回 token 过期信息
- **实际结果**：
  - [ ] 待测试

## Postman 测试流程

1. 环境设置：
```json
{
    "BASE_URL": "http://localhost:5000/api",
    "TOKEN": "",
    "TEST_USERNAME": "testuser",
    "TEST_PASSWORD": "Test123!"
}
```

2. 测试顺序：
   1. 注册新用户（TC-B001）
   2. 测试重复注册（TC-B002）
   3. 登录测试（TC-B003）
   4. 错误密码测试（TC-B004）
   5. 使用获得的 token 测试用户信息接口（TC-B005）
   6. 测试未授权访问（TC-B006）
   7. 测试密码强度验证（TC-B007）
   8. 测试 token 过期（TC-B008）

3. 自动化测试脚本示例：
```javascript
// 注册成功后的测试脚本
pm.test("注册成功状态码为 200", function () {
    pm.response.to.have.status(200);
});

pm.test("响应包含用户ID", function () {
    const jsonData = pm.response.json();
    pm.expect(jsonData.data).to.have.property('userId');
    // 保存用户ID供后续测试使用
    pm.environment.set("USER_ID", jsonData.data.userId);
});

// 登录成功后的测试脚本
pm.test("登录成功并获取token", function () {
    const jsonData = pm.response.json();
    pm.expect(jsonData.data).to.have.property('token');
    // 保存token供后续测试使用
    pm.environment.set("TOKEN", jsonData.data.token);
});
``` 