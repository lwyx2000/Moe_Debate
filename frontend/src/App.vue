<script setup lang="ts">
import { computed, onMounted, onUnmounted, proxyRefs, ref } from 'vue';
import AppNav from './components/AppNav.vue';
import AuthGate from './components/AuthGate.vue';
import { pageFromPath, pushPageRoute, replacePageRoute, subscribeRouteChange, type PageMode } from './router';
import { addFavoriteTopic, askCoach, createChild, createTopic, createTopicCollection, deleteChild, deleteFavoriteTopic, deleteTopic, deleteTopicCollection, fetchChildren, fetchDebateSessions, fetchDemoReport, fetchFavoriteTopics, fetchIntegrationSettings, fetchMe, fetchTopicCollections, fetchTopics, getAuthToken, importTopicBank, login, logout, register, saveIntegrationSettings, startPracticeSession, finishPracticeSession, synthesizeSpeech, transcribeAudio, updateChild, updateTopic, updateTopicCollection } from './api';
import type { ChildProfile, CoachResponse, DebateTopic, DebateSession, DebateTurn, GrowthReport, IntegrationSettings, ProviderConfig, SessionFilters, TopicCollection, TopicFilters, TrendPoint, UserAccount } from './types';

interface HomeTopic {
  emoji: string;
  title: string;
  positive: string;
  negative: string;
}

interface JourneyStep {
  index: string;
  title: string;
  description: string;
}

interface TopicAdminForm {
  id: string;
  title: string;
  sideA: string;
  sideB: string;
  starterTips: string;
  collectionId: string;
  ageRange: string;
  difficulty: string;
  tags: string;
  background: string;
  sideATips: string;
  sideBTips: string;
  examples: string;
}

interface CollectionAdminForm {
  id: string;
  icon: string;
  title: string;
  description: string;
}

interface ReportItem {
  icon: string;
  title: string;
  value: string;
  hint: string;
}

interface VoiceStep {
  title: string;
  engine: string;
  description: string;
}

const featuredTopics: HomeTopic[] = [
  {
    emoji: '📚',
    title: '每天固定阅读时间好不好？',
    positive: '好：习惯会一点点长大',
    negative: '不好：可以更自由安排',
  },
  {
    emoji: '🎮',
    title: '周末能不能多玩一小时游戏？',
    positive: '能：完成任务后可奖励',
    negative: '不能：要保护眼睛和睡眠',
  },
  {
    emoji: '🧹',
    title: '值日小队长要不要轮流当？',
    positive: '要：每个人都有练习机会',
    negative: '不要：负责的人更有效率',
  },
];

const fallbackTopics: DebateTopic[] = [
  {
    id: 'screen-time',
    title: '周末能不能多玩一小时电子游戏？',
    sideA: '正方：可以多玩一小时',
    sideB: '反方：不应该增加时长',
    starterTips: [
      '我的观点是可以，但需要先完成作业和运动。',
      '我担心时间太长会影响眼睛，所以要设置闹钟。',
      '如果我是反方，我会问：多玩以后还能保证睡眠吗？',
    ],
    collectionId: 'interest-growth',
    ageRange: '8-10',
    difficulty: 'medium',
    tags: ['游戏', '时间管理', '兴趣'],
    background: '电子游戏是很多孩子熟悉的兴趣活动。这个题目帮助孩子练习讨论奖励、规则和健康边界。',
    sideATips: ['完成作业和运动后，可以把游戏当作奖励。', '提前约好时间，能练习自我管理。'],
    sideBTips: ['多玩可能影响眼睛和睡眠。', '周末也需要运动、阅读和家人相处。'],
    examples: ['设置 45 分钟闹钟，到点就停。', '先完成作业、运动，再开始游戏。'],
  },
];

const journeySteps: JourneyStep[] = [
  {
    index: '01',
    title: '选一个儿童辩题',
    description: '把抽象议题换成孩子熟悉的校园、家庭和兴趣场景。',
  },
  {
    index: '02',
    title: '用提示卡说观点',
    description: '按“我认为—因为—例如”的句式组织表达，降低开口压力。',
  },
  {
    index: '03',
    title: '教练给温柔反馈',
    description: '围绕清楚表达、理由例子、礼貌回应三项给出下一句建议。',
  },
];

const coachMessages = [
  {
    role: 'kid',
    badge: '小辩手',
    text: '我认为周末可以多玩一小时游戏，因为我会先完成作业。',
  },
  {
    role: 'coach',
    badge: '小鹿教练',
    text: '观点很清楚！如果再加一个例子，比如“我上周怎么安排时间”，说服力会更强。',
  },
];

const fallbackTopicCollections: TopicCollection[] = [
  {
    id: 'school-life',
    icon: '🏫',
    title: '校园生活',
    description: '值日、班干部、作业、课间活动等孩子每天都会遇到的讨论。',
    count: 1,
    topicIds: ['class-leader'],
  },
  {
    id: 'family-rules',
    icon: '🏡',
    title: '家庭规则',
    description: '阅读时间、电子屏幕、零花钱和家务分工，适合亲子共练。',
    count: 1,
    topicIds: ['homework-pet'],
  },
  {
    id: 'small-society',
    icon: '🌍',
    title: '小小社会',
    description: '环保、公共礼仪、宠物和社区活动，练习从不同角度看问题。',
    count: 0,
    topicIds: [],
  },
  {
    id: 'interest-growth',
    icon: '🎨',
    title: '兴趣成长',
    description: '兴趣班、比赛、游戏和创作，让孩子讨论“喜欢”和“坚持”。',
    count: 1,
    topicIds: ['screen-time'],
  },
];

