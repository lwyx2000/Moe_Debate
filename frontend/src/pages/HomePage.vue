<script setup lang="ts">
import { Button, Card } from 'animal-island-vue';

defineProps<{
  ctx: Record<string, any>;
}>();
</script>

<template>
  <section id="top" class="hero-section" aria-labelledby="home-title">
        <div class="hero-content">
          <p class="eyebrow">MOE DEBATE ISLAND</p>
          <h1 id="home-title">让孩子在小岛上，勇敢说出自己的理由</h1>
          <p class="hero-copy">
            萌辩岛是儿童辩论练习主页：用动森风格的温暖界面，把观点表达、理由举例和礼貌回应变成一次轻松闯关。
          </p>

          <div class="hero-actions">
            <Button type="primary" @click="ctx.openPractice">进入练习页</Button>
            <a class="secondary-action" href="#practice-preview" @click.prevent="ctx.scrollToPracticePreview">先看看预览</a>
          </div>

          <dl class="hero-stats" aria-label="首页能力概览">
            <div>
              <dt>3 步</dt>
              <dd>完成一次表达练习</dd>
            </div>
            <div>
              <dt>3 项</dt>
              <dd>儿童友好反馈维度</dd>
            </div>
            <div>
              <dt>本地</dt>
              <dd>预留语音输入输出</dd>
            </div>
          </dl>
        </div>

        <div class="hero-island" aria-label="萌辩岛首页插画">
          <div class="sun">☀️</div>
          <div class="cloud cloud-one">☁️</div>
          <div class="cloud cloud-two">☁️</div>
          <div class="island-card">
            <div class="mascot">🦌</div>
            <div class="speech-card">
              <strong>今日任务</strong>
              <span>说出 1 个观点 + 1 个理由 + 1 个例子</span>
            </div>
            <div class="path-stones" aria-hidden="true">
              <span></span>
              <span></span>
              <span></span>
            </div>
          </div>
        </div>
      </section>

      <section id="journey" class="section-block" aria-labelledby="journey-title">
        <div class="section-heading">
          <p class="eyebrow">HOW IT WORKS</p>
          <h2 id="journey-title">主页先讲清楚：孩子怎么开始一场辩论</h2>
        </div>
        <div class="journey-grid">
          <Card v-for="step in ctx.journeySteps" :key="step.index" class="step-card" color="app-yellow">
            <span class="step-index">{{ step.index }}</span>
            <h3>{{ step.title }}</h3>
            <p>{{ step.description }}</p>
          </Card>
        </div>
      </section>

      <section id="practice-preview" class="practice-preview" aria-labelledby="practice-title">
        <Card class="practice-card" color="app-blue">
          <div class="section-heading compact">
            <p class="eyebrow">PRACTICE PREVIEW</p>
            <h2 id="practice-title">下一个页面：辩论练习室</h2>
            <p>练习页已加入页面切换：孩子可以选择辩题、选择正反方、套用提示卡、提交观点并收到教练反馈。</p>
          </div>

          <div class="preview-board">
            <div class="topic-ticket">
              <span>🎮</span>
              <div>
                <strong>周末能不能多玩一小时游戏？</strong>
                <p>选择正方或反方，再用提示卡开口。</p>
              </div>
              <Button type="primary" @click="ctx.openPractice">打开练习页</Button>
            </div>
            <div class="chat-preview" aria-label="教练反馈示例">
              <article v-for="message in ctx.coachMessages" :key="message.text" :class="['preview-bubble', message.role]">
                <span>{{ message.badge }}</span>
                <p>{{ message.text }}</p>
              </article>
            </div>
            <div class="rubric-preview" aria-label="表达能量示例">
              <div>
                <span>清楚表达</span>
                <strong>86</strong>
              </div>
              <div>
                <span>理由例子</span>
                <strong>74</strong>
              </div>
              <div>
                <span>礼貌回应</span>
                <strong>90</strong>
              </div>
            </div>
          </div>
        </Card>
      </section>

      <section id="topics" class="section-block" aria-labelledby="topics-title">
        <div class="section-heading">
          <p class="eyebrow">TOPICS</p>
          <h2 id="topics-title">首页展示的精选儿童辩题</h2>
        </div>
        <div class="topic-grid">
          <Card v-for="topic in ctx.featuredTopics" :key="topic.title" class="topic-card" color="app-green">
            <span class="topic-emoji">{{ topic.emoji }}</span>
            <h3>{{ topic.title }}</h3>
            <div class="side-pill positive">{{ topic.positive }}</div>
            <div class="side-pill negative">{{ topic.negative }}</div>
          </Card>
        </div>
      </section>

      <section id="voice" class="voice-strip" aria-labelledby="voice-title">
        <div>
          <p class="eyebrow">VOICE READY</p>
          <h2 id="voice-title">语音能力先在首页说明，不抢主流程</h2>
          <p>主页面只展示规划：后续练习页接入浏览器录音，后端统一封装 Qwen3-ASR-0.6B 识别和 Kitten-TTS-Server 合成。</p>
        </div>
        <div class="voice-badges" aria-label="语音方案标签">
          <span>🎙️ Qwen3-ASR 输入</span>
          <span>🔊 Kitten TTS 输出</span>
          <span>⚡ Moonshine 备选实时 Agent</span>
        </div>
      </section>
</template>
