<template>
  <div class="search-page">
    <h2>发音矫正（Soundex）</h2>
    <p class="hint">
      将输入词通过 Soundex 算法编码为「首字母 + 3 位数字」，在词典中查找发音相近的候选词，用于拼写纠错与检索。
    </p>
    <div class="search-bar">
      <input
        v-model="query"
        @keyup.enter="doSearch"
        placeholder="输入查询词，如 bounderi / flo / heet"
      />
      <select v-model.number="limitPerTerm">
        <option :value="3">3 个候选</option>
        <option :value="5">5 个候选</option>
        <option :value="10">10 个候选</option>
      </select>
      <button class="btn-search" @click="doSearch" :disabled="loading">搜索</button>
    </div>

    <div class="expansion-info" v-if="suggestionMap && Object.keys(suggestionMap).length > 0">
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

    <div class="loading" v-if="loading">搜索中...</div>
    <ResultList
      :results="results"
      :total-count="totalCount"
      :searched="searched"
      :highlight-terms="highlightTerms"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { soundexSearch } from '../api'
import ResultList from './ResultList.vue'

const route = useRoute()
const query = ref('')
const limitPerTerm = ref(5)
const results = ref([])
const totalCount = ref(0)
const searched = ref(false)
const loading = ref(false)
const highlightTerms = ref('')
const suggestionMap = ref(null)

onMounted(() => {
  if (route.query.q) {
    query.value = String(route.query.q)
    doSearch()
  }
})

async function doSearch() {
  if (!query.value.trim()) return
  loading.value = true
  searched.value = true
  try {
    const res = await soundexSearch(query.value, limitPerTerm.value)
    results.value = res.data.results
    totalCount.value = res.data.result_count
    suggestionMap.value = res.data.suggestion_map
    highlightTerms.value = res.data.expanded_query_terms.join(',')
  } catch (e) {
    results.value = []
    totalCount.value = 0
    suggestionMap.value = null
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.hint {
  color: var(--text-tertiary);
  font-size: 13px;
  margin-bottom: 14px;
}
.code-tag {
  font-family: var(--font-mono);
  font-size: 12px;
  background: var(--border-light);
  border: 1px solid var(--border);
  border-radius: 4px;
  padding: 1px 8px;
  color: var(--text-secondary);
  margin: 0 6px;
}
</style>