const reportIcons: Record<string, string> = { clarity: '💬', evidence: '🔎', manners: '🤝' };

const fallbackReportItems: ReportItem[] = [
  {
    icon: '💬',
    title: '表达清楚度',
    value: '86',
    hint: '能说出观点，下一步练习把理由分成第一、第二。',
  },
  {
    icon: '🔎',
    title: '理由与例子',
    value: '74',
    hint: '已经会说“因为”，继续补生活例子会更有说服力。',
  },
  {
    icon: '🤝',
    title: '礼貌回应',
    value: '90',
    hint: '能用“我理解你的担心”回应对方，保持温和语气。',
  },
];

const voiceSteps: VoiceStep[] = [
  {
    title: '录音上传',
    engine: 'Browser MediaRecorder',
    description: '练习页后续加入按住说话/点击录音，把 webm 或 wav 交给后端。',
  },
  {
    title: '语音识别',
    engine: 'Qwen3-ASR-0.6B',
    description: '后端统一封装本地 ASR，把孩子语音转成文字后进入教练流程。',
  },
  {
    title: '语音合成',
    engine: 'Kitten-TTS-Server',
    description: '教练文本生成后调用本地 TTS，返回卡通教练音频给前端播放。',
  },
];

const defaultIntegrationSettings: IntegrationSettings = {
  llm: { enabled: false, baseUrl: 'https://api.openai.com/v1', model: 'gpt-4o-mini', apiKey: '' },
  asr: { enabled: false, baseUrl: 'http://127.0.0.1:8002', model: 'Qwen3-ASR-0.6B', apiKey: '' },
  tts: { enabled: false, baseUrl: 'http://127.0.0.1:8005', model: 'kitten-tts', apiKey: '' },
  updatedAt: '',
};

const ageRangeOptions = ['7-9', '8-10', '9-12'];
const difficultyOptions = [
  { value: 'easy', label: '简单' },
  { value: 'medium', label: '中等' },
  { value: 'hard', label: '挑战' },
];

const emptyTopicAdminForm = (): TopicAdminForm => ({
  id: '',
  title: '',
  sideA: '正方：',
  sideB: '反方：',
  starterTips: '',
  collectionId: 'school-life',
  ageRange: '8-10',
  difficulty: 'easy',
  tags: '',
  background: '',
  sideATips: '',
  sideBTips: '',
  examples: '',
});

const emptyCollectionAdminForm = (): CollectionAdminForm => ({
  id: '',
  icon: '📚',
  title: '',
  description: '',
});

const emptyChildProfile = (): ChildProfile => ({
  id: `child-${Date.now()}`,
  userId: 'demo-parent',
  name: '',
  age: 8,
  grade: '二年级',
  avatar: '🦊',
  debateGoal: '每次表达都说清观点和理由。',
  createdAt: '',
});

const providerKeys = ['llm', 'asr', 'tts'] as const;

const providerLabels: Record<keyof Omit<IntegrationSettings, 'updatedAt'>, string> = {
  llm: '大模型教练 API',
  asr: 'Qwen3-ASR 识别',
  tts: 'Kitten-TTS 输出',
};

const page = ref<PageMode>(pageFromPath());
const currentUser = ref<UserAccount | null>(null);
const authMode = ref<'login' | 'register'>('login');
const authEmail = ref('demo@example.com');
const authPassword = ref('demo123456');
const authDisplayName = ref('家长/老师');
const authStatus = ref('请先登录。Demo 账号：demo@example.com / demo123456');
const childProfiles = ref<ChildProfile[]>([]);
const activeChildId = ref('demo-child');
const childProfileForm = ref<ChildProfile>(emptyChildProfile());
const childProfileStatus = ref('可以为多个孩子建立独立档案，练习历史和成长报告会按当前孩子筛选。');
const topics = ref<DebateTopic[]>(fallbackTopics);
const topicCollections = ref<TopicCollection[]>(fallbackTopicCollections);
const libraryTopics = ref<DebateTopic[]>(fallbackTopics);
const topicFilters = ref<Required<TopicFilters>>({ collectionId: '', ageRange: '', difficulty: '', tag: '', q: '' });
const showFavoritesOnly = ref(false);
const favoriteTopicIds = ref<string[]>([]);
const selectedLibraryTopicId = ref('');
const topicAdminForm = ref<TopicAdminForm>(emptyTopicAdminForm());
const collectionAdminForm = ref<CollectionAdminForm>(emptyCollectionAdminForm());
const bulkImportText = ref('');
const bulkReplaceExisting = ref(false);
const isSavingTopic = ref(false);
const isSavingCollection = ref(false);
const isImportingTopics = ref(false);
const topicAdminStatus = ref('可在这里新增或编辑辩题，保存后会写入后端 MySQL 题库。');
const collectionAdminStatus = ref('可以在这里维护题库分类，分类会写入后端 MySQL。');
const bulkImportStatus = ref('支持粘贴 JSON：{ "collections": [...], "topics": [...] }。');
const topicLibraryStatus = ref('可以按分类、年龄、难度、标签筛选辩题。');
const selectedTopicId = ref(fallbackTopics[0].id);
const selectedSide = ref<'正方' | '反方'>('正方');
const draft = ref('');
const isLoadingTopics = ref(false);
const isLoadingReply = ref(false);
const isRecording = ref(false);
const isSynthesizing = ref(false);
const speechRate = ref(0.92);
const speechPitch = ref(1.08);
const mediaRecorder = ref<MediaRecorder | null>(null);
const audioChunks = ref<Blob[]>([]);
const voiceStatus = ref('语音输入输出已接入前端流程，当前后端仍是占位服务。');
const lastCoachText = ref('');
const activePracticeSessionId = ref('');
const sessions = ref<DebateSession[]>([]);
const isLoadingSessions = ref(false);
const historyStatus = ref('练习后会自动保存到这里。');
const reportItems = ref<ReportItem[]>(fallbackReportItems);
const reportSummary = ref({ childName: '小辩手', weekLabel: '本周练习报告', completedDebates: 3, streakDays: 2, totalPracticeMinutes: 15, activeDays: 2 });
const reportCoachNote = ref('孩子已经能说清楚观点，建议下一轮练习时要求每次发言都补一个生活中的小例子。');
const reportNextGoal = ref('每次发言都加入一个具体例子。');
const reportTrend = ref<TrendPoint[]>([]);
const reportWeakSpot = ref('理由与例子');
const reportRecommendedTopic = ref({ id: '', title: '周末能不能多玩一小时电子游戏？' });
const reportParentComment = ref('建议家长在练习后追问一个“你能举例吗？”。');
const reportTeacherComment = ref('建议老师关注孩子是否能礼貌回应对方观点。');
const sessionFilters = ref<SessionFilters>({ range: 'week', dateFrom: isoDate(6), dateTo: isoDate(0), topicId: '', collectionId: '' });
const integrationSettings = ref<IntegrationSettings>(structuredClone(defaultIntegrationSettings));
const isSavingIntegrations = ref(false);
const integrationStatus = ref('可以填写买来的云端大模型 API，也可以填写本地 ASR/TTS 服务地址；配置会保存到后端 MySQL。');
const error = ref('');
const rubric = ref<CoachResponse['rubric']>({ clarity: 72, evidence: 60, manners: 88 });
const turns = ref<DebateTurn[]>([
  {
    speaker: 'coach',
    badge: '开场',
    text: '欢迎来到练习岛！选一个辩题和立场，然后用“我认为—因为—例如”说出你的观点。',
  },
]);

