import { BellFilled, House, Checked, User, UserFilled, Failed } from '@element-plus/icons-vue'
import { Plus, CirclePlusFilled, List, MessageBox } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { ref, computed, reactive } from 'vue'
import { Fold, Expand } from '@element-plus/icons-vue'
import { ArrowDown } from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth.js'
import router from '@/router/index.js'
import AuthHttp from '@/api/AuthHttp.js'

// 导出frame组件的逻辑
export default function useFrameComposable() {
  // 响应式状态定义
  const isCollapse = ref(false)
  // 从auth store中获取当前登录用户信息
  const authStore = useAuthStore()

  // 个人信息框显示状态
  const profileVisible = ref(false)

  // 密码重置相关状态定义
  let dialogVisible = ref(false)
  let reSetPassword = reactive({
    oldPassword: '',
    newPassword: '',
    confirmPassword: '',
  })

  // 表单验证规则
  let rules = reactive({
    oldPassword: [
      { required: true, message: '请输入旧密码', trigger: 'blur' },
      { min: 6, max: 20, message: '长度在 6 到 20 个字符', trigger: 'blur' },
    ],
    newPassword: [
      { required: true, message: '请输入新密码', trigger: 'blur' },
      { min: 6, max: 20, message: '长度在 6 到 20 个字符', trigger: 'blur' },
    ],
    confirmPassword: [
      { required: true, message: '请确认新密码', trigger: 'blur' },
      { min: 6, max: 20, message: '长度在 6 到 20 个字符', trigger: 'blur' },
      {
        validator: (rule, value, callback) => {
          if (value === reSetPassword.newPassword) {
            callback()
          } else {
            callback(new Error('两次输入密码不一致'))
          }
        },
        message: '两次输入密码不一致',
        trigger: 'blur',
      },
    ],
  })

  // 表单标签宽度
  const formLabelWidth = '100px'

  // 计算属性
  let asideWidth = computed(() => {
    return isCollapse.value ? '64px' : '200px'
  })

  // 计算属性，获取用户名，支持不同可能的字段名
  const username = computed(() => {
    const user = authStore.user
    return user.username || user.name || user.account || '用户'
  })

  // 方法定义
  // 定义退出登录函数
  const logout = () => {
    authStore.clearUserToken()
    // 跳转到登录页
    router.push({ name: 'login' })
  }

  // 点击显示修改密码的对话框
  const showChangePasswordDialog = () => {
    // 清空表单数据
    reSetPassword.oldPassword = ''
    reSetPassword.newPassword = ''
    reSetPassword.confirmPassword = ''
    dialogVisible.value = true
  }

  // 点击显示个人信息框
  const showProfileBox = () => {
    profileVisible.value = !profileVisible.value
  }

  // 格式化日期时间函数
  const formatDate = (dateString) => {
    if (!dateString) return null

    const date = new Date(dateString)
    if (isNaN(date.getTime())) return null

    // 格式化日期：YYYY-MM-DD HH:MM:SS
    const year = date.getFullYear()
    const month = String(date.getMonth() + 1).padStart(2, '0')
    const day = String(date.getDate()).padStart(2, '0')
    const hours = String(date.getHours()).padStart(2, '0')
    const minutes = String(date.getMinutes()).padStart(2, '0')
    const seconds = String(date.getSeconds()).padStart(2, '0')

    return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`
  }

  // 提交密码修改
  const handleSubmit = async () => {
    // 检查必填字段
    if (
      !reSetPassword.oldPassword ||
      !reSetPassword.newPassword ||
      !reSetPassword.confirmPassword
    ) {
      ElMessage.error('请填写完整信息')
      return
    }

    // 检查密码一致性
    if (reSetPassword.newPassword !== reSetPassword.confirmPassword) {
      ElMessage.error('两次输入密码不一致')
      return
    }

    try {
      // 使用async/await发送POST请求
      const response = await AuthHttp.resetPassword(
        reSetPassword.oldPassword,
        reSetPassword.newPassword,
        reSetPassword.confirmPassword,
      )

      // 处理成功响应
      ElMessage.success('密码修改成功')
      dialogVisible.value = false
    } catch (error) {
      // 处理错误响应，添加详细的错误信息
      console.error('密码重置请求失败:', error)

      // 尝试获取更详细的错误信息
      const errorMessage =
        error.response?.data?.message ||
        error.response?.data?.detail ||
        error.message ||
        '密码修改失败'

      ElMessage.error(errorMessage)
    }
  }

  // 切换菜单折叠状态
  let changeCollapse = () => {
    isCollapse.value = !isCollapse.value
  }

  // 导出所有需要的状态和方法
  return {
    isCollapse,
    authStore,
    profileVisible,
    dialogVisible,
    reSetPassword,
    rules,
    formLabelWidth,
    asideWidth,
    username,
    logout,
    showChangePasswordDialog,
    showProfileBox,
    formatDate,
    handleSubmit,
    changeCollapse,
  }
}
