import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import App from './App.vue'
import BooleanSearch from './components/BooleanSearch.vue'
import PhraseSearch from './components/PhraseSearch.vue'
import ExpandedSearch from './components/ExpandedSearch.vue'
import SoundexSearch from './components/SoundexSearch.vue'
import IndexViewer from './components/IndexViewer.vue'
import './style.css'

const routes = [
  { path: '/', redirect: '/boolean' },
  { path: '/boolean', component: BooleanSearch },
  { path: '/phrase', component: PhraseSearch },
  { path: '/expanded', component: ExpandedSearch },
  { path: '/soundex', component: SoundexSearch },
  { path: '/index', component: IndexViewer },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

createApp(App).use(router).mount('#app')
