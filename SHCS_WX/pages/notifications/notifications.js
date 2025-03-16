Page({
  data: {
    activeTab: 0, // 当前选中标签
    messages: []
  },

  // 切换消息分类
  switchTab(e) {
    const index = e.currentTarget.dataset.index;
    this.setData({ activeTab: index });
    this.fetchMessages();  // 重新获取数据
  },

  // 获取通知数据
  fetchMessages() {
    const userId = 1;  // 假设是用户ID 1，实际中应该获取真实的用户 ID
    
    wx.request({
      url: `http://127.0.0.1:5000/api/message/messages_user/${userId}`,
      method: 'GET',
      success: res => {
        if (res.data.code === 200) {
          this.setData({
            messages: res.data.data
          });
        }
      },
      fail: err => {
        console.error("请求失败", err);
      }
    });
  },

  // 查看消息详情
  viewDetail(e) {
    const messageId = e.currentTarget.dataset.id;
    console.log('传递的 messageId:', messageId);
    wx.navigateTo({
      url: `/pages/message-detail/message-detail?record_id=1`
    });
  },

  // 页面加载时
  onLoad() {
    this.fetchMessages();  // 加载数据
  }
});
