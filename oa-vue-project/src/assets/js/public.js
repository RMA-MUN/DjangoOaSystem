import { reactive, ref, shallowRef, onBeforeUnmount } from 'vue'
import { ElMessage } from 'element-plus'
import '@wangeditor/editor/dist/css/style.css' // 引入 css
import { Editor, Toolbar } from '@wangeditor/editor-for-vue'
import pageHeader from '@/components/pageHeader.vue'
import http from '@/api/http.js'
import staffHttp from '@/api/staffHttp.js'
import informHttp from '@/api/informHttp'
import { useRouter } from 'vue-router'

const router = useRouter()

// 表单数据
const formData = reactive({
    title: '',
    content: '',
    department_ids: [],
})

const rules = reactive({
    title: [
        { required: true, message: '请输入通知标题', trigger: 'blur' }
    ],
    content: [
        { required: true, message: '请输入通知内容', trigger: 'blur' }
    ],
    department_ids: [
        { required: true, message: '请选择发布部门', trigger: 'change' }
    ]
})

let formRef = ref(null)
let departments = ref([])

// 初始化部门数据的函数
const initDepartments = async () => {
    try {
        console.log('开始获取部门数据...')
        let response = await staffHttp.get_all_staff_department()
        console.log('获取部门数据响应:', response)

        // 检查响应状态和数据格式
        if (response && response.status === 200 && response.data && Array.isArray(response.data.results)) {
            // 使用后端返回的results数组，其中已包含id字段
            departments.value = response.data.results
            console.log('部门数据处理成功，共', departments.value.length, '个部门')
        } else if (response && response.data && Array.isArray(response.data)) {
            // 兼容另一种可能的数据格式
            departments.value = response.data
            console.log('部门数据处理成功(兼容格式)，共', departments.value.length, '个部门')
        } else {
            console.error('部门数据格式不正确:', response)
            ElMessage.warning('部门数据格式不正确，请联系管理员')
        }
    } catch (error) {
        console.error('获取部门信息失败:', error)
        ElMessage.error('获取部门信息失败，请稍后重试')
    }
}

// 状态变量
const isLoading = ref(false)
const errorMessage = ref('')
const successMessage = ref('')

// 表单验证
const validateForm = () => {
    if (!formData.title.trim()) {
        errorMessage.value = '请输入通知标题'
        return false
    }
    if (!formData.content.trim()) {
        errorMessage.value = '请输入通知内容'
        return false
    }
    if (formData.department_ids.length === 0) {
        errorMessage.value = '请选择发布部门'
        return false
    }
    return true
}

// 发布通知
const handlePublish = async () => {
    // 这里先判断表单是否验证通过
    if (!validateForm()) {
        return
    }

    // 这里异步使用informHttp.publish_inform方法发布通知
    try {
        isLoading.value = true
        const response = await informHttp.publish_inform(formData)
        if (response.status === 201) {
            ElMessage.success('通知发布成功')
            // 使用response.data中的id构建成功消息
            successMessage.value = `通知发布成功，通知ID: ${response.data.id}`
            // 重置表单
            formRef.value.resetFields()
            formData.title = ''
            formData.content = ''
            formData.department_ids = []
        } else {
            ElMessage.error('通知发布失败')
        }
    } catch (error) {
        console.error('发布通知失败:', error)
        ElMessage.error('发布通知失败，请稍后重试')
    } finally {
        isLoading.value = false
    }

}

// 清除错误信息
const clearError = () => {
    errorMessage.value = ''
}

// wangeditor配置
// 编辑器实例，必须用 shallowRef
const editorRef = shallowRef()

const toolbarConfig = {}
const editorConfig = {
    placeholder: '请输入内容...',
    MENU_CONF: {
        uploadImage: { // file/upload/
            // 使用环境变量中的API地址
            server: import.meta.env.VITE_API_URL + '/file/upload/',
            fieldName: 'img',
            maxFileSize: 1 * 1024 * 1024,
            maxNumberOfFiles: 9,
            timeout: 6 * 1000,
            allowedFileTypes: ['image/*'],
            // 直接获取当前token，使用静态对象形式
            headers: {
                // 优先从localStorage获取token，兼容非组件环境
                'Authorization': 'Bearer ' + (localStorage.getItem('TOKEN_KEY') || window.authToken || '')
            },
            // 自定义插入图片
            customInsert(res, insertFn) {
                try {
                    console.log('图片上传响应:', res)
                    // 检查响应格式
                    if (res && res.errno === 0 && res.data) {
                        // 处理不同的响应格式
                        if (res.data.url) {
                            let url = import.meta.env.VITE_API_URL + res.data.url
                            let alt = res.data.alt || ''
                            let href = res.data.href ? import.meta.env.VITE_API_URL + res.data.href : url
                            insertFn(url, alt, href)
                        } else if (res.data) {
                            // 兼容其他可能的响应格式
                            let url = typeof res.data === 'string' ? res.data : 
                                      (res.data.image_url || res.data.img_url || JSON.stringify(res.data))
                            insertFn(url, '', url)
                        }
                    } else {
                        const errorMsg = res?.message || res?.errmsg || '未知错误'
                        console.error('图片上传失败:', errorMsg)
                        ElMessage.error(`图片上传失败: ${errorMsg}`)
                    }
                } catch (error) {
                    console.error('处理图片响应时出错:', error)
                    ElMessage.error(`处理图片上传响应时出错: ${error.message}`)
                }
            },
            // 单个文件上传失败
            onFailed(file, res) {
                console.error(`${file.name} 上传失败`, res)
                const errorMsg = res?.message || res?.errmsg || '上传失败'
                ElMessage.error(`${file.name} 上传失败: ${errorMsg}`)
            },

            // 上传错误，或者触发 timeout 超时
            onError(file, err, res) {
                console.error(`${file.name} 上传出错`, err, res)
                let errorMsg = '上传出错'
                
                if (err) {
                    errorMsg = err.message || '网络错误'
                    if (errorMsg.includes('timeout')) {
                        errorMsg = '上传超时，请检查网络连接'
                    }
                } else if (res) {
                    errorMsg = typeof res === 'string' ? res : (res.message || res.errmsg || '服务器错误')
                    // 处理文件重复的特殊情况
                    const resStr = JSON.stringify(res).toLowerCase()
                    if (resStr.includes('duplicate') || resStr.includes('重复')) {
                        errorMsg = '文件已存在，请更换文件名后重试'
                    }
                }
                
                ElMessage.error(`${file.name} 上传出错: ${errorMsg}`)
            },
            // 上传进度回调，可以添加进度条等功能
            onProgress(progress) {
                console.log('上传进度:', progress)
            }
        }
    }
}

// 组件销毁时，也及时销毁编辑器
onBeforeUnmount(() => {
    const editor = editorRef.value
    if (editor == null) return
    editor.destroy()
})

const handleCreated = (editor) => {
    editorRef.value = editor // 记录 editor 实例，重要！
}

// 编辑器模式设置为 default
const mode = 'default'

export { formData, rules, formRef, departments, isLoading, errorMessage, successMessage, validateForm, handlePublish, clearError, editorRef, toolbarConfig, editorConfig, handleCreated, mode, initDepartments };