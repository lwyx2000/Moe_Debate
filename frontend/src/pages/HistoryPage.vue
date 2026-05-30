<script setup lang="ts">
import { Button, Card } from 'animal-island-vue';

defineProps<{
  ctx: Record<string, any>;
}>();
</script>

<template>
  <section class="simple-page" aria-labelledby="history-title">
    <div class="simple-hero">
      <p class="eyebrow">PRACTICE HISTORY</p>
      <h1 id="history-title">练习历史</h1>
      <p class="hero-copy">{{ ctx.activeChild?.avatar }} {{ ctx.activeChild?.name || '当前孩子' }}：{{ ctx.historyStatus }}</p>
      <Button type="primary" :disabled="ctx.isLoadingSessions" @click="ctx.loadSessions">
        {{ ctx.isLoadingSessions ? '刷新中…' : '刷新历史' }}
      </Button>
    </div>

    <div class="topic-filter-bar enhanced history-filter-bar">
      <label>
        <span>时间范围</span>
        <select :value="ctx.sessionFilters.range" @change="ctx.updateSessionRange(($event.target as HTMLSelectElement).value)">
          <option value="week">本周</option>
          <option value="month">本月</option>
          <option value="all">全部</option>
          <option value="custom">自定义</option>
        </select>
      </label>
      <label>
        <span>开始日期</span>
        <input :value="ctx.sessionFilters.dateFrom" type="date" @input="ctx.updateSessionFilter('dateFrom', ($event.target as HTMLInputElement).value)" />
      </label>
      <label>
        <span>结束日期</span>
        <input :value="ctx.sessionFilters.dateTo" type="date" @input="ctx.updateSessionFilter('dateTo', ($event.target as HTMLInputElement).value)" />
      </label>
      <label>
        <span>题目</span>
        <select :value="ctx.sessionFilters.topicId" @change="ctx.updateSessionFilter('topicId', ($event.target as HTMLSelectElement).value)">
          <option value="">全部题目</option>
          <option v-for="topic in ctx.topics" :key="topic.id" :value="topic.id">{{ topic.title }}</option>
        </select>
      </label>
      <label>
        <span>分类</span>
        <select :value="ctx.sessionFilters.collectionId" @change="ctx.updateSessionFilter('collectionId', ($event.target as HTMLSelectElement).value)">
          <option value="">全部分类</option>
          <option v-for="collection in ctx.topicCollections" :key="collection.id" :value="collection.id">{{ collection.title }}</option>
        </select>
      </label>
    </div>

    <div v-if="ctx.sessions.length === 0" class="empty-state">
      <span>📝</span>
      <h2>还没有练习记录</h2>
      <p>去辩论练习室提交一次观点，后端会自动保存历史。</p>
      <Button type="primary" @click="ctx.openPractice">去练习</Button>
    </div>

    <div v-else class="history-list">
      <Card v-for="session in ctx.sessions" :key="session.id" class="history-card" color="app-blue">
        <div class="history-card-head">
          <div>
            <span class="history-time">{{ ctx.formatSessionTime(session.startedAt || session.createdAt) }} · {{ session.durationMinutes }} 分钟 · {{ session.totalTurns }} 轮</span>
            <h2>{{ ctx.topics.find((topic) => topic.id === session.topicId)?.title ?? session.topicId }} · {{ session.side }}</h2>
            <p v-if="session.summary" class="history-summary">{{ session.summary }}</p>
          </div>
          <div class="history-scores">
            <span>清楚 {{ session.rubric.clarity }}</span>
            <span>例子 {{ session.rubric.evidence }}</span>
            <span>礼貌 {{ session.rubric.manners }}</span>
          </div>
        </div>
        <div class="history-copy">
          <template v-for="turn in session.conversation" :key="`${session.id}-${turn.badge}-${turn.text}`">
            <strong>{{ turn.badge || (turn.speaker === 'kid' ? '我的观点' : '教练反馈') }} <small v-if="turn.source">{{ turn.source }}</small></strong>
            <p>{{ turn.text }}</p>
          </template>
        </div>
      </Card>
    </div>
  </section>
</template>
