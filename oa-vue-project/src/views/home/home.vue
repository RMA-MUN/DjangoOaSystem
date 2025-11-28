<script setup name="Home">
import pageHeader from '@/components/pageHeader.vue'
import { useHomeLogic } from '@/assets/js/home.js'

// 使用从外部JS导入的逻辑
const {
    title,
    department_staff_count,
    isLoading,
    latestInforms,
    latestAttendances,
    tableData,
    formatDate,
    stripHtml
} = useHomeLogic()
</script>

<template>
    <el-card class="card-container">
        <div id="staff_count_chart" class="staff-chart-container"></div>
        <!-- 最新通知和考勤列表容器 -->
        <div class="list-container">
            <!-- 最新通知列表 -->
            <div class="list-card">
                <div class="list-title">
                    <h3>最新通知</h3>
                </div>
                <div v-if="latestInforms.length > 0" class="list-content">
                    <div v-for="(inform, index) in latestInforms" :key="index" class="inform-item">
                        <a :href="'/inform/detail/' + (inform.id || 0)" class="inform-link">
                            <div class="inform-title">{{ inform.title || '通知标题' }}</div>
                        </a>
                        <div class="inform-text">{{ stripHtml(inform.content) || '暂无内容' }}</div>
                        <div class="inform-date">{{ formatDate(inform.create_time || new Date()) }}</div>
                    </div>
                </div>
                <div v-else class="empty-tip">
                    暂无最新通知
                </div>
            </div>

            <!-- 最新考勤列表 -->
            <div class="list-card">
                <div class="list-title">
                    <h3>最新考勤</h3>
                </div>
                <el-table :data="tableData" stripe style="width: 100%">
                    <el-table-column prop="date" label="考勤日期" width="180" />
                    <el-table-column prop="name" label="员工姓名" width="180" />
                    <el-table-column prop="address" label="考勤类型" />
                </el-table>
                <div v-if="tableData.length === 0" class="empty-tip">
                    暂无最新考勤记录
                </div>
            </div>
        </div>
    </el-card>
</template>

<style scoped>
/* 导入外部CSS */
@import "@/assets/css/home.css";
</style>
