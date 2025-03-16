Page({
  data: {
      fallDetectionRecord: {}
  },
  onLoad: function (options) {
      const recordId = options.record_id;
      if (recordId) {
          this.fetchFallDetectionRecord(recordId);
      } else {
          console.error('缺少 record_id 参数');
      }
  },
  fetchFallDetectionRecord: function (recordId) {
      wx.request({
          url: `http://127.0.0.1:5000/api/message/fall_detection_records/${recordId}`,
          method: 'GET',
          success: (res) => {
              if (res.statusCode === 200) {
                  const data = res.data.data;
                  const videoFramePath = data.video_frame_path.replace(/\\/g, '/');
                  data.snapshots = [];
                  for (let i = 0; i < 3; i++) {
                      const snapshotUrl = `http://127.0.0.1:5000/${videoFramePath}/${recordId}-${i}.jpg`;
                      data.snapshots.push(snapshotUrl);
                  }
                  console.log('拼接后的图片 URL 数组:', data.snapshots); // 打印数组，确认 URL 是否正确
                  this.setData({
                      fallDetectionRecord: data
                  });
              } else {
                  console.error('请求失败，状态码：', res.statusCode);
              }
          },
          fail: (err) => {
              console.error('请求出错：', err);
          }
      });
  }
});