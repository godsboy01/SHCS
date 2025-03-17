const { api } = require('../../utils/api')

Page({
  data: {
    isLoading: true,    // 页面加载状态
    isSaving: false,    // 保存地址状态
    isAdding: false,    // 添加成员状态
    address: '',
    familyMembers: [],
    showAddModal: false,
    newMember: {
      phone: '',
      role: 'cared'  // 默认为被监护人
    }
  },

  onLoad() {
    this.fetchFamilyInfo()
  },

  // 下拉刷新
  async onPullDownRefresh() {
    await this.fetchFamilyInfo()
    wx.stopPullDownRefresh()
  },

  // 获取家庭信息
  async fetchFamilyInfo() {
    this.setData({ isLoading: true })
    try {
      const res = await api.family.getFamilyInfo()
      if (res) {
        this.setData({
          address: res.address || '',
          familyMembers: res.members || []
        })
      }
    } catch (err) {
      console.error('获取家庭信息失败:', err)
      wx.showToast({
        title: '获取信息失败',
        icon: 'none'
      })
    } finally {
      this.setData({ isLoading: false })
    }
  },

  // 处理地址输入
  handleAddressInput(e) {
    this.setData({
      address: e.detail.value
    })
  },

  // 保存地址
  async saveAddress() {
    const { address } = this.data
    if (!address.trim()) {
      wx.showToast({
        title: '请输入地址',
        icon: 'none'
      })
      return
    }

    this.setData({ isSaving: true })

    try {
      await api.family.updateAddress({
        address: address.trim()
      })
      
      wx.showToast({
        title: '保存成功',
        icon: 'success'
      })
    } catch (err) {
      console.error('保存地址失败:', err)
      wx.showToast({
        title: '保存失败',
        icon: 'none'
      })
    } finally {
      this.setData({ isSaving: false })
    }
  },

  // 显示添加成员弹窗
  showAddMember() {
    this.setData({
      showAddModal: true,
      newMember: {
        phone: '',
        role: 'cared'  // 默认为被监护人
      }
    })
  },

  // 隐藏添加成员弹窗
  hideAddMember() {
    this.setData({
      showAddModal: false
    })
  },

  // 阻止冒泡
  stopPropagation() {
    return
  },

  // 处理弹窗输入
  handleModalInput(e) {
    const { field } = e.currentTarget.dataset
    const { value } = e.detail
    
    this.setData({
      [`newMember.${field}`]: value
    })
  },

  // 处理角色选择
  handleRoleChange(e) {
    this.setData({
      'newMember.role': 'cared'  // 统一设置为被监护人
    })
  },

  // 验证手机号
  validatePhone(phone) {
    const phoneReg = /^1[3-9]\d{9}$/
    return phoneReg.test(phone)
  },

  // 添加成员
  async addMember() {
    const { phone } = this.data.newMember
    
    if (!phone || !this.validatePhone(phone)) {
      wx.showToast({
        title: '请输入正确的手机号',
        icon: 'none'
      })
      return
    }

    // 添加确认弹窗
    wx.showModal({
      title: '添加确认',
      content: '确定要添加该用户为家庭成员吗？',
      success: async (res) => {
        if (res.confirm) {
          this.setData({ isAdding: true })

          try {
            await api.family.addMember({
              phone,
              role: 'user'
            })
            
            await this.fetchFamilyInfo()
            
            wx.showToast({
              title: '添加成功',
              icon: 'success'
            })
            
            this.hideAddMember()
          } catch (err) {
            console.error('添加成员失败:', err)
            if (err.data && err.data.message) {
              if (err.data.need_force_transfer) {
                wx.showModal({
                  title: '用户已在其他家庭',
                  content: '该用户已经是其他家庭的成员，是否将其转移到您的家庭？转移后将自动退出原家庭。',
                  confirmText: '确认转移',
                  cancelText: '取消',
                  success: async (modalRes) => {
                    if (modalRes.confirm) {
                      try {
                        await api.family.transferMember({
                          phone
                        })
                        
                        await this.fetchFamilyInfo()
                        
                        wx.showToast({
                          title: '转移成功',
                          icon: 'success'
                        })
                        
                        this.hideAddMember()
                      } catch (transferErr) {
                        wx.showToast({
                          title: transferErr.data?.message || '转移失败',
                          icon: 'none',
                          duration: 2000
                        })
                      }
                    }
                  }
                })
                return
              }
              
              let errorMsg = '添加失败'
              switch(err.data.message) {
                case '该用户未注册':
                  errorMsg = '该用户还未注册，请先邀请注册'
                  break
                default:
                  errorMsg = err.data.message
              }
              wx.showToast({
                title: errorMsg,
                icon: 'none',
                duration: 2000
              })
            }
          } finally {
            this.setData({ isAdding: false })
          }
        }
      }
    })
  },

  // 删除成员
  async deleteMember(e) {
    const { id } = e.currentTarget.dataset
    
    wx.showModal({
      title: '删除确认',
      content: '确定要删除该成员吗？删除后无法恢复',
      confirmText: '删除',
      confirmColor: '#ff3b30',
      success: async (res) => {
        if (res.confirm) {
          wx.showLoading({
            title: '删除中...',
            mask: true
          })

          try {
            await api.family.deleteMember({
              userId: id
            })
            
            // 刷新家庭成员列表
            await this.fetchFamilyInfo()
            
            wx.showToast({
              title: '删除成功',
              icon: 'success'
            })
          } catch (err) {
            console.error('删除成员失败:', err)
            wx.showToast({
              title: '删除失败',
              icon: 'none'
            })
          } finally {
            wx.hideLoading()
          }
        }
      }
    })
  }
}) 