import http from './http'
import { ElMessage } from 'element-plus'

// 获取到所有部门的接口
const get_all_staff_department = () => {
  const path = 'staff/department/'
  return http.get(path)
}

// 添加员工的接口
const add_staff = (username, password, email, department) => {
  // 验证参数
  if (!username || !password || !email || !department) {
    console.error('缺少必要的员工信息参数')
    return Promise.reject(new Error('缺少必要的员工信息参数'))
  }

  // 构建请求数据对象
  const data = {
    username,
    password,
    email,
    department,
  }

  // 调试信息
  console.log('向API发送的数据:', data)

  // 发送请求
  return http.post('staff/staff/', data).catch((error) => {
    console.error('添加员工请求失败:', error)
    let errorMessage = '添加员工失败，请稍后重试'

    // 增强错误信息，方便调试和用户查看
    if (error.response) {
      console.error('响应状态:', error.response.status)
      console.error('响应数据:', error.response.data)

      // 根据不同的错误格式提取错误信息
      if (error.response.data && error.response.data.detail) {
        errorMessage = error.response.data.detail
      } else if (error.response.data && typeof error.response.data === 'object') {
        // 处理字段级别的错误，确保中文友好显示
        const fieldErrors = Object.entries(error.response.data)
          .map(([field, msgs]) => {
            // 字段名映射为中文
            const fieldNameMap = {
              username: '用户名',
              password: '密码',
              email: '邮箱',
              department: '部门',
            }
            const fieldName = fieldNameMap[field] || field
            return `${fieldName}: ${msgs.join(', ')}`
          })
          .join('; ')
        errorMessage = fieldErrors || errorMessage
      }
    }

    // 设置错误消息并返回拒绝的Promise
    error.message = errorMessage
    return Promise.reject(error)
  })
}

// 获取所有员工的接口
const get_all_staff = () => {
  const path = 'staff/user/'
  return http.get(path)
}

// 编辑员工信息的接口
const update_staff = (uuid, updateData) => {
  // 验证必要参数
  if (!uuid) {
    console.error('缺少员工ID参数')
    return Promise.reject(new Error('缺少员工ID参数'))
  }

  // 构建请求路径
  const path = `staff/staff/edit/${uuid}/`

  // 调试信息
  console.log('更新员工ID:', uuid)
  console.log('更新的数据:', updateData)

  // 发送PUT请求
  return http.put(path, updateData).catch((error) => {
    console.error('更新员工请求失败:', error)
    let errorMessage = '更新员工失败，请稍后重试'

    // 增强错误信息，方便调试和用户查看
    if (error.response) {
      console.error('响应状态:', error.response.status)
      console.error('响应数据:', error.response.data)

      // 根据不同的错误格式提取错误信息
      if (error.response.data && error.response.data.detail) {
        errorMessage = error.response.data.detail
      } else if (error.response.data && typeof error.response.data === 'object') {
        // 处理字段级别的错误，确保中文友好显示
        const fieldErrors = Object.entries(error.response.data)
          .map(([field, msgs]) => {
            // 字段名映射为中文
            const fieldNameMap = {
              username: '用户名',
              name: '姓名',
              email: '邮箱',
              department: '部门',
              status: '状态',
              isLeader: '是否领导',
            }
            const fieldName = fieldNameMap[field] || field
            return `${fieldName}: ${msgs.join(', ')}`
          })
          .join('; ')
        errorMessage = fieldErrors || errorMessage
      }
    }

    // 设置错误消息并返回拒绝的Promise
    error.message = errorMessage
    return Promise.reject(error)
  })
}

// 设置领导的接口
const set_leader = (department_id, new_leader_id) => {
  // 验证必要参数
  if (!department_id || !new_leader_id) {
    console.error('缺少部门ID或新领导ID参数')
    return Promise.reject(new Error('缺少部门ID或新领导ID参数'))
  }

  // 构建请求数据对象
  const data = {
    department_id,
    new_leader_uuid: new_leader_id,
  }

  // 调试信息
  console.log('向API发送的数据:', data)

  // 发送请求
  return http.post('officeAuth/department/update-leader/', data).catch((error) => {
    console.error('设置领导请求失败:', error)
    let errorMessage = '设置领导失败，请稍后重试'

    // 增强错误信息，方便调试和用户查看
    if (error.response) {
      console.error('响应状态:', error.response.status)
      console.error('响应数据:', error.response.data)

      // 根据不同的错误格式提取错误信息
      if (error.response.data && error.response.data.detail) {
        errorMessage = error.response.data.detail
      } else if (error.response.data && typeof error.response.data === 'object') {
        // 处理字段级别的错误，确保中文友好显示
        const fieldErrors = Object.entries(error.response.data)
          .map(([field, msgs]) => {
            // 字段名映射为中文
            const fieldNameMap = {
              department_id: '部门ID',
              new_leader_uuid: '新领导UUID',
            }
            const fieldName = fieldNameMap[field] || field
            return `${fieldName}: ${msgs.join(', ')}`
          })
          .join('; ')
        errorMessage = fieldErrors || errorMessage
      }
    }

    // 设置错误消息并返回拒绝的Promise
    error.message = errorMessage
    return Promise.reject(error)
  })
}

const download_staff_data = (uuids) => {
  // 构建URL，包含多个独立的uuid参数，格式为 /staff/download?uuid=uuid1&uuid=uuid2&uuid=uuid3
  const path = `staff/download?${uuids.map(id => `uuid=${encodeURIComponent(id)}`).join('&')}/`
  return http.download(path)
}

export default {
  get_all_staff_department,
  add_staff,
  get_all_staff,
  update_staff,
  set_leader,
  download_staff_data,
}
