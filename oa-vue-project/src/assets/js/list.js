import { ref, reactive } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import http from '@/api/http.js';
import informHttp from '@/api/informHttp';
import { useRouter } from 'vue-router';
// 初始化通知列表数据
const informs = ref([]);
const router = useRouter();

// 删除通知函数
const handleDelete = (row) => {
    // 确认删除
    ElMessageBox.confirm('确定删除该通知吗？', '删除确认', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
    }).then(() => {
        // 调用删除API
        informHttp.delete_inform(row.id).then(response => {
            // 删除成功后，从列表中移除该通知
            informs.value = informs.value.filter(item => item.id !== row.id);
            ElMessage.success('删除通知成功');
        }).catch(error => {
            // 处理删除失败的情况
            ElMessage.error('删除通知失败');
        });
    }).catch(() => {
        // 用户取消删除
        ElMessage.info('已取消删除');
    });
};

// 编辑通知函数
const handleEdit = (row) => {
    // 先简单的弹窗提示，后续在实现编辑功能
    ElMessageBox.confirm('确定编辑该通知吗？', '编辑确认', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
    }).then(() => {
        // 跳转到编辑页面，传递通知ID
        router.push({ name: 'informEdit', params: { id: row.id } });
    }).catch(() => {
        // 用户取消编辑
        ElMessage.info('已取消编辑');
    });
};

// 初始化通知列表的函数
const initInforms = async () => {
    try {
        // 调用获取通知列表的API
        const response = await informHttp.get_inform_list();
        // 后端返回的数据包含在results字段中
        const results = response.data.results || [];

        // 去重处理，避免重复显示同一条通知
        // 使用Map数据结构进行高效去重，以通知的id作为唯一标识
        const uniqueInformsMap = new Map();

        results.forEach(inform => {
            // 只保留第一次出现的通知（按id去重）
            if (!uniqueInformsMap.has(inform.id)) {
                uniqueInformsMap.set(inform.id, inform);
            }
        });

        // 将去重后的Map转换为数组
        informs.value = Array.from(uniqueInformsMap.values());
    } catch (error) {
        console.error('获取通知列表失败:', error);
        ElMessage.error('获取通知列表失败');
    }
};

export { informs, handleDelete, handleEdit, initInforms };