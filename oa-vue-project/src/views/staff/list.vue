<script setup name="stafflist">
import pageHeader from '@/components/pageHeader.vue';
import { useStaffListLogic } from '@/assets/js/staff_list.js';

// 导入所有需要在模板中使用的状态和方法
const {
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
    closeEditDialog
} = useStaffListLogic();
</script>

<template>
    <div class="staff-list-container">
        <pageHeader title="员工列表" />
        <div class="content-wrapper">
            <!-- 加载状态 -->
            <el-skeleton v-if="loading" :rows="6" animated class="loading-skeleton" />

            <!-- 错误提示 -->
            <el-alert v-else-if="error" :title="error" type="error" show-icon class="error-alert" />

            <!-- 空数据提示 -->
            <el-empty v-else-if="departmentGroups.length === 0" description="暂无员工数据" class="empty-data" />

            <!-- 员工数据列表 -->
            <el-row v-else :gutter="20" class="department-grid">
                <el-col v-for="group in departmentGroups" :key="group.department" :xs="24" :sm="12" :md="12" :lg="12"
                    :xl="12" class="department-col">
                    <el-card class="department-card">
                        <template #header>
                            <div class="card-header">
                                <span class="department-title">{{ group.department }}</span>
                                <span class="department-leader">领导: {{ group.leader }}</span>
                            </div>
                        </template>
                        <el-table :data="group.staffs" style="width: 100%"
                            @selection-change="(selection) => handleSelectionChange(group.department, selection)"
                            height="240" size="small">

                            <el-table-column type="selection" label="选择" width="40" />

                            <el-table-column fixed="left" prop="name" label="姓名" width="70">
                                <template #default="{ row }">
                                    <div>
                                        {{ row.name }}
                                        <el-tag v-if="row.isLeader" size="small" type="success" effect="plain"
                                            style="margin-left: 4px;">
                                            领导
                                        </el-tag>
                                    </div>
                                </template>
                            </el-table-column>
                            <el-table-column prop="date" label="入职日期" width="90" />
                            <el-table-column prop="email" label="邮箱" width="150" />
                            <!-- <el-table-column prop="status" label="状态" width="80">
                                <template #default="{ row }">
                                    {{ statusMap[row.status] || row.status || '未设置' }}
                                </template>
                            </el-table-column> -->

                            <el-table-column fixed="right" label="操作" min-width="80">
                                <template #default="{ row }">
                                    <el-button size="mini" type="primary" @click="showEditDialog(row)">编辑</el-button>
                                </template>

                            </el-table-column>
                        </el-table>

                        <el-button type="primary" size="mini" @click="downloadStaffData(group.department)">
                            下载员工数据
                        </el-button>

                    </el-card>
                </el-col>
            </el-row>
        </div>
    </div>

    <!-- 编辑员工信息对话框 -->
    <el-dialog v-model="dialogVisible" title="编辑员工信息" width="500px" @close="closeEditDialog">
        <el-form label-width="100px" :model="editForm"
            :disabled="editForm.department === '董事会' && !checkIfBoardLeader()">
            <el-form-item label="员工姓名">
                <el-input v-model="editForm.name" placeholder="请输入员工姓名" />
            </el-form-item>
            <el-form-item label="员工UUID">
                <el-input v-model="editForm.uuid" placeholder="员工UUID" disabled />
            </el-form-item>
            <el-form-item label="电子邮箱">
                <el-input v-model="editForm.email" placeholder="请输入电子邮箱" />
            </el-form-item>
            <el-form-item label="所属部门">
                <el-select v-model="editForm.department_id" placeholder="请选择部门" filterable>
                    <!-- 绑定到部门ID -->
                    <el-option v-for="dept in departmentOptions" :key="dept.id" :label="dept.name" :value="dept.id" />
                </el-select>
            </el-form-item>
            <!-- 状态列 -->
            <el-form-item label="状态">
                <!-- 给一个下拉菜单，选项有正常、禁用 -->
                <el-select v-model="editForm.status" placeholder="请选择状态">
                    <el-option label="未激活" :value="0" />
                    <el-option label="在职" :value="1" />
                    <el-option label="离职" :value="2" />
                </el-select>
            </el-form-item>
            <el-form-item label="是否领导">
                <!-- 如果是董事会，有权利设置为领导； 否则，只能查看 -->
                <!-- 如果是董事会成员，给出提示；董事会成员不能被设置为领导 -->
                <div>
                    <el-tag v-if="editForm.department === '董事会'" type="info" size="small" style="margin-left: 8px;">
                        董事会成员不能被设置为领导
                    </el-tag>
                    <el-tag v-if="editForm.department === '董事会' && !checkIfBoardLeader()" type="warning" size="small"
                        style="margin-left: 8px;">
                        董事会成员只能由董事会领导编辑
                    </el-tag>
                    <el-switch v-model="editForm.isLeader" :disabled="editForm.department === '董事会'">
                        设置为领导
                    </el-switch>
                </div>
            </el-form-item>
        </el-form>

        <template #footer>
            <span class="dialog-footer">
                <el-button @click="closeEditDialog">取消</el-button>
                <el-button type="primary" @click="saveEditDialog">保存</el-button>
            </span>
        </template>
    </el-dialog>
</template>

<style scoped>
@import "@/assets/css/staff_list.css";
</style>
