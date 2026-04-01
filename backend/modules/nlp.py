# ============================================================
#  modules/nlp.py — NLP Text Processing
#  Handles: tokenization, lemmatization, TF-IDF, BERT
# ============================================================

import re
import nltk
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from config import USE_BERT

# Download required NLTK data on first run
nltk.download('punkt',      quiet=True)
nltk.download('stopwords',  quiet=True)
nltk.download('wordnet',    quiet=True)

from nltk.corpus   import stopwords
from nltk.stem     import WordNetLemmatizer
from nltk.tokenize import word_tokenize

lemmatizer = WordNetLemmatizer()
stop_words  = set(stopwords.words('english'))

# ── Optional: Load BERT model ─────────────────────────────
bert_model = None
if USE_BERT:
    try:
        from sentence_transformers import SentenceTransformer
        bert_model = SentenceTransformer('all-MiniLM-L6-v2')
        print("✅ BERT model loaded")
    except Exception as e:
        print(f"⚠️  BERT load failed, falling back to TF-IDF: {e}")


# ── Text Preprocessing ────────────────────────────────────

def preprocess(text: str) -> str:
    """
    Clean and normalize text:
    1. Lowercase
    2. Remove special characters
    3. Tokenize
    4. Remove stopwords
    5. Lemmatize
    """
    text   = text.lower()
    text   = re.sub(r'[^a-z0-9\s]', '', text)
    tokens = word_tokenize(text)
    tokens = [lemmatizer.lemmatize(t) for t in tokens if t not in stop_words]
    return ' '.join(tokens)


# ── TF-IDF Similarity ─────────────────────────────────────

def tfidf_similarity(query: str, corpus: list[str]) -> np.ndarray:
    """
    Compute cosine similarity between the query and each item in corpus.
    Returns an array of similarity scores.
    """
    if not corpus:
        return np.array([])

    vectorizer = TfidfVectorizer()
    processed  = [preprocess(query)] + [preprocess(c) for c in corpus]
    tfidf_mat  = vectorizer.fit_transform(processed)
    scores     = cosine_similarity(tfidf_mat[0:1], tfidf_mat[1:])
    return scores[0]


# ── BERT Similarity (optional) ────────────────────────────

def bert_similarity(query: str, corpus: list[str]) -> np.ndarray:
    """
    Compute semantic similarity using Sentence-BERT.
    More accurate than TF-IDF for paraphrased queries.
    """
    if bert_model is None or not corpus:
        return tfidf_similarity(query, corpus)

    embeddings = bert_model.encode([query] + corpus)
    scores     = cosine_similarity([embeddings[0]], embeddings[1:])
    return scores[0]


# ── Unified Similarity Interface ─────────────────────────

def get_similarity(query: str, corpus: list[str]) -> np.ndarray:
    """Use BERT if available, else fall back to TF-IDF."""
    if USE_BERT and bert_model:
        return bert_similarity(query, corpus)
    return tfidf_similarity(query, corpus)
