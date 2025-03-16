// utils/api.js

const BASE_URL = 'http://localhost:5000/api';

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
    })
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
        'Authorization': `Bearer ${wx.getStorageSync('token')}`
      },
      data: params
    }),
    // 添加设备
    addDevice: (data) => request('/device/devices', {
      method: 'POST',
      header: {
        'Authorization': `Bearer ${wx.getStorageSync('token')}`
      },
      data
    }),
    // 更新设备
    updateDevice: (deviceId, data) => request(`/device/devices/${deviceId}`, {
      method: 'PUT',
      header: {
        'Authorization': `Bearer ${wx.getStorageSync('token')}`
      },
      data
    }),
    // 删除设备
    deleteDevice: (deviceId) => request(`/device/devices/${deviceId}`, {
      method: 'DELETE',
      header: {
        'Authorization': `Bearer ${wx.getStorageSync('token')}`
      }
    })
  }
};

module.exports = api;  // 使用module.exports导出