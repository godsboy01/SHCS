Page({
  data: {
    isLoggedIn: false, // 是否登录
    userInfo: null,    // 用户信息
    isLoading: true,   // 加载状态
    errorMessage: '' ,  // 错误信息
    roles: ['elderly', 'family', 'admin'], // 角色选项
  },

  onLoad() {
    this.checkLoginStatus(); // 检查登录状态
  },

  onShow() {
    this.checkLoginStatus(); // 每次页面显示时检查登录状态
  },

  // 检查登录状态
  checkLoginStatus() {
    const user = wx.getStorageSync('user'); // 从本地存储获取用户信息
    if (user && user.userid) {
      console.log('已登录用户信息:', user.userid); // 添加日志输出
      this.setData({
        isLoggedIn: true,
        userInfo: user,
      }, () => {
        // 使用 user_id 加载用户信息
        this.loadUserInfo(user.userid);
      });
    } else {
      console.warn('未找到有效的用户信息，即将跳转到登录页面');
      wx.redirectTo({ url: '/pages/login/login' }); // 跳转到登录页面
    }
  },

  // 加载用户信息
  loadUserInfo(userid) {
    wx.request({
      url: `http://127.0.0.1:5000/api/auth/get_info/${userid}`, // 通过 user_id 获取用户信息
      method: 'GET',
      header: {
        'Authorization': `Bearer ${wx.getStorageSync('token')}`, // 携带 token
      },
      success: (res) => {
        if (res.statusCode === 200) {
          const userInfo = res.data;
          console.log('获取到的用户信息:', userInfo); // 添加日志输出
          // 更新页面数据
          this.setData({ userInfo: userInfo, isLoading: false });
        } else {
          this.setData({ isLoading: false, errorMessage: '获取用户信息失败' });
          wx.showToast({ title: '获取用户信息失败', icon: 'none' });
        }
      },
      fail: (err) => {
        console.error('请求失败：', err);
        this.setData({ isLoading: false, errorMessage: '网络请求失败' });
        wx.showToast({ title: '网络请求失败', icon: 'none' });
      },
    });
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
    const userid = userInfo?.user_id || wx.getStorageSync('user.userid'); // 从 userInfo 或本地缓存中获取 user_id
  
    if (!userid) {
      wx.showToast({ title: '用户信息无效', icon: 'none' });
      return;
    }
  
    wx.showLoading({ title: '上传中...' }); // 显示加载提示
  
    wx.uploadFile({
      url: `http://127.0.0.1:5000/api/auth/upload_avatar/${userid}`, // 通过 user_id 上传头像
      filePath: tempFilePath,
      name: 'file', // 确保文件字段名与服务器端一致
      header: {
        'Authorization': `Bearer ${wx.getStorageSync('token')}`, // 携带 token
      },
      success: (res) => {
        wx.hideLoading(); // 隐藏加载提示
        let data;
        try {
          data = JSON.parse(res.data);
        } catch (e) {
          console.error('解析服务器响应失败:', res.data);
          wx.showToast({ title: '解析响应失败', icon: 'none' });
          return;
        }
  
        console.log('服务器响应:', data); // 添加日志输出
  
        if (data.message === '头像上传成功' && data.avatar_url) {
          this.setData({
            'userInfo.avatar': data.avatar_url, // 更新本地头像 URL
          });
          console.log('更新后的头像 URL:', data.avatar_url); // 添加日志输出
          wx.showToast({ title: '头像上传成功', icon: 'success' });
        } else {
          wx.showToast({ title: data.message || '头像上传失败', icon: 'none' });
        }
      },
      fail: (err) => {
        wx.hideLoading(); // 隐藏加载提示
        console.error('上传失败：', err);
        wx.showToast({ title: '网络请求失败', icon: 'none' });
      },
    });
  },
  // 姓名输入
  onNameInput(event) {
    this.setData({
      'userInfo.name': event.detail.value,
    });
  },


  // 电话输入
  onPhoneInput(event) {
    this.setData({
      'userInfo.phone': event.detail.value,
    });
  },

  // 邮箱输入
  onEmailInput(event) {
    this.setData({
      'userInfo.email': event.detail.value,
    });
  },

  // 地址输入
  onAddressInput(event) {
    this.setData({
      'userInfo.address': event.detail.value,
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