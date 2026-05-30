<script setup lang="ts">
import { Button, Card } from 'animal-island-vue';

defineProps<{
  authMode: 'login' | 'register';
  authEmail: string;
  authPassword: string;
  authDisplayName: string;
  authStatus: string;
}>();

const emit = defineEmits<{
  'update:authMode': [value: 'login' | 'register'];
  'update:authEmail': [value: string];
  'update:authPassword': [value: string];
  'update:authDisplayName': [value: string];
  submit: [];
  demo: [];
}>();
</script>

<template>
  <section class="simple-page" aria-labelledby="auth-title">
    <div class="simple-hero">
      <p class="eyebrow">AUTH</p>
      <h1 id="auth-title">登录萌辩岛</h1>
      <p class="hero-copy">{{ authStatus }}</p>
    </div>
    <Card class="topic-admin-card auth-card" color="app-green">
      <div class="auth-mode-row">
        <button type="button" :class="{ active: authMode === 'login' }" @click="emit('update:authMode', 'login')">登录</button>
        <button type="button" :class="{ active: authMode === 'register' }" @click="emit('update:authMode', 'register')">注册家长账号</button>
      </div>
      <div class="admin-form-grid">
        <label>
          <span>邮箱</span>
          <input :value="authEmail" type="email" @input="emit('update:authEmail', ($event.target as HTMLInputElement).value)" />
        </label>
        <label v-if="authMode === 'register'">
          <span>显示名称</span>
          <input :value="authDisplayName" @input="emit('update:authDisplayName', ($event.target as HTMLInputElement).value)" />
        </label>
        <label>
          <span>密码</span>
          <input :value="authPassword" type="password" @input="emit('update:authPassword', ($event.target as HTMLInputElement).value)" @keydown.enter="emit('submit')" />
        </label>
      </div>
      <div class="integration-footer">
        <span>后台权限 Demo：demo@example.com / demo123456</span>
        <div class="topic-card-actions">
          <button type="button" @click="emit('demo')">使用 Demo 登录</button>
          <Button type="primary" @click="emit('submit')">{{ authMode === 'login' ? '登录' : '注册并登录' }}</Button>
        </div>
      </div>
    </Card>
  </section>
</template>
