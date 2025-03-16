Page({
  data: {
    username: '',
    password: '',
  },
  // 输入用户名
  onUsernameInput(event) {
    this.setData({ username: event.detail.value });
  },

  // 输入密码
  onPasswordInput(event) {
    this.setData({ password: event.detail.value });
  },

  // 登录
  goadmin() {
    const { username, password } = this.data;
    wx.request({
      url: 'http://127.0.0.1:5000/api/auth/login',
      method: 'POST',
      header: {
        'content-type': 'application/json',
      },
      data: JSON.stringify({
        username,
        password,
      }),
      success(res) {
        if (res.statusCode === 200) {
          const { user } = res.data; // 获取用户信息
          const { role, userid, username } = user; // 解构用户信息
          // 登录成功后
          const app = getApp();
          app.globalData.user = user; // 更新全局变量
          wx.setStorageSync('user', user); // 同步到本地缓存
          // 将用户信息存储到本地缓存
          wx.setStorageSync('user', {
            role: role,
            userid: userid,
            username: username,
          });

          wx.switchTab({ // 跳转到 TabBar 页面
            url: '/pages/home/home',
          });
        } else {
          wx.showToast({
            title: res.data.message || '登录失败，请重试',
            icon: 'none',
          });
        }
      },
      fail() {
        wx.showToast({
          title: '网络错误，请稍后再试',
          icon: 'none',
        });
      },
    });
  },

  // 去注册页面
  goregister() {
    wx.navigateTo({
      url: '/pages/register/register',
    });
  },
});