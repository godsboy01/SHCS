Page({
  data: {
    videoSrc: '',      // 视频帧地址
    isPlaying: false,  // 是否播放中（初始状态为未播放）
    isLoading: true,   // 加载状态
    errorMessage: '' ,  // 错误信息
    currentTime: '',  //当前时间
    familyName: '张', // 家庭名称
  },
  onLoad() {
    // 初始化时间
    this.updateTime();
    this.timeUpdateTimer = setInterval(() => {
      this.updateTime();
    }, 1000); // 每秒更新一次时间
  },
  // 更新时间
  updateTime() {
    const now = new Date();
    const timeString = now.toLocaleTimeString(); // 格式化时间
    this.setData({ currentTime: timeString });
  },
  // 切换播放/暂停
  togglePlay() {
    const { isPlaying } = this.data;
    this.setData({ isPlaying: !isPlaying });

    if (isPlaying) {
      // 暂停逻辑：停止更新视频帧并清空地址
      clearInterval(this.timer);
      this.setData({ videoSrc: '' }); // 清空视频地址
    } else {
      // 播放逻辑：开始加载视频流
      this.startVideoStream();
    }
  },

  // 开始视频流
  startVideoStream() {
    // 设置初始视频帧地址
    this.setData({
      videoSrc: `http://127.0.0.1:5000/api/camera/video_feed`
    });

    // // 定时更新视频帧
    // this.timer = setInterval(() => {
    //   this.setData({
    //     videoSrc: `http://127.0.0.1:5000/api/camera/video_feed?t=${Date.now()}`
    //   });
    // }, 100); // 每 100ms 更/新一次视频帧
  },

  onUnload() {
    // 页面卸载时清除定时器
    clearInterval(this.timer);
  }
});