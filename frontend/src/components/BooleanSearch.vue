<template>
  <div class="search-page">
    <h2>布尔检索</h2>
    <div class="search-bar">
      <input
        ref="inputRef"
        v-model="query"
        @keyup.enter="doSearch"
        placeholder="输入查询词，如 aerodynamics AND wing NOT flutter"
      />
      <button class="btn-search" @click="doSearch" :disabled="loading">搜索</button>
    </div>
    <div class="operator-buttons">
      <button @click="insertOp('AND')">AND</button>
      <button @click="insertOp('OR')">OR</button>
      <button @click="insertOp('NOT')">NOT</button>
      <button @click="insertOp('(')">(</button>
      <button @click="insertOp(')')">)</button>
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
import { booleanSearch } from '../api'
import ResultList from './ResultList.vue'

const route = useRoute()

const query = ref('')
const results = ref([])
const totalCount = ref(0)
const searched = ref(false)
const loading = ref(false)
const highlightTerms = ref('')
const inputRef = ref(null)

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
    const res = await booleanSearch(query.value)
    results.value = res.data.results
    totalCount.value = res.data.result_count
    // 提取纯词项用于高亮
    highlightTerms.value = query.value
      .replace(/[()]/g, ' ')
      .split(/\s+/)
      .filter(t => !['AND', 'OR', 'NOT', ''].includes(t.toUpperCase()))
      .join(',')
  } catch (e) {
    results.value = []
    totalCount.value = 0
  } finally {
    loading.value = false
  }
}
</script>
