<script setup lang="ts">
import { Button, Card } from 'animal-island-vue';

defineProps<{
  ctx: Record<string, any>;
}>();
</script>

<template>
  <section class="practice-page" aria-labelledby="practice-room-title">
        <div class="practice-hero">
          <div>
            <p class="eyebrow">DEBATE ROOM</p>
            <h1 id="practice-room-title">辩论练习室</h1>
            <p class="hero-copy">这一步先完成可交互练习页面：孩子选题、选立场、使用提示卡发言，教练返回下一句建议。</p>
          </div>
          <div class="practice-hero-card" aria-label="练习页状态">
            <span>{{ ctx.activeChild?.avatar || '🏕️' }}</span>
            <strong>{{ ctx.currentTopic?.title }}</strong>
            <p>{{ ctx.activeChild?.name || '小辩手' }} · {{ ctx.currentSideLabel }}</p>
            <small v-if="ctx.activePracticeSessionId">会话 {{ ctx.activePracticeSessionId.slice(0, 8) }} · 多轮记录中</small>
          </div>
        </div>

        <div class="practice-layout">
          <Card class="practice-panel setup-panel" color="app-green">
            <div class="panel-title-row">
              <h2>练习设置</h2>
              <span v-if="ctx.isLoadingTopics" class="loading-pill">加载中</span>
            </div>

            <label class="field-label" for="practice-topic">选择辩题</label>
            <select id="practice-topic" v-model="ctx.selectedTopicId" class="select-box">
              <option v-for="topic in ctx.topics" :key="topic.id" :value="topic.id">{{ topic.title }}</option>
            </select>

            <p class="field-label side-label">选择立场</p>
            <div class="side-switcher" role="group" aria-label="选择正方或反方">
              <button :class="{ active: ctx.selectedSide === '正方' }" type="button" @click="ctx.selectedSide = '正方'">
                {{ ctx.currentTopic?.sideA }}
              </button>
              <button :class="{ active: ctx.selectedSide === '反方' }" type="button" @click="ctx.selectedSide = '反方'">
                {{ ctx.currentTopic?.sideB }}
              </button>
            </div>

            <div class="tips-box">
              <p class="field-label">开口提示卡</p>
              <button v-for="tip in ctx.tips" :key="tip" class="tip-chip" type="button" @click="ctx.applyTip(tip)">
                {{ tip }}
              </button>
            </div>
          </Card>

          <Card class="practice-panel debate-panel" color="app-blue">
            <div class="panel-title-row">
              <h2>对话练习</h2>
              <button class="ghost-button" type="button" @click="ctx.resetPractice">重新开始</button>
            </div>

            <div class="turn-list" aria-live="polite">
              <article v-for="(turn, index) in ctx.turns" :key="`${turn.speaker}-${index}`" :class="['turn-bubble', turn.speaker]">
                <span>{{ turn.badge }}</span>
                <p>{{ turn.text }}</p>
              </article>
              <article v-if="ctx.isLoadingReply" class="turn-bubble coach thinking">
                <span>小鹿教练</span>
                <p>我正在想一个温柔又有用的建议……</p>
              </article>
            </div>

            <div class="sentence-helper" aria-label="表达句式提示">
              <span>推荐句式</span>
              <strong>我认为……因为……例如……所以……</strong>
            </div>

            <div class="composer">
              <textarea
                v-model="ctx.draft"
                maxlength="1200"
                :placeholder="`我是${ctx.selectedSide}，我认为${ctx.currentSideLabel ?? ''}，因为……`"
                @keydown.ctrl.enter="ctx.submitArgument"
              />
              <div class="composer-actions">
                <span>{{ ctx.wordCount }}/1200</span>
                <Button type="primary" :disabled="!ctx.canSubmit" @click="ctx.submitArgument">
                  {{ ctx.isLoadingReply ? '教练思考中…' : '发送观点' }}
                </Button>
              </div>
            </div>
            <p v-if="ctx.error" class="error-text">{{ ctx.error }}</p>
          </Card>

          <Card class="practice-panel progress-panel" color="app-yellow">
            <h2>表达能量</h2>
            <div class="score-row">
              <span>清楚表达</span>
              <div class="meter"><span :style="{ width: `${ctx.rubric.clarity}%` }"></span></div>
              <strong>{{ ctx.rubric.clarity }}</strong>
            </div>
            <div class="score-row">
              <span>理由例子</span>
              <div class="meter"><span :style="{ width: `${ctx.rubric.evidence}%` }"></span></div>
              <strong>{{ ctx.rubric.evidence }}</strong>
            </div>
            <div class="score-row">
              <span>礼貌回应</span>
              <div class="meter"><span :style="{ width: `${ctx.rubric.manners}%` }"></span></div>
              <strong>{{ ctx.rubric.manners }}</strong>
            </div>

            <div class="voice-note">
              <strong>语音输入/输出联调</strong>
              <p>{{ ctx.voiceStatus }}</p>
              <div class="voice-action-row">
                <button v-if="!ctx.isRecording" type="button" @click="ctx.startRecording">🎙️ 开始录音</button>
                <button v-else type="button" @click="ctx.stopRecording">⏹️ 停止录音</button>
                <button type="button" :disabled="ctx.isSynthesizing" @click="ctx.playCoachVoice">
                  {{ ctx.isSynthesizing ? '合成中…' : '🔊 播放教练' }}
                </button>
                <button type="button" @click="ctx.stopCoachVoice">⏸️ 停止播放</button>
              </div>
              <div class="voice-slider-grid" aria-label="浏览器朗读参数">
                <label>
                  <span>语速 {{ speechRate.toFixed(2) }}</span>
                  <input v-model.number="speechRate" type="range" min="0.7" max="1.2" step="0.05" />
                </label>
                <label>
                  <span>音调 {{ speechPitch.toFixed(2) }}</span>
                  <input v-model.number="speechPitch" type="range" min="0.8" max="1.4" step="0.05" />
                </label>
              </div>
            </div>
          </Card>
        </div>
      </section>
</template>
