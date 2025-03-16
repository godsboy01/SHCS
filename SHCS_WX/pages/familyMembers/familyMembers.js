Page({
  data: {
    familyId: null,
    familyInfo: null,
  },

  onLoad(options) {
    // 从 URL 参数中获取 familyId
    this.setData({ familyId: options.familyId });
    this.getFamilyInfo();
  },

  getFamilyInfo() {
    const { familyId } = this.data;
    wx.request({
      url: `http://127.0.0.1:5000/api/family/get_family/${familyId}`,
      success: (res) => {
        const familyInfo = res.data;
         // 如果头像路径不是完整的 URL，可以在这里进行转换
         familyInfo.members.forEach(member => {
          if (member.avatar_url && !/^https?:\/\//.test(member.avatar_url)) {
            member.avatar_url = `http://127.0.0.1:5000${member.avatar_url}`;
          }
        });
        this.setData({ familyInfo });
      },
      fail: (err) => {
        console.error('获取家庭信息失败:', err);
        wx.showToast({ title: '获取家庭信息失败', icon: 'none' });
      }
    });
  },

  showUserInfo(e) {
    const userId = e.currentTarget.dataset.userId;
    wx.navigateTo({
      url: `/pages/userInfo/userInfo?userId=${userId}`,
    });
  },

  addMember() {
    // 跳转到添加家庭成员页面或弹出选择用户界面
    wx.navigateTo({
      url: '/pages/addMember/addMember?familyId=' + this.data.familyInfo.family_id,
    });
  }
});