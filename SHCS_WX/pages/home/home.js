// pages/home/home.js
const api = require('../../utils/api');
const weatherService = require('../../utils/weather');
const app = getApp();

Page({
  data: {
    cameras: [],
    weightScales: [],
    bloodPressures: [],
    loading: false,
    weather: {
      temp: '--',
      text: '未知',
      location: '定位中...',
      date: ''
    },
    defaultCity: '南京市'
  },

  onLoad() {
    this.loadDevices();
    this.initWeather();
    this.setCurrentDate();
  },

  onShow() {
    this.loadDevices();
  },

  onPullDownRefresh() {
    this.loadDevices();
  },

  async loadDevices() {
    if (this.data.loading) return;
    this.setData({ loading: true });

    try {
      const res = await api.device.getDevices();
      const devices = res.devices || [];

      this.setData({
        cameras: devices.filter(d => d.device_type === 'camera'),
        weightScales: devices.filter(d => d.device_type === 'weight_scale'),
        bloodPressures: devices.filter(d => d.device_type === 'blood_pressure')
      });
    } catch (err) {
      wx.showToast({
        title: '加载失败',
        icon: 'none'
      });
    } finally {
      this.setData({ loading: false });
      wx.stopPullDownRefresh();
    }
  },

  async initWeather() {
    wx.showLoading({
      title: '获取位置中',
      mask: true
    });

    try {
      const locationInfo = await weatherService.getLocation();
      
      if (locationInfo) {
        const city = locationInfo.city;
        const weatherData = await weatherService.getWeather(city);
        
        if (weatherData) {
          this.setData({
            weather: {
              ...this.data.weather,
              temp: weatherData.temp,
              text: weatherData.text,
              location: `${city}`
            }
          });
        }
      } else {
        const weatherData = await weatherService.getWeather(this.data.defaultCity);
        this.setData({
          weather: {
            ...this.data.weather,
            temp: weatherData.temp,
            text: weatherData.text,
            location: this.data.defaultCity
          }
        });
      }
    } catch (err) {
      console.error('初始化天气失败:', err);
      wx.showToast({
        title: '获取天气信息失败',
        icon: 'none'
      });
    } finally {
      wx.hideLoading();
    }
  },

  setCurrentDate() {
    const date = new Date();
    const month = date.getMonth() + 1;
    const day = date.getDate();
    const weekDay = ['周日', '周一', '周二', '周三', '周四', '周五', '周六'][date.getDay()];
    
    this.setData({
      'weather.date': `${month}月${day}日 ${weekDay}`
    });
  },

  navigateToDevice(e) {
    const { id, type } = e.currentTarget.dataset;
    
    // 根据设备类型跳转到不同页面
    switch(type) {
      case 'camera':
        wx.navigateTo({
          url: `/pages/realtime-monitor/realtime-monitor?id=${id}`
        });
        break;
      case 'weight_scale':
        wx.navigateTo({
          url: `/pages/weight-record/weight-record?id=${id}`
        });
        break;
      case 'blood_pressure':
        wx.navigateTo({
          url: `/pages/bloodpressure-record/bloodpressure-record?id=${id}`
        });
        break;
    }
  },

  navigateToDeviceManage() {
    wx.navigateTo({
      url: '/pages/device-manage/device-manage'
    });
  },

  async refreshWeather() {
    await this.initWeather();
  },

  async onPullDownRefresh() {
    await Promise.all([
      this.loadDevices(),
      this.refreshWeather()
    ]);
    wx.stopPullDownRefresh();
  }
});