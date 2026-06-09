import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import App from './App.vue'
import SearchWorkspace from './components/SearchWorkspace.vue'
import IndexViewer from './components/IndexViewer.vue'
import './style.css'

const routes = [
  { path: '/', redirect: '/search' },
  { path: '/search', component: SearchWorkspace },
  { path: '/boolean', redirect: { path: '/search', query: { mode: 'boolean' } } },
  { path: '/phrase', redirect: { path: '/search', query: { mode: 'phrase' } } },
  { path: '/expanded', redirect: { path: '/search', query: { mode: 'expanded' } } },
  { path: '/soundex', redirect: { path: '/search', query: { mode: 'soundex' } } },
  { path: '/index', component: IndexViewer },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

createApp(App).use(router).mount('#app')
