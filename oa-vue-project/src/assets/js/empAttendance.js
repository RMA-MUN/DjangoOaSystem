import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import AttendanceHttp from '@/api/AttendanceHttp.js'

// 导出empAttendance组件的逻辑
export default function useEmpAttendance() {
  // 响应式数据
  const tableData = ref([])
  const loading = ref(false)
  const dialogVisible = ref(false)
  const currentAttendance = ref(null)
  
  // 分页相关状态
  const currentPage = ref(1)
  const pageSize = ref(10)
  const total = ref(0)
  
  const statusMap = {
    1: { label: '审核中', type: 'warning' },
    2: { label: '已审批', type: 'success' },
    3: { label: '已拒绝', type: 'danger' }
  }

  const approveForm = reactive({
    status: 2, // 默认同意
    approval_content: ''
  })

  const formLabelWidth = '100px'

  // 加载待审批的考勤记录（支持分页）
  const loadAttendanceData = async () => {
    loading.value = true
    console.log(`[分页调试] 加载第${currentPage.value}页，每页${pageSize.value}条数据`)
    try {
      // 直接使用axios实例进行请求，以获取完整的请求信息
      const response = await AttendanceHttp.getAttendances('responser', currentPage.value, pageSize.value)
      console.log('[分页调试] API响应数据:', response.data)
      console.log('[分页调试] 请求URL:', response.config?.url || '未知')
      console.log('[分页调试] 请求参数:', response.config?.params || '未知')

      // 适配后端新的分页响应格式
      if (response.data && typeof response.data === 'object') {
        // 检查是否为新的分页格式
        if ('code' in response.data && 'results' in response.data && 'total_count' in response.data) {
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
          // 如果直接返回数组
          tableData.value = response.data
          total.value = response.data.length
        } else {
          // 默认处理
          tableData.value = []
          total.value = 0
          console.warn('[分页调试] 未知的响应格式:', response.data)
        }
      } else {
        tableData.value = []
        total.value = 0
        console.error('[分页调试] 无效的响应数据:', response.data)
      }

      console.log(`[分页调试] 最终设置的total值: ${total.value}`)
      console.log(`[分页调试] 当前页面数据条数: ${tableData.value.length}`)
      console.log(`[分页调试] 理论上应显示的总页数: ${Math.ceil(total.value / pageSize.value)}`)
    } catch (error) {
      console.error('获取考勤记录失败:', error)
      console.error('错误详情:', error.response?.data)
      ElMessage.error('获取考勤记录失败: ' + (error.message || '未知错误'))
    } finally {
      loading.value = false
    }
  }

  // 打开审批对话框
  const openApproveDialog = (row) => {
    currentAttendance.value = row
    approveForm.status = 2
    approveForm.approval_content = ''
    dialogVisible.value = true
  }

  // 提交审批
  const submitApproval = async () => {
    if (!currentAttendance.value) return

    try {
      await AttendanceHttp.approveAttendance(currentAttendance.value.id, {
        status: approveForm.status,
        approval_content: approveForm.approval_content
      })

      ElMessage.success('审批成功')
      dialogVisible.value = false
      // 重新加载数据并重置到第一页
      currentPage.value = 1
      loadAttendanceData()
    } catch (error) {
      // 检查是否为权限不足错误，根据后端返回的错误信息进行判断
      const errorMessage = error.response?.data?.detail || error.message || '审批失败'
      // 如果错误信息包含权限相关关键词，显示权限不足提示
      if (errorMessage.includes('权限') || errorMessage.includes('permission') || error.response?.status === 403) {
        ElMessage.error('权限不足，无法进行审批操作')
      } else {
        ElMessage.error(errorMessage)
      }
      console.error('审批失败:', error)
    }
  }

  // 处理页面大小变化
  const handleSizeChange = (size) => {
    console.log(`[分页调试] 页面大小变更为: ${size}`)
    pageSize.value = size
    currentPage.value = 1 // 重置为第一页
    loadAttendanceData()
  }

  // 处理当前页码变化
  const handleCurrentChange = (current) => {
    console.log(`[分页调试] 页码变更为: ${current}`)
    currentPage.value = current
    loadAttendanceData()
  }

  // 组件挂载时加载数据
  const initData = () => {
    loadAttendanceData()
  }

  // 暴露需要在模板中使用的变量和方法
  return {
    tableData,
    loading,
    dialogVisible,
    currentAttendance,
    currentPage,
    pageSize,
    total,
    statusMap,
    approveForm,
    formLabelWidth,
    openApproveDialog,
    submitApproval,
    handleSizeChange,
    handleCurrentChange,
    initData
  }
}