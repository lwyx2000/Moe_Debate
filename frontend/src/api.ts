import type { AuthToken, ChildProfile, CoachResponse, DebateSession, DebateTopic, GrowthReport, SessionFilters, TopicBulkImportResult, TopicCollection, TopicFilters, IntegrationSettings, PracticeSession, SpeechSynthesisResult, SpeechTranscription, UserAccount } from './types';

const API_BASE = import.meta.env.VITE_API_BASE ?? '';
const AUTH_TOKEN_KEY = 'moe-debate-auth-token';

let authToken = localStorage.getItem(AUTH_TOKEN_KEY) ?? '';

export function setAuthToken(token: string) {
  authToken = token;
  if (token) {
    localStorage.setItem(AUTH_TOKEN_KEY, token);
  } else {
    localStorage.removeItem(AUTH_TOKEN_KEY);
  }
}

export function getAuthToken() {
  return authToken;
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const headers = init?.body instanceof FormData ? { ...(init.headers ?? {}) } : { 'Content-Type': 'application/json', ...(init?.headers ?? {}) };
  if (authToken) {
    (headers as Record<string, string>).Authorization = `Bearer ${authToken}`;
  }
  const response = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers,
  });

  if (!response.ok) {
    throw new Error(`API ${path} failed with ${response.status}`);
  }

  return response.json() as Promise<T>;
}

export async function login(email: string, password: string): Promise<AuthToken> {
  const result = await request<AuthToken>('/api/auth/login', {
    method: 'POST',
    body: JSON.stringify({ email, password }),
  });
  setAuthToken(result.accessToken);
  return result;
}

export async function register(email: string, password: string, displayName: string): Promise<AuthToken> {
  const result = await request<AuthToken>('/api/auth/register', {
    method: 'POST',
    body: JSON.stringify({ email, password, displayName }),
  });
  setAuthToken(result.accessToken);
  return result;
}

export function fetchMe(): Promise<UserAccount> {
  return request<UserAccount>('/api/auth/me');
}

export async function logout(): Promise<void> {
  try {
    await request<{ status: string }>('/api/auth/logout', { method: 'POST' });
  } finally {
    setAuthToken('');
  }
}

export function fetchTopics(filters: TopicFilters = {}): Promise<DebateTopic[]> {
  const params = new URLSearchParams();
  Object.entries(filters).forEach(([key, value]) => {
    if (value) params.set(key, value);
  });
  const query = params.toString();
  return request<DebateTopic[]>(`/api/topics${query ? `?${query}` : ''}`);
}


export function fetchTopic(topicId: string): Promise<DebateTopic> {
  return request<DebateTopic>(`/api/topics/${topicId}`);
}

export function fetchTopicCollections(): Promise<TopicCollection[]> {
  return request<TopicCollection[]>('/api/topic-collections');
}

export function createTopicCollection(collection: TopicCollection): Promise<TopicCollection> {
  return request<TopicCollection>('/api/admin/topic-collections', {
    method: 'POST',
    body: JSON.stringify(collection),
  });
}

export function updateTopicCollection(collection: TopicCollection): Promise<TopicCollection> {
  return request<TopicCollection>(`/api/admin/topic-collections/${collection.id}`, {
    method: 'PUT',
    body: JSON.stringify(collection),
  });
}

export function deleteTopicCollection(collectionId: string): Promise<{ status: string; id: string }> {
  return request<{ status: string; id: string }>(`/api/admin/topic-collections/${collectionId}`, { method: 'DELETE' });
}

