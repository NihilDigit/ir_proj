<template>
  <div class="search-workspace" :class="{ 'has-results': searched }">
    <section class="search-hero" v-if="!searched">
      <h1 class="hero-title">
        <span class="hero-logo">
          <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
            <circle cx="11" cy="11" r="8"/>
            <path d="m21 21-4.3-4.3"/>
          </svg>
        </span>
        Cranfield IR
      </h1>
      <div class="workspace-search">
        <div class="search-pill">
          <div class="search-input-wrap">
          <div class="operator-float" v-if="selectedMode === 'boolean'">
            <button type="button" @click="insertOp('AND')">AND</button>
            <button type="button" @click="insertOp('OR')">OR</button>
            <button type="button" @click="insertOp('NOT')">NOT</button>
            <span class="operator-divider" aria-hidden="true"></span>
            <button type="button" @click="insertOp('(')">(</button>
            <button type="button" @click="insertOp(')')">)</button>
          </div>
          <input
            ref="inputRef"
            v-model="query"
            @click="showHistory = true"
            @blur="hideHistory"
            @keyup.enter="doSearch"
            @keydown.tab="completeExample"
            :placeholder="currentMode.placeholder"
          />
          <div class="search-history" v-if="showHistoryPanel">
            <div
              v-for="item in currentHistory"
              :key="item"
              class="history-row"
            >
              <button type="button" class="history-text" @mousedown.prevent="useHistory(item)">
                {{ item }}
              </button>
              <button
                type="button"
                class="history-delete"
                aria-label="删除搜索记录"
                @mousedown.prevent="deleteHistory(item)"
              >
                ×
              </button>
            </div>
          </div>
          </div>
          <div class="pill-divider" v-if="hasInlineSetting" aria-hidden="true"></div>
          <div class="inline-dropdown" v-if="hasInlineSetting" @focusout="hideInlineMenu">
            <button type="button" class="inline-dropdown-trigger" @click="toggleInlineMenu">
              {{ currentSettingLabel }}
              <span class="dropdown-caret" aria-hidden="true"></span>
            </button>
            <div class="inline-dropdown-menu" v-if="showInlineMenu">
              <button
                v-for="option in currentSettingOptions"
                :key="option.value"
                type="button"
                :class="{ selected: option.value === currentSettingValue }"
                @mousedown.prevent="selectInlineValue(option.value)"
              >
                {{ option.label }}
              </button>
            </div>
          </div>
        </div>
        <button class="btn-search" @click="doSearch" :disabled="loading">搜索</button>
      </div>

      <div class="mode-chips">
        <button
          v-for="mode in modes"
          :key="mode.key"
          class="mode-chip"
          :class="{ active: selectedMode === mode.key }"
          @click="selectMode(mode.key)"
        >
          <span class="mode-icon" :class="`mode-icon-${mode.key}`" v-html="mode.icon" />
          {{ mode.label }}
        </button>
      </div>

      <div class="mode-options"></div>
    </section>

    <section class="search-results-page" v-else>
      <div class="results-searchbar">
        <router-link class="results-brand" to="/search">Cranfield IR</router-link>
        <div class="workspace-search compact">
          <div class="search-pill">
            <div class="search-input-wrap">
            <div class="operator-float" v-if="selectedMode === 'boolean'">
              <button type="button" @click="insertOp('AND')">AND</button>
              <button type="button" @click="insertOp('OR')">OR</button>
              <button type="button" @click="insertOp('NOT')">NOT</button>
              <span class="operator-divider" aria-hidden="true"></span>
              <button type="button" @click="insertOp('(')">(</button>
              <button type="button" @click="insertOp(')')">)</button>
            </div>
            <input
              ref="inputRef"
              v-model="query"
              @click="showHistory = true"
              @blur="hideHistory"
              @keyup.enter="doSearch"
              @keydown.tab="completeExample"
              :placeholder="currentMode.placeholder"
            />
            <div class="search-history" v-if="showHistoryPanel">
              <div
                v-for="item in currentHistory"
                :key="item"
                class="history-row"
              >
                <button type="button" class="history-text" @mousedown.prevent="useHistory(item)">
                  {{ item }}
                </button>
                <button
                  type="button"
                  class="history-delete"
                  aria-label="删除搜索记录"
                  @mousedown.prevent="deleteHistory(item)"
                >
                  ×
                </button>
              </div>
            </div>
            </div>
            <div class="pill-divider" v-if="hasInlineSetting" aria-hidden="true"></div>
            <div class="inline-dropdown" v-if="hasInlineSetting" @focusout="hideInlineMenu">
              <button type="button" class="inline-dropdown-trigger" @click="toggleInlineMenu">
                {{ currentSettingLabel }}
                <span class="dropdown-caret" aria-hidden="true"></span>
              </button>
              <div class="inline-dropdown-menu" v-if="showInlineMenu">
                <button
                  v-for="option in currentSettingOptions"
                  :key="option.value"
                  type="button"
                  :class="{ selected: option.value === currentSettingValue }"
                  @mousedown.prevent="selectInlineValue(option.value)"
                >
                  {{ option.label }}
                </button>
              </div>
            </div>
          </div>
          <button class="btn-search" @click="doSearch" :disabled="loading">搜索</button>
        </div>
      </div>

      <div class="result-summary">
        <span v-if="loading">搜索中...</span>
        <span v-else>约 {{ totalCount }} 条结果 · {{ currentMode.label }}</span>
      </div>

      <div class="expansion-info compact-info" v-if="selectedMode === 'expanded' && expansionMap && Object.keys(expansionMap).length > 0">
        <h3>同义词扩展</h3>
        <div class="expansion-grid">
          <div class="expansion-item" v-for="(synonyms, term) in expansionMap" :key="term">
            <span class="original-term">{{ term }}</span>
            <span class="arrow">&rarr;</span>
            <span class="synonyms">
              <span class="synonym-tag" v-for="s in synonyms" :key="s">{{ s }}</span>
              <span v-if="synonyms.length === 0" class="no-synonyms">无同义词</span>
            </span>
          </div>
        </div>
      </div>

      <div class="expansion-info compact-info" v-if="selectedMode === 'soundex' && suggestionMap && Object.keys(suggestionMap).length > 0">
        <h3>发音编码与候选词</h3>
        <div class="expansion-grid">
          <div class="expansion-item" v-for="(info, term) in suggestionMap" :key="term">
            <span class="original-term">{{ term }}</span>
            <span class="code-tag">{{ info.code }}</span>
            <span class="arrow">&rarr;</span>
            <span class="synonyms">
              <span class="synonym-tag" v-for="c in info.candidates" :key="c">{{ c }}</span>
              <span v-if="info.candidates.length === 0" class="no-synonyms">词典中无相近词</span>
            </span>
          </div>
        </div>
      </div>

      <ResultList
        :results="results"
        :total-count="totalCount"
        :searched="searched"
        :highlight-terms="highlightTerms"
      />
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { booleanSearch, expandedSearch, phraseSearch, soundexSearch } from '../api'
import ResultList from './ResultList.vue'

