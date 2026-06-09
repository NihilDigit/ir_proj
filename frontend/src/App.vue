<template>
  <div class="app" :class="{ 'search-home-app': isSearchHome }">
    <header :class="{ 'home-header': isSearchHome }">
      <div class="header-top">
        <router-link v-if="!isSearchHome" class="brand-link" to="/search">
          <span class="logo-icon">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/>
            </svg>
          </span>
          Cranfield IR
        </router-link>
        <div v-else class="brand-spacer" />
        <router-link v-if="!isIndex" class="top-action dictionary-action" to="/index">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
            <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/>
            <path d="M4 4.5A2.5 2.5 0 0 1 6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5z"/>
          </svg>
          词典浏览
        </router-link>
        <button v-else class="top-action icon-action" @click="closeIndex" aria-label="关闭词典浏览">
          ×
        </button>
      </div>
    </header>
    <main>
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()
const isIndex = computed(() => route.path === '/index')
const isSearchHome = computed(() => route.path === '/search' && !route.query.q)

function closeIndex() {
  if (window.history.state?.back) {
    router.back()
  } else {
    router.push('/search')
  }
}
</script>

<style scoped>
.header-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

:global(header.home-header) {
  border-bottom-color: transparent;
}

.brand-spacer {
  width: 1px;
}

.brand-link {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--text);
  font-size: 22px;
  font-weight: 700;
  letter-spacing: -0.3px;
  text-decoration: none;
}

.logo-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  background: var(--primary);
  color: white;
  border-radius: 8px;
}

.top-action {
  min-height: 36px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border: 1px solid var(--border);
  border-radius: var(--radius);
  background: var(--card-bg);
  color: var(--text-secondary);
  padding: 7px 13px;
  text-decoration: none;
  font-size: 13px;
  font-weight: 500;
  font-family: var(--font-sans);
  cursor: pointer;
  transition: all var(--transition);
  gap: 8px;
}

.top-action:hover {
  border-color: var(--primary);
  color: var(--primary);
  background: var(--primary-soft);
}

.dictionary-action {
  background: var(--primary);
  border-color: var(--primary);
  color: white;
}

.dictionary-action:hover {
  background: var(--primary-hover);
  border-color: var(--primary-hover);
  color: white;
  box-shadow: 0 2px 8px rgba(37, 99, 235, 0.25);
}

.icon-action {
  width: 36px;
  padding: 0;
  font-size: 22px;
  line-height: 1;
}

@media (max-width: 480px) {
  .brand-link {
    font-size: 18px;
  }

  .logo-icon {
    width: 28px;
    height: 28px;
    border-radius: 6px;
  }

  .logo-icon svg {
    width: 16px;
    height: 16px;
  }
}
</style>
