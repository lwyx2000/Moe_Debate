<script setup lang="ts">
import { Button, Card } from 'animal-island-vue';

defineProps<{
  ctx: Record<string, any>;
}>();
</script>

<template>
  <section class="simple-page" aria-labelledby="voice-setup-title">
        <div class="simple-hero">
          <p class="eyebrow">VOICE SETUP</p>
          <h1 id="voice-setup-title">语音设置</h1>
          <p class="hero-copy">语音页先做产品级说明和接入步骤，后续再把录音权限、识别状态、音色选择和播放控件接到真实接口。</p>
        </div>

        <div class="voice-flow-grid">
          <Card v-for="(step, index) in ctx.voiceSteps" :key="step.title" class="voice-step-card" color="app-blue">
            <span class="step-index">0{{ index + 1 }}</span>
            <h2>{{ step.title }}</h2>
            <strong>{{ step.engine }}</strong>
            <p>{{ step.description }}</p>
          </Card>
        </div>

        <Card class="wide-card" color="app-yellow">
          <div>
            <p class="eyebrow">SAFE BY DEFAULT</p>
            <h2>儿童语音默认不保存原始音频</h2>
            <p>页面会明确显示录音状态；如后续要保存音频，需要增加家长授权、删除入口和隐私提示。</p>
          </div>
          <Button type="primary" @click="ctx.openPractice">返回练习页</Button>
        </Card>

        <Card class="integration-card" color="app-green">
          <div class="section-heading compact">
            <p class="eyebrow">MODEL CONFIG</p>
            <h2>模型服务配置</h2>
            <p>{{ ctx.integrationStatus }}</p>
          </div>

          <div class="integration-grid">
            <div v-for="provider in ctx.providerKeys" :key="provider" class="provider-config">
              <label class="toggle-row">
                <input
                  type="checkbox"
                  :checked="ctx.integrationSettings[provider].enabled"
                  @change="ctx.updateProvider(provider, { enabled: ($event.target as HTMLInputElement).checked })"
                />
                <strong>{{ ctx.providerLabels[provider] }}</strong>
              </label>

              <label>
                <span>服务地址</span>
                <input
                  :value="ctx.integrationSettings[provider].baseUrl"
                  type="text"
                  @input="ctx.updateProvider(provider, { baseUrl: ($event.target as HTMLInputElement).value })"
                />
              </label>
              <label>
                <span>模型名</span>
                <input
                  :value="ctx.integrationSettings[provider].model"
                  type="text"
                  @input="ctx.updateProvider(provider, { model: ($event.target as HTMLInputElement).value })"
                />
              </label>
              <label>
                <span>API Key（本地可留空）</span>
                <input
                  :value="ctx.integrationSettings[provider].apiKey"
                  type="password"
                  autocomplete="off"
                  @input="ctx.updateProvider(provider, { apiKey: ($event.target as HTMLInputElement).value })"
                />
              </label>
            </div>
          </div>

          <div class="integration-footer">
            <span>更新时间：{{ ctx.integrationSettings.updatedAt || '尚未保存' }}</span>
            <Button type="primary" :disabled="ctx.isSavingIntegrations" @click="ctx.persistIntegrationSettings">
              {{ ctx.isSavingIntegrations ? '保存中…' : '保存模型配置' }}
            </Button>
          </div>
        </Card>
      </section>
</template>
