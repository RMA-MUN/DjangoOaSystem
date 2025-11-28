import axios from 'axios'
import { ElMessage } from 'element-plus'
import router from '@/router'

class http {
  // 构造函数
  constructor() {
    this.instance = axios.create({
      baseURL: import.meta.env.VITE_API_URL,
      timeout: 5000,
      headers: {
        'Content-Type': 'application/json'
      }
    })

    // 请求拦截器，除了登录以外，其他请求都需要添加token
    this.instance.interceptors.request.use(
      (config) => {
        // 避免在登录请求中添加token
        if (!config.url.includes('/login/')) {
          // 直接从localStorage获取token，避免在非组件环境中使用store
          const token = localStorage.getItem('TOKEN_KEY')
          if (token) {
            config.headers['Authorization'] = 'Bearer ' + token
          }
        }
        return config
      },
      (error) => {
        // 处理请求配置错误
        console.error('请求配置错误:', error)
        return Promise.reject(this.formatError(error))
      },
    )

    // 响应拦截器，处理token过期等错误
    this.instance.interceptors.response.use(
      (response) => {
        return response
      },
      (error) => {
        // 格式化错误信息
        const formattedError = this.formatError(error)
        
        // 处理token过期错误（401 Unauthorized）
        if (error.response && error.response.status === 401) {
          // 清除本地存储的token
          localStorage.removeItem('TOKEN_KEY')
          
          // 避免重复提示
          if (!this.isTokenExpiredAlertShown) {
            this.isTokenExpiredAlertShown = true
            ElMessage.error('token已过期，请重新登录')
            
            // 延迟跳转，让用户看到提示
            setTimeout(() => {
              this.isTokenExpiredAlertShown = false
              router.push('/login')
            }, 1500)
          }
        }
        
        return Promise.reject(formattedError)
      },
    )
    
    // 防止重复显示token过期提示
    this.isTokenExpiredAlertShown = false
  }
  
  // 格式化错误信息
  formatError(error) {
    if (error.code === 'ECONNABORTED') {
      // 请求超时
      return new Error('请求超时，请检查网络连接或稍后重试')
    } else if (!error.response) {
      // 网络错误或服务器未响应
      return new Error('网络连接失败，请检查网络设置')
    } else if (error.response.status >= 500) {
      // 服务器错误
      return new Error('服务器暂时不可用，请稍后重试')
    } else if (error.response.status >= 400) {
      // 客户端错误
      return new Error(error.response.data?.message || '请求失败，请检查输入信息')
    }
    // 其他错误
    return new Error(error.message || '未知错误')
  }

  post(url, data, config = {}) {
    // path: /officeAuth/login/
    // url: http://127.0.0.1:8000/officeAuth/login/
    // 支持传递完整的config对象，包括headers等
    return this.instance.post(url, data, config)
  }

  get(url, config = {}) {
    // 支持传入完整的config对象，包括params和headers
    // 如果config是一个简单的对象且不是完整的配置对象，将其视为params
    const requestConfig =
      typeof config === 'object' && !config.params && !config.headers ? { params: config } : config
    return this.instance.get(url, requestConfig)
  }

  delete(url) {
    return new Promise((resolve, reject) => {
      try {
        let response = this.instance.delete(url)
        resolve(response)
      } catch (error) {
        // 处理删除失败的情况
        ElMessage.error('删除通知失败')
        reject(error)
      }
    })
  }

  put(url, data, config = {}) {
    // 支持传递完整的config对象，包括headers等
    return this.instance.put(url, data, config)
  }

  async download(url, params = {}) {
    return new Promise((resolve, reject) => {
      try {
        // 构建请求配置对象
        const config = {
          responseType: 'blob',
        }

        // 只有当params不为空对象时才添加到配置中
        if (Object.keys(params).length > 0) {
          config.params = params
        }

        this.instance.get(url, config).then((response) => {
          resolve(response)
        })
      } catch (error) {
        // 处理下载失败的情况
        ElMessage.error('下载数据失败')
        reject(error)
      }
    })
  }
}

export default new http()
