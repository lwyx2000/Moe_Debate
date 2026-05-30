export interface DebateTopic {
  id: string;
  title: string;
  sideA: string;
  sideB: string;
  starterTips: string[];
  collectionId: string;
  ageRange: string;
  difficulty: string;
  tags: string[];
  background: string;
  sideATips: string[];
  sideBTips: string[];
  examples: string[];
}

export interface TopicCollection {
  id: string;
  icon: string;
  title: string;
  description: string;
  count: number;
  topicIds: string[];
}

export interface TopicBulkImportResult {
  importedTopics: number;
  importedCollections: number;
  mode: string;
}

export interface UserAccount {
  id: string;
  email: string;
  displayName: string;
  role: string;
  createdAt: string;
}

export interface AuthToken {
  accessToken: string;
  tokenType: string;
  user: UserAccount;
}

export interface ChildProfile {
  id: string;
  userId: string;
  name: string;
  age: number;
  grade: string;
  avatar: string;
  debateGoal: string;
  createdAt: string;
}

export interface DebateTurn {
  speaker: 'kid' | 'coach';
  text: string;
  badge?: string;
}

export interface Rubric {
  clarity: number;
  evidence: number;
  manners: number;
}

export interface CoachResponse {
  reply: string;
  rubric: Rubric;
  nextPrompt: string;
  practiceSessionId: string;
}

export interface SpeechTranscription {
  filename: string;
  text: string;
  engine: string;
}

export interface SpeechSynthesisResult {
  text: string;
  audioUrl: string;
  engine: string;
}


export interface ProviderConfig {
  enabled: boolean;
  baseUrl: string;
  model: string;
  apiKey: string;
}

export interface IntegrationSettings {
  llm: ProviderConfig;
  asr: ProviderConfig;
  tts: ProviderConfig;
  updatedAt: string;
}


export interface ReportMetric {
  key: string;
  title: string;
  score: number;
  hint: string;
}

export interface TrendPoint {
  label: string;
  clarity: number;
  evidence: number;
  manners: number;
}

export interface GrowthReport {
  childName: string;
  weekLabel: string;
  completedDebates: number;
  streakDays: number;
  metrics: ReportMetric[];
  coachNote: string;
  nextGoal: string;
  trend: TrendPoint[];
  weakSpot: string;
  recommendedTopicId: string;
  recommendedTopicTitle: string;
  parentComment: string;
  teacherComment: string;
  totalPracticeMinutes: number;
  activeDays: number;
}


export interface DebateConversationTurn {
  speaker: string;
  text: string;
  badge?: string;
  audioUrl?: string;
  source?: string;
  createdAt?: string;
  rubric?: Rubric | null;
}

export interface PracticeTurn extends DebateConversationTurn {
  id: string;
  sessionId: string;
  createdAt: string;
}

export interface PracticeSession {
  id: string;
  childId?: string | null;
  topicId: string;
  side: string;
  startedAt: string;
  endedAt?: string | null;
  durationSeconds: number;
  summary: string;
  totalTurns: number;
  averageRubric?: Rubric | null;
  turns: PracticeTurn[];
}

export interface DebateSession {
  id: string;
  practiceSessionId: string;
  childId?: string | null;
  topicId: string;
  side: string;
  message: string;
  coachReply: string;
  nextPrompt: string;
  rubric: Rubric;
  createdAt: string;
  durationMinutes: number;
  durationSeconds: number;
  startedAt: string;
  endedAt?: string | null;
  summary: string;
  totalTurns: number;
  conversation: DebateConversationTurn[];
}

export interface SessionFilters {
  range: 'all' | 'week' | 'month' | 'custom';
  dateFrom: string;
  dateTo: string;
  topicId: string;
  collectionId: string;
}


export interface TopicFilters {
  collectionId?: string;
  ageRange?: string;
  difficulty?: string;
  tag?: string;
  q?: string;
}
