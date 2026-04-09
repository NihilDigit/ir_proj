<template>
  <div class="results" v-if="results.length > 0">
    <p class="result-count">
      共找到 <strong>{{ totalCount }}</strong> 条结果
      <span v-if="results.length < totalCount">（显示前 {{ results.length }} 条）</span>
    </p>
    <div class="result-item" v-for="(item, i) in results" :key="item.doc_id">
      <div class="result-header">
        <span class="result-rank">#{{ i + 1 }}</span>
        <span class="result-docid">Doc {{ item.doc_id }}</span>
        <span class="result-score" v-if="item.score != null">
          相似度: {{ item.score.toFixed(4) }}
        </span>
      </div>
      <h3 class="result-title" v-html="item.highlighted_title"></h3>
      <p class="result-author" v-if="item.author">{{ item.author }}</p>
      <p class="result-snippet" v-html="item.highlighted_snippet"></p>
      <button class="btn-detail" @click="toggleDetail(item.doc_id)">
        {{ expandedId === item.doc_id ? '收起' : '查看详情' }}
      </button>
      <div class="doc-detail" v-if="expandedId === item.doc_id && detailDoc">
        <h4>完整内容</h4>
        <p><strong>标题:</strong> <span v-html="detailDoc.highlighted_title"></span></p>
        <p><strong>作者:</strong> {{ detailDoc.author }}</p>
        <p><strong>出处:</strong> {{ detailDoc.bib }}</p>
        <div class="doc-text" v-html="detailDoc.highlighted_text"></div>
      </div>
    </div>
  </div>
  <div class="no-results" v-else-if="searched">
    未找到结果
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { getDocument } from '../api'

const props = defineProps({
  results: { type: Array, default: () => [] },
  totalCount: { type: Number, default: 0 },
  searched: { type: Boolean, default: false },
  highlightTerms: { type: String, default: '' },
})

const expandedId = ref(null)
const detailDoc = ref(null)

async function toggleDetail(docId) {
  if (expandedId.value === docId) {
    expandedId.value = null
    detailDoc.value = null
    return
  }
  expandedId.value = docId
  const res = await getDocument(docId, props.highlightTerms)
  detailDoc.value = res.data
}
</script>
