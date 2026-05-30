import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router';
import HomePage from './pages/HomePage.vue';
import PracticePage from './pages/PracticePage.vue';
import TopicLibraryPage from './pages/TopicLibraryPage.vue';
import ProfilesPage from './pages/ProfilesPage.vue';
import HistoryPage from './pages/HistoryPage.vue';
import ReportPage from './pages/ReportPage.vue';
import VoiceSetupPage from './pages/VoiceSetupPage.vue';

export type PageMode = 'home' | 'practice' | 'topicLibrary' | 'profiles' | 'history' | 'report' | 'voiceSetup';

export const routes: RouteRecordRaw[] = [
  { path: '/', name: 'home', component: HomePage },
  { path: '/practice', name: 'practice', component: PracticePage },
  { path: '/topics', name: 'topicLibrary', component: TopicLibraryPage },
  { path: '/profiles', name: 'profiles', component: ProfilesPage },
  { path: '/history', name: 'history', component: HistoryPage },
  { path: '/report', name: 'report', component: ReportPage },
  { path: '/voice-setup', name: 'voiceSetup', component: VoiceSetupPage },
];

export const router = createRouter({
  history: createWebHistory(),
  routes,
});

export function pageFromPath(pathname = window.location.pathname): PageMode {
  const resolved = router.resolve(pathname);
  return (resolved.name as PageMode | undefined) ?? 'home';
}

export function pathForPage(page: PageMode): string {
  return router.resolve({ name: page }).href;
}

export function pushPageRoute(page: PageMode) {
  void router.push({ name: page });
}

export function replacePageRoute(page: PageMode) {
  void router.replace({ name: page });
}

export function subscribeRouteChange(callback: (page: PageMode) => void) {
  return router.afterEach((to) => callback((to.name as PageMode | undefined) ?? 'home'));
}
