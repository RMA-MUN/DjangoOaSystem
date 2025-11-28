import http from './http'

const get_department_staff_count = () => {
  return http.get('home/department/staff/count/')
}

const get_latest_inform = () => {
  return http.get('home/latest/inform/')
}

const get_latest_attendance = () => {
  return http.get('home/latest/attendance/')
}

export { get_department_staff_count, get_latest_inform, get_latest_attendance }
