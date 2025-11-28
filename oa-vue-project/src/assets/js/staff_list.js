import { ref, computed, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/auth.js'
import staffHttp from '@/api/staffHttp'

export function useStaffListLogic() {
  // 创建authStore实例
  const authStore = useAuthStore()

  // 使用对象存储每个部门的表格引用
  const staffTables = ref({})

  // 检查当前用户是否是董事会领导
  const checkIfBoardLeader = () => {
    try {
      // 获取当前登录用户信息
      const user = authStore.user
      if (!user || !user.uuid) {
        console.log('调试 - 未找到用户信息')
        return false
      }

      // 从rawStaffData中查找董事会部门的领导UUID
      const boardLeaders = rawStaffData.value.filter(
        (staff) => staff.department === '董事会' && staff.isLeader === true,
      )

      console.log('调试 - 用户信息:', user)
      console.log('调试 - 用户UUID:', user.uuid)
      console.log('调试 - 董事会领导列表:', boardLeaders)

      // 检查用户是否是董事会领导（通过UUID匹配）
      const isBoardLeader = boardLeaders.some((leader) => leader.uuid === user.uuid)
      console.log('调试 - 是否为董事会领导:', isBoardLeader)

      return isBoardLeader
    } catch (error) {
      console.error('调试 - 检查董事会领导权限时出错:', error)
      return false
    }
  }

  // 响应式状态
  const rawStaffData = ref([])
  const departments = ref({}) // 使用对象存储部门名称到ID的映射
  const departmentOptions = ref([]) // 存储部门数组格式，用于select选项
  const loading = ref(false)
  const error = ref('')

  // 定义每个status对应的状态
  const statusMap = {
    0: '未激活',
    1: '在职',
    2: '离职',
  }

  // 编辑对话框相关状态
  const dialogVisible = ref(false)
  const editingStaff = ref(null)
  const editForm = reactive({
    checked: false,
    uuid: '',
    name: '',
    email: '',
    department: '', // 部门名称
    department_id: '', // 部门ID
    status: '',
    isLeader: false,
  })

  // 存储后端返回的所有用户信息
  const allStaffData = ref([])

  // 日期格式化函数
  const formatDate = (dateString) => {
    if (!dateString) return ''
    try {
      const date = new Date(dateString)
      return date.toLocaleDateString('zh-CN')
    } catch (e) {
      console.error('日期格式化错误:', e)
      return dateString
    }
  }

  // 检查用户是否有权限访问员工管理模块
  const checkStaffPermission = () => {
    const authStore = useAuthStore()
    const user = authStore.user

    if (!user) {
      ElMessage.warning('请先登录')
      return false
    }

    // 检查是否是超级用户或部门领导
    const userData = typeof user === 'string' ? JSON.parse(user) : user
    const isSuperuser = userData.is_superuser || false
    const isLeader = userData.is_leader || false

    if (!isSuperuser && !isLeader) {
      ElMessage.warning('您没有权限访问员工管理模块')
      return false
    }

    return true
  }

  // 将后端数据转换为前端需要的数据格式的箭头函数
  const transformStaffData = (backendData) => {
    const result = []
    let idCounter = 1

    // 确保backendData是对象
    if (!backendData || typeof backendData !== 'object' || Array.isArray(backendData)) {
      console.error('无效的后端数据格式:', backendData)
      return result
    }

    // 遍历后端数据中的每个部门
    Object.entries(backendData).forEach(([departmentName, departmentData]) => {
      // 安全检查
      if (!departmentData || typeof departmentData !== 'object') return

      // 获取部门领导信息
      const departmentLeader =
        departmentData.leader && departmentData.leader[0] ? departmentData.leader[0].username : '无'

      // 处理部门领导
      if (
        departmentData.leader &&
        Array.isArray(departmentData.leader) &&
        departmentData.leader.length > 0
      ) {
        departmentData.leader.forEach((leader) => {
          if (leader && typeof leader === 'object') {
            result.push({
              uuid: leader.uuid || '',
              id: idCounter++,
              date: formatDate(leader.date_joined),
              name: leader.username || '未设置',
              department: departmentName,
              leader: departmentLeader,
              email: leader.email || '未设置',
              status: leader.status,
              isLeader: true,
            })
          }
        })
      }

      // 处理部门成员
      if (
        departmentData.members &&
        Array.isArray(departmentData.members) &&
        departmentData.members.length > 0
      ) {
        departmentData.members.forEach((member) => {
          if (member && typeof member === 'object' && member.status !== 2) {
            // 过滤掉status为2（离职）的成员
            result.push({
              uuid: member.uuid || '',
              id: idCounter++,
              date: formatDate(member.date_joined),
              name: member.username || '未设置',
              department: departmentName,
              leader: departmentLeader,
              email: member.email || '未设置',
              status: member.status,
              isLeader: false,
            })
          }
        })
      }
    })

    return result
  }

  // 获取部门数据
  const fetchDepartmentData = async () => {
    try {
      const response = await staffHttp.get_all_staff_department()
      // 将部门数据转换为Map，方便查找部门id
      const deptMap = {}
      const deptOptions = []

      if (response.data && response.data.results && Array.isArray(response.data.results)) {
        response.data.results.forEach((dept) => {
          deptMap[dept.name] = dept.id
          deptOptions.push({
            name: dept.name,
            id: dept.id,
          })
        })
      }

      departments.value = deptMap
      departmentOptions.value = deptOptions
    } catch (err) {
      console.error('获取部门数据失败:', err)
    }
  }

  // 获取员工数据
  const fetchStaffData = async () => {
    loading.value = true
    error.value = ''
    try {
      // 先获取部门数据
      await fetchDepartmentData()
      // 再获取员工数据
      const response = await staffHttp.get_all_staff()
      rawStaffData.value = transformStaffData(response.data)
    } catch (err) {
      console.error('获取员工数据失败:', err)
      error.value = '获取员工数据失败，请稍后重试'
    } finally {
      loading.value = false
    }
  }

  // 按部门分组的计算属性
  const departmentGroups = computed(() => {
    const groups = {}

    // 按部门名称分组，区分领导和成员
    rawStaffData.value.forEach((staff) => {
      if (!groups[staff.department]) {
        groups[staff.department] = {
          leaders: [],
          members: [],
        }
      }

      if (staff.isLeader) {
        groups[staff.department].leaders.push(staff)
      } else {
        groups[staff.department].members.push(staff)
      }
    })

    // 转换为数组格式并按部门ID排序
    return Object.keys(groups)
      .sort((a, b) => {
        const idA = departments.value[a] || 999
        const idB = departments.value[b] || 999
        return idA - idB
      })
      .map((department) => ({
        department: department,
        departmentId: departments.value[department] || 999,
        staffs: [...groups[department].leaders, ...groups[department].members],
        leader: groups[department].leaders[0]?.name || '无',
      }))
  })

  // 显示编辑对话框
  const showEditDialog = (row) => {
    // 权限检查：董事会成员只能由董事会领导编辑
    const currentUser = authStore.user
    const isBoardMember = row.department === '董事会'
    const isCurrentUserBoardLeader = checkIfBoardLeader()

    // 如果编辑的是董事会成员，但当前用户不是董事会领导，则不允许编辑
    if (isBoardMember && !isCurrentUserBoardLeader) {
      ElMessage.warning('董事会成员只能由董事会领导编辑')
      return
    }

    // 复制员工信息到编辑表单
    editForm.uuid = row.uuid || ''
    editForm.name = row.name
    editForm.email = row.email
    editForm.department = row.department // 保存部门名称
    // 获取部门ID
    editForm.department_id = departments.value[row.department] || ''
    editForm.status = row.status
    editForm.isLeader = row.isLeader
    dialogVisible.value = true
  }

  // 保存编辑对话框中的员工信息
  const saveEditDialog = async () => {
    try {
      // 权限检查：董事会成员只能由董事会领导编辑
      const isBoardMember = editForm.department === '董事会'
      const isCurrentUserBoardLeader = checkIfBoardLeader()

      // 如果编辑的是董事会成员，但当前用户不是董事会领导，则不允许编辑
      if (isBoardMember && !isCurrentUserBoardLeader) {
        ElMessage.warning('董事会成员只能由董事会领导编辑')
        return
      }

      // 当部门ID改变时，获取对应的部门名称
      if (editForm.department_id) {
        const selectedDept = departmentOptions.value.find(
          (dept) => dept.id === editForm.department_id,
        )
        if (selectedDept) {
          // 额外检查：如果当前编辑的是董事会成员，不允许改变其部门
          if (editForm.department === '董事会' && selectedDept.name !== '董事会') {
            ElMessage.warning('不能修改董事会成员的部门')
            return
          }
          editForm.department = selectedDept.name
        }
      }

      // 构建更新数据对象，只包含允许更新的字段
      // 后端期望department字段（int类型）
      const updateData = {
        name: editForm.name,
        email: editForm.email,
        status: editForm.status,
        isLeader: editForm.isLeader,
        department: parseInt(editForm.department_id) || 0, // 将部门ID转换为int类型并使用department字段名
      }

      // 调试信息
      console.log('传递给后端的数据:', updateData)
      console.log('部门ID类型:', typeof updateData.department)

      // 调用更新员工接口
      await staffHttp.update_staff(editForm.uuid, updateData)

      // 如果isLeader为true，设置该员工为部门领导
      if (editForm.isLeader && editForm.department_id) {
        // 使用转换后的部门ID（确保是int类型）
        const departmentId = parseInt(editForm.department_id) || 0
        // 调用设置领导接口
        await staffHttp.set_leader(departmentId, editForm.uuid)
        console.log('设置领导时使用的部门ID:', departmentId, '类型:', typeof departmentId)
        ElMessage.success('部门领导设置成功')
      }

      // 显示成功消息
      ElMessage.success('员工信息更新成功')

      // 关闭对话框并重置表单
      closeEditDialog()

      // 重新获取员工数据以更新列表
      fetchStaffData()
    } catch (error) {
      // 显示错误消息
      ElMessage.error(error.message || '更新员工信息失败')
    }
  }

  // 存储选中的员工ID
  const selectedStaffIds = ref(new Set())

  // 监听表格的selection-change事件
  const handleSelectionChange = (department, selection) => {
    console.log('选择变更事件，部门:', department, '选中数量:', selection.length)
    // 为指定部门更新选中的员工ID
    if (!selectedStaffIds.value) {
      selectedStaffIds.value = new Set()
    }

    // 清除该部门之前的选中状态
    const newSelectionSet = new Set()
    selection.forEach((row) => {
      newSelectionSet.add(row.uuid)
    })

    // 保存当前部门的选中状态
    selectedStaffIds.value = newSelectionSet
    console.log('当前选中的员工ID:', Array.from(selectedStaffIds.value))
  }

  const downloadStaffData = (department) => {
    console.log('下载数据函数调用，部门:', department)
    console.log('当前选中的员工ID集合:', Array.from(selectedStaffIds.value))

    // 直接从选中的ID集合中获取数据
    const selectedRows = rawStaffData.value.filter(
      (staff) => staff.department === department && selectedStaffIds.value.has(staff.uuid),
    )

    if (selectedRows.length === 0) {
      ElMessage.warning('请选择要下载数据的员工')
      return
    }

    console.log('找到选中的员工数据:', selectedRows)

    //打印调试信息
    console.log('选中的行:', selectedRows)
    // 打印选中的行的UUID
    console.log(
      '选中的行UUID:',
      selectedRows.map((row) => row.uuid),
    )

    // 调用下载接口
    staffHttp
      .download_staff_data(selectedRows.map((row) => row.uuid))
      .then((response) => {
        // 处理下载成功的情况
        ElMessage.success('数据下载成功')
        // 触发文件下载
        const url = window.URL.createObjectURL(new Blob([response.data]))
        const link = document.createElement('a')
        link.href = url
        link.setAttribute('download', '员工信息.xlsx')
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
      })
      .catch((error) => {
        // 处理下载失败的情况
        ElMessage.error('数据下载失败')
      })
  }

  // 关闭编辑对话框
  const closeEditDialog = () => {
    dialogVisible.value = false
    editingStaff.value = null
    // 重置表单
    Object.keys(editForm).forEach((key) => {
      editForm[key] = ''
    })
  }

  onMounted(() => {
    // 首先检查权限
    if (!checkStaffPermission()) {
      return
    }
    fetchStaffData()
  })

  // 导出所有需要在模板中使用的状态和方法
  return {
    staffTables,
    checkIfBoardLeader,
    rawStaffData,
    departments,
    departmentOptions,
    loading,
    error,
    statusMap,
    dialogVisible,
    editingStaff,
    editForm,
    allStaffData,
    formatDate,
    checkStaffPermission,
    transformStaffData,
    fetchDepartmentData,
    fetchStaffData,
    departmentGroups,
    showEditDialog,
    saveEditDialog,
    selectedStaffIds,
    handleSelectionChange,
    downloadStaffData,
    closeEditDialog,
  }
}
