<script setup name="informPublic">
import { Editor, Toolbar } from '@wangeditor/editor-for-vue'
import { onMounted, onBeforeUnmount } from 'vue'
import pageHeader from '@/components/pageHeader.vue'
import { useAuthStore } from '@/stores/auth'
import { ElMessage } from 'element-plus'
import router from '@/router/index.js'
import {
  formData, rules, formRef, departments,
  isLoading, errorMessage, successMessage,
  validateForm, handlePublish, clearError,
  editorRef, toolbarConfig, editorConfig,
  handleCreated, mode, initDepartments
} from '@/assets/js/public.js';

// 获取认证store
const authStore = useAuthStore();

// 设置全局authToken以便编辑器配置使用
onMounted(async () => {
  // 权限检查：如果不是超级管理员，则重定向到通知列表
  if (!authStore.user?.is_superuser) {
    ElMessage.warning('您没有权限发布通知');
    router.push('/inform/list');
    return;
  }
  
  window.authToken = authStore.token;
  // 加载部门数据
  await initDepartments();
});

onBeforeUnmount(() => {
  // 清理全局变量
  if (window.authToken) {
    delete window.authToken;
  }
});
</script>

<template>
    <pageHeader title="通知发布" />
    <el-card style="margin: 20px;">
        <template #header>
            <span>通知发布</span>
        </template>

        <el-form rules="rules" ref="formRef" :model="formData" label-width="100px" @submit.prevent>
            <!-- 通知标题 -->
            <el-form-item label="通知标题" required>
                <el-input v-model="formData.title" placeholder="请输入通知标题" maxlength="100" show-word-limit
                    @input="clearError" />
            </el-form-item>

            <!-- 发布部门 -->
            <el-form-item label="发布部门" required>
                <!-- 部门数据调试 -->
                <!-- <div v-if="departments && departments.length > 0"
                    style="margin-bottom: 10px; font-size: 12px; color: #606266;">
                    已加载 {{ departments.length }} 个部门
                </div> -->
                <el-select v-model="formData.department_ids" multiple placeholder="请选择发布部门" clearable
                    @change="clearError" filterable>
                    <el-option label="所有部门" :value="0"></el-option>
                    <!-- 渲染所有部门选项 -->
                    <el-option v-for="dept in departments" :key="dept.id || Math.random()" :label="dept.name || '未命名部门'"
                        :value="dept.id || ''" />
                </el-select>
                <div class="hint-text">选择所有部门将自动视为发送给全体员工</div>
            </el-form-item>

            <!-- 通知内容 -->
            <el-form-item label="通知内容" required>
                <div style="border: 1px solid #ccc">
                    <Toolbar style="border-bottom: 1px solid #ccc" :editor="editorRef" :defaultConfig="toolbarConfig"
                        :mode="mode" />
                    <Editor style="height: 200px; overflow-y: hidden;" v-model="formData.content"
                        :defaultConfig="editorConfig" :mode="mode" @onCreated="handleCreated" />
                </div>
            </el-form-item>


            <!-- 错误信息显示 -->
            <el-form-item v-if="errorMessage" class="error-message">
                <div class="error-text">{{ errorMessage }}</div>
            </el-form-item>

            <!-- 成功信息显示 -->
            <el-form-item v-if="successMessage" class="success-message">
                <div class="success-text">{{ successMessage }}</div>
            </el-form-item>

            <!-- 操作按钮 -->
            <el-form-item>
                <el-button type="primary" @click="handlePublish" :loading="isLoading">
                    发布通知
                </el-button>
                <el-button @click="$router.back()">返回</el-button>
            </el-form-item>
        </el-form>
    </el-card>
</template>

<style scoped>
@import '@/assets/css/public.css';
</style>
