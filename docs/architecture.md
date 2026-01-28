# NOBLTY AI × aastrax Architecture

NOBLTY AI × aastrax is a **self-hosted, multilingual AI system** designed for safe, context-aware reasoning and creative response generation.  
It is fully proprietary and does **not** rely on publicly branded LLMs or vector databases.

This document provides a complete overview of the system's internal architecture, components, and security considerations.

---

## System Overview

The AI system combines two proprietary engines that work together to generate high-quality responses:

- **NOBLTY Engine:** Handles logical reasoning, safety, and rule enforcement  
- **aastrax Engine:** Handles creativity, contextual expansion, and refinement  

Supporting components include:

- **Memory Layer:** Redis-based short-term conversation memory for context  
- **Database Layer:** PostgreSQL for securely storing training data and examples  
- **Authentication Layer:** OAuth 2.0 with Google, Microsoft, and Zoho  
- **Frontend:** Responsive HTML/CSS/JS interface compatible with desktop, tablet, and mobile  

The architecture ensures that AI responses are accurate, safe, context-aware, and multilingual.

---

## System Architecture & Data Flow

The system processes user queries through several layers:

1. **Language Detection:** Determines the input language (English/Hindi/Hinglish) to adapt reasoning  
2. **Memory Layer:** Retrieves previous interactions from Redis for context  
3. **NOBLTY Engine:** Applies logical rules, safety checks, and controlled reasoning  
4. **aastrax Engine:** Adds creativity, context refinement, and intelligent enhancements  
5. **Answer Merge Layer:** Combines outputs from both engines into a final response  
6. **Memory Update:** Saves the interaction to Redis for future context

### Backend Components

- **FastAPI** as the ASGI server  
- **Key Endpoints:**  
  - `/ask` → Processes user queries  
  - `/train` → Owner-only AI training  
  - `/login/{provider}` → OAuth login initiation  
  - `/auth/{provider}` → OAuth callback for session creation  
  - `/health` → System health check  

- **Session Management:** Server-side sessions using `SESSION_SECRET`  
- **Owner Controls:** Training endpoint restricted via `OWNER_SECRET`  

### AI Engines

- **NOBLTY Engine:** Rules, logic, safety enforcement  
- **aastrax Engine:** Creativity, context refinement, answer enhancement  
- **Answer Merge Layer:** Produces the final unified response from both engines  

### Memory & Database

- **Redis:** Short-term context memory (default TTL 3 days, configurable)  
- **PostgreSQL:** Persistent storage for training data and examples  
- **Memory Max Entries:** Configurable per user (default 10)  

### Authentication & Security

- OAuth login via Google, Microsoft, and Zoho  
- Session-based access control  
- Input validation prevents unsafe or malicious prompts  
- Owner-only AI training endpoint  
- No API key required for end users  

### Frontend

- Responsive interface for desktop, tablet, and mobile  
- Dark/Light mode toggle  
- Input box for queries and AI responses  
- Copy-to-clipboard functionality  
- OAuth login buttons integrated with providers  

### Technology Stack

- **Backend:** Python, FastAPI, Uvicorn  
- **Frontend:** HTML, CSS, JavaScript  
- **Database:** PostgreSQL  
- **Memory:** Redis  
- **Authentication:** OAuth 2.0 (Authlib)  
- **Deployment:** ASGI-compatible server  

---

## Security Highlights

- Session-based access control for users  
- Owner-only training endpoint  
- Environment variables for secrets (`SESSION_SECRET`, `OWNER_SECRET`)  
- Prompt validation to block unsafe content  
- Fully self-hosted; no external LLM or vector DB dependencies  

---

## Notes

- Fully self-hosted and flexible for future AI enhancements  
- Context-aware, multilingual AI (English, Hindi, Hinglish)  
- Proprietary engines; no third-party branding exposed  
- Owner-controlled AI training ensures integrity of AI behavior  
- Safe, secure, and responsive design across devices
