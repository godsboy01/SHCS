// components/navigation-bar/navigation-bar.js
Component({
  properties: {
    title: String, // 标题
    back: true, // 是否显示返回按钮
    homeButton: true, // 是否显示首页按钮
    color: {
      type: String,
      value: '#000000', // 默认文字颜色
    },
    background: {
      type: String,
      value: '#ffffff', // 默认背景颜色
    },
  },

  data: {
    ios: false, // 是否为 iOS 系统
  },

  methods: {
    // 返回上一页
    back() {
      wx.navigateBack();
    },

    // 返回首页
    home() {
      wx.switchTab({ url: '/pages/home/home' }); // 跳转到首页
    },
  },
});