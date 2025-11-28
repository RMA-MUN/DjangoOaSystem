import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { get_department_staff_count, get_latest_inform, get_latest_attendance } from "@/api/homeHttp.js"
import * as echarts from 'echarts';

// 导出home组件的组合式API
export function useHomeLogic() {
    // 声明变量
    let myChart = null;
    const title = ref('首页')
    const department_staff_count = ref(0)
    const isLoading = ref(true)
    // 状态管理
    const latestInforms = ref([])
    const latestAttendances = ref([])
    const tableData = ref([])

    onMounted(() => {
        // 初始化ECharts
        initECharts()

        // 初始化最新通知
        initLatestInform()

        // 初始化最新考勤
        initLatestAttendance()

        // 单独处理API请求，使用Promise.race实现超时控制
        fetchDataWithTimeout()
    })


    function initLatestInform() {
        get_latest_inform().then(data => {
            console.log('最新通知:', data);
            // 处理最新通知数据，更新到页面
            // 去重返回 - 基于id字段去重，如果没有id则使用其他唯一标识字段
            const informsArray = data.data || [];
            const uniqueInforms = Array.from(
                informsArray.reduce((map, item) => {
                    // 使用id作为唯一标识，如果没有id字段可以改为其他唯一标识字段
                    const key = item.id || JSON.stringify(item);
                    map.set(key, item);
                    return map;
                }, new Map())
            ).map(([_, value]) => value);
            // 输出调试信息
            console.log('去重后的最新通知:', uniqueInforms);

            // 将去重后的通知数据保存到响应式引用中
            latestInforms.value = uniqueInforms;

        }).catch(error => {
            console.error('获取最新通知失败:', error);
            ElMessage.error(error.message || '获取最新通知失败');
        });
    }

    // 格式化日期显示
    function formatDate(date) {
        if (!date) return '';
        const d = new Date(date);
        return d.toLocaleDateString('zh-CN', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit'
        });
    }

    // 过滤HTML标签
    function stripHtml(html) {
        if (!html) return '';
        // 使用正则表达式去除所有HTML标签
        return html.replace(/<[^>]*>/g, '').trim();
    }

    function initLatestAttendance() {
        // 调用API接口获取到最新的请假数据
        get_latest_attendance().then(data => {
            console.log('最新考勤:', data);
            // 处理最新考勤数据，更新到页面
            // 去重返回 - 基于id字段去重，如果没有id则使用其他唯一标识字段
            const attendanceArray = data.data || [];
            const uniqueAttendance = Array.from(
                attendanceArray.reduce((map, item) => {
                    // 使用id作为唯一标识，如果没有id字段可以改为其他唯一标识字段
                    const key = item.id || JSON.stringify(item);
                    map.set(key, item);
                    return map;
                }, new Map())
            ).map(([_, value]) => value);
            // 输出调试信息
            console.log('去重后的最新考勤:', uniqueAttendance);
            // 保存到响应式变量
            latestAttendances.value = uniqueAttendance;

            // 转换为表格数据格式
            tableData.value = uniqueAttendance.map(item => ({
                date: formatDate(item.create_time || item.createDate || item.created_at),
                name: item.requester_name || '未知员工',
                address: item.attendance_type?.name || '未知类型'
            }));
        }).catch(error => {
            console.error('获取最新考勤失败:', error);
            ElMessage.error(error.message || '获取最新考勤失败');
        });
    }

    // 初始化ECharts图表
    function initECharts() {
        const chartDom = document.getElementById('staff_count_chart');
        if (chartDom) {
            myChart = echarts.init(chartDom);

            // 设置默认空数据的图表配置
            const defaultOption = {
                title: {
                    text: '部门人员统计'
                },
                tooltip: {},
                xAxis: {
                    data: []
                },
                yAxis: {},
                series: [
                    {
                        name: '人数',
                        type: 'bar',
                        data: []
                    }
                ]
            };

            myChart.setOption(defaultOption);
        } else {
            console.error('ECharts DOM element not found');
        }
    }

    // 带超时控制的数据获取
    function fetchDataWithTimeout() {
        // 设置5秒的请求超时
        const timeoutPromise = new Promise((_, reject) => {
            setTimeout(() => {
                reject(new Error('请求超时，请稍后重试'));
            }, 5000);
        });

        // 使用Promise.race进行超时控制
        Promise.race([get_department_staff_count(), timeoutPromise])
            .then(data => {
                console.log('API响应数据:', data);
                department_staff_count.value = data.data || 0;

                // 如果有数据，更新图表
                if (myChart && data.data) {
                    // 根据实际返回的数据结构更新图表
                    // 这里根据实际返回数据格式调整
                    updateChartData(data);
                }
            })
            .catch(error => {
                console.error('API请求错误:', error);
                // 提供友好的错误提示
                ElMessage.error(error.message || '获取数据失败，请检查网络连接');
            })
            .finally(() => {
                // 无论成功失败，都结束加载状态
                isLoading.value = false;
            });
    }

    // 更新图表数据
    function updateChartData(data) {
        // 确保data.data是数组格式
        const departmentsData = Array.isArray(data.data) ? data.data : [];

        // 从数组中提取部门名称作为x轴数据
        const departmentNames = departmentsData.map(item => item.name);

        // 从数组中提取人员数量作为系列数据
        const staffCounts = departmentsData.map(item => item.staff_count);

        // 构建完整的图表配置
        const option = {
            tooltip: {
                trigger: 'axis',
                axisPointer: {
                    type: 'shadow'
                }
            },
            xAxis: {
                type: 'category',
                data: departmentNames,
                axisLabel: {
                    interval: 0,
                    rotate: 30
                }
            },
            yAxis: {
                type: 'value',
                name: '人员数量',
                minInterval: 1 // 确保Y轴只显示整数
            },
            series: [
                {
                    name: '人员数量',
                    type: 'bar',
                    data: staffCounts,
                    itemStyle: {
                        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                            { offset: 0, color: '#83bff6' },
                            { offset: 0.5, color: '#188df0' },
                            { offset: 1, color: '#188df0' }
                        ])
                    },
                    emphasis: {
                        itemStyle: {
                            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                                { offset: 0, color: '#2378f7' },
                                { offset: 0.7, color: '#2378f7' },
                                { offset: 1, color: '#83bff6' }
                            ])
                        }
                    },
                    label: {
                        show: true,
                        position: 'top',
                        formatter: '{c}'
                    }
                }
            ]
        };

        myChart.setOption(option);
    }

    // 导出需要在模板中使用的变量和方法
    return {
        title,
        department_staff_count,
        isLoading,
        latestInforms,
        latestAttendances,
        tableData,
        formatDate,
        stripHtml
    }
}