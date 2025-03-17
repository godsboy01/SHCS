const { api } = require('../../utils/api')

Page({
  data: {
    videoSrc: '',      // 视频帧地址
    isPlaying: false,  // 是否播放中（初始状态为未播放）
    isLoading: true,   // 加载状态
    errorMessage: '',  // 错误信息
    currentTime: '',   // 当前时间
    deviceInfo: {      // 设备信息
      name: '',
      location: ''
    }
  },

  onLoad(options) {
    // 获取传入的设备ID
    const deviceId = options.id;
    
    // 获取设备信息
    this.loadDeviceInfo(deviceId);
    
    // 初始化时间并启动定时器
    this.updateTime();
    this.timeUpdateTimer = setInterval(() => {
      this.updateTime();
    }, 1000);
  },

  // 加载设备信息
  async loadDeviceInfo(deviceId) {
    try {
      const res = await api.device.getDeviceDetail(deviceId);
      if (res) {
        this.setData({
          'deviceInfo.name': res.device_name || '未命名设备',
          'deviceInfo.location': res.location || '未设置位置'
        });
      }
    } catch (err) {
      console.error('获取设备信息失败:', err);
      wx.showToast({
        title: '获取设备信息失败',
        icon: 'none'
      });
    }
  },

  // 更新时间
  updateTime() {
    const now = new Date();
    const timeString = now.toLocaleTimeString('zh-CN', { hour12: false }); // 24小时制
    this.setData({ currentTime: timeString });
  },

  // 返回上一页
  handleBack() {
    wx.navigateBack();
  },

  // 切换播放/暂停
  togglePlay() {
    const { isPlaying } = this.data;
    this.setData({ isPlaying: !isPlaying });

    if (isPlaying) {
      this.stopVideoStream();
    } else {
      this.startVideoStream();
    }
  },

  // 开始视频流
  startVideoStream() {
    this.setData({
      isPlaying: true,
      isLoading: false,
      videoSrc: `http://127.0.0.1:5000/api/camera/video_feed?t=${Date.now()}`
    });
  },

  // 停止视频流
  stopVideoStream() {
    this.setData({
      isPlaying: false,
      videoSrc: ''
    });
  },

  onUnload() {
    // 页面卸载时清除定时器和停止视频流
    if (this.timeUpdateTimer) {
      clearInterval(this.timeUpdateTimer);
    }
    this.stopVideoStream();
  }
});