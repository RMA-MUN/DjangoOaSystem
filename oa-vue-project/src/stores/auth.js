import { ref, computed } from 'vue'
import { defineStore } from 'pinia'

const USER_KEY = 'USER_KEY'
const TOKEN_KEY = 'TOKEN_KEY'

export const useAuthStore = defineStore('auth', () => {
  // 定义两个私有状态变量
  let _user = ref({})
  let _token = ref({})

  // 计算属性 - 应该定义在setup函数的顶层，而不是函数内部
  let user = computed(() => {
    if (!_user.value || Object.keys(_user.value).length === 0) {
      // 如果内存里没有用户数据
      // 从localStorage里获取
      const userStr = localStorage.getItem(USER_KEY)
      if (userStr) {
        _user.value = JSON.parse(userStr)
      }
    }
    return _user.value
  })

  function clearUserToken() {
    // 清空内存里的用户数据
    _user.value = {}
    _token.value = ''

    // 从浏览器的localStorage(硬盘上)删除用户数据
    localStorage.removeItem(USER_KEY)
    localStorage.removeItem(TOKEN_KEY)
  }

  let token = computed(() => {
    if (!_token.value || Object.keys(_token.value).length === 0) {
      // 如果内存里没有token数据
      // 从localStorage里获取
      const tokenStr = localStorage.getItem(TOKEN_KEY)
      if (tokenStr) {
        _token.value = tokenStr
      }
    }
    return _token.value
  })

  function setUserToken(userData, token) {
    // 保存到对象里(内存里)
    _user.value = userData
    _token.value = token

    // 存储到浏览器的localStorage(硬盘上)
    localStorage.setItem(USER_KEY, JSON.stringify(userData))
    localStorage.setItem(TOKEN_KEY, token)
  }

  // 判断用户是否登录
  const isAuthenticated = computed(() => {
    // 使用token或user对象来判断是否登录
    if (token.value !== null && token.value !== '') {
      return true
    }
    if (user.value !== null && user.value !== '') {
      return true
    }
    return false
  })

  // 初始化 - 尝试从localStorage加载数据
  const init = () => {
    const userStr = localStorage.getItem(USER_KEY)
    if (userStr) {
      _user.value = JSON.parse(userStr)
    }
    const tokenStr = localStorage.getItem(TOKEN_KEY)
    if (tokenStr) {
      _token.value = tokenStr
    }
  }
  
  // 调用初始化函数
  init()

  return { user, token, setUserToken, isAuthenticated, clearUserToken }
})
