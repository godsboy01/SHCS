Page({
  data: {
    isLoggedIn: false, // 是否登录
    userInfo: null, // 用户信息
    isLoading: true, // 页面加载状态
    errorMessage: '' // 错误信息
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
      // console.log('当前用户ID:', user.userid); // 添加日志输出
      this.setData({ 
        isLoggedIn: true, 
        userInfo: user,
      });
      this.loadUserInfo(user.userid); // 使用 userid 加载用户信息
    } else {
      console.error('User or userid is missing in user object:', user);
      wx.redirectTo({ url: '/pages/login/login' }); // 跳转到登录页面
    }
  },

  // 加载用户信息
  loadUserInfo(userid) {
    wx.request({
      url: `http://127.0.0.1:5000/api/auth/get_info/${userid}`, // 通过 userid 获取用户信息
      method: 'GET',
      header: {
        'Authorization': `Bearer ${wx.getStorageSync('token')}`, // 携带 token
      },
      success: (res) => {
        if (res.statusCode === 200) {
          const userInfo = res.data;
          // console.log('获取到的用户信息:', userInfo); // 添加日志输出
          // 更新页面数据
          this.setData({ 
            userInfo: userInfo, 
            isLoading: false 
          });
          this.loadFamilyMembers(userInfo)
        } else {
          this.setData({ 
            isLoading: false, 
            errorMessage: '获取用户信息失败' 
          });
          wx.showToast({ title: '获取用户信息失败', icon: 'none' });
        }
      },
      fail: (err) => {
        console.error('请求失败：', err);
        this.setData({ 
          isLoading: false, 
          errorMessage: '网络请求失败' 
        });
        wx.showToast({ title: '网络请求失败', icon: 'none' });
      },
    });
  },
  
  // 加载家庭成员信息
  loadFamilyMembers(userInfo) {
    const user = userInfo
    console.log(user)
    if (user && user.family_id) {
      wx.request({
        url: `http://127.0.0.1:5000/api/family/get_family/${user.family_id}`, // 通过 user_id 获取家庭成员信息
        method: 'GET',
        header: {
          'Authorization': `Bearer ${wx.getStorageSync('token')}`, // 携带 token
        },
        success: (res) => {
          if (res.statusCode === 200) {
            let familyInfo = res.data;

            // 如果头像路径不是完整的 URL，可以在这里进行转换
            familyInfo.members.forEach(member => {
              if (member.avatar_url && !/^https?:\/\//.test(member.avatar_url)) {
                member.avatar_url = `http://127.0.0.1:5000${member.avatar_url}`;
              }
            });

            console.log('获取到的家庭成员信息:', familyInfo); // 添加日志输出
            this.setData({ familyMembers: familyInfo.members });
          } else {
            wx.showToast({ title: '获取家庭成员信息失败', icon: 'none' });
          }
        },
        fail: (err) => {
          console.error('请求失败：', err);
          wx.showToast({ title: '网络请求失败', icon: 'none' });
        },
      });
    }
  },

  // 头像加载失败时的处理函数
  onImageError(e) {
    console.warn('头像加载失败:', e);
    this.setData({
      'userInfo.avatar': '../../assets/tabbar/people.png' // 设置默认头像
    });
  },

   // 跳转到家庭管理页面
   navigateToFamilyManagement() {
    const familyId = this.data.userInfo.family_id;
    if (!familyId) {
      wx.showToast({ title: '尚未绑定家庭', icon: 'none' });
      return;
    }
    wx.navigateTo({
      url: `/pages/familyMembers/familyMembers?familyId=${familyId}`
    });
  },
  
  // 跳转到家庭成员信息页面
  navigateToMemberInfo(event) {
    const memberId = event.currentTarget.dataset.memberId;
    wx.navigateTo({
      url: `/pages/member-info/member-info?memberId=${memberId}`,
    });
  },
  // 跳转到编辑信息页面
  navigateToEditProfile() {
    wx.navigateTo({ url: '/pages/edit-profile/edit-profile' });
  },
});