const modes = [
  {
    key: 'boolean',
    label: '布尔检索',
    placeholder: '输入查询词，如 aerodynamics AND wing NOT flutter',
    example: 'aerodynamics AND wing NOT flutter',
    icon: '<span>AND</span>',
  },
  {
    key: 'phrase',
    label: '短语查询',
    placeholder: '输入短语，如 aerodynamic heating',
    example: 'aerodynamic heating',
    icon: '<span>&quot;&quot;</span>',
  },
  {
    key: 'expanded',
    label: '查询扩展',
    placeholder: '输入查询词，如 velocity',
    example: 'velocity',
    icon: '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="2"/><circle cx="5" cy="6" r="2"/><circle cx="19" cy="6" r="2"/><circle cx="5" cy="18" r="2"/><circle cx="19" cy="18" r="2"/><path d="m7 7 3.5 3.5"/><path d="m17 7-3.5 3.5"/><path d="m7 17 3.5-3.5"/><path d="m17 17-3.5-3.5"/></svg>',
  },
  {
    key: 'soundex',
    label: '发音矫正',
    placeholder: '输入查询词，如 shok',
    example: 'shok',
    icon: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 9v6"/><path d="M9 6v12"/><path d="M13 10v4"/><path d="M17 7v10"/><path d="M21 11v2"/></svg>',
  },
]