const currentTopic = computed(() => topics.value.find((topic) => topic.id === selectedTopicId.value) ?? topics.value[0]);
const activeChild = computed(() => childProfiles.value.find((child) => child.id === activeChildId.value) ?? childProfiles.value[0]);
const selectedLibraryTopic = computed(() => libraryTopics.value.find((topic) => topic.id === selectedLibraryTopicId.value) ?? null);
const currentSideLabel = computed(() => (selectedSide.value === '正方' ? currentTopic.value?.sideA : currentTopic.value?.sideB));
const tips = computed(() => currentTopic.value?.starterTips ?? []);
const wordCount = computed(() => draft.value.trim().length);
const canSubmit = computed(() => Boolean(draft.value.trim()) && !isLoadingReply.value);
const availableTags = computed(() => Array.from(new Set(topics.value.flatMap((topic) => topic.tags))).sort());
const canManageTopics = computed(() => currentUser.value?.role === 'admin' || currentUser.value?.role === 'teacher');

let unsubscribeRouteChange: (() => void) | undefined;

onMounted(async () => {
  replacePageRoute(page.value);
  unsubscribeRouteChange = subscribeRouteChange((nextPage) => {
    page.value = nextPage;
    if (!currentUser.value && nextPage !== 'home') {
      authStatus.value = '请先登录后再使用该页面。';
      return;
    }
    void runPageSideEffects(nextPage);
  });

  if (getAuthToken()) {
    try {
      currentUser.value = await fetchMe();
      authStatus.value = `已登录：${currentUser.value.displayName}`;
    } catch {
      authStatus.value = '登录已过期，请重新登录。';
    }
  }
  if (currentUser.value) {
    await loadChildProfiles();
    await loadFavoriteTopics();
  }
  isLoadingTopics.value = true;

  try {
    const apiTopics = await fetchTopics();
    if (apiTopics.length > 0) {
      topics.value = apiTopics;
      libraryTopics.value = apiTopics;
      selectedTopicId.value = apiTopics[0].id;
    }
  } catch (err) {
    error.value = err instanceof Error ? `辩题接口暂时不可用，已使用本地示例：${err.message}` : '辩题接口暂时不可用，已使用本地示例。';
  } finally {
    isLoadingTopics.value = false;
  }

  await loadTopicCollections();

  if (currentUser.value) {
    try {
      integrationSettings.value = await fetchIntegrationSettings();
    } catch (err) {
      integrationStatus.value = err instanceof Error ? `模型配置读取失败，正在使用默认值：${err.message}` : '模型配置读取失败，正在使用默认值。';
    }

    try {
      applyGrowthReport(await fetchDemoReport(activeChildId.value, sessionFilters.value));
    } catch {
      // 成长报告接口不可用时保留本地示例数据。
    }
    await runPageSideEffects(page.value);
  }
});

onUnmounted(() => {
  unsubscribeRouteChange?.();
});

async function afterAuthLoaded(user: UserAccount) {
  currentUser.value = user;
  authStatus.value = `已登录：${user.displayName}（${user.role}）`;
  await loadChildProfiles();
  await loadFavoriteTopics();
  await runPageSideEffects(page.value);
  try {
    integrationSettings.value = await fetchIntegrationSettings();
  } catch {
    // 普通家长账号没有模型配置权限时保留默认配置。
  }
  try {
    applyGrowthReport(await fetchDemoReport(activeChildId.value, sessionFilters.value));
  } catch {
    // 登录后报告加载失败时保留当前展示。
  }
}

async function submitAuth() {
  authStatus.value = authMode.value === 'login' ? '正在登录……' : '正在注册……';
  try {
    const result = authMode.value === 'login'
      ? await login(authEmail.value, authPassword.value)
      : await register(authEmail.value, authPassword.value, authDisplayName.value);
    await afterAuthLoaded(result.user);
  } catch (err) {
    authStatus.value = err instanceof Error ? `认证失败：${err.message}` : '认证失败，请稍后再试。';
  }
}

