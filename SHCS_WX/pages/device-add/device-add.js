const api = require('../../utils/api');
const app = getApp();

Page({
  data: {
    typeList: [
      { value: 'camera', text: '摄像头' },
      { value: 'weight_scale', text: '体重计' },
      { value: 'blood_pressure', text: '血压计' },
      { value: 'other', text: '其他' }
    ],
    typeIndex: null
  },

  handleTypeChange(e) {
    this.setData({
      typeIndex: parseInt(e.detail.value)
    });
  },

  async handleSubmit(e) {
    const formData = e.detail.value;
    
    if (!formData.device_name || this.data.typeIndex === null || !formData.location || !formData.ip_address) {
      wx.showToast({
        title: '请填写完整信息',
        icon: 'none'
      });
      return;
    }

    const deviceData = {
      ...formData,
      device_type: this.data.typeList[this.data.typeIndex].value,
      elderly_id: app.globalData.userInfo.user_id
    };

    wx.showLoading({
      title: '添加中...'
    });

    try {
      await api.device.addDevice(deviceData);
      wx.showToast({
        title: '添加成功',
        icon: 'success'
      });
      
      // 返回设备列表页面并刷新
      setTimeout(() => {
        wx.navigateBack();
      }, 1500);
    } catch (err) {
      wx.showToast({
        title: err.data?.message || '添加失败',
        icon: 'none'
      });
    } finally {
      wx.hideLoading();
    }
  }
}); 