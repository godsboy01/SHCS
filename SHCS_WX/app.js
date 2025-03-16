// app.js
import storage from './utils/storage';

App({
  globalData: {
    userInfo: null,
    isLoggedIn: false
  },

  onLaunch() {
    // 检查登录状态
    const isLoggedIn = storage.isLoggedIn();
    if (isLoggedIn) {
      this.globalData.isLoggedIn = true;
      this.globalData.userInfo = storage.getUserInfo();
    }

    // 获取系统信息
    wx.getSystemInfo({
      success: (res) => {
        this.globalData.systemInfo = res;
      }
    });
  },

  // 登录方法
  login(userInfo, token) {
    storage.setUserInfo(userInfo);
    storage.setToken(token);
    this.globalData.userInfo = userInfo;
    this.globalData.isLoggedIn = true;
  },

  // 登出方法
  logout() {
    storage.clear();
    this.globalData.userInfo = null;
    this.globalData.isLoggedIn = false;
    wx.redirectTo({
      url: '/pages/login/login'
    });
  }
});