async function loginWithDemo() {
  authEmail.value = 'demo@example.com';
  authPassword.value = 'demo123456';
  authMode.value = 'login';
  await submitAuth();
}

async function signOut() {
  await logout();
  currentUser.value = null;
  childProfiles.value = [];
  sessions.value = [];
  favoriteTopicIds.value = [];
  authStatus.value = '已退出登录。';
  page.value = 'home';
  replacePageRoute('home');
}

async function loadChildProfiles() {
  try {
    const profiles = await fetchChildren();
    childProfiles.value = profiles;
    if (profiles.length > 0 && !profiles.some((child) => child.id === activeChildId.value)) {
      activeChildId.value = profiles[0].id;
    }
    childProfileForm.value = profiles[0] ? { ...profiles[0] } : emptyChildProfile();
  } catch (err) {
    childProfileStatus.value = err instanceof Error ? `孩子档案加载失败：${err.message}` : '孩子档案加载失败。';
  }
}

function editChildProfile(profile: ChildProfile) {
  childProfileForm.value = { ...profile };
  childProfileStatus.value = `正在编辑：${profile.name}`;
}

function resetChildProfileForm() {
  childProfileForm.value = emptyChildProfile();
  childProfileStatus.value = '已清空表单，可以新增孩子档案。';
}

async function persistChildProfile() {
  if (!childProfileForm.value.id.trim() || !childProfileForm.value.name.trim()) {
    childProfileStatus.value = '请填写孩子 ID 和姓名。';
    return;
  }
  const profile = { ...childProfileForm.value, id: childProfileForm.value.id.trim(), name: childProfileForm.value.name.trim() };
  childProfileStatus.value = '正在保存孩子档案……';
  try {
    const exists = childProfiles.value.some((child) => child.id === profile.id);
    const saved = exists ? await updateChild(profile) : await createChild(profile);
    childProfiles.value = [saved, ...childProfiles.value.filter((child) => child.id !== saved.id)];
    activeChildId.value = saved.id;
    childProfileForm.value = { ...saved };
    childProfileStatus.value = `已保存：${saved.name}`;
    await refreshChildScopedData();
  } catch (err) {
    childProfileStatus.value = err instanceof Error ? `保存失败：${err.message}` : '保存失败，请稍后再试。';
  }
}

async function removeChildProfile(childId: string) {
  childProfileStatus.value = '正在删除孩子档案……';
  try {
    await deleteChild(childId);
    childProfiles.value = childProfiles.value.filter((child) => child.id !== childId);
    if (activeChildId.value === childId) {
      activeChildId.value = childProfiles.value[0]?.id ?? '';
    }
    childProfileForm.value = childProfiles.value[0] ? { ...childProfiles.value[0] } : emptyChildProfile();
    childProfileStatus.value = '孩子档案已删除。';
    await refreshChildScopedData();
  } catch (err) {
    childProfileStatus.value = err instanceof Error ? `删除失败：${err.message}` : '删除失败，请稍后再试。';
  }
}

async function selectActiveChild(childId: string) {
  activeChildId.value = childId;
  const profile = childProfiles.value.find((child) => child.id === childId);
  if (profile) childProfileForm.value = { ...profile };
  await refreshChildScopedData();
}

async function refreshChildScopedData() {
  if (page.value === 'history') {
    await loadSessions();
  }
  if (page.value === 'report') {
    try {
      applyGrowthReport(await fetchDemoReport(activeChildId.value, sessionFilters.value));
    } catch {
      // 成长报告接口不可用时保留当前展示。
    }
  }
}

async function loadTopicCollections() {
  try {
    const apiCollections = await fetchTopicCollections();
    if (apiCollections.length > 0) {
      topicCollections.value = apiCollections;
    }
  } catch {
    // 题库分类接口不可用时保留前端内置兜底分类。
  }
}

async function loadLibraryTopics() {
  topicLibraryStatus.value = '正在筛选辩题……';
  try {
    const filteredTopics = await fetchTopics(topicFilters.value);
    libraryTopics.value = showFavoritesOnly.value ? filteredTopics.filter((topic) => favoriteTopicIds.value.includes(topic.id)) : filteredTopics;
    if (selectedLibraryTopicId.value && !libraryTopics.value.some((topic) => topic.id === selectedLibraryTopicId.value)) {
      selectedLibraryTopicId.value = '';
    }
    topicLibraryStatus.value = libraryTopics.value.length > 0 ? `找到 ${libraryTopics.value.length} 个辩题。` : '没有符合条件的辩题，请放宽筛选条件。';
  } catch (err) {
    topicLibraryStatus.value = err instanceof Error ? `筛选失败：${err.message}` : '筛选失败，请稍后再试。';
  }
}

function updateTopicFilter(key: keyof Required<TopicFilters>, value: string) {
  topicFilters.value = { ...topicFilters.value, [key]: value };
  void loadLibraryTopics();
}

function chooseTopicAndPractice(topicId: string) {
  selectedTopicId.value = topicId;
  activePracticeSessionId.value = '';
  openPractice();
}

function topicDifficultyLabel(difficulty: string) {
  return difficultyOptions.find((option) => option.value === difficulty)?.label ?? difficulty;
}

function splitLines(value: string) {
  return value
    .split(/[,，\n]/)
    .map((item) => item.trim())
    .filter(Boolean);
}

async function loadFavoriteTopics() {
  try {
    favoriteTopicIds.value = await fetchFavoriteTopics();
  } catch {
    favoriteTopicIds.value = [];
  }
}

