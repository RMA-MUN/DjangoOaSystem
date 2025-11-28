<script setup name="informList">
import pageHeader from '@/components/pageHeader.vue';
import { onMounted } from 'vue';
import { informs, handleDelete, handleEdit, initInforms } from '@/assets/js/list.js';
import { useAuthStore } from '@/stores/auth';
// 获取认证store
const authStore = useAuthStore();

// 组件挂载时初始化通知列表
onMounted(() => {
    initInforms();
});
</script>

<template>
    <pageHeader title="通知列表" />
    <el-card style="margin: 20px;">
        <template slot="header">
            <span>通知列表</span>
        </template>
        <el-table :data="informs" style="width: 100%" stripe="true">

            <el-table-column prop="title" label="通知标题" width="200">
                <template #default="scope">
                    <router-link :to="{ name: 'informDetail', params: { id: scope.row.id } }">{{ scope.row.title
                        }}</router-link>
                </template>
            </el-table-column>
            <el-table-column prop="content" label="内容预览" width="300">
                <template #default="scope">
                    <!-- 过滤掉html标签后，不显示图片等元素，只显示前20个文字 -->
                    <div v-html="scope.row.content.replace(/<[^>]+>/g, '').slice(0, 20) + '...'"></div>
                </template>
            </el-table-column>

            <el-table-column prop="author" label="发布者" width="100">
                <template #default="scope">
                    <!-- 部门+发布者 -->
                    【{{ scope.row.author?.username || '未命名发布者' }}】
                </template>
            </el-table-column>

            <el-table-column prop="departments" label="可见部门" width="200">
                <template #default="scope">
                    <div v-if="scope.row.departments && scope.row.departments.length > 0">
                        <el-tag v-for="dept in scope.row.departments" :key="dept.id" type="info">{{ dept.name
                        }}</el-tag>
                    </div>
                    <el-tag v-else type="info" size="small" class="department-tag">
                        所有部门
                    </el-tag>
                </template>
            </el-table-column>

            <el-table-column prop="create_time" label="创建时间" width="200">
                <template #default="scope">
                    <!-- 格式化创建时间 -->
                    {{ new Date(scope.row.create_time).toLocaleString('zh-CN', {
                        year: 'numeric', month: '2-digit', day:
                            '2-digit', hour: '2-digit', minute: '2-digit'
                    }) }}
                </template>
            </el-table-column>

            <el-table-column prop="actions" label="操作" width="150"
                v-if="authStore.isAdmin || authStore.user?.uuid && informs.some(item => item.author?.uuid === authStore.user.uuid)">
                <template #default="scope">
                    <el-tag type="primary" size="mini"
                        v-if="authStore.isAdmin || (authStore.user?.uuid && scope.row.author?.uuid === authStore.user.uuid)"
                        @click="handleEdit(scope.row)">编辑</el-tag>
                    <el-tag type="danger" size="mini"
                        v-if="authStore.isAdmin || (authStore.user?.uuid && scope.row.author?.uuid === authStore.user.uuid)"
                        @click="handleDelete(scope.row)">删除</el-tag>
                </template>
            </el-table-column>

        </el-table>
    </el-card>
</template>

<style scoped>
@import '@/assets/css/list.css';
</style>
