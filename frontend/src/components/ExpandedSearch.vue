<template>
  <div class="search-page">
    <h2>查询扩展</h2>
    <div class="search-bar">
      <input
        v-model="query"
        @keyup.enter="doSearch"
        placeholder="输入查询词，如 heat transfer"
      />
      <select v-model.number="maxSynonyms">
        <option :value="1">1 个同义词</option>
        <option :value="2">2 个同义词</option>
        <option :value="3">3 个同义词</option>
        <option :value="5">5 个同义词</option>
      </select>
      <button class="btn-search" @click="doSearch" :disabled="loading">搜索</button>
    </div>

    <div class="expansion-info" v-if="expansionMap && Object.keys(expansionMap).length > 0">
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
import { ref } from 'vue'
import { expandedSearch } from '../api'
import ResultList from './ResultList.vue'

const query = ref('')
const maxSynonyms = ref(3)
const results = ref([])
const totalCount = ref(0)
const searched = ref(false)
const loading = ref(false)
const highlightTerms = ref('')
const expansionMap = ref(null)

async function doSearch() {
  if (!query.value.trim()) return
  loading.value = true
  searched.value = true
  try {
    const res = await expandedSearch(query.value, maxSynonyms.value)
    results.value = res.data.results
    totalCount.value = res.data.result_count
    expansionMap.value = res.data.expansion_map
    highlightTerms.value = res.data.expanded_query_terms.join(',')
  } catch (e) {
    results.value = []
    totalCount.value = 0
    expansionMap.value = null
  } finally {
    loading.value = false
  }
}
</script>
