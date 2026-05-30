<script setup lang="ts">
import type { PageMode } from '../router';
import type { UserAccount } from '../types';

defineProps<{
  page: PageMode;
  currentUser: UserAccount | null;
}>();

const emit = defineEmits<{
  navigate: [page: PageMode];
  signOut: [];
}>();
</script>

<template>
  <nav class="top-nav" aria-label="主导航">
    <button class="brand nav-button" type="button" aria-label="萌辩岛首页" @click="emit('navigate', 'home')">
      <span class="brand-mark">🦌</span>
      <span>萌辩岛</span>
    </button>
    <div class="nav-links">
      <a v-if="page === 'home'" href="#journey">练习流程</a>
      <button class="nav-button" type="button" @click="emit('navigate', 'practice')">练习页</button>
      <button class="nav-button" type="button" @click="emit('navigate', 'topicLibrary')">题库页</button>
      <button class="nav-button" type="button" @click="emit('navigate', 'profiles')">孩子档案</button>
      <button class="nav-button" type="button" @click="emit('navigate', 'history')">练习历史</button>
      <button class="nav-button" type="button" @click="emit('navigate', 'report')">成长报告</button>
      <button class="nav-button" type="button" @click="emit('navigate', 'voiceSetup')">语音设置</button>
      <button v-if="page !== 'home'" class="nav-button" type="button" @click="emit('navigate', 'home')">返回主页</button>
      <button v-if="currentUser" class="nav-button" type="button" @click="emit('signOut')">退出 {{ currentUser.displayName }}</button>
    </div>
  </nav>
</template>
