import { createApp } from 'vue';
import App from './App.vue';
import { router } from './router';
import 'animal-island-vue/style';
import './styles.css';

createApp(App).use(router).mount('#app');
