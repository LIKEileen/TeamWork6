import request from '@/utils/request'
import { IS_DEV } from '@/config'
import { useUserStore } from '@/store/user'

export const updateUserInfo = (data) => {
  return request.post('/api/user/update', data)
}

export const changePasswordApi = (data) => {
  return request.post('/api/user/change-password', data)
}

// 上传头像
export const uploadAvatarApi = (data) => {
  return request.post('/api/user/avatar/upload', data, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}

// 使用 QQ 头像
export const useQQAvatarApi = (data) => {
  return request.post('/api/user/avatar/qq', data)
}

// 获取用户日程
export const getUserScheduleApi = (token) => {
  if (IS_DEV) {
    return new Promise((resolve) => {
      resolve({
        code: 1,
        message: 'success',
        data: [
          { id: 1, title: '数学课', day: '2025-04-26', start: '08:00', end: '09:30', color: '#F56C6C' },
          { id: 2, title: '干活', day: '2025-04-27', start: '10:00', end: '11:30', color: '#67C23A' },
          { id: 3, title: '干活', day: '2025-04-28', start: '13:00', end: '15:00' },
          { id: 4, title: '起义', day: '2025-04-29', start: '16:00', end: '18:00' },
          { id: 5, title: '上课', day: '2025-04-30', start: '08:00', end: '09:30' },
          { id: 6, title: '干活', day: '2025-05-06', start: '10:00', end: '11:30' },
          { id: 7, title: '干活', day: '2025-05-08', start: '13:00', end: '15:00' },
          { id: 8, title: '上课', day: '2025-05-16', start: '10:00', end: '18:00', color: '#86C23A' }
        ]
      })
    })
  } else {
    const userStore = useUserStore()
    // 从 Pinia store 中获取 token，这是最佳实践
    const token = userStore.token || localStorage.getItem('token')
    
    // 使用 axios 的通用请求方式来发送带 body 的 GET 请求
    return request({
      url: '/api/user/schedule',
      method: 'post',
      
      data: { // 将 token 放入 data 字段，axios 会将其作为请求体
        token: token
      },
      //skipAuth: true // ！！！告诉拦截器，跳过为这个请求添加 Authorization 头
    })
  }
}

// 添加单个事件
export const addEventApi = (eventData) => {
  if (IS_DEV) {
    return new Promise((resolve) => {
      console.log('模拟添加事件：', eventData)
      resolve({ code: 1, message: '添加成功', data: { id: Math.floor(Math.random() * 10000) } })
    })
  } else {
    return request({
      url: '/api/user/schedule/add',
      method: 'post',
      // headers: { Authorization: token },
      data: eventData
    })
  }
}

// 编辑事件
export const editEventApi = (token, eventData) => {
  if (IS_DEV) {
    return new Promise((resolve) => {
      console.log('模拟编辑事件：', eventData)
      resolve({ code: 1, message: '修改成功' })
    })
  } else {
    return request({
      url: '/api/user/schedule/edit',
      method: 'post',
      headers: { Authorization: token },
      data: eventData
    })
  }
}

// 删除事件
export const deleteEventApi = (token, eventId) => {
  if (IS_DEV) {
    return new Promise((resolve) => {
      console.log('模拟删除事件 ID：', eventId)
      resolve({ code: 1, message: '删除成功' })
    })
  } else {
    return request({
      url: '/api/user/schedule/delete',
      method: 'post',
      headers: { Authorization: token },
      data: { id: eventId }
    })
  }
}

// 导入 Excel
export const importScheduleExcelApi = (token, file) => {
  if (IS_DEV) {
    return new Promise((resolve) => {
      console.log('模拟导入 Excel：', file)
      resolve({ code: 1, message: '导入成功' })
    })
  } else {
    const formData = new FormData()
    formData.append('token', token); // ！！！将 token 也作为表单字段！！！
    formData.append('file', file);
    

    return request({
      url: '/api/user/schedule/import/excel',
      method: 'post',
      //headers: { Authorization: token },
      data: formData
    })
  }
}

// 导入学校课表
export const importScheduleSchoolApi = (token, school) => {
  if (IS_DEV) {
    return new Promise((resolve) => {
      console.log('模拟导入学校课表：', school)
      resolve({ code: 1, message: '导入成功' })
    })
  } else {
    return request({
      url: '/api/user/schedule/import/school',
      method: 'post',
      headers: { Authorization: token },
      data: { school }
    })
  }
}

// 添加长期事件
export const addRecurringEventApi = (token, recurringData) => {
  if (IS_DEV) {
    return new Promise((resolve) => {
      console.log('模拟添加长期事件：', recurringData)
      resolve({ code: 1, message: '添加成功' })
    })
  } else {
    return request({
      url: '/api/user/schedule/add/recurring',
      method: 'post',
      headers: { Authorization: token },
      data: recurringData
    })
  }
}

// 获取收到的组织邀请
export const getUserInvitationsApi = (token) => {
  if (IS_DEV) {
    return new Promise((resolve) => {
      resolve({
        code: 1,
        message: 'success',
        data: [
          {
            id: 'inv1',
            orgId: 'org1',
            orgName: '人工智能实验室',
            inviterName: '张三',
            inviterAvatar: '/assets/demo_icon.jpg',
            createdAt: '2025-01-15T10:30:00Z'
          },
          {
            id: 'inv2',
            orgId: 'org2',
            orgName: '数据科学研究组',
            inviterName: '李四',
            inviterAvatar: '/assets/demo_icon_.jpg',
            createdAt: '2025-01-14T14:20:00Z'
          }
        ]
      })
    })
  } else {
    const userStore = useUserStore()
    const token = userStore.token || localStorage.getItem('token')
    
    return request({
      url: '/api/user/invitations',
      method: 'post',
      data: { 
        token: token
      },
      headers: { // ！！！添加这一部分！！！
        'Content-Type': 'application/json'
      },
      skipAuth: true
    })
  }
}
