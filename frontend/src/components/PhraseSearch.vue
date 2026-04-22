<template>
  <div class="search-page">
    <h2>短语查询</h2>
    <div class="search-bar">
      <input
        v-model="query"
        @keyup.enter="doSearch"
        placeholder="输入短语，如 boundary layer"
      />
      <button class="btn-search" @click="doSearch" :disabled="loading">搜索</button>
    </div>
    <p class="hint">输入连续的短语，系统会查找这些词按顺序连续出现的文档</p>
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
import { phraseSearch } from '../api'
import ResultList from './ResultList.vue'

const route = useRoute()
const query = ref('')
const results = ref([])
const totalCount = ref(0)
const searched = ref(false)
const loading = ref(false)
const highlightTerms = ref('')

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
    const res = await phraseSearch(query.value)
    results.value = res.data.results
    totalCount.value = res.data.result_count
    highlightTerms.value = query.value.trim().split(/\s+/).join(',')
  } catch (e) {
    results.value = []
    totalCount.value = 0
  } finally {
    loading.value = false
  }
}
</script>
