// pages/home/home.js
Page({
  data: {
    familyName: '张', // 家庭名称
    temperature: '--',       // 当前温度
    location: '加载中...',   // 当前位置
    devices: [               // 设备列表
      { id: 1, name: '客厅摄像头', icon: '../../assets/icon/camera01.png', type: 'camera' },
      { id: 2, name: '卧室摄像头', icon: '../../assets/icon/camera02.png', type: 'camera' },
      { id: 3, name: '体重计', icon: '../../assets/icon/weight.png', type: 'weight' },
      { id: 4, name: '血压计', icon: '../../assets/icon/blood.png', type: 'bloodpressure' },
    ],
  },

  onLoad() {
    const user = wx.getStorageSync('user'); // 读取本地缓存
    if (!user) {
      wx.redirectTo({ url: '/pages/login/login' }); // 如果未登录，跳转到登录页面
    }
    // this.loadFamilyName(); // 加载家庭名称
    this.loadWeather();    // 加载天气数据
  },
  // 调用天气 API 获取温度
  loadWeather() {
    const apiKey = '3e7aea94f84345cf97a145138252702'; // 你的天气 API Key
    const location = '南京、'; // 指定城市名称
  
    wx.request({
      url: `https://api.weatherapi.com/v1/current.json?key=${apiKey}&q=${location}`,
      method: 'GET',
      success: (res) => {
        console.log('API 返回数据：', res); // 打印完整响应
        if (res.statusCode === 200 && res.data && res.data.current) {
          // 更新页面数据
          this.setData({
            temperature: res.data.current.temp_c, // 当前温度（摄氏度）
            location: res.data.location.name,     // 当前城市名称
            weatherDescription: res.data.current.condition.text, // 设置天气描述
            weatherIcon: res.data.current.condition.icon.startsWith('//') ? 'https:' + res.data.current.condition.icon : res.data.current.condition.icon, // 设置天气图标URL
          });
        } else {
          console.error('获取天气数据失败：', res);
          wx.showToast({
            title: '获取天气数据失败',
            icon: 'none',
          });
        }
      },
      fail: (err) => {
        console.error('请求天气 API 失败：', err);
        wx.showToast({
          title: '网络请求失败',
          icon: 'none',
        });
      },
    });
  },


  onDeviceTap(event) {
    const device = event.currentTarget.dataset.item; // 获取点击的设备对象
    const deviceId = device.id;
    const deviceType = device.type;

    switch (deviceType) {
      case 'camera':
        // 跳转到实时监控页面
        wx.navigateTo({
          url: `/pages/realtime-monitor/realtime-monitor?id=${deviceId}`,
        });
        break;
      case 'weight':
        // 跳转到体重记录页面
        wx.navigateTo({
          url: `/pages/weight-record/weight-record`,
        });
        break;
      case 'bloodpressure':
        // 跳转到血压记录页面
        wx.navigateTo({
          url: `/pages/bloodpressure-record/bloodpressure-record`,
        });
        break;
      default:
        wx.showToast({
          title: '未知设备类型',
          icon: 'none',
        });
    }
  },
});