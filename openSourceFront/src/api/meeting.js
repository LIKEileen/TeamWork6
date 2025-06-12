import request from '@/utils/request'
import { IS_DEV } from '@/config'

// 获取组织成员
export const getOrgMembersApi = (orgId) => {
  if (IS_DEV) {
    return new Promise((resolve) => {
      resolve({
        code: 1,
        message: 'success',
        data: [
          { uid: 101, name: '张三' },
          { uid: 102, name: '李四' },
          { uid: 103, name: '王五' },
          { uid: 104, name: '赵六' }
        ]
      })
    })
  } else {
    return request({
      url: `/api/organization/${orgId}/members`,
      method: 'get'
    })
  }
}

// 获取组织热力图（用于会议时间选择）
export const getOrgHeatmapApi = ({ orgId, startDate, endDate, members }) => {
  if (IS_DEV) {
    const heatmap = Array.from({ length: 24 }, () => Array(7).fill(0).map(() => Math.floor(Math.random() * members.length)))
    return new Promise((resolve) => {
      resolve({
        code: 1,
        message: 'success',
        data: { heatmap }
      })
    })
  } else {
    return request({
      url: `/api/heatmap/${orgId}`,
      method: 'post',
      data: { startDate, endDate, members }
    })
  }
}

// 创建会议
export const createMeetingApi = (meetingData) => {
  if (IS_DEV) {
    return new Promise((resolve) => {
      console.log('模拟创建会议：', meetingData)
      resolve({
        code: 1,
        message: '会议创建成功'
      })
    })
  } else {
    return request({
      url: '/api/meeting/create',
      method: 'post',
      data: meetingData
    })
  }
}
