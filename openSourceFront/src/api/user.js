import request from '@/utils/request'
import { IS_DEV } from '@/config'

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
    return request({
      url: '/api/user/schedule',
      method: 'get',
      headers: { Authorization: token }
    })
  }
}

// 添加单个事件
export const addEventApi = (token, eventData) => {
  if (IS_DEV) {
    return new Promise((resolve) => {
      console.log('模拟添加事件：', eventData)
      resolve({ code: 1, message: '添加成功', data: { id: Math.floor(Math.random() * 10000) } })
    })
  } else {
    return request({
      url: '/api/user/schedule/add',
      method: 'post',
      headers: { Authorization: token },
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
    formData.append('file', file)
    return request({
      url: '/api/user/schedule/import/excel',
      method: 'post',
      headers: { Authorization: token },
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