function isFavoriteTopic(topicId: string) {
  return favoriteTopicIds.value.includes(topicId);
}

async function toggleFavoriteTopic(topicId: string) {
  const wasFavorite = isFavoriteTopic(topicId);
  favoriteTopicIds.value = wasFavorite ? favoriteTopicIds.value.filter((id) => id !== topicId) : [...favoriteTopicIds.value, topicId];
  try {
    if (wasFavorite) {
      await deleteFavoriteTopic(topicId);
    } else {
      await addFavoriteTopic(topicId);
    }
  } catch (err) {
    favoriteTopicIds.value = wasFavorite ? [...favoriteTopicIds.value, topicId] : favoriteTopicIds.value.filter((id) => id !== topicId);
    topicLibraryStatus.value = err instanceof Error ? `收藏同步失败：${err.message}` : '收藏同步失败，请稍后再试。';
  }
  if (showFavoritesOnly.value) {
    void loadLibraryTopics();
  }
}

function updateFavoriteOnly(value: boolean) {
  showFavoritesOnly.value = value;
  void loadLibraryTopics();
}

function openTopicDetail(topicId: string) {
  selectedLibraryTopicId.value = topicId;
}

function topicToForm(topic: DebateTopic): TopicAdminForm {
  return {
    id: topic.id,
    title: topic.title,
    sideA: topic.sideA,
    sideB: topic.sideB,
    starterTips: topic.starterTips.join('\n'),
    collectionId: topic.collectionId,
    ageRange: topic.ageRange,
    difficulty: topic.difficulty,
    tags: topic.tags.join('，'),
    background: topic.background,
    sideATips: topic.sideATips.join('\n'),
    sideBTips: topic.sideBTips.join('\n'),
    examples: topic.examples.join('\n'),
  };
}

function formToTopic(): DebateTopic {
  return {
    id: topicAdminForm.value.id.trim(),
    title: topicAdminForm.value.title.trim(),
    sideA: topicAdminForm.value.sideA.trim(),
    sideB: topicAdminForm.value.sideB.trim(),
    starterTips: splitLines(topicAdminForm.value.starterTips),
    collectionId: topicAdminForm.value.collectionId,
    ageRange: topicAdminForm.value.ageRange,
    difficulty: topicAdminForm.value.difficulty,
    tags: splitLines(topicAdminForm.value.tags),
    background: topicAdminForm.value.background.trim(),
    sideATips: splitLines(topicAdminForm.value.sideATips),
    sideBTips: splitLines(topicAdminForm.value.sideBTips),
    examples: splitLines(topicAdminForm.value.examples),
  };
}

function editTopic(topic: DebateTopic) {
  topicAdminForm.value = topicToForm(topic);
  topicAdminStatus.value = `正在编辑：${topic.title}`;
  window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });
}

function resetTopicAdminForm() {
  topicAdminForm.value = emptyTopicAdminForm();
  topicAdminStatus.value = '已清空表单，可以新增辩题。';
}

async function persistAdminTopic() {
  const topic = formToTopic();
  if (!topic.id || !topic.title || !topic.background || topic.starterTips.length === 0) {
    topicAdminStatus.value = '请至少填写 ID、标题、背景和提示卡。';
    return;
  }

  isSavingTopic.value = true;
  topicAdminStatus.value = '正在保存辩题……';
  try {
    const exists = topics.value.some((item) => item.id === topic.id);
    const saved = exists ? await updateTopic(topic) : await createTopic(topic);
    topics.value = [saved, ...topics.value.filter((item) => item.id !== saved.id)];
    await loadLibraryTopics();
    await loadTopicCollections();
    selectedLibraryTopicId.value = saved.id;
    topicAdminStatus.value = `已保存：${saved.title}`;
  } catch (err) {
    topicAdminStatus.value = err instanceof Error ? `保存失败：${err.message}` : '保存失败，请稍后再试。';
  } finally {
    isSavingTopic.value = false;
  }
}

async function removeAdminTopic(topicId: string) {
  topicAdminStatus.value = '正在删除辩题……';
  try {
    await deleteTopic(topicId);
    topics.value = topics.value.filter((topic) => topic.id !== topicId);
    favoriteTopicIds.value = favoriteTopicIds.value.filter((id) => id !== topicId);
    selectedLibraryTopicId.value = '';
    await loadLibraryTopics();
    await loadTopicCollections();
    topicAdminStatus.value = '辩题已删除。';
  } catch (err) {
    topicAdminStatus.value = err instanceof Error ? `删除失败：${err.message}` : '删除失败，请稍后再试。';
  }
}


function collectionToPayload(): TopicCollection {
  return {
    id: collectionAdminForm.value.id.trim(),
    icon: collectionAdminForm.value.icon.trim() || '📚',
    title: collectionAdminForm.value.title.trim(),
    description: collectionAdminForm.value.description.trim(),
    count: 0,
    topicIds: [],
  };
}

function editCollection(collection: TopicCollection) {
  collectionAdminForm.value = {
    id: collection.id,
    icon: collection.icon,
    title: collection.title,
    description: collection.description,
  };
  collectionAdminStatus.value = `正在编辑分类：${collection.title}`;
}

function resetCollectionAdminForm() {
  collectionAdminForm.value = emptyCollectionAdminForm();
  collectionAdminStatus.value = '已清空分类表单，可以新增分类。';
}

