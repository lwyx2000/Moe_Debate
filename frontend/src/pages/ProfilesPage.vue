<script setup lang="ts">
import { Button, Card } from 'animal-island-vue';

defineProps<{
  ctx: Record<string, any>;
}>();
</script>

<template>
  <section class="simple-page" aria-labelledby="profiles-title">
        <div class="simple-hero">
          <p class="eyebrow">CHILD PROFILES</p>
          <h1 id="profiles-title">多孩子档案</h1>
          <p class="hero-copy">当前练习对象：{{ ctx.activeChild?.avatar }} {{ ctx.activeChild?.name || '未选择孩子' }}。切换孩子后，练习历史和成长报告会按孩子单独筛选。</p>
        </div>

        <div class="simple-grid profile-grid">
          <Card v-for="child in ctx.childProfiles" :key="child.id" class="profile-card" color="app-blue">
            <span class="simple-icon">{{ child.avatar }}</span>
            <h2>{{ child.name }}</h2>
            <p>{{ child.age }} 岁 · {{ child.grade }}</p>
            <p>{{ child.debateGoal }}</p>
            <div class="topic-card-actions">
              <button type="button" @click="ctx.selectActiveChild(child.id)">{{ ctx.activeChildId === child.id ? '当前孩子' : '设为当前' }}</button>
              <button type="button" @click="ctx.editChildProfile(child)">编辑</button>
            </div>
          </Card>
        </div>

        <Card class="topic-admin-card" color="app-green">
          <div class="section-heading compact">
            <p class="eyebrow">PROFILE FORM</p>
            <h2>孩子档案管理</h2>
            <p>{{ ctx.childProfileStatus }}</p>
          </div>
          <div class="admin-form-grid">
            <label>
              <span>孩子 ID</span>
              <input :value="ctx.childProfileForm.id" placeholder="例如 child-luna" @input="ctx.childProfileForm.id = ($event.target as HTMLInputElement).value" />
            </label>
            <label>
              <span>姓名</span>
              <input :value="ctx.childProfileForm.name" placeholder="例如 小鹿" @input="ctx.childProfileForm.name = ($event.target as HTMLInputElement).value" />
            </label>
            <label>
              <span>年龄</span>
              <input :value="ctx.childProfileForm.age" type="number" min="3" max="18" @input="ctx.childProfileForm.age = Number(($event.target as HTMLInputElement).value)" />
            </label>
            <label>
              <span>年级</span>
              <input :value="ctx.childProfileForm.grade" placeholder="例如 二年级" @input="ctx.childProfileForm.grade = ($event.target as HTMLInputElement).value" />
            </label>
            <label>
              <span>头像 Emoji</span>
              <input :value="ctx.childProfileForm.avatar" placeholder="🦊" @input="ctx.childProfileForm.avatar = ($event.target as HTMLInputElement).value" />
            </label>
            <label class="wide-field">
              <span>练习目标</span>
              <textarea :value="ctx.childProfileForm.debateGoal" rows="3" @input="ctx.childProfileForm.debateGoal = ($event.target as HTMLTextAreaElement).value"></textarea>
            </label>
          </div>
          <div class="integration-footer">
            <span>保存后会写入后端 MySQL；当前孩子会自动切换为刚保存的档案。</span>
            <div class="topic-card-actions">
              <button type="button" @click="ctx.resetChildProfileForm">新增档案</button>
              <button type="button" :disabled="!ctx.childProfileForm.id" @click="ctx.removeChildProfile(ctx.childProfileForm.id)">删除当前 ID</button>
              <Button type="primary" @click="ctx.persistChildProfile">保存孩子档案</Button>
            </div>
          </div>
        </Card>
      </section>
</template>
