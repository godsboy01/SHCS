const { api } = require('../../utils/api');

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
    const token = wx.getStorageSync('token');
    if (!token) {
      wx.redirectTo({
        url: '/pages/login/login'
      });
      return;
    }
    this.deviceId = options.id;
    this.loadDeviceInfo();
  },

  async loadDeviceInfo() {
    wx.showLoading({
      title: '加载中...'
    });

    try {
      const device = await api.device.getDeviceDetail(this.deviceId);
      if (device) {
        // 确保device_type存在，如果不存在则设为'other'
        device.device_type = device.device_type || 'other';
        device.typeText = this.data.deviceTypes[device.device_type];
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
      console.error('加载设备详情失败:', err);
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
      // 构造更新数据
      const updateData = {
        ...formData,
        device_type: this.data.device.device_type,
        elderly_id: this.data.device.elderly_id
      };

      await api.device.updateDevice(this.deviceId, updateData);
      
      wx.showToast({
        title: '保存成功',
        icon: 'success'
      });
      
      // 刷新设备信息
      await this.loadDeviceInfo();
    } catch (err) {
      console.error('更新设备失败:', err);
      wx.showToast({
        title: '保存失败',
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
}); 