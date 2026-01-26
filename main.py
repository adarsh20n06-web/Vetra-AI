import os, json, re, unicodedata
from datetime import datetime
from typing import List
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import aioredis, asyncpg, uvicorn
from authlib.integrations.starlette_client import OAuth, OAuthError
from starlette.config import Config
from starlette.requests import Request as StarletteRequest
from starlette.middleware.sessions import SessionMiddleware

# =====================
# CONFIG
# =====================
DATABASE_URL = os.getenv("DATABASE_URL")
REDIS_URL = os.getenv("REDIS_URL")
PORT = 8000

OWNER_SECRET = os.getenv("OWNER_SECRET", "only-owner-can-train")

MEMORY_TTL = 3 * 24 * 60 * 60
MEMORY_MAX_ENTRIES = 10
MAX_PROMPT_LEN = 4000

BLOCK_PATTERNS = [
    r"(ignore|bypass).*(rules|policy)",
    r"(hack|crack|steal|ddos)",
    r"(admin|root|password|drop|delete)",
]

# =====================
# APP INIT
# =====================
app = FastAPI(title="NOBLTY AI", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SESSION_SECRET", "super-secret-session")
)

# =====================
# REDIS + DATABASE
# =====================
@app.on_event("startup")
async def startup():
    app.state.redis = await aioredis.from_url(REDIS_URL)
    app.state.db = await asyncpg.create_pool(DATABASE_URL)

@app.on_event("shutdown")
async def shutdown():
    await app.state.redis.close()
    await app.state.db.close()

# =====================
# OAUTH CONFIG
# =====================
config_data = Config('.env')
oauth = OAuth(config_data)

oauth.register(
    name='google',
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'},
)

oauth.register(
    name='microsoft',
    client_id=os.getenv("MS_CLIENT_ID"),
    client_secret=os.getenv("MS_CLIENT_SECRET"),
    server_metadata_url='https://login.microsoftonline.com/common/v2.0/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'},
)

oauth.register(
    name='zoho',
    client_id=os.getenv("ZOHO_CLIENT_ID"),
    client_secret=os.getenv("ZOHO_CLIENT_SECRET"),
    authorize_url='https://accounts.zoho.com/oauth/v2/auth',
    access_token_url='https://accounts.zoho.com/oauth/v2/token',
    client_kwargs={'scope': 'AaaServer.profile.READ'},
)

# =====================
# MODELS
# =====================
class AskModel(BaseModel):
    prompt: str

class TrainModel(BaseModel):
    language: str
    instruction: str
    examples: List[dict]

# =====================
# HELPERS
# =====================
def detect_language(text: str) -> str:
    if re.search(r'[\u0900-\u097F]', text):
        return "hi" if not re.search(r'[a-zA-Z]', text) else "hi-en"
    return "en"

def validate_prompt(prompt: str):
    if len(prompt) > MAX_PROMPT_LEN:
        raise HTTPException(400, "Prompt too long")
    for p in BLOCK_PATTERNS:
        if re.search(p, prompt.lower()):
            raise HTTPException(400, "Prompt blocked by safety rules")

# =====================
# MEMORY
# =====================
async def get_memory(email: str):
    data = await app.state.redis.get(f"mem:{email}")
    return json.loads(data) if data else []

async def save_memory(email: str, prompt: str, answer: str):
    mem = await get_memory(email)
    mem.append({"q": prompt, "a": answer})
    mem = mem[-MEMORY_MAX_ENTRIES:]
    await app.state.redis.set(
        f"mem:{email}",
        json.dumps(mem),
        ex=MEMORY_TTL
    )

# =====================
# LANGUAGE CORE
# =====================
class LanguageCore:
    def analyze(self, prompt: str, lang: str, memory: list) -> dict:
        intent = "general"
        p = prompt.lower()

        if p.endswith("?"):
            intent = "question"
        elif p.startswith(("how", "why", "explain")):
            intent = "explanation"
        elif p.startswith(("create", "make", "build")):
            intent = "instruction"

        context = " ".join(m["a"] for m in memory[-3:])

        return {
            "intent": intent,
            "language": lang,
            "context": context,
            "prompt": unicodedata.normalize("NFKC", prompt)
        }

language_core = LanguageCore()

# =====================
# AI ENGINES
# =====================
class NOBLTYEngine:
    def process(self, core: dict):
        return (
            f"NOBLTY reasoning [{core['intent']}]: "
            f"{core['context']} → {core['prompt']}"
        )

class aastraxEngine:
    def process(self, core: dict):
        return f"aastrax refined response: {core['prompt']}"

NOBLTY = NOBLTYEngine()
aastrax = aastraxEngine()

def merge_answers(a: str, b: str, lang: str):
    final = a if len(a) >= len(b) else b
    if lang == "hi":
        return f"अंतिम उत्तर:\n{final}"
    if lang == "hi-en":
        return f"Final Answer (Hinglish):\n{final}"
    return f"Final Answer:\n{final}"

# =====================
# ROUTES
# =====================
@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/ask")
async def ask_ai(data: AskModel, request: Request):
    email = request.session.get("user_email")
    if not email:
        raise HTTPException(403, "Login required")

    validate_prompt(data.prompt)

    lang = detect_language(data.prompt)
    memory = await get_memory(email)

    core = language_core.analyze(data.prompt, lang, memory)

    n_ans = NOBLTY.process(core)
    a_ans = aastrax.process(core)

    final_answer = merge_answers(n_ans, a_ans, lang)

    await save_memory(email, data.prompt, final_answer)

    return {
        "answer": final_answer,
        "language": lang,
        "timestamp": datetime.utcnow().isoformat()
    }

# =====================
# RUN
# =====================
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=PORT)
