const api = require('../../utils/api');

Page({
  data: {
    device: null,
    deviceTypes: {
      'camera': '摄像头',
      'weight_scale': '体重计',
      'blood_pressure': '血压计',
      'other': '其他'
    }
  },

  onLoad(options) {
    this.deviceId = options.id;
    this.loadDeviceInfo();
  },

  async loadDeviceInfo() {
    wx.showLoading({
      title: '加载中...'
    });

    try {
      const devices = await api.device.getDevices();
      const device = devices.devices.find(d => d.device_id === parseInt(this.deviceId));
      if (device) {
        this.setData({ device });
      } else {
        wx.showToast({
          title: '设备不存在',
          icon: 'none'
        });
        setTimeout(() => {
          wx.navigateBack();
        }, 1500);
      }
    } catch (err) {
      wx.showToast({
        title: '加载失败',
        icon: 'none'
      });
    } finally {
      wx.hideLoading();
    }
  },

  async handleSubmit(e) {
    const formData = e.detail.value;
    
    if (!formData.device_name || !formData.location || !formData.ip_address) {
      wx.showToast({
        title: '请填写完整信息',
        icon: 'none'
      });
      return;
    }

    wx.showLoading({
      title: '保存中...'
    });

    try {
      await api.device.updateDevice(this.deviceId, formData);
      wx.showToast({
        title: '保存成功',
        icon: 'success'
      });
      
      // 刷新设备信息
      this.loadDeviceInfo();
    } catch (err) {
      wx.showToast({
        title: err.data?.message || '保存失败',
        icon: 'none'
      });
    } finally {
      wx.hideLoading();
    }
  },

  handleDelete() {
    wx.showModal({
      title: '确认删除',
      content: '确定要删除此设备吗？',
      success: async (res) => {
        if (res.confirm) {
          try {
            await api.device.deleteDevice(this.deviceId);
            wx.showToast({
              title: '删除成功',
              icon: 'success'
            });
            setTimeout(() => {
              wx.navigateBack();
            }, 1500);
          } catch (err) {
            wx.showToast({
              title: '删除失败',
              icon: 'none'
            });
          }
        }
      }
    });
  }
}); 