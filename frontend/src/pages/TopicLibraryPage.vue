<script setup lang="ts">
import { Button, Card } from 'animal-island-vue';

defineProps<{
  ctx: Record<string, any>;
}>();
</script>

<template>
  <section class="simple-page" aria-labelledby="topic-library-title">
        <div class="simple-hero">
          <p class="eyebrow">TOPIC LIBRARY</p>
          <h1 id="topic-library-title">儿童辩题库</h1>
          <p class="hero-copy">现在支持关键词搜索、收藏、详情预览、分类管理和批量导入；新增内容保存到后端 MySQL 后即可筛选和练习。</p>
        </div>

        <div class="topic-filter-bar enhanced">
          <label class="search-field">
            <span>搜索</span>
            <input :value="ctx.topicFilters.q" type="search" placeholder="搜标题、背景、标签" @input="ctx.updateTopicFilter('q', ($event.target as HTMLInputElement).value)" />
          </label>
          <label>
            <span>分类</span>
            <select :value="ctx.topicFilters.collectionId" @change="ctx.updateTopicFilter('collectionId', ($event.target as HTMLSelectElement).value)">
              <option value="">全部分类</option>
              <option v-for="collection in ctx.topicCollections" :key="collection.title" :value="collection.id">{{ collection.title }}</option>
            </select>
          </label>
          <label>
            <span>年龄</span>
            <select :value="ctx.topicFilters.ageRange" @change="ctx.updateTopicFilter('ageRange', ($event.target as HTMLSelectElement).value)">
              <option value="">全部年龄</option>
              <option v-for="ageRange in ctx.ageRangeOptions" :key="ageRange" :value="ageRange">{{ ageRange }} 岁</option>
            </select>
          </label>
          <label>
            <span>难度</span>
            <select :value="ctx.topicFilters.difficulty" @change="ctx.updateTopicFilter('difficulty', ($event.target as HTMLSelectElement).value)">
              <option value="">全部难度</option>
              <option v-for="option in ctx.difficultyOptions" :key="option.value" :value="option.value">{{ option.label }}</option>
            </select>
          </label>
          <label>
            <span>标签</span>
            <select :value="ctx.topicFilters.tag" @change="ctx.updateTopicFilter('tag', ($event.target as HTMLSelectElement).value)">
              <option value="">全部标签</option>
              <option v-for="tag in ctx.availableTags" :key="tag" :value="tag">{{ tag }}</option>
            </select>
          </label>
          <label class="favorite-toggle">
            <input type="checkbox" :checked="ctx.showFavoritesOnly" @change="ctx.updateFavoriteOnly(($event.target as HTMLInputElement).checked)" />
            <span>只看收藏</span>
          </label>
        </div>

        <p class="topic-library-status">{{ ctx.topicLibraryStatus }} 已收藏 {{ ctx.favoriteTopicIds.length }} 个辩题。</p>

        <div class="simple-grid library-grid">
          <Card v-for="collection in ctx.topicCollections" :key="collection.title" class="simple-card" color="app-green">
            <span class="simple-icon">{{ collection.icon }}</span>
            <div>
              <h2>{{ collection.title }}</h2>
              <p>{{ collection.description }}</p>
              <strong>{{ collection.count }} 个辩题</strong>
              <div v-if="ctx.canManageTopics" class="topic-card-actions collection-actions">
                <button type="button" @click="ctx.editCollection(collection)">编辑分类</button>
                <button type="button" @click="ctx.removeAdminCollection(collection.id)">删除</button>
              </div>
            </div>
          </Card>
        </div>

        <div class="topic-result-grid">
          <Card v-for="topic in ctx.libraryTopics" :key="topic.id" class="topic-result-card" color="app-blue">
            <div>
              <p class="eyebrow">{{ topic.ageRange }} 岁 · {{ ctx.topicDifficultyLabel(topic.difficulty) }}</p>
              <h2>{{ topic.title }}</h2>
              <p>{{ topic.sideA }} / {{ topic.sideB }}</p>
              <div class="tag-row">
                <span v-for="tag in topic.tags" :key="tag">{{ tag }}</span>
              </div>
            </div>
            <div class="topic-card-actions">
              <button type="button" @click="ctx.openTopicDetail(topic.id)">详情</button>
              <button type="button" @click="ctx.toggleFavoriteTopic(topic.id)">{{ ctx.isFavoriteTopic(topic.id) ? '★ 已收藏' : '☆ 收藏' }}</button>
              <button v-if="ctx.canManageTopics" type="button" @click="ctx.editTopic(topic)">编辑</button>
              <Button type="primary" @click="ctx.chooseTopicAndPractice(topic.id)">练习</Button>
            </div>
          </Card>
        </div>

        <Card v-if="ctx.selectedLibraryTopic" class="topic-detail-card" color="app-yellow">
          <div class="detail-header">
            <div>
              <p class="eyebrow">TOPIC DETAIL</p>
              <h2>{{ ctx.selectedLibraryTopic.title }}</h2>
              <p>{{ ctx.selectedLibraryTopic.background }}</p>
            </div>
            <button type="button" @click="ctx.openTopicDetail('')">关闭</button>
          </div>
          <div class="detail-grid">
            <div>
              <h3>{{ ctx.selectedLibraryTopic.sideA }}</h3>
              <ul>
                <li v-for="tip in ctx.selectedLibraryTopic.sideATips" :key="tip">{{ tip }}</li>
              </ul>
            </div>
            <div>
              <h3>{{ ctx.selectedLibraryTopic.sideB }}</h3>
              <ul>
                <li v-for="tip in ctx.selectedLibraryTopic.sideBTips" :key="tip">{{ tip }}</li>
              </ul>
            </div>
            <div>
              <h3>生活例子</h3>
              <ul>
                <li v-for="example in ctx.selectedLibraryTopic.examples" :key="example">{{ example }}</li>
              </ul>
            </div>
          </div>
          <div class="topic-card-actions detail-actions">
            <button type="button" @click="ctx.toggleFavoriteTopic(ctx.selectedLibraryTopic.id)">{{ ctx.isFavoriteTopic(ctx.selectedLibraryTopic.id) ? '★ 已收藏' : '☆ 收藏' }}</button>
            <Button type="primary" @click="ctx.chooseTopicAndPractice(ctx.selectedLibraryTopic.id)">用这个题练习</Button>
          </div>
        </Card>

        <Card v-if="ctx.canManageTopics" class="topic-admin-card" color="app-green">
          <div class="section-heading compact">
            <p class="eyebrow">ADMIN</p>
            <h2>题库后台管理</h2>
            <p>{{ ctx.topicAdminStatus }}</p>
          </div>
          <div class="admin-form-grid">
            <label>
              <span>题目 ID</span>
              <input :value="ctx.topicAdminForm.id" placeholder="例如 class-break" @input="ctx.topicAdminForm.id = ($event.target as HTMLInputElement).value" />
            </label>
            <label>
              <span>标题</span>
              <input :value="ctx.topicAdminForm.title" placeholder="输入儿童辩题标题" @input="ctx.topicAdminForm.title = ($event.target as HTMLInputElement).value" />
            </label>
            <label>
              <span>分类</span>
              <select :value="ctx.topicAdminForm.collectionId" @change="ctx.topicAdminForm.collectionId = ($event.target as HTMLSelectElement).value">
                <option v-for="collection in ctx.topicCollections" :key="collection.id" :value="collection.id">{{ collection.title }}</option>
              </select>
            </label>
            <label>
              <span>年龄</span>
              <select :value="ctx.topicAdminForm.ageRange" @change="ctx.topicAdminForm.ageRange = ($event.target as HTMLSelectElement).value">
                <option v-for="ageRange in ctx.ageRangeOptions" :key="ageRange" :value="ageRange">{{ ageRange }} 岁</option>
              </select>
            </label>
            <label>
              <span>难度</span>
              <select :value="ctx.topicAdminForm.difficulty" @change="ctx.topicAdminForm.difficulty = ($event.target as HTMLSelectElement).value">
                <option v-for="option in ctx.difficultyOptions" :key="option.value" :value="option.value">{{ option.label }}</option>
              </select>
            </label>
            <label>
              <span>标签（逗号或换行分隔）</span>
              <input :value="ctx.topicAdminForm.tags" placeholder="校园，规则，公平" @input="ctx.topicAdminForm.tags = ($event.target as HTMLInputElement).value" />
            </label>
            <label>
              <span>正方观点</span>
              <input :value="ctx.topicAdminForm.sideA" @input="ctx.topicAdminForm.sideA = ($event.target as HTMLInputElement).value" />
            </label>
            <label>
              <span>反方观点</span>
              <input :value="ctx.topicAdminForm.sideB" @input="ctx.topicAdminForm.sideB = ($event.target as HTMLInputElement).value" />
            </label>
            <label class="wide-field">
              <span>背景说明</span>
              <textarea :value="ctx.topicAdminForm.background" rows="3" @input="ctx.topicAdminForm.background = ($event.target as HTMLTextAreaElement).value"></textarea>
            </label>
            <label>
              <span>开口提示卡</span>
              <textarea :value="ctx.topicAdminForm.starterTips" rows="4" placeholder="每行一条" @input="ctx.topicAdminForm.starterTips = ($event.target as HTMLTextAreaElement).value"></textarea>
            </label>
            <label>
              <span>正方提示</span>
              <textarea :value="ctx.topicAdminForm.sideATips" rows="4" placeholder="每行一条" @input="ctx.topicAdminForm.sideATips = ($event.target as HTMLTextAreaElement).value"></textarea>
            </label>
            <label>
              <span>反方提示</span>
              <textarea :value="ctx.topicAdminForm.sideBTips" rows="4" placeholder="每行一条" @input="ctx.topicAdminForm.sideBTips = ($event.target as HTMLTextAreaElement).value"></textarea>
            </label>
            <label>
              <span>生活例子</span>
              <textarea :value="ctx.topicAdminForm.examples" rows="4" placeholder="每行一条" @input="ctx.topicAdminForm.examples = ($event.target as HTMLTextAreaElement).value"></textarea>
            </label>
          </div>
          <div class="integration-footer">
            <span>提示：编辑已有题目会覆盖同 ID 内容。</span>
            <div class="topic-card-actions">
              <button type="button" @click="ctx.resetTopicAdminForm">清空</button>
              <button type="button" :disabled="!ctx.topicAdminForm.id" @click="ctx.removeAdminTopic(ctx.topicAdminForm.id)">删除当前 ID</button>
              <Button type="primary" :disabled="ctx.isSavingTopic" @click="ctx.persistAdminTopic">{{ ctx.isSavingTopic ? '保存中…' : '保存题目' }}</Button>
            </div>
          </div>
        </Card>

        <Card v-if="ctx.canManageTopics" class="topic-admin-card" color="app-yellow">
          <div class="section-heading compact">
            <p class="eyebrow">COLLECTION ADMIN</p>
            <h2>分类管理页面</h2>
            <p>{{ ctx.collectionAdminStatus }}</p>
          </div>
          <div class="admin-form-grid">
            <label>
              <span>分类 ID</span>
              <input :value="ctx.collectionAdminForm.id" placeholder="例如 debate-manners" @input="ctx.collectionAdminForm.id = ($event.target as HTMLInputElement).value" />
            </label>
            <label>
              <span>图标 Emoji</span>
              <input :value="ctx.collectionAdminForm.icon" placeholder="📚" @input="ctx.collectionAdminForm.icon = ($event.target as HTMLInputElement).value" />
            </label>
            <label>
              <span>分类标题</span>
              <input :value="ctx.collectionAdminForm.title" placeholder="例如 礼貌表达" @input="ctx.collectionAdminForm.title = ($event.target as HTMLInputElement).value" />
            </label>
            <label class="wide-field">
              <span>分类说明</span>
              <textarea :value="ctx.collectionAdminForm.description" rows="3" placeholder="说明这个分类适合练习什么" @input="ctx.collectionAdminForm.description = ($event.target as HTMLTextAreaElement).value"></textarea>
            </label>
          </div>
          <div class="integration-footer">
            <span>分类保存后会立刻出现在筛选器和题目编辑下拉框中。</span>
            <div class="topic-card-actions">
              <button type="button" @click="ctx.resetCollectionAdminForm">清空</button>
              <button type="button" :disabled="!ctx.collectionAdminForm.id" @click="ctx.removeAdminCollection(ctx.collectionAdminForm.id)">删除当前分类</button>
              <Button type="primary" :disabled="ctx.isSavingCollection" @click="ctx.persistAdminCollection">{{ ctx.isSavingCollection ? '保存中…' : '保存分类' }}</Button>
            </div>
          </div>
        </Card>

        <Card v-if="ctx.canManageTopics" class="topic-admin-card" color="app-blue">
          <div class="section-heading compact">
            <p class="eyebrow">BULK IMPORT</p>
            <h2>批量导入题库</h2>
            <p>{{ ctx.bulkImportStatus }}</p>
          </div>
          <label class="bulk-import-box">
            <span>JSON 内容</span>
            <textarea
              :value="ctx.bulkImportText"
              rows="10"
              placeholder='{ "collections": [{ "id": "daily-talk", "icon": "💬", "title": "日常表达", "description": "生活沟通题", "count": 0, "topicIds": [] }], "topics": [{ "id": "say-sorry", "title": "做错事后要不要马上道歉？", "sideA": "正方：要马上道歉", "sideB": "反方：先想清楚再道歉", "starterTips": ["我认为……"], "collectionId": "daily-talk", "ageRange": "7-9", "difficulty": "easy", "tags": ["礼貌"], "background": "练习承担责任。", "sideATips": ["及时道歉能修复关系。"], "sideBTips": ["先想清楚原因再表达。"], "examples": ["打翻水杯后主动说明。"] }] }'
              @input="ctx.bulkImportText = ($event.target as HTMLTextAreaElement).value"
            ></textarea>
          </label>
          <label class="favorite-toggle bulk-replace-toggle">
            <input type="checkbox" :checked="ctx.bulkReplaceExisting" @change="ctx.bulkReplaceExisting = ($event.target as HTMLInputElement).checked" />
            <span>替换现有题库（会先清空分类和题目）</span>
          </label>
          <div class="integration-footer">
            <span>默认是合并更新：同 ID 会覆盖，未出现的题目会保留。</span>
            <div class="topic-card-actions">
              <Button type="primary" :disabled="ctx.isImportingTopics" @click="ctx.importTopicBankJson">{{ ctx.isImportingTopics ? '导入中…' : '开始批量导入' }}</Button>
            </div>
          </div>
        </Card>
      </section>
</template>
