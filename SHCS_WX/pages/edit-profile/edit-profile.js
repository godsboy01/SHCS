const api = require('../../utils/api').api
const { STATIC_URL } = require('../../utils/api')

Page({
  data: {
    isLoggedIn: false, // 是否登录
    userInfo: {
      name: '',
      phone: '',
      email: '',
      avatar: ''
    },
    isLoading: true,   // 加载状态
    errorMessage: '',  // 错误信息
    roles: ['elderly', 'family', 'admin'], // 角色选项
  },

  onLoad() {
    const token = wx.getStorageSync('token');
    if (!token) {
      wx.redirectTo({
        url: '/pages/login/login'
      });
      return;
    }
    this.fetchUserInfo();
  },

  onShow() {
    const token = wx.getStorageSync('token');
    if (!token) {
      wx.redirectTo({
        url: '/pages/login/login'
      });
      return;
    }
    this.fetchUserInfo();
  },

  // 获取用户信息
  async fetchUserInfo() {
    wx.showLoading({
      title: '加载中...'
    });

    try {
      const res = await api.auth.getProfile();
      if (res) {
        // 处理头像URL
        const avatar = res.avatar ? `${STATIC_URL}${res.avatar}` : '';
        this.setData({
          userInfo: { ...res, avatar },
          isLoading: false
        });
      } else {
        throw new Error('获取用户信息失败');
      }
    } catch (err) {
      console.error('获取用户信息失败:', err);
      wx.showToast({
        title: '获取信息失败',
        icon: 'none'
      });
      this.setData({
        isLoading: false
      });
    } finally {
      wx.hideLoading();
    }
  },

  // 处理输入
  handleInput(e) {
    const { field } = e.currentTarget.dataset
    const { value } = e.detail
    
    this.setData({
      [`userInfo.${field}`]: value
    })
  },

  // 验证手机号
  validatePhone(phone) {
    const phoneReg = /^1[3-9]\d{9}$/
    return phoneReg.test(phone)
  },

  // 验证邮箱
  validateEmail(email) {
    const emailReg = /^[a-zA-Z0-9_.-]+@[a-zA-Z0-9-]+(\.[a-zA-Z0-9-]+)*\.[a-zA-Z0-9]{2,6}$/
    return emailReg.test(email)
  },

  // 提交表单
  async handleSubmit() {
    const { name, phone, email, user_id } = this.data.userInfo
    
    // 验证表单
    if (!name.trim()) {
      wx.showToast({
        title: '请输入姓名',
        icon: 'none'
      })
      return
    }

    if (phone && !this.validatePhone(phone)) {
      wx.showToast({
        title: '手机号格式不正确',
        icon: 'none'
      })
      return
    }

    if (email && !this.validateEmail(email)) {
      wx.showToast({
        title: '邮箱格式不正确',
        icon: 'none'
      })
      return
    }

    if (!user_id) {
      wx.showToast({
        title: '用户信息无效',
        icon: 'none'
      })
      return
    }

    wx.showLoading({
      title: '保存中...',
      mask: true
    })

    try {
      await api.auth.updateProfile(user_id, {
        name: name.trim(),
        phone: phone.trim(),
        email: email.trim()
      })
      
      wx.showToast({
        title: '保存成功',
        icon: 'success'
      })

      // 延迟返回上一页
      setTimeout(() => {
        wx.navigateBack()
      }, 1500)

    } catch (err) {
      console.error('更新用户信息失败:', err)
      wx.showToast({
        title: '保存失败',
        icon: 'none'
      })
    } finally {
      wx.hideLoading()
    }
  },

  // 选择新头像
  changeAvatar() {
    wx.chooseImage({
      count: 1, // 只能选择一张图片
      success: (res) => {
        const tempFilePath = res.tempFilePaths[0]; // 获取临时文件路径
        this.uploadAvatar(tempFilePath); // 上传头像
      },
    });
  },
  uploadAvatar(tempFilePath) {
    const { userInfo } = this.data;
    const userid = userInfo?.user_id || wx.getStorageSync('user')?.userid;
  
    if (!userid) {
      wx.showToast({ title: '用户信息无效', icon: 'none' });
      return;
    }
  
    wx.showLoading({ title: '上传中...' });
  
    wx.uploadFile({
      url: 'http://127.0.0.1:5000/api/auth/upload_avatar',
      filePath: tempFilePath,
      name: 'avatar',
      formData: {
        user_id: userid
      },
      header: {
        'Authorization': `Bearer ${wx.getStorageSync('token')}`
      },
      success: (res) => {
        wx.hideLoading();
        let data;
        try {
          data = JSON.parse(res.data);
        } catch (e) {
          console.error('解析服务器响应失败:', res.data);
          wx.showToast({ title: '解析响应失败', icon: 'none' });
          return;
        }
  
        if (data.code === 200 && data.data?.avatar_url) {
          this.setData({
            'userInfo.avatar': data.data.avatar_url
          });
          wx.showToast({ title: '头像上传成功', icon: 'success' });
        } else {
          wx.showToast({ title: data.message || '头像上传失败', icon: 'none' });
        }
      },
      fail: (err) => {
        wx.hideLoading();
        console.error('上传失败：', err);
        wx.showToast({ title: '网络请求失败', icon: 'none' });
      }
    });
  },

  // 角色选择
  onRoleChange(event) {
    const selectedIndex = event.detail.value;
    const selectedRole = this.data.roles[selectedIndex];
    this.setData({
      'userInfo.role': selectedRole,
    });
  },

  // 家庭编号输入（假设家庭编号是只读）
  onFamilyIdInput(event) {
    this.setData({
      'userInfo.family_id': event.detail.value,
    });
    console.log(userInfo.family_id)
  },

  // 提交修改
  submit() {
    const { userInfo } = this.data;
    const user_id = userInfo.user_id; // 从 userInfo 中获取 user_id
    if (!user_id) {
      wx.showToast({ title: '用户信息无效', icon: 'none' });
      return;
    }

    wx.request({
      url: `http://127.0.0.1:5000/api/auth/update_user/${user_id}`, // 通过 user_id 提交修改
      method: 'PUT',
      header: {
        'Authorization': `Bearer ${wx.getStorageSync('token')}`, // 携带 token
        'Content-Type': 'application/json',
      },
      data: userInfo, // 提交修改后的用户信息
      success: (res) => {
        if (res.statusCode === 200) {
          wx.showToast({ title: '修改成功', icon: 'success' });
          wx.navigateBack(); // 返回上一页
        } else {
          wx.showToast({ title: '修改失败', icon: 'none' });
        }
      },
      fail: (err) => {
        console.error('请求失败：', err);
        wx.showToast({ title: '网络请求失败', icon: 'none' });
      },
    });
  },
});