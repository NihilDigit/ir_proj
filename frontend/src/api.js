import axios from 'axios'

const api = axios.create({ baseURL: '/api' })

export const booleanSearch = (query, topK = 50) =>
  api.post('/search/boolean', { query, top_k: topK })

export const phraseSearch = (query, topK = 50) =>
  api.post('/search/phrase', { query, top_k: topK })

export const expandedSearch = (query, maxSynonyms = 3, topK = 50) =>
  api.post('/search/expanded', { query, max_synonyms: maxSynonyms, top_k: topK })

export const soundexSearch = (query, limitPerTerm = 5, topK = 50) =>
  api.post('/search/soundex', { query, limit_per_term: limitPerTerm, top_k: topK })

export const getDictionary = (page = 1, size = 50, search = '') =>
  api.get('/index/dictionary', { params: { page, size, search } })

export const getPostings = (term) =>
  api.get(`/index/postings/${encodeURIComponent(term)}`)

export const getDocument = (docId, highlightTerms = '') =>
  api.get(`/documents/${docId}`, { params: { highlight_terms: highlightTerms } })

export const getQueries = () => api.get('/queries')
