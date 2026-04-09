<template>
  <div class="search-page">
    <h2>词典与倒排记录表</h2>
    <div class="search-bar">
      <input
        v-model="search"
        @keyup.enter="loadDict(1)"
        placeholder="按前缀过滤词项，如 aero"
      />
      <button class="btn-search" @click="loadDict(1)">筛选</button>
    </div>

    <div class="postings-panel" v-if="postingsData" ref="postingsRef">
      <h3>
        倒排记录: <code>{{ postingsData.term }}</code>
        (词干: <code>{{ postingsData.stemmed_term }}</code>, DF: {{ postingsData.df }})
      </h3>
      <div class="postings-scroll">
        <table class="postings-table">
          <thead>
            <tr>
              <th>文档 ID</th>
              <th>词频 (TF)</th>
              <th>位置列表</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="p in postingsData.postings" :key="p.doc_id">
              <td>{{ p.doc_id }}</td>
              <td>{{ p.tf }}</td>
              <td class="positions">{{ p.positions.join(', ') }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div class="dict-info" v-if="total > 0">
      <p>共 <strong>{{ total }}</strong> 个词项（第 {{ page }} 页）</p>
    </div>

    <table class="dict-table" v-if="terms.length > 0">
      <colgroup>
        <col style="width: 35%" />
        <col style="width: 20%" />
        <col style="width: 20%" />
        <col style="width: 25%" />
      </colgroup>
      <thead>
        <tr>
          <th>词项 (Term)</th>
          <th>文档频率 (DF)</th>
          <th>总词频</th>
          <th>操作</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="t in terms" :key="t.term">
          <td class="term-cell">{{ t.term }}</td>
          <td>{{ t.df }}</td>
          <td>{{ t.total_freq }}</td>
          <td><button class="btn-small" @click="loadPostings(t.term)">查看倒排记录</button></td>
        </tr>
      </tbody>
    </table>

    <div class="pagination" v-if="totalPages > 1">
      <button :disabled="page <= 1" @click="loadDict(page - 1)">上一页</button>
      <span>{{ page }} / {{ totalPages }}</span>
      <button :disabled="page >= totalPages" @click="loadDict(page + 1)">下一页</button>
    </div>

  </div>
</template>

<script setup>
import { ref, nextTick, onMounted } from 'vue'
import { getDictionary, getPostings } from '../api'

const search = ref('')
const terms = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = 50
const totalPages = ref(0)
const postingsData = ref(null)
const postingsRef = ref(null)

async function loadDict(p = 1) {
  page.value = p
  const res = await getDictionary(p, pageSize, search.value.trim())
  terms.value = res.data.terms
  total.value = res.data.total
  totalPages.value = Math.ceil(res.data.total / pageSize)
}

async function loadPostings(term) {
  try {
    const res = await getPostings(term)
    postingsData.value = res.data
    await nextTick()
    postingsRef.value?.scrollIntoView({ behavior: 'smooth', block: 'start' })
  } catch (e) {
    console.error('Failed to load postings:', e)
  }
}

onMounted(() => loadDict(1))
</script>
