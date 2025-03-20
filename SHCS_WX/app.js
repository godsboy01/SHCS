// app.js
import storage from './utils/storage';
import permission from './utils/permission';

App({
  globalData: {
    userInfo: null,
    isLoggedIn: false,
    role: null
  },

  onLaunch() {
    // 检查登录状态
    const isLoggedIn = storage.isLoggedIn();
    if (isLoggedIn) {
      this.globalData.isLoggedIn = true;
      this.globalData.userInfo = storage.getUserInfo();
      this.globalData.role = storage.getRole();
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
    storage.setRole(userInfo.role);
    this.globalData.userInfo = userInfo;
    this.globalData.isLoggedIn = true;
    this.globalData.role = userInfo.role;
  },

  // 登出方法
  logout() {
    storage.clear();
    this.globalData.userInfo = null;
    this.globalData.isLoggedIn = false;
    this.globalData.role = null;
    wx.redirectTo({
      url: '/pages/login/login'
    });
  },

  // 检查页面权限
  checkPagePermission(pagePath) {
    const role = this.globalData.role;
    return permission.checkPagePermission(pagePath, role);
  },

  // 检查功能权限
  checkFeaturePermission(feature) {
    const role = this.globalData.role;
    return permission.checkFeaturePermission(feature, role);
  }
});