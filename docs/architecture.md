# 🏗️ ShopMind AI — System Architecture

## Full Data Flow

```
┌─────────────────────────────────────────────────────────────┐
│                        USER                                  │
│                  (Browser / Mobile)                          │
└──────────────────────────┬──────────────────────────────────┘
                           │  Types query
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                   FRONTEND (HTML/CSS/JS)                     │
│                                                             │
│  index.html ──► css/style.css   (glassmorphism UI)          │
│             ──► js/chat.js      (message rendering)         │
│             ──► js/api.js       (fetch to Flask)            │
│                                                             │
│  Flow:  User types → sendMessage() → handleSend()           │
│         → sendQueryToBackend()  → POST /api/chat            │
│         → renderBotResponse()   → shows card/text           │
└──────────────────────────┬──────────────────────────────────┘
                           │  POST /api/chat { query: "..." }
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                  FLASK BACKEND (Python)                      │
│                                                             │
│  app.py                                                     │
│  └── routes/chat.py    → /api/chat  (POST)                  │
│  └── routes/admin.py   → /api/admin/* (CRUD)                │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    NLP MODULE (nlp.py)                       │
│                                                             │
│  1. preprocess(text)                                        │
│     ├── Lowercase                                           │
│     ├── Remove special chars                                │
│     ├── Tokenize (NLTK word_tokenize)                       │
│     ├── Remove stopwords                                    │
│     └── Lemmatize (WordNetLemmatizer)                       │
│                                                             │
│  2. get_similarity(query, corpus)                           │
│     ├── TF-IDF + Cosine Similarity (default)                │
│     └── Sentence-BERT (if USE_BERT=True in config)         │
└──────────────────────────┬──────────────────────────────────┘
                           │  preprocessed text + scores
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                 INTENT DETECTION (intent.py)                 │
│                                                             │
│  Step 1: Rule-Based (Regex) — fast, high confidence         │
│  ┌──────────────────────────────────────────────────┐       │
│  │  "track order 101" → track_order  (conf: 0.95)   │       │
│  │  "return my item"  → return_req   (conf: 0.95)   │       │
│  │  "show shoes"      → search_prods (conf: 0.95)   │       │
│  └──────────────────────────────────────────────────┘       │
│                                                             │
│  Step 2: NLP Similarity Fallback (if no rule matches)       │
│  ┌──────────────────────────────────────────────────┐       │
│  │  Query vs 30+ corpus phrases                     │       │
│  │  Best match above threshold → intent             │       │
│  └──────────────────────────────────────────────────┘       │
│                                                             │
│  Step 3: Entity Extraction                                  │
│  ┌──────────────────────────────────────────────────┐       │
│  │  order_id, category, max_price                   │       │
│  └──────────────────────────────────────────────────┘       │
│                                                             │
│  Returns: { type, confidence, entities, method }            │
└──────────────────────────┬──────────────────────────────────┘
                           │  intent dict
                           ▼
┌─────────────────────────────────────────────────────────────┐
│               DECISION ENGINE / AGENT (agent.py)             │
│                                                             │
│  process(intent, raw_text)                                  │
│       │                                                     │
│       ├── track_order      → get_order(id) from MySQL       │
│       ├── search_products  → get_products_by_category()     │
│       ├── return_request   → return workflow steps          │
│       ├── compare_products → comparison guide               │
│       ├── recommend        → top rated products from DB     │
│       ├── payment_info     → static payment info            │
│       ├── delivery_info    → static delivery info           │
│       ├── faq              → get_all_faqs() from MySQL      │
│       └── unknown          → fallback help message          │
│                                                             │
│  Logs every interaction → chat_logs table                   │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                   DATABASE (MySQL)                           │
│                                                             │
│  products   → name, price, category, rating, stock          │
│  orders     → order_id, user_id, product_id, status, date   │
│  users      → user_id, name, email, phone                   │
│  faqs       → question, answer, category                    │
│  chat_logs  → query, intent, confidence, response           │
└──────────────────────────┬──────────────────────────────────┘
                           │  structured data
                           ▼
┌─────────────────────────────────────────────────────────────┐
│               JSON RESPONSE → FRONTEND                       │
│                                                             │
│  { type: "order",    data: {...}, confidence: 99 }           │
│  { type: "products", data: [...], confidence: 94 }           │
│  { type: "steps",    data: [...], confidence: 96 }           │
│  { type: "text",     text: "...", confidence: 88 }           │
└─────────────────────────────────────────────────────────────┘
```

## Module Responsibilities

| File | Role |
|------|------|
| `frontend/index.html` | UI structure, screens |
| `frontend/css/style.css` | All visual styling |
| `frontend/js/api.js` | Backend communication |
| `frontend/js/chat.js` | Message rendering |
| `backend/app.py` | Flask app + CORS setup |
| `backend/config.py` | Config, constants |
| `backend/modules/db.py` | MySQL queries |
| `backend/modules/nlp.py` | Text preprocessing + similarity |
| `backend/modules/intent.py` | Intent detection (rules + NLP) |
| `backend/modules/agent.py` | Decision engine |
| `backend/routes/chat.py` | `/api/chat` endpoint |
| `backend/routes/admin.py` | Admin CRUD endpoints |
| `database/schema.sql` | Tables + seed data |
