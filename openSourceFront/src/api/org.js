import request from '@/utils/request'
import { IS_DEV } from '@/config'

export const getUserOrgs = () => {
  if (IS_DEV) {
    // 模拟数据
    return new Promise((resolve) => {
      resolve({
        "code": 1,
        "message": "success",
        "data": [
          {
            "id": 1,
            "name": "开发组",
            "members": 12
          },
          {
            "id": 2,
            "name": "唐高祖",
            "members": 8
          },
          {
            "id": 3,
            "name": "电阻",
            "members": 8888888
          }
        ]
      })
    })
  }
  return request.get('/api/user/orglist')
}

export const getOrgHeatmap = (orgId) => {
  if (IS_DEV) {
    // 模拟数据
    if (orgId === 1) {
      const rows = 24
      const cols = 30
      const result = []
      for (let i = 0; i < rows; i++) {
        result.push(Array.from({ length: cols }, () => Math.floor(Math.random() * 301)))
      }
      return new Promise((resolve) => {
        resolve({
          code: 1,
          message: '模拟热力图数据',
          data: {
            heatmap: result
          }
        })
      })
    }
    return new Promise((resolve) => {
      resolve({
        code: 1,
        message: '模拟热力图数据',
        data: {
          heatmap: [
            ...Array(4).fill(Array(30).fill(0)),
            [0, 0, 0, 0, 255, 80, 80, 255, 255, 48, 48, 48, 48, 48, 255, 255, 255, 255, 80, 80, 0, 0, 0, 144, 144, 144, 144, 0, 0, 0], 
            [0, 0, 0, 0, 255, 80, 80, 48, 5, 5, 5, 5, 5, 5, 5, 5, 80, 80, 80, 80, 0, 0, 144, 144, 144, 144, 144, 144, 0, 0], 
            [0, 0, 0, 0, 80, 80, 5, 5, 5, 5, 5, 5, 48, 48, 5, 5, 5, 5, 80, 80, 0, 0, 144, 144, 0, 0, 144, 144, 0, 0], 
            [0, 0, 0, 0, 80, 5, 5, 5, 48, 48, 48, 48, 48, 48, 48, 5, 5, 5, 5, 80, 0, 0, 0, 0, 0, 144, 144, 144, 0, 0], 
            [0, 0, 0, 0, 5, 5, 48, 210, 210, 210, 210, 210, 210, 210, 210, 48, 48, 48, 5, 48, 0, 0, 0, 0, 144, 144, 144, 0, 0, 0], 
            [0, 0, 0, 0, 5, 48, 210, 48, 48, 48, 48, 48, 48, 48, 48, 48, 210, 48, 48, 5, 0, 0, 0, 0, 144, 144, 0, 0, 0, 0], 
            [0, 0, 0, 0, 48, 210, 48, 14, 48, 14, 14, 48, 48, 48, 14, 14, 68, 210, 48, 48, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
            [0, 0, 0, 0, 210, 14, 14, 79, 14, 14, 14, 14, 48, 14, 14, 14, 14, 167, 210, 48, 0, 0, 0, 0, 144, 144, 0, 0, 0, 0], 
            [0, 0, 0, 0, 48, 14, 14, 28, 14, 14, 14, 48, 48, 14, 14, 14, 14, 167, 167, 210, 0, 0, 0, 0, 144, 144, 0, 0, 0, 0], 
            [0, 0, 0, 0, 48, 29, 79, 28, 48, 14, 29, 48, 28, 48, 14, 14, 29, 210, 210, 210, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
            [0, 0, 0, 0, 29, 79, 28, 136, 6, 29, 29, 6, 136, 28, 48, 29, 29, 48, 210, 210, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
            [0, 0, 0, 0, 48, 79, 6, 136, 6, 6, 6, 6, 136, 6, 48, 48, 68, 210, 48, 210, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
            [0, 0, 0, 0, 48, 79, 6, 136, 6, 6, 6, 6, 136, 6, 48, 48, 68, 48, 48, 48, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
            [0, 0, 0, 0, 48, 79, 6, 6, 6, 6, 6, 6, 6, 6, 48, 48, 68, 48, 48, 48, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
            [0, 0, 0, 0, 48, 79, 96, 6, 6, 6, 6, 6, 6, 28, 48, 48, 79, 119, 48, 255, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
            [0, 0, 0, 0, 255, 48, 79, 96, 119, 119, 207, 207, 58, 48, 48, 109, 119, 96, 96, 48, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
            ...Array(3).fill(Array(30).fill(0))
          ]
        }
      })
    })
  }
  return request.get(`/api/heatmap/${orgId}`)
}

// 新增：设置管理员
export const setOrgAdmins = (orgId, adminIds) => {
  return request.post(`/api/org/${orgId}/admins`, { adminIds })
}

// 新增：搜索用户
export const searchUsers = (query) => {
  return request.get('/api/users/search', { params: { q: query } })
}

// 新增：邀请成员
export const inviteOrgMember = (orgId, userId) => {
  return request.post(`/api/org/${orgId}/invite`, { userId })
}

// 新增：搜索组织
export const searchOrg = (orgId) => {
  return request.get(`/api/org/search`, { params: { id: orgId } })
}

// 新增：申请加入组织
export const applyJoinOrg = (orgId, message) => {
  return request.post(`/api/org/join-request`, { orgId, message })
}

// 新增：获取收到的邀请
export const getPendingInvitations = () => {
  return request.get('/api/user/invitations')
}

// 新增：接受组织邀请
export const acceptInvitation = (invitationId) => {
  return request.post(`/api/invitation/${invitationId}/accept`)
}

// 新增：拒绝组织邀请
export const rejectInvitation = (invitationId) => {
  return request.post(`/api/invitation/${invitationId}/reject`)
}