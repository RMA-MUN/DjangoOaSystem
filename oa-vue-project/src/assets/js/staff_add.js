import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/auth.js'
import staffHttp from '@/api/staffHttp.js'

/**
 * 员工添加页面的逻辑组合式API
 * @returns {Object} 组件需要的响应式数据和方法
 */
export function useStaffAddLogic() {
  // 表单数据
  const form = reactive({
    name: '',
    email: '',
    password: '',
    department: '',
    Leader: '',
  })

  // 用户信息（包含部门ID）
  const userInfo = ref({})

  const rules = reactive({
    name: [{ required: true, message: '请输入员工姓名', trigger: 'blur' }],
    email: [{ required: true, message: '请输入员工邮箱', trigger: 'blur' }],
    password: [{ required: true, message: '请输入初始密码', trigger: 'blur' }],
  })

  const formRef = ref(null)

  /**
   * 通用的用户信息提取函数
   * @param {string|Object} data - JSON字符串或对象
   * @returns {Object} 包含提取信息的对象
   */
  const extractUserInfo = (data) => {
    try {
      // 如果输入是字符串，尝试解析为JSON对象
      const userData = typeof data === 'string' ? JSON.parse(data) : data

      // 参数验证
      if (!userData || typeof userData !== 'object') {
        return {
          username: '',
          departmentName: '',
        }
      }

      // 安全提取用户名
      const username = userData.username || ''

      // 安全提取部门名称
      const departmentName =
        userData.department && userData.department.name ? userData.department.name : ''

      // 提取部门id
      const departmentId =
        userData.department && userData.department.id ? userData.department.id : ''

      return {
        username,
        departmentName,
        departmentId,
      }
    } catch (error) {
      console.error('解析用户数据时出错:', error)
      return {
        username: '',
        departmentName: '',
        departmentId: '',
      }
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

  const cleanForm = () => {
    form.name = ''
    form.email = ''
    form.password = ''
    // 重置表单验证状态
    if (formRef.value) {
      formRef.value.resetFields()
    }
  }

  const submitForm = async () => {
    // 表单验证
    try {
      await formRef.value.validate()

      // 获取部门ID并转换为数字类型
      const departmentId = Number(userInfo.value.departmentId)

      // 验证departmentId是否有效
      if (!departmentId || isNaN(departmentId)) {
        ElMessage.warning('部门信息无效，请刷新页面重试')
        return
      }

      // 准备提交数据，确保符合后端接口要求
      const submitData = {
        username: form.name.trim(), // 使用表单中的name作为username并去除前后空格
        password: form.password,
        email: form.email.trim(), // 去除邮箱前后空格
        department: departmentId, // 确保department是有效数字
      }

      // 调试信息
      console.log('提交员工数据:', submitData)

      // 调用staffHttp.add_staff函数添加员工
      const response = await staffHttp.add_staff(
        submitData.username,
        submitData.password,
        submitData.email,
        submitData.department,
      )

      if (response.status === 201) {
        ElMessage.success('添加员工成功')
        cleanForm()
      } else {
        ElMessage.error(response.message || '添加员工失败')
      }
    } catch (error) {
      // 检查当前登录的用户是否是leader
      if (userInfo.value.username !== form.Leader) {
        ElMessage.warning('您不是该部门的领导，不能添加员工')
        return
      }
    }
  }

  onMounted(() => {
    // 首先检查权限
    if (!checkStaffPermission()) {
      return
    }

    // 初始化部门和部门领导
    const authStore = useAuthStore()
    const user = authStore.user

    // 使用extractUserInfo函数安全地提取用户信息
    userInfo.value = extractUserInfo(user)

    // 设置表单数据
    form.department = userInfo.value.departmentName || ''
    form.Leader = userInfo.value.username || ''
  })

  return {
    form,
    userInfo,
    rules,
    formRef,
    cleanForm,
    submitForm,
  }
}
