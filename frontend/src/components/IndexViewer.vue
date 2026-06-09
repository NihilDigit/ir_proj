<template>
  <div class="search-page index-page">
    <div class="index-layout">
      <section class="dictionary-pane" aria-label="Dictionary">
        <div class="search-bar index-search">
          <input
            v-model="search"
            @keyup.enter="applySearch"
            placeholder="按前缀过滤词项，如 aero"
          />
          <button class="btn-search" @click="applySearch">筛选</button>
        </div>

        <div class="alphabet-row">
          <button class="alpha-arrow" @click="scrollAlphabet(-1)" aria-label="向左滚动">
            ◂
          </button>
          <div class="alpha-strip" ref="alphabetRef">
            <button
              v-for="letter in alphabet"
              :key="letter"
              class="alpha-item"
              :class="{ active: selectedLetter === letter && !search.trim() }"
              @click="selectLetter(letter)"
            >
              {{ selectedLetter === letter && !search.trim() ? `[${letter}]` : letter }}
            </button>
          </div>
          <button class="alpha-arrow" @click="scrollAlphabet(1)" aria-label="向右滚动">
            ▸
          </button>
        </div>

        <div class="dict-info" v-if="total > 0">
          共 {{ total }} 个词项（第 {{ page }} 页）
        </div>

        <div class="dictionary-body" ref="dictionaryBodyRef">
          <table class="dict-table" v-if="terms.length > 0">
            <colgroup>
              <col style="width: 48%" />
              <col style="width: 22%" />
              <col style="width: 30%" />
            </colgroup>
            <thead>
              <tr>
                <th>
                  <button class="sort-head" @click="toggleSort('term')">
                    Term <span class="sort-mark">{{ sortMark('term') }}</span>
                  </button>
                </th>
                <th>
                  <button class="sort-head" @click="toggleSort('df')">
                    DF <span class="sort-mark">{{ sortMark('df') }}</span>
                  </button>
                </th>
                <th>
                  <button class="sort-head" @click="toggleSort('tf')">
                    TF <span class="sort-mark">{{ sortMark('tf') }}</span>
                  </button>
                </th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="t in terms"
                :key="t.term"
                class="dict-row"
                :class="{ selected: selectedTerm === t.term }"
                @click="loadPostings(t.term)"
              >
                <td class="term-cell">{{ t.term }}</td>
                <td>{{ t.df }}</td>
                <td>{{ t.total_freq }}</td>
              </tr>
            </tbody>
          </table>

          <div class="no-results" v-else>
            未找到匹配词项
          </div>
        </div>

        <div class="pagination" v-if="totalPages > 1">
          <button :disabled="page <= 1" @click="loadDict(page - 1)">上一页</button>
          <span>{{ page }} / {{ totalPages }}</span>
          <button :disabled="page >= totalPages" @click="loadDict(page + 1)">下一页</button>
        </div>
      </section>

      <section class="postings-pane" aria-label="Postings">
        <div v-if="!postingsData" class="postings-empty">
          从左侧词典选择一个词项
        </div>

        <div v-else-if="postingsData.postings.length === 0" class="postings-empty">
          当前词项没有倒排记录
        </div>

        <div v-else class="posting-list">
          <article
            v-for="p in postingsData.postings"
            :key="p.doc_id"
            class="posting-card"
            tabindex="0"
            @click="openDocument(p.doc_id)"
            @keyup.enter="openDocument(p.doc_id)"
          >
            <div class="posting-card-head">
              <span class="posting-doc">Doc {{ p.doc_id }}</span>
              <span class="posting-occ">Occ. {{ p.tf }}</span>
            </div>
            <h3 class="posting-title">{{ formatPlainTitle(p.title || 'Untitled document') }}</h3>
            <p class="posting-meta">
              <span v-if="p.author">{{ p.author }}</span>
              <span v-if="p.author && p.bib"> · </span>
              <span v-if="p.bib">{{ p.bib }}</span>
            </p>
            <div class="context-lines">
              <p
                v-for="ctx in p.contexts"
                :key="`${p.doc_id}-${ctx.position}`"
                class="context-line"
                v-html="ctx.html"
              />
            </div>
          </article>
        </div>
      </section>
    </div>
    <DocumentModal v-if="detailDoc" :document="detailDoc" @close="closeDocument" />
  </div>
</template>

<script setup>
import { nextTick, onBeforeUnmount, onMounted, ref } from 'vue'
import { getDictionary, getDocument, getPostings } from '../api'
import DocumentModal from './DocumentModal.vue'

const alphabet = ['All', ...'ABCDEFGHIJKLMNOPQRSTUVWXYZ'.split(''), '#']
const search = ref('')
const terms = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(50)
const totalPages = ref(0)
const postingsData = ref(null)
const detailDoc = ref(null)
const selectedTerm = ref('')
const selectedLetter = ref('All')
const alphabetRef = ref(null)
const dictionaryBodyRef = ref(null)
const sortBy = ref('term')
const sortOrder = ref('asc')

async function loadDict(p = 1) {
  page.value = p
  const res = await getDictionary(
    p,
    pageSize.value,
    search.value.trim(),
    selectedLetter.value === 'All' ? 'all' : selectedLetter.value.toLowerCase(),
    sortBy.value,
    sortOrder.value
  )
  terms.value = res.data.terms
  total.value = res.data.total
  totalPages.value = Math.ceil(res.data.total / pageSize.value)
}

async function loadPostings(term) {
  selectedTerm.value = term
  try {
    const res = await getPostings(term)
    postingsData.value = res.data
  } catch (e) {
    console.error('Failed to load postings:', e)
  }
}

async function openDocument(docId) {
  const res = await getDocument(docId, selectedTerm.value)
  detailDoc.value = res.data
}

function closeDocument() {
  detailDoc.value = null
}

function formatPlainTitle(title) {
  const cleaned = title
    .replace(/\s+/g, ' ')
    .replace(/\s+([,.;:!?])/g, '$1')
    .trim()
  if (!cleaned) return ''
  return cleaned.replace(/(^|[.!?]\s+)([a-z])/g, (_, prefix, letter) => (
    `${prefix}${letter.toUpperCase()}`
  ))
}

function applySearch() {
  selectedTerm.value = ''
  postingsData.value = null
  loadDict(1)
}

function selectLetter(letter) {
  selectedLetter.value = letter
  search.value = ''
  selectedTerm.value = ''
  postingsData.value = null
  loadDict(1)
}

function scrollAlphabet(direction) {
  alphabetRef.value?.scrollBy({ left: direction * 120, behavior: 'smooth' })
}

function toggleSort(column) {
  if (sortBy.value === column) {
    sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortBy.value = column
    sortOrder.value = 'asc'
  }
  selectedTerm.value = ''
  postingsData.value = null
  loadDict(1)
}

function sortMark(column) {
  if (sortBy.value !== column) return '↕'
  return sortOrder.value === 'asc' ? '▲' : '▼'
}

function calculatePageSize() {
  const body = dictionaryBodyRef.value
  if (!body) return
  const tableHeadHeight = body.querySelector('thead')?.offsetHeight || 40
  const rowHeight = body.querySelector('tbody tr')?.offsetHeight || 37
  const available = body.clientHeight - tableHeadHeight
  const nextSize = Math.max(8, Math.floor(available / rowHeight))
  if (nextSize !== pageSize.value) {
    pageSize.value = nextSize
    loadDict(1)
  }
}

function handleResize() {
  calculatePageSize()
}

onMounted(async () => {
  await loadDict(1)
  await nextTick()
  calculatePageSize()
  window.addEventListener('resize', handleResize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
})
</script>
