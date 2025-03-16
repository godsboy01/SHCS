const app = getApp();
const user = app.globalData.user; // 直接读取全局变量
// 定义 timeOptions
// 引入 ECharts 小程序版本
import *as echarts from "../../components/echarts/echarts.min"

const timeOptions = [
  { days: 7, label: '最近7天' },
  { days: 30, label: '最近30天' },
  { days: 90, label: '最近90天' }
];

function initChart(canvas, width, height, dpr) {
  const chart = echarts.init(canvas, null, {
    width: width,
    height: height,
    devicePixelRatio: dpr
  });
  canvas.setChart(chart);

  const dates = ['2025-03-01', '2025-03-02', '2025-03-03'];
  const bmiValues = [21.3, 20.28, 20.76];

  chart.setOption({
    title: {
      text: 'BMI 趋势图'
    },
    tooltip: {
      trigger: 'axis'
    },
    xAxis: {
      type: 'category',
      data: dates
    },
    yAxis: {
      type: 'value',
      name: 'BMI 值'
    },
    series: [
      {
        name: 'BMI',
        type: 'line',
        data: bmiValues
      }
    ]
  });
}

Page({
  data: {
    formData: {
      height: '',
      weight: ''
    },
    timeOptions: [
      { name: '最近一周', value: '7d' },
      { name: '最近一个月', value: '30d' },
      { name: '最近三个月', value: '90d' }
    ],
    selectedTimeOption: { name: '最近一周', value: '7d' }, // 默认选中项
    user_id: null,
    currentBMI: 0,
    bmiClass: '',
    leftData: [], // 左侧数据
    rightData: [], // 右侧数据
    bmiMessage: '未记录数据',
    selectedTimeOption: timeOptions[0],
    showSetting: false,
    chartData: [],
    ec: {
      onInit: initChart
    }
  },

  // 页面加载时检查登录状态
  onLoad() {
    // 调用辅助方法获取 user_id，并更新到 data 中
    const userId = this.getUserId();
    if (userId) {
      this.setData({ user_id: userId });
      this.fetchWeightData();
    } else {
      // 处理未登录的情况（如跳转登录页）
      wx.showToast({ title: '请先登录', icon: 'none' });
    }
  },

  // 检查登录状态（确保 userId 存在）
  checkLogin() {
    const userId = this.getUserId();
    console.log(userId)
    if (!userId) {
      wx.showToast({ title: '请先登录', icon: 'none' });
      wx.switchTab({ url: '/pages/login/login' }); // 跳转登录页
    }
  },
  onTimeRangeChange(e) {
    const selectedOption = this.data.timeOptions[e.detail.value];
    this.setData({ selectedTimeOption: selectedOption }, () => {
      this.fetchWeightData(); // 根据选择的时间段重新加载数据
    });
  },
  // 获取 userId 的辅助方法
  getUserId() {
    const user = wx.getStorageSync('user'); // 正确键名为 'user'
    if (!user || !user.userid) {
      console.error('未获取到用户ID，请检查登录状态');
      return null;
    }
    return user.userid; // 返回 userid 字段
  },

  //提交身高体重
  async submitRecord() {
    const { formData, user_id } = this.data;
    // 校验表单
    if (
      !formData.height ||
      !formData.weight ||
      isNaN(parseFloat(formData.height)) ||
      isNaN(parseFloat(formData.weight))
    ) {
      wx.showToast({ title: '请填写有效数值', icon: 'none' });
      return;
    }

    // 构造 payload（确保类型正确）
    const payload = {
      user_id: parseInt(user_id), // 强制转换为整数
      height: parseFloat(formData.height),
      weight: parseFloat(formData.weight),
      recorded_at: this.getCurrentDateTime()
    };

    // 打印 payload 以便调试
    // console.log('发送的 payload:', payload);

    try {
      const res = await wx.request({
        url: 'http://127.0.0.1:5000/api/health/height-weight',
        method: 'POST',
        data: payload,
        header: {
          'content-type': 'application/json'
        }
      });

      if (res.data && res.data.status === 'success') {
        wx.showToast({ title: '记录成功', icon: 'success' });
        this.setData({ 'formData.height': '', 'formData.weight': '' });
      } else {
        throw new Error(res.data?.message || '未知错误');
      }
    } catch (err) {
      // console.error('接口调用失败:', err);
      let errorMessage = '网络请求失败';
      // 尝试获取后端返回的 message
      if (err.response && err.response.data) {
        errorMessage = err.response.data.message || errorMessage;
      } else if (err.message) {
        errorMessage = err.message;
      }
      wx.showToast({
        title: `错误: ${errorMessage}`,
        icon: 'none'
      });
    }


    // 计算 BMI
    const heightM = parseFloat(this.data.formData.height) / 100; // 转换为米
    const weight = parseFloat(this.data.formData.weight);
    const bmi = weight / (heightM * heightM);
    const bmiMessage = this.getBMIResult(bmi);
    const bmiClass = this.getBMIStatusClass(bmi);

    // 更新数据
    this.setData({
      currentBMI: bmi.toFixed(1),
      bmiMessage: bmiMessage,
      bmiClass: bmiClass
    });

  },


  // 获取体重记录数据
  async fetchWeightData() {
    const userId = this.getUserId();
    const selectedOption = this.data.selectedTimeOption;
    if (!userId || !selectedOption) return;

    try {
      wx.showLoading({ title: '加载中...' });
      const res = await wx.request({
        url: `http://127.0.0.1:5000/api/health/weight-record?user_id=${userId}&days=${selectedOption.days}`,
        method: 'GET',
        header: {
          'Content-Type': 'application/json'
        }
      });

      if (res.statusCode === 200 && res.data && res.data.status === 'success') {
        const { bmi_values, dates } = res.data.data;
        this.setData({
          leftData: dates,
          rightData: bmi_values
        }, () => {
          this.initGraph(this.data.leftData, this.data.rightData);
          wx.hideLoading();
        });
      } else {
        console.error('接口返回数据结构不符合预期:', res);
        wx.showToast({ title: '数据加载失败，请检查接口返回', icon: 'none' });
      }
    } catch (e) {
      console.error('获取数据失败:', e);
      wx.showToast({ title: '网络错误，请重试', icon: 'none' });
    }
  },
  initGraph(leftData, rightData) {
    this.oneComponent.init((canvas, width, height) => {
      const chart = echarts.init(canvas, null, {
        width: width,
        height: height
      });
      initChart(chart, leftData, rightData);
      this.chart = chart;
      return chart;
    });
  }
  // // ECharts 初始化
  // onInitChart(canvas, width, height, dpr) {
  //   const chart = echarts.init(canvas, null, {
  //     width: width,
  //     height: height,
  //     devicePixelRatio: dpr
  //   });
  //   canvas.setChart(chart);

  //   this.drawChart(chart);
  // },
,
  drawChart(chart) {
    const { chartData } = this.data;
    const dates = chartData.map(item => item.date);
    const bmiValues = chartData.map(item => item.bmi);
  
    chart.setOption({
      title: {
        text: 'BMI 趋势图'
      },
      tooltip: {
        trigger: 'axis'
      },
      xAxis: {
        type: 'category',
        data: dates
      },
      yAxis: {
        type: 'value',
        name: 'BMI 值'
      },
      series: [
        {
          name: 'BMI',
          type: 'line',
          data: bmiValues
        }
      ]
    });
  },
  // 封装 POST 请求
  postWeightRecord(data) {
    return new Promise((resolve, reject) => {
      wx.request({
        url: 'http://127.0.0.1:5000/api/health/weight-record',
        method: 'POST',
        data: data,
        header: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${wx.getStorageSync('token')}` // 如果需要 token
        },
        success: (res) => resolve(res.data),
        fail: (err) => reject(err)
      });
    });
  },

  // // 封装 GET 请求
  // getWeightRecords(params) {
  //   return new Promise((resolve, reject) => {
  //     wx.request({
  //       url: 'http://127.0.0.1:5000/api/health/weight-record',
  //       method: 'GET',
  //       data: params,
  //       header: {
  //         'Content-Type': 'application/json',
  //         'Authorization': `Bearer ${wx.getStorageSync('token')}` // 如果需要 token
  //       },
  //       success: (res) => resolve(res.data),
  //       fail: (err) => reject(err)
  //     });
  //   });
  // },

  // 重置表单
  resetForm() {
    this.setData({
      formData: { height: '', weight: '' },
      currentBMI: '--',
      bmiMessage: '未记录数据'
    });
  },

  // 计算 BMI（确保输入有效性）
  calculateBMI() {
    const { height, weight } = this.data.formData;
    if (!height || !weight) {
      this.setData({
        currentBMI: '--',
        bmiClass: '',
        bmiMessage: '请输入身高和体重'
      });
      return;
    }

    const heightM = height / 100;
    const bmi = (weight / (heightM * heightM)).toFixed(1);
    const { class: bmiClass, message } = this.getBMIStatus(bmi);

    this.setData({
      currentBMI: bmi,
      bmiClass,
      bmiMessage: message
    });
  },
  // 辅助方法：根据 BMI 值返回对应信息和样式类
  getBMIResult(bmi) {
    if (bmi < 18.5) return '偏瘦';
    if (bmi < 24) return '正常';
    if (bmi < 28) return '超重';
    return '肥胖';
  },
  getBMIStatusClass(bmi) {
    if (bmi < 18.5) return 'bmi-lean';
    if (bmi < 24) return 'bmi-normal';
    if (bmi < 28) return 'bmi-over';
    return 'bmi-obese';
  },

  // 时间段选择
  onTimeRangeChange(e) {
    const selectedOption = timeOptions[e.detail.value];
    this.setData({ selectedTimeOption: selectedOption }, () => {
      this.fetchWeightData();
    });
  },


  // 设置弹窗
  showSettingModal() {
    this.setData({ showSetting: true });
  },
  hideSettingModal() {
    this.setData({ showSetting: false });
  },

  // 监听身高输入
  onHeightInput(e) {
    const value = e.detail.value;
    this.setData({
      'formData.height': value // 更新表单数据
    });
  },

  // 监听体重输入
  onWeightInput(e) {
    const value = e.detail.value;
    this.setData({
      'formData.weight': value // 更新表单数据
    });
  },
  getCurrentDateTime() {
    const now = new Date();
    const pad = (n) => n.toString().padStart(2, '0');
    return `${now.getFullYear()}-${pad(now.getMonth() + 1)}-${pad(now.getDate())} ` +
      `${pad(now.getHours())}:${pad(now.getMinutes())}:${pad(now.getSeconds())}`;
  }
});