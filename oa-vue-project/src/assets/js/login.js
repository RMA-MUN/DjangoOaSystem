// 登录相关功能模块
import AuthHttp from '@/api/AuthHttp.js'

/**
 * 邮箱验证函数
 * @param {string} email - 要验证的邮箱地址
 * @returns {boolean} - 是否为有效的邮箱地址
 */
export function validateEmail(email) {
  const re = /^[\w-\.]+@([\w-]+\.)+[\w-]{2,4}$/
  return re.test(email)
}

/**
 * 密码验证函数
 * @param {string} password - 要验证的密码
 * @returns {object} - 包含验证结果和消息的对象
 */
export function validatePassword(password) {
  if (!password) {
    return { valid: false, message: '请输入密码' }
  }
  if (password.length < 6) {
    return { valid: false, message: '密码长度不能少于6个字符' }
  }
  return { valid: true }
}

/**
 * 模拟登录API调用
 * @param {string} email - 邮箱
 * @param {string} password - 密码
 * @returns {Promise} - 登录结果Promise
 */
export async function loginUser(email, password) {
  // 使用axios进行post请求发送到服务器
  try {
    // 调用AuthHttp的login方法
    const response = await AuthHttp.login(email, password)

    // 直接使用async/await方式处理响应
    console.log(response.data)

    // 返回标准化的响应格式
    return {
      success: true,
      data: response.data,
    }
  } catch (error) {
    console.error('登录失败:', error)

    // 返回标准化的错误格式
    return {
      success: false,
      error: error.response?.data?.message || '登录失败，请稍后重试',
    }
  }
}

/**
 * 保存登录状态到本地存储
 * @param {object} userData - 用户数据
 * @param {string} token - JWT token
 */
export function saveLoginState(userData, token) {
  localStorage.setItem('user', JSON.stringify(userData))
  localStorage.setItem('token', token)
}

/**
 * 清除登录状态
 */
export function clearLoginState() {
  localStorage.removeItem('user')
  localStorage.removeItem('token')
}

/**
 * 检查是否已登录
 * @returns {boolean} - 是否已登录
 */
export function isLoggedIn() {
  return !!localStorage.getItem('token')
}
