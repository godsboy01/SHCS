Page({
  data: {
    userList: [],
    searchQuery: '',
    familyId: null,  // 当前家庭ID
    selectedUserId: null,  // 选中的用户ID
    selectedUser: null,  // 选中的用户信息
  },

  onLoad(options) {
    this.setData({ familyId: options.familyId });
    this.getUsers();
  },

  onPullDownRefresh() {
    // 下拉刷新时重新获取数据
    this.getUsers().then(() => {
      // 停止下拉刷新动画
      wx.stopPullDownRefresh();
    }).catch(() => {
      // 如果获取数据失败，也停止下拉刷新动画
      wx.stopPullDownRefresh();
    });
  },

  getUsers(searchQuery = '') {
    return new Promise((resolve, reject) => {
      wx.request({
        url: 'http://127.0.0.1:5000/api/auth/users',
        data: { q: searchQuery },
        success: (res) => {
          const { users } = res.data;

          users.forEach(user => {
            if (user.avatar && !/^https?:\/\//.test(user.avatar)) {
              user.avatar = `http://127.0.0.1:5000${user.avatar}`;
            }
          });

          this.setData({ userList: users }, () => resolve());
        },
        fail: (err) => {
          console.error('获取用户列表失败:', err);
          wx.showToast({ title: '获取用户列表失败', icon: 'none' });
          reject();
        }
      });
    });
  },

  onSearch(e) {
    const searchQuery = e.detail.value;
    this.setData({ searchQuery });
    this.getUsers(searchQuery);
  },

  clearSearch() {
    this.setData({ searchQuery: '' }, () => this.getUsers());
  },

  selectUser(e) {
    const userId = e.currentTarget.dataset.userId;
    const selectedUser = this.data.userList.find(user => user.user_id === parseInt(userId));

    this.setData({
      selectedUserId: userId,
      selectedUser: selectedUser,
    }, () => {
      console.log('Selected User:', this.data.selectedUser);
    });
  },

  addUserToFamily() {
    const userId = this.data.selectedUserId;
    const familyId = this.data.familyId;
    const selectedUser = this.data.selectedUser;

    // 参数校验增强
    if (!userId || !familyId) {
      wx.showToast({ title: '参数不完整', icon: 'none' });
      return;
    }

    // 检查用户是否已经是当前家庭的成员
    if (selectedUser.family_id === familyId) {
      wx.showToast({ title: '用户已经是当前家庭的成员', icon: 'none' });
      return;
    }

    // 处理当前家庭ID为null的情况
    const currentFamilyId = selectedUser.family_id || null;  // 明确传递null

    // 打印调试信息
    console.log('Sending data:', JSON.stringify({
      family_id: familyId,
      current_family_id: currentFamilyId
    }));

    wx.request({
      url: `http://127.0.0.1:5000/api/auth/update_user/${userId}`,
      method: 'PUT',
      header: {
        'Authorization': `Bearer ${wx.getStorageSync('token')}`,
        'Content-Type': 'application/json'
      },
      data: JSON.stringify({
        family_id: parseInt(familyId, 10),  // 确保是整数
        current_family_id: currentFamilyId !== null ? parseInt(currentFamilyId, 10) : null  // 如果为 null 则保持 null
      }),
      success: (res) => {
        console.log('响应状态码:', res.statusCode, '响应数据:', res.data);
        const messages = {
          200: '添加成功',
          400: res.data.message || '请求参数错误',
          404: '用户或家庭不存在',
          409: '家庭状态冲突'
        };
        wx.showToast({
          title: messages[res.statusCode] || '操作失败',
          icon: res.statusCode === 200 ? 'success' : 'none'
        });
        if (res.statusCode === 200) {
          this.getUsers();
          setTimeout(() => wx.navigateBack(), 1500);
        }
      },
      fail: (err) => {
        console.error('网络错误:', err);
        wx.showToast({ title: '网络连接失败', icon: 'none' });
      }
    });
  }
});