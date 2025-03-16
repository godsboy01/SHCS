// 引入必要的库
const app = getApp();

Page({
  data: {
    username: '',  // 用户名
    phone: '',     // 手机号
    password: '',  // 密码
    code: '',      // 验证码
    clientHeight: 0,  // 动态高度
    canSendCode: true, // 控制是否可以发送验证码
    countdown: 60, // 倒计时时间
  },

  onLoad() {
    // 获取屏幕高度并设置到data中
    const that = this;
    wx.getSystemInfo({
      success(res) {
        that.setData({
          clientHeight: res.windowHeight
        });
      }
    });
  },

  // 输入框事件处理函数
  username(e) {
    this.setData({
      username: e.detail.value
    });
  },

  phone(e) {
    this.setData({
      phone: e.detail.value
    });
  },

  password(e) {
    this.setData({
      password: e.detail.value
    });
  },

  code(e) {
    this.setData({
      code: e.detail.value
    });
  },

  // 发送验证码按钮点击事件处理函数
  sendCode() {
    const { phone } = this.data;

    if (!phone) {
      wx.showToast({
        title: '请输入手机号',
        icon: 'none'
      });
      return;
    }

    // 模拟发送验证码（实际应用中应调用后端接口）
    wx.request({
      url: 'http://127.0.0.1:5000/api/auth/send_code', // 替换为你的实际后端URL
      method: 'POST',
      header: {
        'content-type': 'application/json'
      },
      data: JSON.stringify({
        phone
      }),
      success: (res) => {
        if (res.statusCode === 200) {
          wx.showToast({
            title: '验证码已发送，请查收',
            icon: 'success'
          });

          // 启动倒计时
          let countdown = 60;
          this.setData({ canSendCode: false, countdown });

          const timer = setInterval(() => {
            countdown--;
            this.setData({ countdown });
            if (countdown <= 0) {
              clearInterval(timer);
              this.setData({ canSendCode: true, countdown: 60 });
            }
          }, 1000);
        } else {
          wx.showToast({
            title: res.data.message || '发送验证码失败，请重试',
            icon: 'none'
          });
        }
      },
      fail: () => {
        wx.showToast({
          title: '网络错误，请稍后再试',
          icon: 'none'
        });
      }
    });
  },

  // 注册按钮点击事件处理函数
  goRegister() {
    const { username, phone, password, code } = this.data;

    if (!username || !phone || !password || !code) {
      wx.showToast({
        title: '请填写所有必填项',
        icon: 'none'
      });
      return;
    }

    // 调用注册接口
    wx.request({
      url: 'http://127.0.0.1:5000/api/auth/register', // 替换为你的实际后端URL
      method: 'POST',
      header: {
        'content-type': 'application/json'
      },
      data: JSON.stringify({
        username,
        password,
        role: 'elderly',   // 默认角色，可以根据实际情况修改
        name: username, // 使用用户名作为姓名，可以根据实际情况修改
        phone,
        code,
        email: '',      // 可选字段，可以根据实际情况修改
        address: '',    // 可选字段，可以根据实际情况修改
        family_id: null // 可选字段，可以根据实际情况修改
      }),
      success: (res) => {
        if (res.statusCode === 201) {
          wx.showToast({
            title: '注册成功',
            icon: 'success'
          });
          setTimeout(() => {
            wx.navigateTo({
              url: '/pages/login/login' // 注册成功跳转到登录页面
            });
          }, 1500);
        } else {
          wx.showToast({
            title: res.data.message || '注册失败，请重试',
            icon: 'none'
          });
        }
      },
      fail: () => {
        wx.showToast({
          title: '网络错误，请稍后再试',
          icon: 'none'
        });
      }
    });
  }
});