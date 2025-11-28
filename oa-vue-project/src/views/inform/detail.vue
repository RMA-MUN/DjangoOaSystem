<script setup name="informDetail">
import pageHeader from '@/components/pageHeader.vue';
import { onMounted } from 'vue';
import { useRoute } from 'vue-router';
import { ElMessage } from 'element-plus';
import { formatTime, informDetail, initInformDetail } from '@/assets/js/detail.js';
import { useAuthStore } from '@/stores/auth';
// 获取认证store
const authStore = useAuthStore();
// 获取路由实例
const route = useRoute();

// 组件挂载时初始化通知详情
onMounted(() => {
  const id = route.params.id;
  if (id) {
    initInformDetail(id);
  } else {
    console.error('未找到通知ID');
    ElMessage.error('未找到通知ID');
  }
});
</script>

<template>
  <pageHeader title="通知详情" />
  <el-card style="margin: 20px;">
    <template #header>
      <span>通知详情</span>
    </template>

    <!-- 通知标题区域 -->
    <div class="title-section">
      <h2 class="inform-title">{{ informDetail.title }}</h2>
    </div>

    <!-- 元信息区域 -->
    <div class="meta-section">
      <!-- 发布人信息 -->
      <div class="meta-item">
        <span class="meta-label">发布人：</span>
        <span class="meta-value">
          【{{ informDetail.author?.username || '未命名发布者' }}】
        </span>
      </div>

      <!-- 可见部门 -->
      <div class="meta-item">
        <span class="meta-label">可见部门：</span>
        <div class="departments-container">
          <el-tag v-for="(dept, index) in (informDetail.departments || [])" :key="index" size="small"
            class="department-tag">
            {{ dept.name || dept }}
          </el-tag>
          <el-tag v-if="!informDetail.departments || informDetail.departments.length === 0" size="small"
            class="department-tag">
            全体部门
          </el-tag>
        </div>
      </div>

      <!-- 发布时间 -->
      <div class="meta-item">
        <span class="meta-label">发布时间：</span>
        <span class="meta-value">{{ formatTime(informDetail.create_time) }}</span>
      </div>
    </div>

    <!-- 内容区域 -->
    <div class="content-section">
      <div class="content-body" v-html="informDetail.content || '暂无内容'"></div>
    </div>
  </el-card>
</template>



<style scoped>
@import '@/assets/css/detail.css';
</style>
