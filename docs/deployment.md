# NOBLTY AI × aastrax Deployment Guide

This guide provides complete instructions for deploying NOBLTY AI × aastrax, a fully self-hosted, multilingual AI system. Before deploying, make sure you have Python 3.10+, PostgreSQL, Redis, Git, and an ASGI-compatible server such as Uvicorn, Gunicorn, or Hypercorn.

Create a `.env` file based on `.env.example` with the following variables: DATABASE_URL for PostgreSQL, REDIS_URL for Redis, SESSION_SECRET for session management, OWNER_SECRET for owner-only AI training access, and OAuth credentials for Google, Microsoft, and Zoho login. Do not commit `.env` to any public repository.

Install dependencies using `pip install -r requirements.txt`. This will install FastAPI, Uvicorn, aioredis, asyncpg, Authlib, Starlette, and Pydantic.

Set up the PostgreSQL database. Create a database named `NOBLTY_AI` and ensure the owner user has proper privileges. Create the training table with `id` as the primary key, `language` for the language code, `instruction` for the AI instruction, `examples` as a JSONB column, and `created_at` timestamp.

Run the application locally with `uvicorn main:app --host 0.0.0.0 --port 8000`. Access the app at `http://localhost:8000`, login using Google, Microsoft, or Zoho, and interact with the AI through the responsive frontend interface.

For production deployment, select a cloud platform (Heroku, AWS, Railway, DigitalOcean, etc.), configure environment variables, and use the provided `Procfile` containing `web: uvicorn main:app --host=0.0.0.0 --port=${PORT:-8000}`. Enable HTTPS for secure connections and monitor logs for errors and performance.

Follow security guidelines by keeping all secrets private, restricting owner-only training endpoints, validating prompts to block unsafe content, and preventing public access to PostgreSQL and Redis. Regular backups of Redis and PostgreSQL are recommended.

Notes: The system is fully self-hosted, production-ready, session-based with OAuth authentication, context-aware, multilingual (English, Hindi, Hinglish), responsive across all devices, safe, reliable, and does not depend on any external LLM or vector database.
