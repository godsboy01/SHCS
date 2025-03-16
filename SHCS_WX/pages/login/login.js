const api = require('../../utils/api');
const app = getApp();

Page({
  data: {
    username: '',
    password: '',
    loading: false
  },

  // 输入框事件处理
  onUsernameInput(e) {
    this.setData({
      username: e.detail.value
    });
  },

  onPasswordInput(e) {
    this.setData({
      password: e.detail.value
    });
  },

  // 登录处理
  handleLogin(e) {
    const { username, password } = e.detail.value;
    
    if (!username || !password) {
      wx.showToast({
        title: '请填写完整信息',
        icon: 'none'
      });
      return;
    }

    wx.showLoading({
      title: '登录中...'
    });

    api.auth.login({
      username,
      password
    }).then(res => {
      wx.hideLoading();
      // 使用全局方法保存用户信息
      app.login(res.user, res.token);
      
      wx.showToast({
        title: '登录成功',
        icon: 'success'
      });

      // 跳转到首页
      wx.switchTab({
        url: '/pages/home/home'
      });
    }).catch(err => {
      wx.hideLoading();
      wx.showToast({
        title: err.data?.message || '登录失败',
        icon: 'none'
      });
    });
  },

  // 跳转到注册页面
  goToRegister() {
    wx.navigateTo({
      url: '/pages/register/register'
    });
  }
});