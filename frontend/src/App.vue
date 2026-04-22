<template>
  <div class="app">
    <header>
      <div class="header-top">
        <h1>
          <span class="logo-icon">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/>
            </svg>
          </span>
          Cranfield IR
        </h1>
        <span class="badge">1,400 docs</span>
      </div>
      <nav>
        <router-link to="/boolean">布尔检索</router-link>
        <router-link to="/phrase">短语查询</router-link>
        <router-link to="/expanded">查询扩展</router-link>
        <router-link to="/soundex">发音矫正</router-link>
        <router-link to="/index">词典浏览</router-link>
      </nav>
    </header>
    <main>
      <router-view />
    </main>
  </div>
</template>

<script setup>
</script>

<style scoped>
.header-top {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 14px;
}

h1 {
  display: flex;
  align-items: center;
  gap: 8px;
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

.badge {
  font-size: 11.5px;
  font-weight: 500;
  color: var(--text-tertiary);
  background: var(--border-light);
  padding: 3px 10px;
  border-radius: 20px;
  font-family: var(--font-mono);
  border: 1px solid var(--border);
}

@media (max-width: 480px) {
  .logo-icon {
    width: 28px;
    height: 28px;
    border-radius: 6px;
  }

  .logo-icon svg {
    width: 16px;
    height: 16px;
  }

  .badge {
    font-size: 10.5px;
    padding: 2px 8px;
  }
}
</style>
