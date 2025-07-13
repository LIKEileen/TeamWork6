import request from '@/utils/request'

export const login = (payload) => {
  return request.post('/api/login', payload)
}

export const register = (payload) => {
  return request.post('/api/register', payload)
}

export const bindPhone = (payload) => {
  return request.post('/api/bind', payload)
}

export const logout = (payload) => {
  return request.post('/api/logout', payload)
}

export const sendVerificationCodeApi = (data) => {
  return request({
    method: 'post',
    url: '/api/send-verification-code',  // 后端的发送验证码接口路径
    data,
  })
}

// 重置密码接口
export const resetPasswordApi = (data) => {
  return request({
    method: 'post',
    url: '/api/reset-password',  // 后端的重置密码接口路径
    data,
  })
}
