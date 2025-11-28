<template>
  <div class="login-container">
    <main class="form-signin">
      <form @submit.prevent="handleLogin">
        <img
          src="@/assets/logo.svg"
          class="login-logo mx-auto d-block"
          alt="系统登录"
        />
        <h1 class="login-title text-center">
          用户登录
        </h1>

        <div class="mb-4 form-group">
          <label 
            for="email" 
            class="form-label"
            :class="{ 'floating': formData.email || isEmailFocused }"
          >
            邮箱地址
          </label>
          <input
            id="email"
            v-model="formData.email"
            type="email"
            class="form-control"
            placeholder="邮箱地址"
            @input="clearError"
            @focus="isEmailFocused = true"
            @blur="isEmailFocused = false"
            required
            autocomplete="email"
          />
        </div>

        <div class="mb-4 form-group">
          <label 
            for="password" 
            class="form-label"
            :class="{ 'floating': formData.password || isPasswordFocused }"
          >
            密码
          </label>
          <input
            id="password"
            v-model="formData.password"
            type="password"
            class="form-control"
            placeholder="密码"
            @input="clearError"
            @focus="isPasswordFocused = true"
            @blur="isPasswordFocused = false"
            required
            autocomplete="current-password"
            @keyup.enter="handleLogin"
          />
        </div>

        <div class="d-flex justify-content-between align-items-center mb-4">
          <div class="checkbox">
            <label class="text-sm">
              <input
                type="checkbox"
                value="remember-me"
                v-model="formData.rememberMe"
              />
              记住我
            </label>
          </div>
        </div>

        <button
          class="w-100 btn btn-lg btn-primary mb-3"
          type="submit"
          :disabled="isLoading"
        >
          {{ isLoading ? '登录中...' : '登录' }}
        </button>

        <!-- 错误信息显示 -->
        <div v-if="errorMessage" class="error-message">
          {{ errorMessage }}
        </div>

        <!-- 成功信息显示 -->
        <div v-if="successMessage" class="success-message">
          {{ successMessage }}
        </div>
      </form>
    </main>
  </div>
</template>

<script setup>
import 'element-plus/dist/index.css'
import '@/assets/css/login.css'
import { setupLoginComponent } from '@/assets/js/login-component.js'
import { useAuthStore } from '@/stores/auth.js'
import { ref } from 'vue'

const { formData, isLoading, errorMessage, successMessage, clearError, handleLogin } = 
  setupLoginComponent()

// 添加输入框焦点状态管理
const isEmailFocused = ref(false)
const isPasswordFocused = ref(false)
</script>
