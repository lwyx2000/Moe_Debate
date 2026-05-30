<script setup lang="ts">
import { Button, Card } from 'animal-island-vue';

defineProps<{
  ctx: Record<string, any>;
}>();
</script>

<template>
  <section class="simple-page report-export-root" aria-labelledby="report-title">
    <div class="simple-hero">
      <p class="eyebrow">GROWTH REPORT</p>
      <h1 id="report-title">成长报告</h1>
      <p class="hero-copy">{{ ctx.reportSummary.weekLabel }}：{{ ctx.reportSummary.childName }} 已完成 {{ ctx.reportSummary.completedDebates }} 次练习，连续练习 {{ ctx.reportSummary.streakDays }} 天。</p>
      <div class="topic-card-actions">
        <Button type="primary" @click="ctx.exportReportPdf">导出 PDF 报告</Button>
      </div>
    </div>

    <div class="topic-filter-bar enhanced history-filter-bar no-print">
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

    <div class="simple-grid report-grid">
      <Card class="report-card" color="app-blue">
        <span class="simple-icon">⏱️</span>
        <h2>总练习时长</h2>
        <strong>{{ ctx.reportSummary.totalPracticeMinutes }} 分钟</strong>
        <p>{{ ctx.reportSummary.activeDays }} 个真实练习日。</p>
      </Card>
      <Card v-for="item in ctx.reportItems" :key="item.title" class="report-card" color="app-yellow">
        <span class="simple-icon">{{ item.icon }}</span>
        <h2>{{ item.title }}</h2>
        <strong>{{ item.value }}</strong>
        <p>{{ item.hint }}</p>
      </Card>
    </div>

    <Card class="wide-card" color="app-green">
      <div>
        <p class="eyebrow">WEAK SPOT</p>
        <h2>最近弱项：{{ ctx.reportWeakSpot }}</h2>
        <p>{{ ctx.reportCoachNote }}</p>
      </div>
      <Button type="primary" @click="ctx.practiceRecommendedTopic">练推荐题</Button>
    </Card>

    <Card class="wide-card trend-card" color="app-blue">
      <div>
        <p class="eyebrow">TREND</p>
        <h2>能力趋势图</h2>
        <div class="trend-grid">
          <div v-for="point in ctx.reportTrend" :key="point.label" class="trend-point">
            <span>{{ point.label }}</span>
            <i :style="{ height: `${point.clarity}%` }" title="清楚表达"></i>
            <i :style="{ height: `${point.evidence}%` }" title="理由例子"></i>
            <i :style="{ height: `${point.manners}%` }" title="礼貌回应"></i>
          </div>
        </div>
      </div>
    </Card>

    <div class="simple-grid report-grid">
      <Card class="report-card" color="app-green">
        <span class="simple-icon">🎯</span>
        <h2>推荐下一题</h2>
        <strong>{{ ctx.reportRecommendedTopic.title || '先完成一次练习' }}</strong>
        <p>根据最近已练题目和弱项自动推荐。</p>
      </Card>
      <Card class="report-card" color="app-yellow">
        <span class="simple-icon">👨‍👩‍👧</span>
        <h2>家长评语</h2>
        <p>{{ ctx.reportParentComment }}</p>
      </Card>
      <Card class="report-card" color="app-blue">
        <span class="simple-icon">👩‍🏫</span>
        <h2>老师评语</h2>
        <p>{{ ctx.reportTeacherComment }}</p>
      </Card>
    </div>

    <Card class="wide-card" color="app-green">
      <div>
        <p class="eyebrow">NEXT GOAL</p>
        <h2>下一步目标：{{ ctx.reportNextGoal }}</h2>
      </div>
      <Button type="primary" @click="ctx.openPractice">去练一次</Button>
    </Card>
  </section>
</template>
