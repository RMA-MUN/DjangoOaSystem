import http from './http.js'

const login = (email, password) => {
  // 这里的login函数是AuthHttp的login方法
  // 完整的url是http://127.0.0.1:8000/officeAuth/login/
  return http.post('/officeAuth/login/', {
    email,
    password,
  })
}

const resetPassword = (oldPassword, newPassword, confirmPassword) => {
  // 这里的resetPassword函数是AuthHttp的resetPassword方法
  // 完整的url是http://127.0.0.1:8000/officeAuth/reset-password/
  
  // 构建请求数据，可能后端期望不同的参数名
  const requestData = {
    old_password: oldPassword,
    new_password: newPassword,
    confirm_password: confirmPassword
  }
  
  console.log('密码重置请求数据:', requestData)
  
  return http.post('/officeAuth/reset-password/', requestData)
}

export default {
  login,
  resetPassword,
}