export function importTopicBank(payload: { topics: DebateTopic[]; collections?: TopicCollection[]; replaceExisting?: boolean }): Promise<TopicBulkImportResult> {
  return request<TopicBulkImportResult>('/api/admin/topics/import', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}


export function fetchFavoriteTopics(): Promise<string[]> {
  return request<string[]>('/api/favorites/topics');
}

export function addFavoriteTopic(topicId: string): Promise<{ status: string; id: string }> {
  return request<{ status: string; id: string }>(`/api/favorites/topics/${topicId}`, { method: 'POST' });
}

export function deleteFavoriteTopic(topicId: string): Promise<{ status: string; id: string }> {
  return request<{ status: string; id: string }>(`/api/favorites/topics/${topicId}`, { method: 'DELETE' });
}

export function createTopic(topic: DebateTopic): Promise<DebateTopic> {
  return request<DebateTopic>('/api/admin/topics', {
    method: 'POST',
    body: JSON.stringify(topic),
  });
}

export function updateTopic(topic: DebateTopic): Promise<DebateTopic> {
  return request<DebateTopic>(`/api/admin/topics/${topic.id}`, {
    method: 'PUT',
    body: JSON.stringify(topic),
  });
}

export function deleteTopic(topicId: string): Promise<{ status: string; id: string }> {
  return request<{ status: string; id: string }>(`/api/admin/topics/${topicId}`, { method: 'DELETE' });
}

export function startPracticeSession(topicId: string, side: string, childId?: string): Promise<PracticeSession> {
  return request<PracticeSession>('/api/practice/sessions', {
    method: 'POST',
    body: JSON.stringify({ topicId, side, childId }),
  });
}

export function finishPracticeSession(sessionId: string, summary = ''): Promise<PracticeSession> {
  return request<PracticeSession>(`/api/practice/sessions/${sessionId}/finish`, {
    method: 'POST',
    body: JSON.stringify({ summary }),
  });
}

export function askCoach(topicId: string, side: string, message: string, childId?: string, practiceSessionId?: string): Promise<CoachResponse> {
  return request<CoachResponse>('/api/debate/respond', {
    method: 'POST',
    body: JSON.stringify({ topicId, side, message, childId, practiceSessionId }),
  });
}

export function transcribeAudio(audio: Blob, filename = 'recording.webm'): Promise<SpeechTranscription> {
  const formData = new FormData();
  formData.append('file', audio, filename);

  return request<SpeechTranscription>('/api/speech/transcribe', {
    method: 'POST',
    body: formData,
  });
}

export function synthesizeSpeech(text: string): Promise<SpeechSynthesisResult> {
  return request<SpeechSynthesisResult>('/api/speech/synthesize', {
    method: 'POST',
    body: JSON.stringify({ text }),
  });
}


export function fetchIntegrationSettings(): Promise<IntegrationSettings> {
  return request<IntegrationSettings>('/api/integrations/settings');
}

export function saveIntegrationSettings(settings: IntegrationSettings): Promise<IntegrationSettings> {
  return request<IntegrationSettings>('/api/integrations/settings', {
    method: 'PUT',
    body: JSON.stringify(settings),
  });
}


function sessionFilterParams(filters: Partial<SessionFilters> = {}) {
  const params = new URLSearchParams();
  if (filters.dateFrom) params.set('dateFrom', filters.dateFrom);
  if (filters.dateTo) params.set('dateTo', filters.dateTo);
  if (filters.topicId) params.set('topicId', filters.topicId);
  if (filters.collectionId) params.set('collectionId', filters.collectionId);
  return params;
}

export function fetchDemoReport(childId?: string, filters: Partial<SessionFilters> = {}): Promise<GrowthReport> {
  const params = sessionFilterParams(filters);
  if (childId) params.set('childId', childId);
  const query = params.toString();
  return request<GrowthReport>(`/api/reports/demo${query ? `?${query}` : ''}`);
}


export function fetchDebateSessions(limit = 20, childId?: string, filters: Partial<SessionFilters> = {}): Promise<DebateSession[]> {
  const params = sessionFilterParams(filters);
  params.set('limit', String(limit));
  if (childId) params.set('childId', childId);
  return request<DebateSession[]>(`/api/debate/sessions?${params.toString()}`);
}

export function fetchDemoUser(): Promise<UserAccount> {
  return request<UserAccount>('/api/users/demo');
}

export function fetchChildren(): Promise<ChildProfile[]> {
  return request<ChildProfile[]>('/api/children');
}

export function createChild(profile: ChildProfile): Promise<ChildProfile> {
  return request<ChildProfile>('/api/children', {
    method: 'POST',
    body: JSON.stringify(profile),
  });
}

export function updateChild(profile: ChildProfile): Promise<ChildProfile> {
  return request<ChildProfile>(`/api/children/${profile.id}`, {
    method: 'PUT',
    body: JSON.stringify(profile),
  });
}

export function deleteChild(childId: string): Promise<{ status: string; id: string }> {
  return request<{ status: string; id: string }>(`/api/children/${childId}`, { method: 'DELETE' });
}
