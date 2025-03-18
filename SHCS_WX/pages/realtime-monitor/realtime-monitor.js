const { api } = require('../../utils/api')

Page({
  data: {
    videoSrc: '',      // 视频流地址
    isPlaying: false,  // 是否正在播放
    currentTime: '',   // 当前时间
    familyName: '张',   // 家庭名称
    errorMsg: '',      // 错误信息
    alertLevel: 0,     // 警报级别
    fallSnapshots: [], // 跌倒截图列表
    sitSnapshots: [],  // 坐下截图列表
  },

  onLoad() {
    // 初始化时间
    this.updateTime();
    this.timeUpdateTimer = setInterval(() => {
      this.updateTime();
    }, 1000);
    
    // 启动警报检测
    // this.startAlertDetection();
  },

  // 更新时间
  updateTime() {
    const now = new Date();
    const timeString = now.toLocaleTimeString('zh-CN', { hour12: false });
    this.setData({ currentTime: timeString });
  },

  // 切换播放/暂停
  togglePlay() {
    const { isPlaying } = this.data;
    if (isPlaying) {
      this.stopVideoStream();
    } else {
      this.startVideoStream();
    }
  },

  // 开始视频流
  startVideoStream() {
    const timestamp = Date.now();
    this.setData({
      videoSrc: `http://127.0.0.1:5000/api/camera/video_feed`,
      isPlaying: true,
      errorMsg: ''
    });
  },

  // 停止视频流
  stopVideoStream() {
    this.setData({
      videoSrc: '',
      isPlaying: false,
      errorMsg: ''
    });
  },

  // 处理视频错误
  handleVideoError(e) {
    console.error('视频加载失败:', e);
    this.setData({
      errorMsg: '摄像头连接失败，请检查摄像头是否正常连接',
      isPlaying: false
    });
  },

  // 启动警报检测
//   startAlertDetection() {
//     this.alertDetectionTimer = setInterval(() => {
//       if (this.data.isPlaying) {
//         wx.request({
//           url: 'http://127.0.0.1:5000/api/camera/alert_level',
//           success: (res) => {
//             if (res.data && res.data.alert_level !== undefined) {
//               this.setData({ alertLevel: res.data.alert_level });
//             }
//           },
//           fail: (err) => {
//             console.error('获取警报级别失败:', err);
//           }
//         });
//       }
//     }, 1000);

    // 定期更新截图列表
//     this.updateSnapshotsTimer = setInterval(() => {
//       this.updateSnapshots();
//     }, 5000);
//   },

//   // 更新截图列表
//   updateSnapshots() {
//     // 获取跌倒截图
//     wx.request({
//       url: 'http://127.0.0.1:5000/api/camera/fall_snapshots',
//       success: (res) => {
//         if (res.data) {
//           this.setData({ fallSnapshots: res.data });
//         }
//       }
//     });

//     // 获取坐下截图
//     wx.request({
//       url: 'http://127.0.0.1:5000/api/camera/sit_snapshots',
//       success: (res) => {
//         if (res.data) {
//           this.setData({ sitSnapshots: res.data });
//         }
//       }
//     });
//   },

  onUnload() {
    // 页面卸载时清理资源
    if (this.timeUpdateTimer) {
      clearInterval(this.timeUpdateTimer);
    }
    if (this.alertDetectionTimer) {
      clearInterval(this.alertDetectionTimer);
    }
    if (this.updateSnapshotsTimer) {
      clearInterval(this.updateSnapshotsTimer);
    }
    this.stopVideoStream();
  }
});