async function persistAdminCollection() {
  const collection = collectionToPayload();
  if (!collection.id || !collection.title || !collection.description) {
    collectionAdminStatus.value = '请填写分类 ID、标题和说明。';
    return;
  }

  isSavingCollection.value = true;
  collectionAdminStatus.value = '正在保存分类……';
  try {
    const exists = topicCollections.value.some((item) => item.id === collection.id);
    const saved = exists ? await updateTopicCollection(collection) : await createTopicCollection(collection);
    topicCollections.value = [saved, ...topicCollections.value.filter((item) => item.id !== saved.id)];
    if (!topicAdminForm.value.collectionId) {
      topicAdminForm.value.collectionId = saved.id;
    }
    await loadTopicCollections();
    collectionAdminStatus.value = `已保存分类：${saved.title}`;
  } catch (err) {
    collectionAdminStatus.value = err instanceof Error ? `分类保存失败：${err.message}` : '分类保存失败，请稍后再试。';
  } finally {
    isSavingCollection.value = false;
  }
}

async function removeAdminCollection(collectionId: string) {
  collectionAdminStatus.value = '正在删除分类……';
  try {
    await deleteTopicCollection(collectionId);
    topicCollections.value = topicCollections.value.filter((collection) => collection.id !== collectionId);
    if (topicAdminForm.value.collectionId === collectionId) {
      topicAdminForm.value.collectionId = topicCollections.value[0]?.id ?? '';
    }
    resetCollectionAdminForm();
    await loadTopicCollections();
    collectionAdminStatus.value = '分类已删除。若分类下已有题目，请先移动或删除题目后再删除分类。';
  } catch (err) {
    collectionAdminStatus.value = err instanceof Error ? `分类删除失败：${err.message}` : '分类删除失败，请稍后再试。';
  }
}

async function importTopicBankJson() {
  if (!bulkImportText.value.trim()) {
    bulkImportStatus.value = '请先粘贴要导入的 JSON。';
    return;
  }

  isImportingTopics.value = true;
  bulkImportStatus.value = '正在导入题库 JSON……';
  try {
    const parsed = JSON.parse(bulkImportText.value) as { topics?: DebateTopic[]; collections?: TopicCollection[] } | DebateTopic[];
    const payload = Array.isArray(parsed)
      ? { topics: parsed, collections: [], replaceExisting: bulkReplaceExisting.value }
      : { topics: parsed.topics ?? [], collections: parsed.collections ?? [], replaceExisting: bulkReplaceExisting.value };
    const result = await importTopicBank(payload);
    const apiTopics = await fetchTopics();
    topics.value = apiTopics.length > 0 ? apiTopics : topics.value;
    await loadLibraryTopics();
    await loadTopicCollections();
    bulkImportStatus.value = `导入完成：${result.importedCollections} 个分类，${result.importedTopics} 个辩题（${result.mode === 'replace' ? '替换' : '合并更新'}模式）。`;
  } catch (err) {
    bulkImportStatus.value = err instanceof Error ? `导入失败：${err.message}` : '导入失败，请检查 JSON 格式。';
  } finally {
    isImportingTopics.value = false;
  }
}

function isoDate(daysAgo = 0) {
  const date = new Date();
  date.setDate(date.getDate() - daysAgo);
  return date.toISOString().slice(0, 10);
}

function updateSessionRange(range: SessionFilters['range']) {
  sessionFilters.value = { ...sessionFilters.value, range };
  if (range === 'week') {
    sessionFilters.value.dateFrom = isoDate(6);
    sessionFilters.value.dateTo = isoDate(0);
  }
  if (range === 'month') {
    sessionFilters.value.dateFrom = isoDate(29);
    sessionFilters.value.dateTo = isoDate(0);
  }
  if (range === 'all') {
    sessionFilters.value.dateFrom = '';
    sessionFilters.value.dateTo = '';
  }
  void refreshHistoryAndReport();
}

function updateSessionFilter(key: keyof SessionFilters, value: string) {
  sessionFilters.value = { ...sessionFilters.value, [key]: value };
  if (key === 'dateFrom' || key === 'dateTo') {
    sessionFilters.value.range = 'custom';
  }
  void refreshHistoryAndReport();
}

async function refreshHistoryAndReport() {
  if (page.value === 'history') {
    await loadSessions();
  }
  if (page.value === 'report') {
    try {
      applyGrowthReport(await fetchDemoReport(activeChildId.value, sessionFilters.value));
    } catch {
      // 报告接口不可用时保留当前展示。
    }
  }
}

function exportReportPdf() {
  window.print();
}

function practiceRecommendedTopic() {
  if (reportRecommendedTopic.value.id) {
    chooseTopicAndPractice(reportRecommendedTopic.value.id);
  } else {
    openPractice();
  }
}

async function loadSessions() {
  isLoadingSessions.value = true;
  historyStatus.value = '正在加载练习历史……';

  try {
    sessions.value = await fetchDebateSessions(50, activeChildId.value, sessionFilters.value);
    historyStatus.value = sessions.value.length > 0 ? `已加载 ${sessions.value.length} 条练习记录。` : '还没有练习记录，先去练习页完成一次辩论吧。';
  } catch (err) {
    historyStatus.value = err instanceof Error ? `历史加载失败：${err.message}` : '历史加载失败，请稍后再试。';
  } finally {
    isLoadingSessions.value = false;
  }
}

