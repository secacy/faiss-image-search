import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useAuthStore = defineStore('auth', () => {
  // 状态
  const isAuthenticated = ref(false)
  const user = ref(null)
  const token = ref(localStorage.getItem('token') || '')

  // 初始化
  if (token.value) {
    isAuthenticated.value = true
    // 这里可以验证token的有效性
  }

  // 登录
  const login = (userInfo, tokenValue) => {
    user.value = userInfo
    token.value = tokenValue
    isAuthenticated.value = true
    localStorage.setItem('token', tokenValue)
    localStorage.setItem('user', JSON.stringify(userInfo))
  }

  // 登出
  const logout = () => {
    user.value = null
    token.value = ''
    isAuthenticated.value = false
    localStorage.removeItem('token')
    localStorage.removeItem('user')
  }

  return {
    isAuthenticated,
    user,
    token,
    login,
    logout
  }
}) 