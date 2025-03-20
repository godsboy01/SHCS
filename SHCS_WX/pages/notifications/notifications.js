const { api } = require('../../utils/api');

Page({
  data: {
    activeTab: 0,
    currentPage: 1,
    pageSize: 10,
    fallTotal: 0,
    sittingTotal: 0,
    fallRecords: [],
    sittingRecords: [],
    healthRecords: [],
    loading: false
  },

  // 切换标签
  switchTab(e) {
    const index = parseInt(e.currentTarget.dataset.index);
    if (this.data.activeTab === index) return;
    
    this.setData({ 
      activeTab: index,
      currentPage: 1
    }, () => {
      this.fetchCurrentTabData();
    });
  },

  // 获取当前标签的数据
  fetchCurrentTabData() {
    switch (this.data.activeTab) {
      case 0:
        this.fetchFallRecords();
        break;
      case 1:
        this.fetchSittingRecords();
        break;
      case 2:
        // 预留健康记录接口
        break;
    }
  },

  // 获取跌倒记录
  fetchFallRecords() {
    if (this.data.loading) return;
    
    this.setData({ loading: true });
    wx.showLoading({ title: '加载中' });
    
    api.monitor.getFallRecords({
      page: this.data.currentPage,
      pageSize: this.data.pageSize
    }).then(res => {
      console.log('跌倒记录响应:', res);
      if (res.code === 200) {
        this.setData({
          fallRecords: res.data.records || [],
          fallTotal: res.data.total || 0
        });
      }
    }).catch(err => {
      console.error('获取跌倒记录失败:', err);
      wx.showToast({
        title: '获取记录失败',
        icon: 'none'
      });
    }).finally(() => {
      this.setData({ loading: false });
      wx.hideLoading();
    });
  },

  // 获取久坐记录
  fetchSittingRecords() {
    if (this.data.loading) return;
    
    this.setData({ loading: true });
    wx.showLoading({ title: '加载中' });
    
    api.monitor.getSittingRecords({
      page: this.data.currentPage,
      pageSize: this.data.pageSize
    }).then(res => {
      console.log('久坐记录响应:', res);
      if (res.code === 200) {
        this.setData({
          sittingRecords: res.data.records || [],
          sittingTotal: res.data.total || 0
        });
      }
    }).catch(err => {
      console.error('获取久坐记录失败:', err);
      wx.showToast({
        title: '获取记录失败',
        icon: 'none'
      });
    }).finally(() => {
      this.setData({ loading: false });
      wx.hideLoading();
    });
  },

  // 获取当前标签的总记录数
  getCurrentTotal() {
    return this.data.activeTab === 0 ? this.data.fallTotal : this.data.sittingTotal;
  },

  // 获取当前标签的记录列表
  getCurrentRecords() {
    return this.data.activeTab === 0 ? this.data.fallRecords : this.data.sittingRecords;
  },

  // 查看详情
  viewDetail(e) {
    const { id, type } = e.currentTarget.dataset;
    let url = '';
    
    switch(type) {
      case 'fall':
        url = `/pages/fall-detail/fall-detail?id=${id}`;
        break;
      case 'sitting':
        url = `/pages/sitting-detail/sitting-detail?id=${id}`;
        break;
    }

    if (url) {
      wx.navigateTo({ url });
    }
  },

  // 上一页
  prevPage() {
    if (this.data.currentPage > 1 && !this.data.loading) {
      this.setData({
        currentPage: this.data.currentPage - 1
      }, () => {
        this.fetchCurrentTabData();
      });
    }
  },

  // 下一页
  nextPage() {
    const total = this.getCurrentTotal();
    const totalPages = Math.ceil(total / this.data.pageSize);
    if (this.data.currentPage < totalPages && !this.data.loading) {
      this.setData({
        currentPage: this.data.currentPage + 1
      }, () => {
        this.fetchCurrentTabData();
      });
    }
  },

  onLoad() {
    this.fetchCurrentTabData();
  },

  onPullDownRefresh() {
    this.setData({
      currentPage: 1
    }, () => {
      this.fetchCurrentTabData();
      wx.stopPullDownRefresh();
    });
  }
});