function formatSessionTime(value: string) {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return value;
  }
  return date.toLocaleString('zh-CN', { month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' });
}

function applyGrowthReport(report: GrowthReport) {
  reportSummary.value = {
    childName: report.childName,
    weekLabel: report.weekLabel,
    completedDebates: report.completedDebates,
    streakDays: report.streakDays,
    totalPracticeMinutes: report.totalPracticeMinutes,
    activeDays: report.activeDays,
  };
  reportCoachNote.value = report.coachNote;
  reportNextGoal.value = report.nextGoal;
  reportTrend.value = report.trend ?? [];
  reportWeakSpot.value = report.weakSpot || '理由与例子';
  reportRecommendedTopic.value = { id: report.recommendedTopicId, title: report.recommendedTopicTitle };
  reportParentComment.value = report.parentComment;
  reportTeacherComment.value = report.teacherComment;
  reportItems.value = report.metrics.map((metric) => ({
    icon: reportIcons[metric.key] ?? '⭐',
    title: metric.title,
    value: String(metric.score),
    hint: metric.hint,
  }));
}

function updateProvider(provider: keyof Omit<IntegrationSettings, 'updatedAt'>, patch: Partial<ProviderConfig>) {
  integrationSettings.value = {
    ...integrationSettings.value,
    [provider]: { ...integrationSettings.value[provider], ...patch },
  };
}

async function persistIntegrationSettings() {
  isSavingIntegrations.value = true;
  integrationStatus.value = '正在保存模型配置……';

  try {
    integrationSettings.value = await saveIntegrationSettings(integrationSettings.value);
    integrationStatus.value = '模型配置已保存。后端后续接真实服务时会优先读取这里的地址和模型名。';
  } catch (err) {
    integrationStatus.value = err instanceof Error ? `保存失败：${err.message}` : '保存失败，请稍后再试。';
  } finally {
    isSavingIntegrations.value = false;
  }
}

function goHome() {
  openPage('home');
}

async function runPageSideEffects(nextPage: PageMode) {
  if (nextPage === 'history') {
    await loadSessions();
  }
  if (nextPage === 'report') {
    await refreshChildScopedData();
  }
  if (nextPage === 'topicLibrary') {
    await loadLibraryTopics();
  }
}

function openPage(nextPage: PageMode) {
  if (!currentUser.value && nextPage !== 'home') {
    authStatus.value = '请先登录后再使用该页面。';
    page.value = 'home';
    pushPageRoute('home');
    return;
  }
  page.value = nextPage;
  pushPageRoute(nextPage);
  void runPageSideEffects(nextPage);
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

function openPractice() {
  openPage('practice');
}

function scrollToPracticePreview() {
  document.querySelector('#practice-preview')?.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function applyTip(tip: string) {
  draft.value = tip;
}

function resetPractice() {
  if (activePracticeSessionId.value) {
    void finishPracticeSession(activePracticeSessionId.value, '本次练习已结束。');
  }
  activePracticeSessionId.value = '';
  draft.value = '';
  lastCoachText.value = '';
  voiceStatus.value = '语音输入输出已接入前端流程，当前后端仍是占位服务。';
  selectedSide.value = '正方';
  rubric.value = { clarity: 72, evidence: 60, manners: 88 };
  turns.value = [
    {
      speaker: 'coach',
      badge: '开场',
      text: '新的练习开始啦！先选立场，再说出你的观点、理由和例子。',
    },
  ];
}

async function submitArgument() {
  if (!currentUser.value) {
    error.value = '请先登录后再开始练习。';
    return;
  }
  const message = draft.value.trim();
  const topic = currentTopic.value;
  if (!message || !topic) return;

  turns.value.push({ speaker: 'kid', badge: selectedSide.value, text: message });
  draft.value = '';
  isLoadingReply.value = true;
  error.value = '';

  try {
    if (!activePracticeSessionId.value) {
      const practiceSession = await startPracticeSession(topic.id, selectedSide.value, activeChildId.value);
      activePracticeSessionId.value = practiceSession.id;
    }
    const result = await askCoach(topic.id, selectedSide.value, message, activeChildId.value, activePracticeSessionId.value);
    activePracticeSessionId.value = result.practiceSessionId || activePracticeSessionId.value;
    rubric.value = result.rubric;
    const coachText = `${result.reply}\n\n下一步：${result.nextPrompt}`;
    lastCoachText.value = coachText;
    turns.value.push({
      speaker: 'coach',
      badge: '小鹿教练',
      text: coachText,
    });
  } catch (err) {
    const fallbackCoachText = '后端教练暂时没有连上。我先给你一个小提示：试着补一句“例如……”，让理由更具体。';
    lastCoachText.value = fallbackCoachText;
    turns.value.push({
      speaker: 'coach',
      badge: '离线教练',
      text: fallbackCoachText,
    });
    error.value = err instanceof Error ? err.message : '教练接口暂时不可用';
  } finally {
    isLoadingReply.value = false;
  }
}

async function startRecording() {
  if (!navigator.mediaDevices?.getUserMedia) {
    voiceStatus.value = '当前浏览器不支持录音，请先使用文字输入。';
    return;
  }

  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    audioChunks.value = [];
    const recorder = new MediaRecorder(stream);
    mediaRecorder.value = recorder;

    recorder.addEventListener('dataavailable', (event) => {
      if (event.data.size > 0) {
        audioChunks.value.push(event.data);
      }
    });

    recorder.addEventListener('stop', async () => {
      stream.getTracks().forEach((track) => track.stop());
      isRecording.value = false;

      if (audioChunks.value.length === 0) {
        voiceStatus.value = '没有录到声音，请再试一次。';
        return;
      }

      voiceStatus.value = '录音已结束，正在上传识别……';
      const audioBlob = new Blob(audioChunks.value, { type: recorder.mimeType || 'audio/webm' });

      try {
        const result = await transcribeAudio(audioBlob);
        draft.value = result.text;
        voiceStatus.value = `识别完成（${result.engine}），文字已放入输入框。`;
      } catch (err) {
        voiceStatus.value = err instanceof Error ? `识别失败：${err.message}` : '识别失败，请改用文字输入。';
      } finally {
        mediaRecorder.value = null;
      }
    });

    recorder.start();
    isRecording.value = true;
    voiceStatus.value = '录音中，说完后点击“停止录音”。';
  } catch (err) {
    voiceStatus.value = err instanceof Error ? `无法开启麦克风：${err.message}` : '无法开启麦克风，请检查浏览器权限。';
  }
}

function stopRecording() {
  if (mediaRecorder.value?.state === 'recording') {
    mediaRecorder.value.stop();
  }
}

function speakWithBrowser(text: string) {
  if (!window.speechSynthesis || typeof SpeechSynthesisUtterance === 'undefined') {
    voiceStatus.value = '后端还没有返回音频，当前浏览器也不支持本地朗读。';
    return false;
  }

  window.speechSynthesis.cancel();
  const utterance = new SpeechSynthesisUtterance(text.replace(/\n+/g, ' '));
  utterance.lang = 'zh-CN';
  utterance.rate = speechRate.value;
  utterance.pitch = speechPitch.value;
  utterance.onstart = () => {
    voiceStatus.value = '后端暂未返回音频 URL，正在使用浏览器本地朗读教练回复。';
  };
  utterance.onend = () => {
    voiceStatus.value = '浏览器本地朗读完成。';
  };
  utterance.onerror = () => {
    voiceStatus.value = '浏览器本地朗读失败，请稍后再试。';
  };
  window.speechSynthesis.speak(utterance);
  return true;
}

function stopCoachVoice() {
  if (window.speechSynthesis?.speaking) {
    window.speechSynthesis.cancel();
    voiceStatus.value = '已停止浏览器本地朗读。';
  }
}

async function playCoachVoice() {
  const text = lastCoachText.value || turns.value.findLast((turn) => turn.speaker === 'coach')?.text || '';
  if (!text) {
    voiceStatus.value = '还没有可播放的教练回复。';
    return;
  }

  isSynthesizing.value = true;
  voiceStatus.value = '正在请求语音合成……';

  try {
    const result = await synthesizeSpeech(text);
    if (result.audioUrl) {
      const audio = new Audio(result.audioUrl);
      await audio.play();
      voiceStatus.value = `正在播放教练语音（${result.engine}）。`;
      return;
    }

    if (!speakWithBrowser(text)) {
      voiceStatus.value = `已调用合成接口（${result.engine}），但当前后端占位服务还没有返回音频 URL。`;
    }
  } catch (err) {
    voiceStatus.value = err instanceof Error ? `播放失败：${err.message}` : '播放失败，请稍后再试。';
  } finally {
    isSynthesizing.value = false;
  }
}

const pageContext = proxyRefs({
  featuredTopics,
  journeySteps,
  coachMessages,
  openPractice,
  scrollToPracticePreview,
  currentTopic,
  activeChild,
  currentSideLabel,
  isLoadingTopics,
  selectedTopicId,
  topics,
  childProfiles,
  activeChildId,
  selectedSide,
  tips,
  applyTip,
  resetPractice,
  draft,
  wordCount,
  canSubmit,
  isRecording,
  stopRecording,
  startRecording,
  isLoadingReply,
  submitArgument,
  rubric,
  turns,
  playCoachVoice,
  isSynthesizing,
  stopCoachVoice,
  voiceStatus,
  activePracticeSessionId,
  error,
  ageRangeOptions,
  difficultyOptions,
  topicCollections,
  topicFilters,
  libraryTopics,
  updateTopicFilter,
  availableTags,
  favoriteTopicIds,
  topicLibraryStatus,
  showFavoritesOnly,
  updateFavoriteOnly,
  topicDifficultyLabel,
  openTopicDetail,
  isFavoriteTopic,
  toggleFavoriteTopic,
  editTopic,
  selectedLibraryTopic,
  chooseTopicAndPractice,
  canManageTopics,
  topicAdminStatus,
  topicAdminForm,
  resetTopicAdminForm,
  persistAdminTopic,
  removeAdminTopic,
  isSavingTopic,
  collectionAdminStatus,
  collectionAdminForm,
  editCollection,
  resetCollectionAdminForm,
  persistAdminCollection,
  removeAdminCollection,
  isSavingCollection,
  bulkImportText,
  bulkImportStatus,
  isImportingTopics,
  bulkReplaceExisting,
  importTopicBankJson,
  loadChildProfiles,
  selectActiveChild,
  childProfileStatus,
  editChildProfile,
  childProfileForm,
  resetChildProfileForm,
  removeChildProfile,
  persistChildProfile,
  voiceSteps,
  providerKeys,
  providerLabels,
  integrationStatus,
  integrationSettings,
  updateProvider,
  isSavingIntegrations,
  persistIntegrationSettings,
  sessions,
  sessionFilters,
  historyStatus,
  isLoadingSessions,
  formatSessionTime,
  loadSessions,
  updateSessionRange,
  updateSessionFilter,
  reportSummary,
  reportItems,
  reportTrend,
  reportWeakSpot,
  reportRecommendedTopic,
  reportParentComment,
  reportTeacherComment,
  reportNextGoal,
  reportCoachNote,
  practiceRecommendedTopic,
  exportReportPdf,
});


</script>

<template>
  <main class="home-shell">
    <AppNav :page="page" :current-user="currentUser" @navigate="openPage" @sign-out="signOut" />

    <AuthGate
      v-if="!currentUser"
      v-model:auth-mode="authMode"
      v-model:auth-email="authEmail"
      v-model:auth-password="authPassword"
      v-model:auth-display-name="authDisplayName"
      :auth-status="authStatus"
      @submit="submitAuth"
      @demo="loginWithDemo"
    />

    <RouterView v-else v-slot="{ Component }">
      <component :is="Component" :ctx="pageContext" />
    </RouterView>
  </main>
</template>
