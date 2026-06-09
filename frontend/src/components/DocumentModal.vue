<template>
  <div class="doc-modal-backdrop" @click="$emit('close')">
    <section class="doc-modal" @click.stop>
      <button class="modal-close" @click="$emit('close')" aria-label="关闭文档">×</button>
      <div class="modal-head">
        <div class="modal-docid">Doc {{ document.doc_id }}</div>
        <h2 v-html="formattedTitle"></h2>
        <p class="modal-meta" v-if="document.author">{{ document.author }}</p>
        <p class="modal-meta" v-if="document.bib">{{ document.bib }}</p>
      </div>
      <div class="modal-body">
        <div class="modal-text">
          <p
            v-for="(paragraph, index) in paragraphs"
            :key="index"
            :class="{ lead: index === 0 }"
            v-html="paragraph"
          />
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  document: { type: Object, required: true },
})

defineEmits(['close'])

const formattedTitle = computed(() => {
  if (!props.document.highlighted_title) return ''
  return capitalizeSentences(cleanHtmlText(props.document.highlighted_title))
})

const paragraphs = computed(() => {
  if (!props.document.highlighted_text) return []
  const cleaned = stripRepeatedTitle(props.document.highlighted_text, props.document.title)
  if (!cleaned) return []
  const sentences = cleaned.match(/[^.!?]+[.!?]+|[^.!?]+$/g) || [cleaned]
  const result = []
  for (let i = 0; i < sentences.length; i += 3) {
    result.push(sentences.slice(i, i + 3).join(' ').trim())
  }
  return result.map((paragraph, index) => (
    index === 0 ? addDropCap(capitalizeSentences(paragraph)) : capitalizeSentences(paragraph)
  ))
})

function normalizePlainText(text) {
  return text
    .replace(/<[^>]*>/g, '')
    .replace(/\s+/g, ' ')
    .replace(/\s+([,.;:!?])/g, '$1')
    .trim()
}

function cleanHtmlText(html) {
  return html
    .replace(/\s+/g, ' ')
    .replace(/\s+([,.;:!?])/g, '$1')
    .trim()
}

function stripRepeatedTitle(html, title) {
  const cleaned = cleanHtmlText(html)
  const plainTitle = normalizePlainText(title)
  if (!cleaned || !plainTitle) return cleaned

  const plainBody = normalizePlainText(cleaned)
  if (!plainBody.toLowerCase().startsWith(plainTitle.toLowerCase())) return cleaned

  const plainPrefixEnd = plainTitle.length
  let plainCount = 0
  let htmlIndex = 0
  while (htmlIndex < cleaned.length && plainCount < plainPrefixEnd) {
    if (cleaned[htmlIndex] === '<') {
      const tagEnd = cleaned.indexOf('>', htmlIndex)
      if (tagEnd === -1) break
      htmlIndex = tagEnd + 1
      continue
    }
    plainCount += 1
    htmlIndex += 1
  }
  return cleaned.slice(htmlIndex).replace(/^\s*[.。]?\s*/, '').trim()
}

function addDropCap(html) {
  return html.replace(/^((?:<[^>]+>)*)([A-Za-z0-9])/, (_, prefix, letter) => (
    `${prefix}<span class="dropcap">${letter.toUpperCase()}</span>`
  ))
}

function capitalizeSentences(html) {
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
