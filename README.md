<<<<<<< HEAD
# 🛍️ ShopMind AI — E-Commerce Customer Support System

An AI-powered e-commerce support chatbot using NLP, Flask, and MySQL.

---

## 📁 Project Structure

```
shopmind-ai/
├── frontend/
│   ├── index.html          ← Welcome + Chat UI
│   ├── css/
│   │   └── style.css       ← All styles (glassmorphism, layout)
│   └── js/
│       ├── chat.js         ← Chat logic, message rendering
│       └── api.js          ← Flask API communication
│
├── backend/
│   ├── app.py              ← Flask app entry point
│   ├── config.py           ← DB config, constants
│   ├── modules/
│   │   ├── nlp.py          ← Text preprocessing, TF-IDF, BERT
│   │   ├── intent.py       ← Intent detection engine
│   │   ├── agent.py        ← Decision engine (core AI logic)
│   │   └── db.py           ← MySQL database helper
│   └── routes/
│       ├── chat.py         ← /api/chat endpoint
│       └── admin.py        ← /api/admin endpoints
│
├── database/
│   └── schema.sql          ← All CREATE TABLE + seed data
│
├── docs/
│   └── architecture.md     ← System architecture notes
│
├── requirements.txt        ← Python dependencies
├── .env.example            ← Environment variable template
├── .gitignore              ← Files to exclude from Git
└── README.md               ← This file
```

---

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/YOUR_USERNAME/shopmind-ai.git
cd shopmind-ai
```

### 2. Set Up Python Environment
```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

pip install -r requirements.txt
```

### 3. Set Up MySQL Database
```bash
mysql -u root -p
# Then inside MySQL:
CREATE DATABASE shopmind_db;
USE shopmind_db;
SOURCE database/schema.sql;
```

### 4. Configure Environment Variables
```bash
cp .env.example .env
# Edit .env with your MySQL credentials
```

### 5. Run the App
```bash
cd backend
python app.py
```

### 6. Open Frontend
Open `frontend/index.html` in your browser, or use VS Code Live Server.

---

## 🔗 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/chat` | Send a user query, get AI response |
| GET | `/api/products` | List all products |
| GET | `/api/order/<id>` | Get order status |
| GET | `/api/admin/faqs` | List all FAQs |
| POST | `/api/admin/faq` | Add a new FAQ |

---

## 🧠 AI Flow

```
User Input → NLP Preprocessing → Intent Detection → Decision Engine → DB/Logic → Response
```

---

## 🛠️ Tech Stack

- **Frontend**: HTML, CSS (Glassmorphism), Vanilla JS
- **Backend**: Python, Flask
- **AI/ML**: NLTK, scikit-learn (TF-IDF), sentence-transformers (BERT)
- **Database**: MySQL

---

## 📌 Git Workflow

```bash
# After making changes:
git add .
git commit -m "feat: describe your change"
git push origin main
```
=======
# ai-faq-chatbot
AI-powered FAQ chatbot using NLP, Flask, and BERT
>>>>>>> 2cb8385eb1c7f7540df06501e24f52425e2e61a2
