<template>
  <div class="results" v-if="results.length > 0">
    <article
      class="result-item"
      v-for="(item, i) in results"
      :key="item.doc_id"
      tabindex="0"
      @click="openDetail(item.doc_id)"
      @keyup.enter="openDetail(item.doc_id)"
    >
      <div class="result-header">
        <span class="result-rank">#{{ i + 1 }}</span>
        <span class="result-docid">Doc {{ item.doc_id }}</span>
        <span class="result-score" v-if="item.score != null">
          相似度: {{ item.score.toFixed(4) }}
        </span>
      </div>
      <h3 class="result-title" v-html="formatTitle(item.highlighted_title)"></h3>
      <p class="result-author" v-if="item.author">{{ item.author }}</p>
      <p class="result-snippet" v-html="item.highlighted_snippet"></p>
    </article>
  </div>
  <div class="no-results" v-else-if="searched">
    未找到结果
  </div>

  <DocumentModal v-if="detailDoc" :document="detailDoc" @close="closeDetail" />
</template>

<script setup>
import { ref } from 'vue'
import { getDocument } from '../api'
import DocumentModal from './DocumentModal.vue'

const props = defineProps({
  results: { type: Array, default: () => [] },
  totalCount: { type: Number, default: 0 },
  searched: { type: Boolean, default: false },
  highlightTerms: { type: String, default: '' },
})

const expandedId = ref(null)
const detailDoc = ref(null)

async function openDetail(docId) {
  expandedId.value = docId
  const res = await getDocument(docId, props.highlightTerms)
  detailDoc.value = res.data
}

function closeDetail() {
  expandedId.value = null
  detailDoc.value = null
}

function formatTitle(html) {
  let result = ''
  let i = 0
  let sentenceStart = true
  while (i < html.length) {
    const char = html[i]
    if (char === '<') {
      const tagEnd = html.indexOf('>', i)
      if (tagEnd === -1) {
        result += char
        i += 1
      } else {
        result += html.slice(i, tagEnd + 1)
        i = tagEnd + 1
      }
      continue
    }
    if (sentenceStart && /[A-Za-z]/.test(char)) {
      result += char.toUpperCase()
      sentenceStart = false
    } else {
      result += char
      if (/[A-Za-z0-9]/.test(char)) sentenceStart = false
    }
    if (/[.!?]/.test(char)) sentenceStart = true
    i += 1
  }
  return result
}
</script>
