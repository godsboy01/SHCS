const app = getApp()
const api = require('../../utils/api')

Page({
  data: {
    userInfo: null,
    devices: []
  },

  onLoad() {
    this.fetchUserInfo()
    this.loadDevices()
  },

  onShow() {
    // 每次显示页面时刷新用户信息
    this.fetchUserInfo()
  },

  // 获取用户信息
  async fetchUserInfo() {
    const token = wx.getStorageSync('token')
    if (!token) {
      wx.navigateTo({
        url: '/pages/login/login'
      })
      return
    }

    try {
      const [userRes, familyRes] = await Promise.all([
        api.auth.getProfile(),
        api.family.getFamilyInfo()
      ])

      if (userRes && familyRes) {
        this.setData({
          userInfo: {
            ...userRes,
            family_address: familyRes.address || '未设置家庭地址'
          }
        })
      } else {
        wx.showToast({
          title: '获取用户信息失败',
          icon: 'none'
        })
      }
    } catch (err) {
      console.error('获取用户信息失败:', err)
      wx.showToast({
        title: '网络错误',
        icon: 'none'
      })
    }
  },

  async loadDevices() {
    try {
      const res = await api.device.getDevices()
      this.setData({
        devices: res.devices || []
      })
    } catch (err) {
      console.error('获取设备信息失败:', err)
      wx.showToast({
        title: '获取设备信息失败',
        icon: 'none'
      })
    }
  },

  // 选择头像
  chooseAvatar() {
    wx.chooseImage({
      count: 1,
      sizeType: ['compressed'],
      sourceType: ['album', 'camera'],
      success: (res) => {
        const tempFilePath = res.tempFilePaths[0]
        this.uploadAvatar(tempFilePath)
      }
    })
  },

  // 上传头像
  async uploadAvatar(filePath) {
    const token = wx.getStorageSync('token')
    if (!token) {
      wx.showToast({
        title: '请先登录',
        icon: 'none'
      })
      return
    }

    wx.showLoading({
      title: '上传中...',
      mask: true
    })

    try {
      const uploadRes = await new Promise((resolve, reject) => {
        wx.uploadFile({
          url: 'http://localhost:5000/api/auth/upload_avatar',
          filePath: filePath,
          name: 'avatar',
          formData: {
            user_id: this.data.userInfo.user_id
          },
          header: {
            'Authorization': `Bearer ${token}`
          },
          success: (res) => {
            if (res.statusCode === 200) {
              resolve(res)
            } else {
              reject(new Error(res.data))
            }
          },
          fail: reject
        })
      })

      let data
      try {
        data = JSON.parse(uploadRes.data)
      } catch (e) {
        throw new Error('服务器响应格式错误')
      }

      if (data.code === 200) {
        // 更新本地头像，添加时间戳防止缓存
        const timestamp = new Date().getTime()
        this.setData({
          'userInfo.avatar': `${data.data.avatar_url}?t=${timestamp}`
        })
        wx.showToast({
          title: '头像更新成功',
          icon: 'success'
        })
      } else {
        throw new Error(data.message || '上传失败')
      }
    } catch (err) {
      console.error('上传头像失败:', err)
      wx.showToast({
        title: err.message || '上传失败',
        icon: 'none'
      })
    } finally {
      wx.hideLoading()
    }
  },

  // 导航到编辑页面
  navigateToEdit() {
    wx.navigateTo({
      url: '/pages/edit-profile/edit-profile'
    })
  },

  // 导航到家庭信息管理页面
  navigateToFamily() {
    wx.navigateTo({
      url: '/pages/family-manage/family-manage'
    })
  }
}) 