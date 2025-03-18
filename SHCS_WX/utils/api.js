// utils/api.js

const BASE_URL = 'http://127.0.0.1:5000/api';
const STATIC_URL = 'http://127.0.0.1:5000';

const request = (url, options = {}) => {
  return new Promise((resolve, reject) => {
    wx.request({
      url: `${BASE_URL}${url}`,
      ...options,
      success: (res) => {
        if (res.statusCode >= 200 && res.statusCode < 300) {
          resolve(res.data);
        } else {
          reject(res);
        }
      },
      fail: reject
    });
  });
};

const api = {
  // 用户认证相关
  auth: {
    login: (data) => request('/auth/login', {
      method: 'POST',
      data
    }),
    register: (data) => request('/auth/register', {
      method: 'POST',
      data
    }),
    getProfile: () => request('/auth/profile', {
      header: {
        'Authorization': `Bearer ${wx.getStorageSync('token')}`
      }
    }),
    updateProfile: (userId, data) => request(`/auth/update_user/${userId}`, {
      method: 'PUT',
      header: {
        'Authorization': `Bearer ${wx.getStorageSync('token')}`,
        'Content-Type': 'application/json'
      },
      data
    })
  },
  // 家庭信息相关
  family: {
    getFamilyInfo: () => request('/family/info', {
      method: 'GET',
      header: {
        'Authorization': `Bearer ${wx.getStorageSync('token')}`
      }
    }),
    updateAddress: (data) => request('/family/address', {
      method: 'PUT',
      header: {
        'Authorization': `Bearer ${wx.getStorageSync('token')}`
      },
      data
    }),
    addMember: (data) => request('/family/members', {
      method: 'POST',
      header: {
        'Authorization': `Bearer ${wx.getStorageSync('token')}`
      },
      data
    }),
    deleteMember: (data) => request('/family/members', {
      method: 'DELETE',
      header: {
        'Authorization': `Bearer ${wx.getStorageSync('token')}`
      },
      data
    }),
    transferMember: (data) => request('/api/family/transfer_member', 'POST', data)
  },
  createFamily: (familyName) => request('/family/create_family', {
    method: 'POST',
    data: { family_name: familyName },
    header: { 'content-type': 'application/json' }
  }),
  addMember: (data) => request('/family/add_member', {
    method: 'POST',
    data,
    header: { 'content-type': 'application/json' }
  }),
  getFamilyMembers: (familyId) => request(`/family/get_members/${familyId}`, {
    method: 'GET',
    header: { 'content-type': 'application/json' }
  }),
  updateMember: (userId, data) => request(`/family/update_member/${userId}`, {
    method: 'PUT',
    data,
    header: { 'content-type': 'application/json' }
  }),
  deleteMember: (userId) => request(`/family/delete_member/${userId}`, {
    method: 'DELETE',
    header: { 'content-type': 'application/json' }
  }),
  // 设备管理相关API
  device: {
    // 获取设备列表
    getDevices: (params) => request('/device/devices', {
      method: 'GET',
      header: {
        'Authorization': `Bearer ${wx.getStorageSync('token')}`,
        'Content-Type': 'application/json'
      },
      data: params
    }).then(res => {
      if (res.code === 200) {
        return res.data;
      }
      throw new Error(res.message || '获取设备列表失败');
    }),
    
    // 获取设备详情
    getDeviceDetail: (deviceId) => request(`/device/devices/${deviceId}`, {
      method: 'GET',
      header: {
        'Authorization': `Bearer ${wx.getStorageSync('token')}`,
        'Content-Type': 'application/json'
      }
    }).then(res => {
      if (res.code === 200) {
        return res.data;
      }
      throw new Error(res.message || '获取设备详情失败');
    }),
    
    // 添加设备
    addDevice: (data) => request('/device/devices', {
      method: 'POST',
      header: {
        'Authorization': `Bearer ${wx.getStorageSync('token')}`,
        'Content-Type': 'application/json'
      },
      data
    }).then(res => {
      if (res.code === 201) {
        return res.data;
      }
      throw new Error(res.message || '添加设备失败');
    }),
    
    // 更新设备
    updateDevice: (deviceId, data) => request(`/device/devices/${deviceId}`, {
      method: 'PUT',
      header: {
        'Authorization': `Bearer ${wx.getStorageSync('token')}`,
        'Content-Type': 'application/json'
      },
      data
    }).then(res => {
      if (res.code === 200) {
        return res.data;
      }
      throw new Error(res.message || '更新设备失败');
    }),
    
    // 删除设备
    deleteDevice: (deviceId) => request(`/device/devices/${deviceId}`, {
      method: 'DELETE',
      header: {
        'Authorization': `Bearer ${wx.getStorageSync('token')}`,
        'Content-Type': 'application/json'
      }
    }).then(res => {
      if (res.code === 200) {
        return res.data;
      }
      throw new Error(res.message || '删除设备失败');
    }),
    
    // 更新设备状态
    updateDeviceStatus: (deviceId, status) => request(`/device/devices/${deviceId}/status`, {
      method: 'PUT',
      header: {
        'Authorization': `Bearer ${wx.getStorageSync('token')}`,
        'Content-Type': 'application/json'
      },
      data: { status }
    }).then(res => {
      if (res.code === 200) {
        return res.data;
      }
      throw new Error(res.message || '更新设备状态失败');
    })
  },
  // 摄像头相关API
  camera: {
    // 获取跌倒记录
    getFallRecords: (userId) => request('/camera/fall_records', {
      method: 'GET',
      header: {
        'Authorization': `Bearer ${wx.getStorageSync('token')}`
      },
      data: { user_id: userId }
    }),
    // 获取跌倒截图
    getFallSnapshot: (fallDir, filename) => request(`/camera/fall_snapshots/${fallDir}/${filename}`, {
      method: 'GET',
      header: {
        'Authorization': `Bearer ${wx.getStorageSync('token')}`
      }
    }),
    // 获取警报级别
    getAlertLevel: () => request('/camera/alert_level', {
      method: 'GET',
      header: {
        'Authorization': `Bearer ${wx.getStorageSync('token')}`
      }
    })
  }
};

// 导出BASE_URL和STATIC_URL供其他模块使用
module.exports = {
  api,
  BASE_URL,
  STATIC_URL
};