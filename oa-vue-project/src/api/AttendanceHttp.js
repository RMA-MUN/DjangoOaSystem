import http from './http.js'

// 获取考勤类型列表
const getAttendanceTypes = () => {
  return http.get('/Attendance/attendance-type/')
}

// 获取考勤列表（支持分页）
const getAttendances = (who = '', page = 1, pageSize = 10) => {
  return http.get('/Attendance/attendance/', {
    params: {
      who,
      page,
      page_size: pageSize
    }
  })
}

// 创建新的考勤申请
const createAttendance = (data) => {
  return http.post('/Attendance/attendance/', data)
}

// 审批考勤申请
const approveAttendance = (id, data) => {
  // 使用PUT方法更新考勤状态，与后端UpdateModelMixin对应
  return http.instance.put(`/Attendance/attendance/${id}/`, data)
}

// 获取当前用户的审批人
const getApprover = () => {
  return http.get('/Attendance/attendance-responser/')
}

export default {
  getAttendanceTypes,
  getAttendances,
  createAttendance,
  approveAttendance,
  getApprover
}