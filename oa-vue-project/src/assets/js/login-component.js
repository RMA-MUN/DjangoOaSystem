import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
        import { validateEmail, validatePassword, loginUser } from './login.js'
import { useAuthStore } from '../../stores/auth.js'

// 密码可见性切换功能
export function setupLoginComponent() {
  const router = useRouter()
  const authStore = useAuthStore()

  // 表单数据
  const formData = reactive({
    email: '',
    password: '',
    rememberMe: false,
  })

  // 状态变量
  const isLoading = ref(false)
  const errorMessage = ref('')
  const successMessage = ref('')
  const showPassword = ref(false)

  // 清除错误信息
  const clearError = () => {
    errorMessage.value = ''
  }

  // 切换密码可见性
  const togglePasswordVisibility = () => {
    showPassword.value = !showPassword.value
  }

  // 忘记密码处理
  const forgotPassword = () => {
    successMessage.value = '请联系管理员重置密码'
    setTimeout(() => {
      successMessage.value = ''
    }, 3000)
  }

  // 处理登录
  const handleLogin = async () => {
    // 清除之前的消息
    errorMessage.value = ''
    successMessage.value = ''

    // 验证邮箱
    if (!validateEmail(formData.email)) {
      errorMessage.value = '请输入有效的邮箱地址'
      return
    }

    // 验证密码
    const passwordValidation = validatePassword(formData.password)
    if (!passwordValidation.valid) {
      errorMessage.value = passwordValidation.message
      return
    }

    try {
      // 设置加载状态
      isLoading.value = true

      // 调用登录函数
      const result = await loginUser(formData.email, formData.password)

      if (result.success) {
        // 保存登录状态到store
        authStore.setUserToken(result.data.user, result.data.token)

        // 显示成功信息
        successMessage.value = '登录成功！'

        // 跳转到主页面
        setTimeout(() => {
          router.push('/')
        }, 1000)
      } else {
        // 显示错误信息
        errorMessage.value = result.error || '登录失败，请检查邮箱和密码'
      }
    } catch (error) {
      errorMessage.value = '登录失败，请稍后重试'
      console.error('登录错误:', error)
    } finally {
      // 重置加载状态
      isLoading.value = false
    }
  }

  return {
    formData,
    isLoading,
    errorMessage,
    successMessage,
    clearError,
    handleLogin,
    showPassword,
    togglePasswordVisibility,
    forgotPassword,
  }
}
