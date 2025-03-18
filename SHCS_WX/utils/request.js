const BASE_URL = 'http://localhost:5000/api';
// 正确导入（假设路径正确）
// const { api } = require('../../utils/api'); // 解构赋值
// 请求拦截器
const requestInterceptor = (options) => {
  const token = wx.getStorageSync('token');
  if (token) {
    options.header = {
      ...options.header,
      'Authorization': `Bearer ${token}`
    };
  }
  return options;
};

// 响应拦截器
const responseInterceptor = (response) => {
  if (response.statusCode === 401) {
    // token过期，清除缓存并跳转到登录页
    wx.clearStorageSync();
    wx.redirectTo({
      url: '/pages/login/login'
    });
    return Promise.reject('未授权或token已过期');
  }
  return response.data;
};

// 统一请求方法
const request = (options) => {
  options.url = `${BASE_URL}${options.url}`;
  options = requestInterceptor(options);
  
  return new Promise((resolve, reject) => {
    wx.request({
      ...options,
      success: (res) => {
        try {
          resolve(responseInterceptor(res));
        } catch (error) {
          reject(error);
        }
      },
      fail: reject
    });
  });
};

// 封装常用请求方法
const http = {
  get: (url, data = {}) => {
    return request({
      url,
      method: 'GET',
      data
    });
  },
  post: (url, data = {}) => {
    return request({
      url,
      method: 'POST',
      data
    });
  },
  put: (url, data = {}) => {
    return request({
      url,
      method: 'PUT',
      data
    });
  },
  delete: (url, data = {}) => {
    return request({
      url,
      method: 'DELETE',
      data
    });
  }
};

export default http; 