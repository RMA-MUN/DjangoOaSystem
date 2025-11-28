<script setup name="EmpAttendance">
import PageHeader from '@/components/pageHeader.vue'
import { onMounted } from 'vue'
import useEmpAttendance from '@/assets/js/empAttendance.js'

// 导入并使用empAttendance逻辑
const {
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
} = useEmpAttendance()

// 组件挂载时加载数据
onMounted(() => {
  initData()
})
</script>

<template>
  <PageHeader title="员工考勤" />
  <el-card style="margin: 20px;">
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
      <el-table-column label="状态" width="100">
        <template #default="scope">
          <el-tag :type="statusMap[scope.row.status]?.type">
            {{ statusMap[scope.row.status]?.label }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="150" fixed="right">
        <template #default="scope">
          <el-button type="primary" size="small" @click="openApproveDialog(scope.row)" v-if="scope.row.status === 1">
            审批
          </el-button>
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

  <!-- 审批对话框 -->
  <el-dialog v-model="dialogVisible" title="审批考勤" width="500">
    <div v-if="currentAttendance" class="approval-info">
      <div class="info-item">
        <strong>请假标题：</strong>{{ currentAttendance.title }}
      </div>
      <div class="info-item">
        <strong>请假人：</strong>{{ currentAttendance.requester_name }}
      </div>
      <div class="info-item">
        <strong>请假类型：</strong>{{ currentAttendance.attendance_type?.name }}
      </div>
      <div class="info-item">
        <strong>请假时间：</strong>
        {{ new Date(currentAttendance.start_time).toLocaleString('zh-CN') }} - {{ new
          Date(currentAttendance.end_time).toLocaleString('zh-CN') }}
      </div>
      <div class="info-item">
        <strong>请假理由：</strong>{{ currentAttendance.request_content }}
      </div>

      <el-form :model="approveForm" label-width="100px" style="margin-top: 20px;">
        <el-form-item label="审批结果">
          <el-select v-model="approveForm.status" placeholder="请选择审批结果">
            <el-option label="同意" :value="2" />
            <el-option label="拒绝" :value="3" />
          </el-select>
        </el-form-item>
        <el-form-item label="审批意见">
          <el-input type="textarea" v-model="approveForm.approval_content" placeholder="请输入审批意见" />
        </el-form-item>
      </el-form>
    </div>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitApproval">确认</el-button>
      </div>
    </template>
  </el-dialog>
</template>

<style scoped>
/* 引入外部CSS样式 */
@import '@/assets/css/empAttendance.css';
</style>