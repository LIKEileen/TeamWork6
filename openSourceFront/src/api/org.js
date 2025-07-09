import request from '@/utils/request'
import { IS_DEV } from '@/config'

// 获取用户的组织列表
export const getUserOrgs = (token) => {
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
  return request.post('/api/user/orglist', { token })
}

// 获取组织热力图数据
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

// 获取组织详情
export const getOrgDetail = (orgId) => {
  if (IS_DEV) {
    // 模拟数据
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve({
          "code": 1,
          "message": "success",
          "data": {
            "id": orgId,
            "name": "数据科学研究组",
            "members": [
              { "id": "u1", "name": "张教授", "role": "creator", "avatarUrl": null },
              { "id": "u2", "name": "李研究员", "role": "admin", "avatarUrl": null },
              { "id": "u3", "name": "王博士", "role": "admin", "avatarUrl": null },
              { "id": "u4", "name": "陈同学", "role": "", "avatarUrl": null },
              { "id": "u5", "name": "林同学", "role": "", "avatarUrl": null }
            ]
          }
        })
      }, 300)
    })
  }
  return request.get(`/api/org/${orgId}`)
}

// 创建组织
export const createOrg = (name, members = []) => {
  if (IS_DEV) {
    // 模拟数据
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve({
          "code": 1,
          "message": "组织创建成功",
          "data": {
            "id": "org" + Date.now(),
            "name": name,
            "members": [
              { "id": "u1", "name": "当前用户", "role": "creator", "avatarUrl": null },
              ...members.map(id => ({ "id": id, "name": `用户${id}`, "role": "", "avatarUrl": null }))
            ]
          }
        })
      }, 500)
    })
  }
  return request.post('/api/org', { name, members })
}

// 更新组织名称
export const updateOrgName = (orgId, name) => {
  if (IS_DEV) {
    // 模拟数据
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve({
          "code": 1,
          "message": "组织名称已更新",
          "success": true
        })
      }, 300)
    })
  }
  return request.put(`/api/org/${orgId}`, { name })
}

// 删除组织
export const deleteOrg = (orgId) => {
  if (IS_DEV) {
    // 模拟数据
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve({
          "code": 1,
          "message": "组织已删除",
          "success": true
        })
      }, 500)
    })
  }
  return request.delete(`/api/org/${orgId}`)
}

// 设置管理员
export const setOrgAdmins = (orgId, adminIds) => {
  if (IS_DEV) {
    // 模拟数据
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve({
          "code": 1,
          "message": "管理员设置成功",
          "success": true
        })
      }, 400)
    })
  }
  return request.post(`/api/org/${orgId}/admins`, { adminIds })
}

// 搜索用户
export const searchUsers = (query) => {
  if (IS_DEV) {
    // 模拟数据
    return new Promise((resolve) => {
      setTimeout(() => {
        const mockUsers = [
          { "id": "u20", "name": "张三", "avatarUrl": null },
          { "id": "u21", "name": "李四", "avatarUrl": null },
          { "id": "u22", "name": "王五", "avatarUrl": null },
          { "id": "u23", "name": "赵六", "avatarUrl": null },
          { "id": "u24", "name": "孙七", "avatarUrl": null }
        ]
        
        const results = mockUsers.filter(user => 
          user.name.includes(query) || user.id.includes(query)
        )
        
        resolve({
          "code": 1,
          "message": "success",
          "data": results
        })
      }, 300)
    })
  }
  return request.get('/api/users/search', { params: { q: query } })
}

// 邀请成员
export const inviteOrgMember = (orgId, userId) => {
  if (IS_DEV) {
    // 模拟数据
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve({
          "code": 1,
          "message": "邀请已发送",
          "success": true
        })
      }, 400)
    })
  }
  return request.post(`/api/org/${orgId}/invite`, { userId })
}

// 搜索组织
export const searchOrg = (orgId) => {
  if (IS_DEV) {
    // 模拟数据
    return new Promise((resolve) => {
      setTimeout(() => {
        // 模拟根据ID查找组织
        const mockOrgs = [
          {
            "id": "org1",
            "name": "数据科学研究组",
            "members": [
              { "id": "u1", "name": "张教授", "role": "creator", "avatarUrl": null },
              { "id": "u2", "name": "李研究员", "role": "admin", "avatarUrl": null }
            ]
          },
          {
            "id": "org2",
            "name": "软件开发小组",
            "members": [
              { "id": "u6", "name": "刘组长", "role": "creator", "avatarUrl": null },
              { "id": "u7", "name": "杨开发", "role": "admin", "avatarUrl": null }
            ]
          }
        ]
        
        const foundOrg = mockOrgs.find(org => org.id === orgId)
        
        resolve({
          "code": 1,
          "message": "success",
          "data": foundOrg || null
        })
      }, 300)
    })
  }
  return request.get(`/api/org/search`, { params: { id: orgId } })
}

// 申请加入组织
export const applyJoinOrg = (orgId, message) => {
  if (IS_DEV) {
    // 模拟数据
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve({
          "code": 1,
          "message": "申请已提交，等待管理员审核",
          "success": true
        })
      }, 500)
    })
  }
  return request.post(`/api/org/join-request`, { orgId, message })
}

// 获取收到的邀请
// export const getPendingInvitations = () => {
//   if (IS_DEV) {
//     // 模拟数据
//     return new Promise((resolve) => {
//       setTimeout(() => {
//         resolve({
//           "code": 1,
//           "message": "success",
//           "data": [
//             {
//               "id": "inv1",
//               "orgId": "org4",
//               "orgName": "人工智能实验室",
//               "inviter": "黄教授",
//               "inviteTime": "2023-06-15T10:30:00Z",
//               "message": "我们正在组建AI研究团队，希望你能加入我们的组织"
//             },
//             {
//               "id": "inv2",
//               "orgId": "org5",
//               "orgName": "数据分析小组",
//               "inviter": "赵分析师",
//               "inviteTime": "2023-06-15T15:45:00Z",
//               "message": ""
//             },
//             {
//               "id": "inv3",
//               "orgId": "org6",
//               "orgName": "前端开发团队",
//               "inviter": "李工程师",
//               "inviteTime": "2023-06-16T12:15:00Z",
//               "message": "看到你有Vue的经验，想邀请你加入我们的前端团队"
//             }
//           ]
//         })
//       }, 300)
//     })
//   }
//   return request.get('/api/user/invitations')
// }

// 接受组织邀请
export const acceptInvitation = (invitationId) => {
  if (IS_DEV) {
    // 模拟数据
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve({
          "code": 1,
          "message": "已加入组织",
          "success": true
        })
      }, 400)
    })
  }
  return request.post(`/api/invitation/${invitationId}/accept`)
}

// 拒绝组织邀请
export const rejectInvitation = (invitationId) => {
  if (IS_DEV) {
    // 模拟数据
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve({
          "code": 1,
          "message": "已拒绝邀请",
          "success": true
        })
      }, 300)
    })
  }
  return request.post(`/api/invitation/${invitationId}/reject`)
}
