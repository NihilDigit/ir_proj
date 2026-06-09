"""查询扩展 — 基于 WordNet 的同义词扩展"""

from nltk.corpus import wordnet

from .preprocessor import Preprocessor


class QueryExpander:
    def __init__(self, preprocessor: Preprocessor):
        self.preprocessor = preprocessor

    def expand(self, query_terms: list[str], max_synonyms: int = 1) -> dict:
        expansion_map: dict[str, list[str]] = {}
        all_terms = set(query_terms)

        for term in query_terms:
            synonyms: set[str] = set()
            stem_of_term = self.preprocessor.stemmer.stem(term)
            for synset in wordnet.synsets(term):
                for lemma in synset.lemmas():
                    synonym = lemma.name().lower().replace("_", " ")
                    if " " in synonym or synonym == term:
                        continue
                    if self.preprocessor.stemmer.stem(synonym) != stem_of_term:
                        synonyms.add(synonym)
                    if len(synonyms) >= max_synonyms:
                        break
                if len(synonyms) >= max_synonyms:
                    break
            expansion_map[term] = sorted(synonyms)[:max_synonyms]
            all_terms.update(expansion_map[term])

        expanded_stemmed = sorted({self.preprocessor.stemmer.stem(t) for t in all_terms})

        return {
            "original_terms": query_terms,
            "expanded_terms": sorted(all_terms),
            "expanded_stemmed": expanded_stemmed,
            "expansion_map": expansion_map,
        }
