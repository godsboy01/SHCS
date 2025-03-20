import * as echarts from '../../components/echarts/echarts.min.js';
import { api } from '../../utils/api.js';

const app = getApp();

Page({
  data: {
    systemInfo: wx.getSystemInfoSync(),
    weightEc: {
      lazyLoad: true
    },
    latestBMI: '--',
    latestWeight: '--',
    latestHeight: '--',
    latestTime: '--',
    bmiClass: '',
    bmiDescription: '',
    inputWeight: '',
    inputHeight: ''
  },

  onLoad: function() {
    this.initChart();
    this.loadHealthData();
  },

  // 返回上一页
  goBack: function() {
    wx.navigateBack({
      delta: 1
    });
  },

  // 初始化图表
  initChart: function() {
    this.ecComponent = this.selectComponent('#weightChart');
    this.ecComponent.init((canvas, width, height, dpr) => {
      const chart = echarts.init(canvas, null, {
        width: width,
        height: height,
        devicePixelRatio: dpr
      });
      canvas.setChart(chart);

      // 先设置一个空的配置
      const option = {
        title: {
          text: '体重和BMI趋势',
          left: 'center',
          top: 10,
          textStyle: {
            fontSize: 14
          }
        },
        tooltip: {
          trigger: 'axis'
        },
        legend: {
          data: ['体重', 'BMI'],
          bottom: 0
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '15%',
          top: '15%',
          containLabel: true
        },
        xAxis: {
          type: 'category',
          data: []
        },
        yAxis: [
          {
            name: '体重(kg)',
            type: 'value',
            splitLine: {
              lineStyle: {
                type: 'dashed'
              }
            }
          },
          {
            name: 'BMI',
            type: 'value',
            splitLine: {
              show: false
            }
          }
        ],
        series: [
          {
            name: '体重',
            type: 'line',
            data: [],
            itemStyle: {
              color: '#4CAF50'
            }
          },
          {
            name: 'BMI',
            type: 'line',
            yAxisIndex: 1,
            data: [],
            itemStyle: {
              color: '#2196F3'
            }
          }
        ]
      };
      chart.setOption(option);
      this.chart = chart;
      return chart;
    });
  },

  // 加载健康数据
  loadHealthData: function() {
    const userId = app.globalData.userInfo?.user_id || 1;
    
    console.log('开始加载健康数据，用户ID:', userId);
    
    // 显示加载提示
    wx.showLoading({
      title: '加载中...'
    });

    api.health.getChartData(userId, { days: 7 })
      .then(res => {
        console.log('获取到的原始数据:', res);
        // 检查响应数据的结构
        if (!res || !res.data) {
          throw new Error('没有收到响应数据');
        }

        const healthData = res.data;
        console.log('健康数据:', healthData);

        // 如果没有数据，显示提示
        if (!healthData.dates || healthData.dates.length === 0) {
          wx.showToast({
            title: '暂无记录数据',
            icon: 'none',
            duration: 2000
          });
          return;
        }

        // 更新图表和记录
        this.updateChart(healthData);
        this.updateLatestRecord(healthData);
        console.log('数据处理完成');
      })
      .catch(err => {
        console.error('获取数据失败，详细错误：', err);
        wx.showToast({
          title: err.message || '获取数据失败',
          icon: 'none',
          duration: 2000
        });
      })
      .finally(() => {
        wx.hideLoading();
      });
  },

  // 更新图表数据
  updateChart: function(data) {
    if (!this.chart) return;
    
    const option = {
      xAxis: {
        data: data.dates || [],
        axisLabel: {
          formatter: function(value) {
            return value ? value.split(' ')[0] : '';
          }
        }
      },
      series: [
        {
          name: '体重',
          data: data.weight?.data || []
        },
        {
          name: 'BMI',
          data: data.bmi?.data || [],
          markLine: {
            data: [
              {
                yAxis: 18.5,
                lineStyle: { color: '#FFC107' },
                label: { formatter: 'BMI偏低' }
              },
              {
                yAxis: 24.9,
                lineStyle: { color: '#FFC107' },
                label: { formatter: 'BMI正常' }
              }
            ]
          }
        }
      ]
    };
    
    this.chart.setOption(option);
  },

  // 更新最新记录
  updateLatestRecord: function(data) {
    const weightData = data.weight?.data || [];
    const bmiData = data.bmi?.data || [];
    const dates = data.dates || [];
    
    if (weightData.length > 0 && bmiData.length > 0) {
      const lastIndex = dates.length - 1;
      const latestBMI = bmiData[lastIndex];
      const latestWeight = weightData[lastIndex];
      
      this.setData({
        latestBMI: latestBMI ? latestBMI.toFixed(1) : '--',
        latestWeight: latestWeight ? latestWeight.toFixed(1) : '--',
        latestHeight: data.height || '--',  // 直接使用当前数据中的身高
        latestTime: dates[lastIndex] || '--',
        bmiClass: this.getBMIClass(latestBMI),
        bmiDescription: this.getBMIDescription(latestBMI)
      });
    } else {
      // 如果没有数据，显示默认值
      this.setData({
        latestBMI: '--',
        latestWeight: '--',
        latestHeight: '--',
        latestTime: '--',
        bmiClass: '',
        bmiDescription: '暂无数据'
      });
    }
  },

  // 获取BMI状态类名
  getBMIClass: function(bmi) {
    if (bmi < 18.5) return 'bmi-warning';
    if (bmi > 24.9) return 'bmi-danger';
    return 'bmi-normal';
  },

  // 获取BMI状态描述
  getBMIDescription: function(bmi) {
    if (bmi < 18.5) return '体重偏低，建议适当增加营养摄入';
    if (bmi > 24.9) return '体重偏高，建议控制饮食并加强运动';
    return '体重正常，请继续保持';
  },

  // 下拉刷新
  onPullDownRefresh: function() {
    this.loadHealthData();
    wx.stopPullDownRefresh();
  },

  // 添加测试数据
  addTestRecord: function() {
    const userId = app.globalData.userInfo?.user_id || 1;
    const weight = Math.round((60 + Math.random() * 10) * 10) / 10; // 60-70kg之间的随机值
    const height = 170;
    const bmi = Math.round((weight / ((height / 100) * (height / 100))) * 10) / 10;

    const testData = {
      user_id: userId,
      weight: weight,
      height: height,
      bmi: bmi,
      measure_time: new Date().toISOString().split('.')[0].replace('T', ' ')  // 格式化为 'YYYY-MM-DD HH:mm:ss'
    };

    console.log('准备添加测试数据:', testData);

    wx.showLoading({
      title: '添加测试数据...'
    });

    api.health.addRecord(testData)
      .then(res => {
        console.log('添加测试数据成功:', res);
        wx.showToast({
          title: '添加成功',
          icon: 'success',
          duration: 1500
        });
        // 延迟一下再刷新数据，让后端有时间处理
        setTimeout(() => {
          this.loadHealthData();
        }, 1500);
      })
      .catch(err => {
        console.error('添加测试数据失败:', err);
        wx.showToast({
          title: err.message || '添加失败',
          icon: 'none',
          duration: 2000
        });
      })
      .finally(() => {
        wx.hideLoading();
      });
  },

  // 处理体重输入
  onWeightInput: function(e) {
    this.setData({
      inputWeight: e.detail.value
    });
  },

  // 处理身高输入
  onHeightInput: function(e) {
    this.setData({
      inputHeight: e.detail.value
    });
  },

  // 提交健康记录
  submitHealthRecord: function() {
    const weight = parseFloat(this.data.inputWeight);
    const height = parseFloat(this.data.inputHeight);

    // 数据验证
    if (!weight || !height) {
      wx.showToast({
        title: '请输入体重和身高',
        icon: 'none',
        duration: 2000
      });
      return;
    }

    // 体重范围验证 (20-200kg)
    if (weight < 20 || weight > 200) {
      wx.showToast({
        title: '体重范围应在20-200kg之间',
        icon: 'none',
        duration: 2000
      });
      return;
    }

    // 身高范围验证 (50-250cm)
    if (height < 50 || height > 250) {
      wx.showToast({
        title: '身高范围应在50-250cm之间',
        icon: 'none',
        duration: 2000
      });
      return;
    }

    // 计算BMI
    const heightInMeters = height / 100;
    const bmi = parseFloat((weight / (heightInMeters * heightInMeters)).toFixed(1));

    const userId = app.globalData.userInfo?.user_id || 1;
    const submitData = {
      user_id: userId,
      weight: weight,
      height: height,
      bmi: bmi,
      measure_time: new Date().toISOString().split('.')[0].replace('T', ' ')
    };

    console.log('准备提交的数据:', submitData);

    wx.showLoading({
      title: '提交中...'
    });

    api.health.addRecord(submitData)
      .then(res => {
        console.log('提交成功:', res);
        wx.showToast({
          title: '提交成功',
          icon: 'success',
          duration: 1500
        });
        // 清空输入框
        this.setData({
          inputWeight: '',
          inputHeight: ''
        });
        // 刷新数据
        setTimeout(() => {
          this.loadHealthData();
        }, 1500);
      })
      .catch(err => {
        console.error('提交失败:', err);
        wx.showToast({
          title: err.message || '提交失败',
          icon: 'none',
          duration: 2000
        });
      })
      .finally(() => {
        wx.hideLoading();
      });
  }
});