import http from './http'

const publish_inform = (data) => {
  const path = '/inform/inform/'
  return http.post(path, data)
}

const get_inform_list = () => {
  const path = '/inform/inform/'
  return http.get(path)
}

const delete_inform = (id) => {
  const path = `/inform/inform/${id}/`
  return http.delete(path)
}

const get_inform_detail = (id) => {
  const path = `/inform/inform/${id}/`
  return http.get(path)
}

export default {
  publish_inform,
  get_inform_list,
  delete_inform,
  get_inform_detail,
}