const route = useRoute()
const router = useRouter()
const inputRef = ref(null)
const selectedMode = ref('boolean')
const query = ref('')
const results = ref([])
const totalCount = ref(0)
const searched = ref(false)
const loading = ref(false)
const highlightTerms = ref('')
const maxSynonyms = ref(1)
const limitPerTerm = ref(5)
const expansionMap = ref(null)
const suggestionMap = ref(null)
const showHistory = ref(false)
const showInlineMenu = ref(false)
const historyByMode = ref({})
const HISTORY_KEY = 'cranfield-ir-search-history'

const currentMode = computed(
  () => modes.find(mode => mode.key === selectedMode.value) || modes[0]
)
const currentHistory = computed(() => historyByMode.value[selectedMode.value] || [])
const hasInlineSetting = computed(() => (
  selectedMode.value === 'expanded' || selectedMode.value === 'soundex'
))
const settingOptions = {
  expanded: [
    { value: 1, label: '1 个同义词' },
    { value: 2, label: '2 个同义词' },
    { value: 3, label: '3 个同义词' },
    { value: 5, label: '5 个同义词' },
  ],
  soundex: [
    { value: 3, label: '3 个候选' },
    { value: 5, label: '5 个候选' },
    { value: 10, label: '10 个候选' },
  ],
}
const currentSettingOptions = computed(() => settingOptions[selectedMode.value] || [])
const currentSettingValue = computed(() => (
  selectedMode.value === 'expanded' ? maxSynonyms.value : limitPerTerm.value
))
const currentSettingLabel = computed(() => {
  const option = currentSettingOptions.value.find(item => item.value === currentSettingValue.value)
  return option?.label || ''
})
const showHistoryPanel = computed(
  () => showHistory.value && !query.value.trim() && currentHistory.value.length > 0
)

function normalizeMode(mode) {
  return modes.some(item => item.key === mode) ? mode : 'boolean'
}

function syncFromRoute(runSearch = false) {
  selectedMode.value = normalizeMode(String(route.query.mode || 'boolean'))
  query.value = route.query.q ? String(route.query.q) : ''
  if (!query.value) {
    resetResults()
    return
  }
  if (runSearch) doSearch(false)
}

function resetResults() {
  searched.value = false
  loading.value = false
  results.value = []
  totalCount.value = 0
  highlightTerms.value = ''
  expansionMap.value = null
  suggestionMap.value = null
}

function selectMode(mode) {
  selectedMode.value = mode
  resetResults()
  showHistory.value = false
  showInlineMenu.value = false
  requestAnimationFrame(() => inputRef.value?.focus())
}

function insertOp(op) {
  const el = inputRef.value
  if (!el) return
  const start = el.selectionStart
  const end = el.selectionEnd
  const before = query.value.slice(0, start)
  const after = query.value.slice(end)
  const insert = (before && !before.endsWith(' ') ? ' ' : '') + op + ' '
  query.value = before + insert + after
  const newPos = start + insert.length
  requestAnimationFrame(() => {
    el.focus()
    el.setSelectionRange(newPos, newPos)
  })
}

function completeExample(event) {
  if (query.value.trim()) return
  event.preventDefault()
  query.value = currentMode.value.example
  requestAnimationFrame(() => {
    inputRef.value?.focus()
    inputRef.value?.setSelectionRange(query.value.length, query.value.length)
  })
}

