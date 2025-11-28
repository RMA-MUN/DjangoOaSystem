import { ref, reactive } from 'vue'
import { ElMessage, ElTag } from 'element-plus'
import informHttp from '@/api/informHttp.js'

// 格式化时间的函数
const formatTime = (time) => {
  if (!time) return '-';
  try {
    const date = new Date(time);
    if (isNaN(date.getTime())) return '-';
    return date.toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    });
  } catch (e) {
    return '-';
  }
};

let informDetail = reactive({
  title: '',
  department: '',
  content: '',
  create_time: '',
  author: {
    username: '',
    department: '',
  },
  departments: []
})

// 初始化通知详情的函数
const initInformDetail = async (id) => {
  try {
    let data = await informHttp.get_inform_detail(id)
    Object.assign(informDetail, data.data)
  } catch (error) {
    console.error('获取通知详情失败:', error)
    ElMessage.error(error.message || '获取通知详情失败')
  }
};

export { formatTime, informDetail, initInformDetail };