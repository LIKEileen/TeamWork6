import request from '@/utils/request'

// 获取大模型配置
export const getLLMConfigApi = () => {
  return request.get('/api/llm/config')
}

// 更新大模型配置
export const saveLLMConfigApi = (data) => {
  return request.post('/api/llm/config/update', data)
}