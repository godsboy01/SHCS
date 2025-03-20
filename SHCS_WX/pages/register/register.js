const { api } = require('../../utils/api');
const app = getApp();

Page({
  data: {
    username: '',  // 用户名
    phone: '',     // 手机号
    password: '',  // 密码
    clientHeight: 0,  // 动态高度
    canSendCode: true, // 控制是否可以发送验证码
    countdown: 60, // 倒计时时间
    roles: ['监护人', '被监护人'],
    roleIndex: 0,
    roleMap: {
      0: 'guardian',
      1: 'elderly'
    }
  },

  onLoad() {
    // 获取屏幕高度并设置到data中
    const that = this;
    wx.getSystemInfo({
      success(res) {
        that.setData({
          clientHeight: res.windowHeight
        });
      }
    });
  },

  // 输入框事件处理函数
  username(e) {
    this.setData({
      username: e.detail.value
    });
  },

  phone(e) {
    this.setData({
      phone: e.detail.value
    });
  },

  password(e) {
    this.setData({
      password: e.detail.value
    });
  },

  // code(e) {
  //   this.setData({
  //     code: e.detail.value
  //   });
  // },

  // // 发送验证码按钮点击事件处理函数
  // sendCode() {
  //   const { phone } = this.data;

  //   if (!phone) {
  //     wx.showToast({
  //       title: '请输入手机号',
  //       icon: 'none'
  //     });
  //     return;
  //   }

  //   // 模拟发送验证码（实际应用中应调用后端接口）
  //   wx.request({
  //     url: 'http://127.0.0.1:5000/api/auth/send_code', // 替换为你的实际后端URL
  //     method: 'POST',
  //     header: {
  //       'content-type': 'application/json'
  //     },
  //     data: JSON.stringify({
  //       phone
  //     }),
  //     success: (res) => {
  //       if (res.statusCode === 200) {
  //         wx.showToast({
  //           title: '验证码已发送，请查收',
  //           icon: 'success'
  //         });

  //         // 启动倒计时
  //         let countdown = 60;
  //         this.setData({ canSendCode: false, countdown });

  //         const timer = setInterval(() => {
  //           countdown--;
  //           this.setData({ countdown });
  //           if (countdown <= 0) {
  //             clearInterval(timer);
  //             this.setData({ canSendCode: true, countdown: 60 });
  //           }
  //         }, 1000);
  //       } else {
  //         wx.showToast({
  //           title: res.data.message || '发送验证码失败，请重试',
  //           icon: 'none'
  //         });
  //       }
  //     },
  //     fail: () => {
  //       wx.showToast({
  //         title: '网络错误，请稍后再试',
  //         icon: 'none'
  //       });
  //     }
  //   });
  // },

  handleRoleChange(e) {
    this.setData({
      roleIndex: e.detail.value
    });
  },

  handleRegister(e) {

    if (!api || !api.auth) {
      console.error('API not properly initialized');
      wx.showToast({
        title: '系统初始化失败',
        icon: 'none'
      });
      return;
    }

    const formData = e.detail.value;
    const role = this.data.roleMap[this.data.roleIndex];


    if (!formData.username || !formData.password || !formData.name || !formData.phone) {
      wx.showToast({
        title: '请填写完整信息',
        icon: 'none'
      });
      return;
    }

    wx.showLoading({
      title: '注册中...'
    });

    api.auth.register({
      ...formData,
      role
    }).then(res => {
      wx.hideLoading();
      app.login(res.user, res.token);
      
      wx.showToast({
        title: '注册成功',
        icon: 'success'
      });

      wx.switchTab({
        url: '/pages/home/home'
      });
    }).catch(err => {
      wx.hideLoading();
      wx.showToast({
        title: err.data?.message || '注册失败',
        icon: 'none'
      });
    });
  }
});