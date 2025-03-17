const api = require('../../utils/api');

Page({
  data: {
    userInfo: {},
    devices: []
  },

  onLoad() {
    this.loadUserInfo();
    this.loadDevices();
  },

  async loadUserInfo() {
    try {
      const res = await api.user.getUserInfo();
      this.setData({
        userInfo: res.data
      });
    } catch (err) {
      wx.showToast({
        title: '获取用户信息失败',
        icon: 'none'
      });
    }
  },

  async loadDevices() {
    try {
      const res = await api.device.getDevices();
      this.setData({
        devices: res.devices || []
      });
    } catch (err) {
      wx.showToast({
        title: '获取设备信息失败',
        icon: 'none'
      });
    }
  },

  async chooseAvatar() {
    try {
      const res = await wx.chooseImage({
        count: 1,
        sizeType: ['compressed'],
        sourceType: ['album', 'camera']
      });

      const tempFilePath = res.tempFilePaths[0];
      await api.user.uploadAvatar(tempFilePath);
      
      this.loadUserInfo(); // 重新加载用户信息
      
      wx.showToast({
        title: '头像更新成功',
        icon: 'success'
      });
    } catch (err) {
      wx.showToast({
        title: '上传头像失败',
        icon: 'none'
      });
    }
  },

  editName() {
    wx.navigateTo({
      url: '/pages/edit-name/edit-name'
    });
  },

  editPhone() {
    wx.navigateTo({
      url: '/pages/edit-phone/edit-phone'
    });
  },

  editFamily() {
    wx.navigateTo({
      url: '/pages/edit-family/edit-family'
    });
  },

  onShow() {
    // 页面显示时重新加载用户信息，以更新可能的修改
    this.loadUserInfo();
  }
}); 