function loadHistory() {
  try {
    const parsed = JSON.parse(localStorage.getItem(HISTORY_KEY) || '{}')
    historyByMode.value = Object.fromEntries(
      modes.map(mode => [
        mode.key,
        Array.isArray(parsed[mode.key]) ? parsed[mode.key].slice(0, 5) : [],
      ])
    )
  } catch (e) {
    historyByMode.value = Object.fromEntries(modes.map(mode => [mode.key, []]))
  }
}

function saveHistory() {
  localStorage.setItem(HISTORY_KEY, JSON.stringify(historyByMode.value))
}

function recordHistory(value) {
  const trimmed = value.trim()
  if (!trimmed) return
  const list = currentHistory.value.filter(item => item !== trimmed)
  historyByMode.value = {
    ...historyByMode.value,
    [selectedMode.value]: [trimmed, ...list].slice(0, 5),
  }
  saveHistory()
}

function useHistory(value) {
  query.value = value
  showHistory.value = false
  requestAnimationFrame(() => inputRef.value?.focus())
}

function deleteHistory(value) {
  historyByMode.value = {
    ...historyByMode.value,
    [selectedMode.value]: currentHistory.value.filter(item => item !== value),
  }
  saveHistory()
  showHistory.value = currentHistory.value.length > 0
  requestAnimationFrame(() => inputRef.value?.focus())
}

function toggleInlineMenu() {
  showInlineMenu.value = !showInlineMenu.value
}

function hideInlineMenu() {
  window.setTimeout(() => {
    showInlineMenu.value = false
  }, 120)
}

function selectInlineValue(value) {
  if (selectedMode.value === 'expanded') {
    maxSynonyms.value = value
  } else if (selectedMode.value === 'soundex') {
    limitPerTerm.value = value
  }
  showInlineMenu.value = false
}

function hideHistory() {
  window.setTimeout(() => {
    showHistory.value = false
  }, 120)
}

async function doSearch(pushRoute = true) {
  const trimmed = query.value.trim()
  if (!trimmed) return
  if (pushRoute) {
    const nextQuery = { mode: selectedMode.value, q: trimmed }
    if (route.path !== '/search' || route.query.mode !== nextQuery.mode || route.query.q !== nextQuery.q) {
      router.push({ path: '/search', query: nextQuery })
      return
    }
  }
  loading.value = true
  searched.value = true
  showHistory.value = false
  recordHistory(trimmed)
  expansionMap.value = null
  suggestionMap.value = null
  try {
    if (selectedMode.value === 'boolean') {
      const res = await booleanSearch(trimmed)
      results.value = res.data.results
      totalCount.value = res.data.result_count
      highlightTerms.value = trimmed
        .replace(/[()]/g, ' ')
        .split(/\s+/)
        .filter(t => !['AND', 'OR', 'NOT', ''].includes(t.toUpperCase()))
        .join(',')
    } else if (selectedMode.value === 'phrase') {
      const res = await phraseSearch(trimmed)
      results.value = res.data.results
      totalCount.value = res.data.result_count
      highlightTerms.value = trimmed.split(/\s+/).join(',')
    } else if (selectedMode.value === 'expanded') {
      const res = await expandedSearch(trimmed, maxSynonyms.value)
      results.value = res.data.results
      totalCount.value = res.data.result_count
      expansionMap.value = res.data.expansion_map
      highlightTerms.value = res.data.expanded_query_terms.join(',')
    } else {
      const res = await soundexSearch(trimmed, limitPerTerm.value)
      results.value = res.data.results
      totalCount.value = res.data.result_count
      suggestionMap.value = res.data.suggestion_map
      highlightTerms.value = res.data.expanded_query_terms.join(',')
    }
  } catch (e) {
    results.value = []
    totalCount.value = 0
    expansionMap.value = null
    suggestionMap.value = null
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadHistory()
  syncFromRoute(true)
  if (!query.value) requestAnimationFrame(() => inputRef.value?.focus())
})

watch(
  () => [route.query.mode, route.query.q],
  () => syncFromRoute(Boolean(route.query.q))
)
</script>
