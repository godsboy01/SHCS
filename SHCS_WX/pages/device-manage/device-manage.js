// pages/device-manage/device-manage.js
const { api } = require('../../utils/api');
const app = getApp();

Page({

  /**
   * 页面的初始数据
   */
  data: {
    devices: [],
    loading: false,
    deviceTypes: {
      'camera': '摄像头',
      'weight_scale': '体重计',
      'blood_pressure': '血压计',
      'other': '其他'
    }
  },

  /**
   * 生命周期函数--监听页面加载
   */
  onLoad(options) {
    const token = wx.getStorageSync('token');
    if (!token) {
      wx.redirectTo({
        url: '/pages/login/login'
      });
      return;
    }
    this.loadDevices();
  },

  /**
   * 生命周期函数--监听页面初次渲染完成
   */
  onReady() {

  },

  /**
   * 生命周期函数--监听页面显示
   */
  onShow() {
    const token = wx.getStorageSync('token');
    if (!token) {
      wx.redirectTo({
        url: '/pages/login/login'
      });
      return;
    }
    this.loadDevices();
  },

  /**
   * 生命周期函数--监听页面隐藏
   */
  onHide() {

  },

  /**
   * 生命周期函数--监听页面卸载
   */
  onUnload() {

  },

  /**
   * 页面相关事件处理函数--监听用户下拉动作
   */
  onPullDownRefresh() {
    this.loadDevices();
  },

  /**
   * 页面上拉触底事件的处理函数
   */
  onReachBottom() {

  },

  /**
   * 用户点击右上角分享
   */
  onShareAppMessage() {

  },

  // 加载设备列表
  async loadDevices() {
    if (this.data.loading) return;
    this.setData({ loading: true });
    try {
      const res = await api.device.getDevices();
      if (res && res.devices) {
        this.setData({ 
          devices: res.devices.map(device => ({
            ...device,
            typeText: this.data.deviceTypes[device.device_type] || '未知'
          }))
        });
      } else {
        throw new Error('获取设备列表失败');
      }
    } catch (err) {
      console.error('加载设备失败:', err);
      wx.showToast({
        title: '加载失败',
        icon: 'none'
      });
    } finally {
      this.setData({ loading: false });
      wx.stopPullDownRefresh();
    }
  },

  // 添加设备
  handleAddDevice() {
    wx.navigateTo({
      url: '/pages/device-add/device-add'
    });
  },

  // 查看设备详情
  handleDeviceDetail(e) {
    const { id } = e.currentTarget.dataset;
    wx.navigateTo({
      url: `/pages/device-detail/device-detail?id=${id}`
    });
  },

  // 删除设备
  handleDeleteDevice(e) {
    const { id, name } = e.currentTarget.dataset;
    wx.showModal({
      title: '确认删除',
      content: `确定要删除设备"${name}"吗？`,
      success: async (res) => {
        if (res.confirm) {
          try {
            await api.device.deleteDevice(id);
            wx.showToast({
              title: '删除成功',
              icon: 'success'
            });
            this.loadDevices();
          } catch (err) {
            console.error('删除设备失败:', err);
            wx.showToast({
              title: '删除失败',
              icon: 'none'
            });
          }
        }
      }
    });
  }
})