<script setup name="staffadd">
import pageHeader from '@/components/pageHeader.vue';
import { useStaffAddLogic } from '@/assets/js/staff_add.js';

// 使用从外部JS导入的逻辑
const { form, userInfo, rules, formRef, cleanForm, submitForm } = useStaffAddLogic();
</script>

<template>
    <div class="staff-add-container">
        <pageHeader title="添加员工" />

        <div class="content-wrapper">
            <el-card class="form-card">
                <template #header>
                    <div class="card-header">
                        <span class="header-title">员工信息录入</span>
                    </div>
                </template>

                <el-form :model="form" :rules="rules" ref="formRef" label-width="120px" class="staff-form">
                    <el-divider content-position="left">基本信息</el-divider>

                    <el-row :gutter="20">
                        <el-col :xs="24" :sm="24" :md="12">
                            <el-form-item label="员工姓名" prop="name" class="form-item">
                                <el-input v-model="form.name" placeholder="请输入员工姓名" class="form-input" />
                            </el-form-item>
                        </el-col>

                        <el-col :xs="24" :sm="24" :md="12">
                            <el-form-item label="员工邮箱" prop="email" class="form-item">
                                <el-input v-model="form.email" placeholder="请输入员工邮箱" class="form-input" />
                            </el-form-item>
                        </el-col>
                    </el-row>

                    <el-row :gutter="20">
                        <el-col :xs="24" :sm="24" :md="12">
                            <el-form-item label="初始密码" prop="password" class="form-item">
                                <el-input v-model="form.password" placeholder="请输入初始密码" type="password"
                                    class="form-input" @keyup.enter="submitForm" />
                            </el-form-item>
                        </el-col>
                    </el-row>

                    <el-divider content-position="left">部门信息</el-divider>

                    <el-row :gutter="20">
                        <el-col :xs="24" :sm="24" :md="12">
                            <el-form-item label="所属部门" prop="department" class="form-item">
                                <el-input v-model="form.department" readonly disabled placeholder="部门默认为当前用户部门"
                                    class="form-input readonly-input" />
                            </el-form-item>
                        </el-col>

                        <el-col :xs="24" :sm="24" :md="12">
                            <el-form-item label="部门领导" prop="Leader" class="form-item">
                                <el-input v-model="form.Leader" readonly disabled placeholder="默认为部门领导"
                                    class="form-input readonly-input" />
                            </el-form-item>
                        </el-col>
                    </el-row>

                    <el-form-item class="form-actions">
                        <el-button type="primary" @click="submitForm" class="submit-button">添加员工</el-button>
                        <el-button @click="cleanForm">重置表单</el-button>
                    </el-form-item>
                </el-form>
            </el-card>
        </div>
    </div>
</template>

<style scoped>
/* 导入外部CSS */
@import "@/assets/css/staff_add.css";
</style>
