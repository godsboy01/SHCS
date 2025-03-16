// 用户信息相关的缓存key
const USER_INFO = 'userInfo';
const TOKEN = 'token';
const ROLE = 'role';

// 设备相关的缓存key
const DEVICE_LIST = 'deviceList';
const CURRENT_DEVICE = 'currentDevice';

const storage = {
  // 用户信息相关
  setUserInfo: (userInfo) => {
    wx.setStorageSync(USER_INFO, userInfo);
  },
  getUserInfo: () => {
    return wx.getStorageSync(USER_INFO);
  },
  setToken: (token) => {
    wx.setStorageSync(TOKEN, token);
  },
  getToken: () => {
    return wx.getStorageSync(TOKEN);
  },
  setRole: (role) => {
    wx.setStorageSync(ROLE, role);
  },
  getRole: () => {
    return wx.getStorageSync(ROLE);
  },

  // 设备相关
  setDeviceList: (devices) => {
    wx.setStorageSync(DEVICE_LIST, devices);
  },
  getDeviceList: () => {
    return wx.getStorageSync(DEVICE_LIST) || [];
  },
  setCurrentDevice: (device) => {
    wx.setStorageSync(CURRENT_DEVICE, device);
  },
  getCurrentDevice: () => {
    return wx.getStorageSync(CURRENT_DEVICE);
  },

  // 通用方法
  clear: () => {
    wx.clearStorageSync();
  },
  
  // 检查是否已登录
  isLoggedIn: () => {
    return !!wx.getStorageSync(TOKEN);
  }
};

export default storage; 