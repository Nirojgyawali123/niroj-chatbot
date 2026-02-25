from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import httpx
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Niroj Portfolio Chatbot API", version="1.0.0")

# ── CORS ──
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_headers=["*"],
)

# ── CONFIG ──
HF_TOKEN = os.getenv("HF_TOKEN")
HF_MODEL = os.getenv("HF_MODEL", "mistralai/Mistral-7B-Instruct-v0.2")
HF_API_URL = f"https://router.huggingface.co/hf-inference/models/{HF_MODEL}"

# ── NIROJ'S PERSONAL INFO ──
NIROJ_CONTEXT = """
You are an AI assistant embedded in Niroj Gyawali's personal portfolio website.
Your job is to answer ALL questions helpfully — both about Niroj and general questions.

Here is everything you know about Niroj:

NAME: Niroj Gyawali
EDUCATION: BSc CSIT (Bachelor of Science in Computer Science and Information Technology), currently in 1st Semester
LOCATION: Lumbini, Nepal
INTERESTS: Artificial Intelligence, Machine Learning, Deep Learning, Data Science, IT Projects
SKILLS: Python, Machine Learning, Deep Learning, Data Analysis, Web Development, Git & GitHub
ROLE: Student, Tech Enthusiast, Community Organizer

COMMUNITY WORK:
- Organizer of "Lumbini Tech Month" — a regional tech initiative in Lumbini Province, Nepal
- The event helps students and participants learn different IT-related courses and skills
- Focused on making tech education accessible in the Lumbini region

PROJECTS:
1. Sentiment Analysis Model — NLP project classifying text sentiment using ML
2. Data Visualization Dashboard — Interactive data exploration tool using Python
3. Lumbini Tech Month — Tech event organization and management
4. AI Portfolio Chatbot — This chatbot you're talking to right now!

PERSONALITY: Curious, passionate, driven, community-focused, always learning

CONTACT:
- Email: niroj@example.com (placeholder)
- LinkedIn: linkedin.com/in/nirojgyawali (placeholder)
- GitHub: github.com/nirojgyawali (placeholder)

IMPORTANT RULES:
- Answer ALL questions, not just ones about Niroj
- For questions about Niroj, use the info above
- For general questions (coding, math, facts, anything), answer them helpfully
- Be warm, friendly, and concise (2-4 sentences unless more is needed)
- Never say you can only answer questions about Niroj
"""

# ── MODELS ──
class ChatRequest(BaseModel):
    message: str
    history: list[dict] = []

class ChatResponse(BaseModel):
    reply: str
    model: str

# ── API ROUTES ──
@app.get("/health")
async def health():
    return {"status": "ok", "model": HF_MODEL}

@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    if not HF_TOKEN:
        raise HTTPException(status_code=500, detail="HF_TOKEN not set in .env file.")
    if not req.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty.")

    prompt = build_prompt(req.message, req.history)
    headers = {
        "Authorization": f"Bearer {HF_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 400,
            "temperature": 0.7,
            "top_p": 0.9,
            "do_sample": True,
            "return_full_text": False
        }
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            response = await client.post(HF_API_URL, json=payload, headers=headers)
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 503:
                raise HTTPException(status_code=503, detail="Model is loading, please retry in a few seconds.")
            if e.response.status_code == 401:
                raise HTTPException(status_code=401, detail="Invalid HF_TOKEN. Check your .env file.")
            raise HTTPException(status_code=e.response.status_code, detail=f"HuggingFace error: {e.response.text}")
        except httpx.TimeoutException:
            raise HTTPException(status_code=504, detail="Request timed out. The model might be loading.")

    data = response.json()
    if isinstance(data, list) and len(data) > 0:
        raw = data[0].get("generated_text", "")
    elif isinstance(data, dict):
        raw = data.get("generated_text", "")
    else:
        raise HTTPException(status_code=500, detail="Unexpected response from HuggingFace.")

    reply = clean_reply(raw)
    return ChatResponse(reply=reply, model=HF_MODEL)


def build_prompt(message: str, history: list[dict]) -> str:
    prompt = f"<s>[INST] {NIROJ_CONTEXT}\n\n"
    for turn in history[-6:]:
        role = turn.get("role", "")
        content = turn.get("content", "")
        if role == "user":
            prompt += f"User: {content}\n"
        elif role == "assistant":
            prompt += f"Assistant: {content}\n"
    prompt += f"User: {message} [/INST]"
    return prompt


def clean_reply(text: str) -> str:
    for tag in ["[INST]", "[/INST]", "</s>", "<s>"]:
        text = text.replace(tag, "")
    if "Assistant:" in text:
        text = text.split("Assistant:")[-1]
    return text.strip()


# ── SERVE FRONTEND ──
FRONTEND_DIR = Path(__file__).parent.parent / "portfolio"

if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")

    @app.get("/")
    async def serve_frontend():
        return FileResponse(str(FRONTEND_DIR / "index.html"))

    @app.get("/{full_path:path}")
    async def catch_all(full_path: str):
        file_path = FRONTEND_DIR / full_path
        if file_path.exists():
            return FileResponse(str(file_path))
        return FileResponse(str(FRONTEND_DIR / "index.html"))
else:
    @app.get("/")
    async def root():
        return {"status": "API running. Put your portfolio folder next to backend folder."}