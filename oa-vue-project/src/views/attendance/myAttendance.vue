<script setup name="MyAttendance">
import PageHeader from '@/components/pageHeader.vue'
import { Plus } from '@element-plus/icons-vue'
import { onMounted, ref } from 'vue'
import useMyAttendance from '@/assets/js/myAttendance.js'

// 导入并使用myAttendance逻辑
const {
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
    handleCurrentChange
} = useMyAttendance()

// 组件挂载时加载数据
onMounted(() => {
    loadAttendanceTypes()
    loadApprover()
    loadAttendanceRecords()
})

</script>

<template>
    <PageHeader title="个人考勤" />
    <!-- 直接在页面显示考勤记录表格 -->
    <el-card style="margin: 20px;">
        <template #header>
            <div class="card-header">
                <span>我的考勤记录</span>
                <el-button type="primary" @click="changeFormVisible" style="margin-left: 20px;">
                    <el-icon>
                        <Plus />
                    </el-icon>发起请假
                </el-button>
            </div>
        </template>
        <el-table :data="tableData" style="width: 100%" :loading="loading" stripe="true">
            <el-table-column prop="title" label="请假标题" width="200" />
            <el-table-column prop="requester_name" label="请假人" width="120" />
            <el-table-column label="考勤类型" width="120">
                <template #default="scope">
                    {{ scope.row.attendance_type?.name || '-' }}
                </template>
            </el-table-column>
            <el-table-column label="请假时间" width="240">
                <template #default="scope">
                    {{ new Date(scope.row.start_time).toLocaleDateString('zh-CN') }} - {{ new
                        Date(scope.row.end_time).toLocaleDateString('zh-CN') }}
                </template>
            </el-table-column>
            <el-table-column prop="request_content" label="请假理由" show-overflow-tooltip />
            <el-table-column label="状态" width="100">
                <template #default="scope">
                    <el-tag :type="statusMap[scope.row.status]?.type">
                        {{ statusMap[scope.row.status]?.label }}
                    </el-tag>
                </template>
            </el-table-column>
            <el-table-column label="审批人" width="120">
                <template #default="scope">
                    <span>{{ scope.row.responser_name || '-' }}</span>
                </template>
            </el-table-column>
            <el-table-column label="审批意见" show-overflow-tooltip>
                <template #default="scope">
                    {{ scope.row.approval_content || '-' }}
                </template>
            </el-table-column>
        </el-table>
        <!-- 分页组件 -->
        <div class="pagination-container" style="margin-top: 20px; display: flex; justify-content: flex-end;">
            <el-pagination v-model:current-page="currentPage" v-model:page-size="pageSize" :page-sizes="[5, 10, 20, 50]"
                layout="total, sizes, prev, pager, next, jumper" :total="total" @size-change="handleSizeChange"
                @current-change="handleCurrentChange" background />
        </div>
    </el-card>

    <el-dialog v-model="dialogFormVisible" title="发起请假" width="500">
        <el-form :model="form" :rules="rules" ref="formRef">

            <el-form-item label="请假标题" :label-width="formLabelWidth">
                <el-input v-model="form.title" autocomplete="off" style="width: 100%;" />
            </el-form-item>

            <el-form-item label="请假类型" :label-width="formLabelWidth" prop="attendance_type_id">
                <el-select v-model="form.attendance_type_id" placeholder="请选择请假类型">
                    <el-option v-for="item in attemdance_type" :label="item.name" :value="item.id" :key="item.name" />
                </el-select>
            </el-form-item>

            <el-form-item label="请假理由" :label-width="formLabelWidth" prop="request_content">
                <el-input type="textarea" v-model="form.request_content" autocomplete="off" style="width: 100%;" />
            </el-form-item>

            <el-form-item label="请假时间" :label-width="formLabelWidth">
                <div class="demo-date-picker">
                    <div class="block">
                        <el-date-picker v-model="form.value1" type="daterange" range-separator="至"
                            start-placeholder="开始时间" end-placeholder="结束时间" format="YYYY-MM-DD" :size="size"
                            :required="true" />
                    </div>
                </div>
            </el-form-item>

            <el-form-item label="审批人" :label-width="formLabelWidth">
                <el-input :value="approverName" readonly disabled autocomplete="off" />
            </el-form-item>
        </el-form>

        <template #footer>
            <div class="dialog-footer">
                <el-button @click="dialogFormVisible = false">取消</el-button>
                <el-button type="primary" @click="submitForm" :loading="loading">确认</el-button>
            </div>
        </template>
    </el-dialog>


</template>

<style>
/* 引入外部CSS样式 */
@import '@/assets/css/myAttendance.css';
</style>