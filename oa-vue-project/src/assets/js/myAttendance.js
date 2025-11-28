import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import AttendanceHttp from '@/api/AttendanceHttp.js'

// 导出myAttendance组件的逻辑
export default function useMyAttendance() {
  // 考勤记录直接在页面显示，不需要弹窗控制变量
  const dialogFormVisible = ref(false)
  const loading = ref(false)
  const approverName = ref('')
  const tableData = ref([])
  // 分页相关状态
  const currentPage = ref(1)
  const pageSize = ref(10)
  const total = ref(0)
  const statusMap = {
    1: { label: '审核中', type: 'warning' },
    2: { label: '已审批', type: 'success' },
    3: { label: '已拒绝', type: 'danger' },
  }

  let attemdance_type = ref([])

  const form = reactive({
    title: '',
    attendance_type_id: '',
    request_content: '',
    value1: null, // 用于日期范围选择器
  })
  const formLabelWidth = '120px'

  const formRef = ref(null)

  // 加载考勤类型
  const loadAttendanceTypes = async () => {
    try {
      const response = await AttendanceHttp.getAttendanceTypes()
      attemdance_type.value = response.data
    } catch (error) {
      ElMessage.error('获取考勤类型失败')
      console.error('获取考勤类型失败:', error)
    }
  }

  // 加载当前用户的审批人
  const loadApprover = async () => {
    try {
      const response = await AttendanceHttp.getApprover()
      approverName.value = response.data.username
    } catch (error) {
      ElMessage.error('获取审批人信息失败')
      console.error('获取审批人信息失败:', error)
    }
  }

  // 加载用户自己的考勤记录（支持分页）
  const loadAttendanceRecords = async () => {
    loading.value = true
    try {
      const response = await AttendanceHttp.getAttendances(
        'requester',
        currentPage.value,
        pageSize.value,
      )
      console.log('API响应:', response.data)

      // 适配后端新的分页响应格式
      if (response.data && typeof response.data === 'object') {
        // 检查是否为新的分页格式
        if (
          'code' in response.data &&
          'results' in response.data &&
          'total_count' in response.data
        ) {
          console.log('[分页调试] 检测到新分页格式，code:', response.data.code)
          console.log('[分页调试] total_count:', response.data.total_count)
          console.log('[分页调试] current_page:', response.data.current_page)
          console.log('[分页调试] results数组长度:', response.data.results?.length)

          // 使用新格式的数据
          tableData.value = response.data.results || []
          total.value = Number(response.data.total_count || 0)

          // 可选：如果需要同步后端返回的页码信息
          // currentPage.value = Number(response.data.current_page || 1)
          // pageSize.value = Number(response.data.page_size || 10)
        } else if (response.data.results) {
          // 兼容旧格式
          tableData.value = response.data.results
          total.value = Number(response.data.count || response.data.total || 0)
        } else if (response.data.data) {
          tableData.value = response.data.data
          total.value = Number(response.data.total || 0)
        } else if (Array.isArray(response.data)) {
          tableData.value = response.data
          total.value = response.data.length
        } else {
          tableData.value = []
          total.value = 0
          console.warn('未知的响应格式:', response.data)
        }
      } else {
        tableData.value = []
        total.value = 0
        console.error('无效的响应数据:', response.data)
      }
    } catch (error) {
      console.error('获取考勤记录失败:', error)
      console.error('错误详情:', error.response?.data)
      ElMessage.error('获取考勤记录失败: ' + (error.message || '未知错误'))
    } finally {
      loading.value = false
    }
  }

  const changeFormVisible = () => {
    form.title = ''
    form.attendance_type_id = ''
    form.request_content = ''
    form.value1 = null
    dialogFormVisible.value = !dialogFormVisible.value
  }

  // 提交成功后重新加载考勤记录
  const submitForm = async () => {
    formRef.value.validate(async (valid) => {
      if (valid) {
        loading.value = true
        try {
          // 准备提交数据，确保日期格式正确
          const submitData = {
            title: form.title,
            attendance_type_id: form.attendance_type_id,
            request_content: form.request_content,
            start_time: form.value1[0],
            end_time: form.value1[1],
          }

          await AttendanceHttp.createAttendance(submitData)
          ElMessage.success('请假申请提交成功')
          dialogFormVisible.value = false
          // 重新加载考勤记录并重置到第一页
          currentPage.value = 1
          loadAttendanceRecords()
        } catch (error) {
          ElMessage.error('请假申请提交失败')
          console.error('提交失败:', error)
        } finally {
          loading.value = false
        }
      } else {
        return false
      }
    })
  }

  let rules = reactive({
    title: [{ required: true, message: '请输入请假标题', trigger: 'blur' }],
    attendance_type_id: [{ required: true, message: '请选择请假类型', trigger: 'change' }],
    request_content: [{ required: true, message: '请输入请假理由', trigger: 'blur' }],
  })

  // 处理页面大小变化
  const handleSizeChange = (size) => {
    pageSize.value = size
    currentPage.value = 1 // 重置为第一页
    loadAttendanceRecords()
  }

  // 处理当前页码变化
  const handleCurrentChange = (current) => {
    currentPage.value = current
    loadAttendanceRecords()
  }

  // 暴露需要在模板中使用的变量和方法
  return {
    dialogFormVisible,
    loading,
    approverName,
    tableData,
    attemdance_type,
    currentPage,
    pageSize,
    total,
    statusMap,
    form,
    formLabelWidth,
    formRef,
    rules,
    loadAttendanceTypes,
    loadApprover,
    loadAttendanceRecords,
    changeFormVisible,
    submitForm,
    handleSizeChange,
    handleCurrentChange,
  }
}
