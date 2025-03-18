const QQ_MAP_KEY = 'YOUR_KEY'; // 替换为您的腾讯地图密钥
const DEFAULT_CITY = '南京市';

const weatherService = {
  // 获取位置信息
  async getLocation() {
    try {
      // 获取位置权限
      const setting = await wx.getSetting();
      if (!setting.authSetting['scope.userLocation']) {
        try {
          await wx.authorize({
            scope: 'scope.userLocation'
          });
        } catch (err) {
          console.log('用户拒绝了位置权限，使用默认城市');
          return { city: DEFAULT_CITY };
        }
      }

      // 获取位置
      try {
        const location = await wx.getLocation({
          type: 'gcj02'
        });
        
        if (!location) {
          console.log('获取位置信息失败，使用默认城市');
          return { city: DEFAULT_CITY };
        }

        // 获取城市信息
        const cityInfo = await this.getCityFromLocation(location);
        return cityInfo || { city: DEFAULT_CITY };
      } catch (err) {
        console.log('获取位置失败，使用默认城市:', err);
        return { city: DEFAULT_CITY };
      }
    } catch (error) {
      console.log('位置服务异常，使用默认城市:', error);
      return { city: DEFAULT_CITY };
    }
  },

  // 根据经纬度获取城市信息
  async getCityFromLocation(location) {
    if (!location || !location.latitude || !location.longitude) {
      console.log('位置信息不完整，使用默认城市');
      return { city: DEFAULT_CITY };
    }

    try {
      const res = await wx.request({
        url: `https://apis.map.qq.com/ws/geocoder/v1/`,
        data: {
          location: `${location.latitude},${location.longitude}`,
          key: QQ_MAP_KEY
        }
      });

      if (res.data && res.data.status === 0 && res.data.result) {
        return {
          city: res.data.result.address_component.city,
          district: res.data.result.address_component.district
        };
      }
      console.log('获取城市信息失败，使用默认城市:', res);
      return { city: DEFAULT_CITY };
    } catch (error) {
      console.log('解析城市信息失败，使用默认城市:', error);
      return { city: DEFAULT_CITY };
    }
  },

  // 获取天气信息
  async getWeather(city) {
    if (!city) {
      console.log('城市信息为空，使用默认城市');
      city = DEFAULT_CITY;
    }

    try {
      // 这里替换为您的天气API
      // 示例使用模拟数据
      return {
        temp: '25',
        text: '晴',
        location: city
      };
    } catch (error) {
      console.log('获取天气信息失败:', error);
      return {
        temp: '--',
        text: '获取失败',
        location: city
      };
    }
  }
};

module.exports = weatherService; 