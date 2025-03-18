const { api } = require('../../utils/api');

Page({
  data: {
    activeTab: 0, // 当前选中标签
    messages: [],
    fallRecords: []
  },

  // 切换消息分类
  switchTab(e) {
    const index = e.currentTarget.dataset.index;
    this.setData({ activeTab: index });
    if (index === 0) {
      this.fetchMessages();
    } else {
      this.fetchFallRecords();
    }
  },

  // 获取通知数据
  fetchMessages() {
    const userId = wx.getStorageSync('user_id');
    if (!userId) {
      wx.showToast({
        title: '请先登录',
        icon: 'none'
      });
      return;
    }
    
    api.message.getUserMessages(userId).then(res => {
      this.setData({
        messages: res.data
      });
    }).catch(err => {
      console.error("获取消息失败", err);
      wx.showToast({
        title: '获取消息失败',
        icon: 'none'
      });
    });
  },

  // 获取跌倒记录
  fetchFallRecords() {
    const userId = wx.getStorageSync('user_id');
    if (!userId) {
      wx.showToast({
        title: '请先登录',
        icon: 'none'
      });
      return;
    }

    api.camera.getFallRecords(userId).then(res => {
      this.setData({
        fallRecords: res.data
      });
    }).catch(err => {
      console.error("获取跌倒记录失败", err);
      wx.showToast({
        title: '获取跌倒记录失败',
        icon: 'none'
      });
    });
  },

  // 查看消息详情
  viewDetail(e) {
    const { id, type } = e.currentTarget.dataset;
    if (type === 'fall') {
      wx.navigateTo({
        url: `/pages/fall-detail/fall-detail?record_id=${id}`
      });
    } else {
      wx.navigateTo({
        url: `/pages/message-detail/message-detail?record_id=${id}`
      });
    }
  },

  // 页面加载时
  onLoad() {
    this.fetchMessages();
  },

  // 下拉刷新
  onPullDownRefresh() {
    if (this.data.activeTab === 0) {
      this.fetchMessages();
    } else {
      this.fetchFallRecords();
    }
    wx.stopPullDownRefresh();
  }
});
