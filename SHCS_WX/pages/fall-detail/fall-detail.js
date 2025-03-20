const { api, STATIC_URL } = require('../../utils/api');

Page({
  data: {
    detail: null,
    loading: true,
    imagePath: ''
  },

  // 格式化路径，将反斜杠转换为正斜杠
  formatPath(path) {
    return path ? path.replace(/\\/g, '/') : '';
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
    
    api.monitor.getFallDetail(recordId)
      .then(res => {
        if (res.code === 200) {
          const detail = res.data;
          // 格式化图片路径
          const imagePath = detail.video_frame_path ? 
            `${STATIC_URL}/${this.formatPath(detail.video_frame_path)}` : '';
          
          this.setData({
            detail,
            imagePath,
            loading: false
          });
        }
      })
      .catch(err => {
        console.error('获取跌倒详情失败:', err);
        wx.showToast({
          title: '获取详情失败',
          icon: 'none'
        });
      })
      .finally(() => {
        wx.hideLoading();
      });
  },

  // 预览图片
  previewImage() {
    if (this.data.imagePath) {
      wx.previewImage({
        urls: [this.data.imagePath],
        current: this.data.imagePath
      });
    }
  }
}); 