# 🤖 Niroj Portfolio — Chatbot Backend

A FastAPI backend that connects your portfolio chatbot to Hugging Face's
Mistral-7B-Instruct model. Fully supports multi-turn conversation with
personal context about Niroj built in.

---

## 📁 Project Structure

```
portfolio/
├── index.html          ← Your portfolio frontend
├── styles.css          ← Portfolio styles

backend/
├── main.py             ← FastAPI app (all logic lives here)
├── .env                ← Your secret API token (never share this!)
├── requirements.txt    ← Python dependencies
└── README.md           ← This file
```

---

## 🚀 Setup — Step by Step

### Step 1 — Install Python
Make sure you have Python 3.10 or newer installed.
Check with: `python --version`

---

### Step 2 — Install dependencies

Open your terminal inside the `backend/` folder and run:

```bash
pip install -r requirements.txt
```

---

### Step 3 — Add your Hugging Face Token

1. Go to 👉 https://huggingface.co/settings/tokens
2. Click **"New token"**
3. Give it a name (e.g. "niroj-portfolio")
4. Select **"Read"** role
5. Copy the token

Now open `.env` and paste it:

```env
HF_TOKEN=hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
HF_MODEL=mistralai/Mistral-7B-Instruct-v0.2
```

---

### Step 4 — Run the backend

```bash
uvicorn main:app --reload --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
```

---

### Step 5 — Open your portfolio

Open `portfolio/index.html` in your browser.
The chatbot will now connect to your backend at `http://localhost:8000`.

---

## 🌐 API Endpoints

| Method | Endpoint  | Description              |
|--------|-----------|--------------------------|
| GET    | /         | Health check             |
| GET    | /health   | Health check (JSON)      |
| POST   | /chat     | Send message to chatbot  |

### POST /chat — Example

**Request:**
```json
{
  "message": "Tell me about Niroj",
  "history": []
}
```

**Response:**
```json
{
  "reply": "Niroj Gyawali is a first-semester BSc CSIT student from Lumbini, Nepal...",
  "model": "mistralai/Mistral-7B-Instruct-v0.2"
}
```

---

## ☁️ Deploying Online (Free Options)

### Option A — Render.com (Recommended, Free)
1. Push your `backend/` folder to a GitHub repo
2. Go to https://render.com → New Web Service
3. Connect your GitHub repo
4. Set:
   - **Build command:** `pip install -r requirements.txt`
   - **Start command:** `uvicorn main:app --host 0.0.0.0 --port 8000`
5. Add environment variable: `HF_TOKEN` = your token
6. Deploy! You'll get a URL like `https://niroj-chatbot.onrender.com`

### Option B — Railway.app (Also Free)
1. Go to https://railway.app
2. New Project → Deploy from GitHub
3. Add `HF_TOKEN` in environment variables
4. Done!

After deploying, update this line in `portfolio/index.html`:
```javascript
const BACKEND_URL = "https://your-app.onrender.com"; // ← your deployed URL
```

---

## 🔧 Customizing Niroj's Info

All personal info the chatbot knows is in `main.py` inside the `NIROJ_CONTEXT` variable.
Just edit that string to update skills, projects, contact info — no restart needed after redeployment.

---

## ⚠️ Common Issues

| Problem | Fix |
|--------|-----|
| `503 Model is loading` | Wait 20 seconds, the model cold-starts on first request |
| `401 Unauthorized` | Your HF_TOKEN is wrong or expired, get a new one |
| `CORS error` in browser | Make sure backend is running on port 8000 |
| Chatbot says "trouble connecting" | Backend isn't running — check `uvicorn` is active |

---

## 🛠 Switching Models

Edit `.env` to swap models anytime:

```env
# Best quality
HF_MODEL=mistralai/Mistral-7B-Instruct-v0.2

# Great for chat
HF_MODEL=HuggingFaceH4/zephyr-7b-beta

# Lighter & faster
HF_MODEL=google/flan-t5-large
```

---

Made with ❤️ for Niroj Gyawali's Portfolio
