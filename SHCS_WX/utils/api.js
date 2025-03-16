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
  })
};

export default api;