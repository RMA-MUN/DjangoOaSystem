<script setup name="PageHeader">
import { useRouter } from 'vue-router'

const router = useRouter()

const goBack = () => {
    router.go(-1);
}

const props = defineProps({
    title: {
        type: String,
        default: '返回'
    }
})
</script>

<template>
    <el-page-header :icon="ArrowLeft" title="返回" @click="goBack">
        <template #content>
            <span class="text-large font-600 mr-3"> {{ title }} </span>
        </template>
    </el-page-header>

</template>
