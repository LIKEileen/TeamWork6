import { defineStore } from 'pinia'

export const useUserStore = defineStore('user', {
  state: () => ({
    token: '',
    nickname: '',
    avatar: '',
    email: '',
    phone: '',
    role: '',
    orgs: [], // 用户所属组织列表
    theme: localStorage.getItem('theme') || 'light'
  }),
  actions: {
    setUserInfo(payload) {
      this.token = payload.token || ''
      this.nickname = payload.nickname || ''
      this.avatar = payload.avatar || ''
      this.email = payload.email || ''
      this.phone = payload.phone || ''
      this.role = payload.role || ''
      this.orgs = payload.orgs || []

      this.theme = localStorage.getItem('theme') || 'light'
      localStorage.setItem('token', this.token)
    },
    
    clearUser() {
      const theme = this.theme

      this.token = ''
      this.nickname = ''
      this.avatar = ''
      this.email = ''
      this.phone = ''
      this.role = ''
      this.orgs = []
      this.theme = theme

      localStorage.removeItem('token')
    }
  }
})