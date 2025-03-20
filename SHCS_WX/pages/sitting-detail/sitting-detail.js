const { api } = require('../../utils/api');

Page({
  data: {
    detail: null,
    loading: true
  },

  onLoad(options) {
    const { id } = options;
    if (id) {
      this.fetchDetail(id);
    }
  },

  // 返回上一页
  goBack() {
    wx.navigateBack({
      delta: 1
    });
  },

  // 获取详情数据
  fetchDetail(recordId) {
    wx.showLoading({ title: '加载中' });
    
    api.monitor.getSittingDetail(recordId)
      .then(res => {
        if (res.code === 200) {
          this.setData({
            detail: res.data,
            loading: false
          });
        }
      })
      .catch(err => {
        console.error('获取久坐详情失败:', err);
        wx.showToast({
          title: '获取详情失败',
          icon: 'none'
        });
      })
      .finally(() => {
        wx.hideLoading();
      });
  }
}); 