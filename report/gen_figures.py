"""Generate IEEE-style figures for the course report using scienceplots."""

import sys
sys.path.insert(0, "../backend")

import matplotlib.pyplot as plt
import scienceplots  # noqa: F401
import numpy as np
from collections import Counter
from pathlib import Path

# IEEE style, no custom overrides
plt.style.use(["science", "ieee"])

FIG_DIR = Path(__file__).parent / "figures"
FIG_DIR.mkdir(exist_ok=True)

# ── Load data via backend modules ──
from app.core.parser import parse_documents
from app.core.preprocessor import Preprocessor
from app.core.indexer import InvertedIndex

DATA_DIR = Path(__file__).parent.parent / "data"
docs = parse_documents(str(DATA_DIR / "cran.all.1400.xml"))
preprocessor = Preprocessor()

# Build index
idx = InvertedIndex()
idx.build(docs)

# ── Figure 1: Zipf's Law - Term Frequency Distribution ──
term_freqs = []
for term, postings in idx.index.items():
    total_tf = sum(len(pos) for pos in postings.values())
    term_freqs.append(total_tf)

term_freqs.sort(reverse=True)
ranks = np.arange(1, len(term_freqs) + 1)

fig, ax = plt.subplots()
ax.loglog(ranks, term_freqs, linewidth=0.8)
ax.set_xlabel("Rank")
ax.set_ylabel("Frequency")
ax.set_title("Term Frequency vs. Rank (Zipf's Law)")
fig.savefig(FIG_DIR / "zipf_distribution.png", dpi=300, bbox_inches="tight")
plt.close()
print("Generated: zipf_distribution.png")


# ── Figure 2: Document Frequency Distribution ──
dfs = [len(postings) for postings in idx.index.values()]

fig, ax = plt.subplots()
ax.hist(dfs, bins=50, edgecolor="black", linewidth=0.3)
ax.set_xlabel("Document Frequency (DF)")
ax.set_ylabel("Number of Terms")
ax.set_title("Distribution of Document Frequencies")
ax.set_yscale("log")
fig.savefig(FIG_DIR / "df_distribution.png", dpi=300, bbox_inches="tight")
plt.close()
print("Generated: df_distribution.png")


# ── Figure 3: Document Length Distribution ──
doc_lengths = []
for doc in docs:
    tokens = preprocessor.process(doc.title + " " + doc.text)
    doc_lengths.append(len(tokens))

fig, ax = plt.subplots()
ax.hist(doc_lengths, bins=40, edgecolor="black", linewidth=0.3)
ax.set_xlabel("Number of Terms (after preprocessing)")
ax.set_ylabel("Number of Documents")
ax.set_title("Document Length Distribution")
fig.savefig(FIG_DIR / "doc_length_distribution.png", dpi=300, bbox_inches="tight")
plt.close()
print("Generated: doc_length_distribution.png")


# ── Figure 4: Top-20 Most Frequent Terms ──
term_freq_pairs = []
for term, postings in idx.index.items():
    total_tf = sum(len(pos) for pos in postings.values())
    term_freq_pairs.append((term, total_tf))

term_freq_pairs.sort(key=lambda x: x[1], reverse=True)
top20 = term_freq_pairs[:20]
terms = [t[0] for t in top20][::-1]
freqs = [t[1] for t in top20][::-1]

fig, ax = plt.subplots()
ax.barh(terms, freqs)
ax.set_xlabel("Total Frequency")
ax.set_title("Top 20 Most Frequent Terms")
fig.savefig(FIG_DIR / "top20_terms.png", dpi=300, bbox_inches="tight")
plt.close()
print("Generated: top20_terms.png")


# ── Figure 5: Index Statistics Summary ──
stats = {
    "Documents": len(docs),
    "Unique Terms": len(idx.index),
    "Avg Doc Length": f"{np.mean(doc_lengths):.1f}",
    "Max DF": max(dfs),
    "Min DF": min(dfs),
    "Median DF": int(np.median(dfs)),
}
print("\n=== Index Statistics ===")
for k, v in stats.items():
    print(f"  {k}: {v}")

print("\nAll figures generated successfully.")
