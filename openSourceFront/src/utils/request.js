import axios from 'axios'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/store/user'
import { IS_DEV } from '@/config'

import router from '@/router'

const service = axios.create({
  baseURL: '/',
  timeout: 10000
})
const whiteList = ['/api/login', '/api/register', '/api/bind']

// 请求拦截器
service.interceptors.request.use(
  (config) => {
    // 如果请求配置中 skipAuth 为 true，则直接返回，不添加 token
    if (config.skipAuth) {
      return config;
    }
    
    const userStore = useUserStore()
    const token = userStore.token

    // 如果是需要 token 的请求且 token 为空，则退出登录
    if (!token) {
      // console.log(config.url)
      if (whiteList.includes(config.url)) {
        return config
      }
      ElMessage.error('登录已过期，请重新登录')
      // userStore.logout() // 清除 token 与用户信息
      router.push('/login')
      return Promise.reject(new Error('Token missing'))
    }
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
      //config.headers[`Content-Type`] = `application/json`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
service.interceptors.response.use(
  (response) => {
    if (IS_DEV) {
      // 开发模式下，直接返回响应数据
      return response.data
    }
    const res = response
    const r=response.data

    //console.log('响应数据:', r)
    if (r.code !== 1) {
      console.log(r)
      ElMessage.error(r.message || '请求失败')
      return Promise.reject(new Error(res.data.message || 'Error'))
    }
    return res
  },
  (error) => {
    const userStore = useUserStore()

    if (error.response && (error.response.status === 401 || error.response.status === 403)) {
      ElMessage.error('登录已过期，请重新登录')
      userStore.logout()
      router.push('/login')
    }

    return Promise.reject(error)
    //console.error('请求错误:', error)
    ElMessage.error(error.response.data.message || '网络错误')
    return Promise.reject(error)
  }
)

export default service
