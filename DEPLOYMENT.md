# Deploying Math Mentor

## Why not Vercel?

**Vercel is not a good fit** for this app: it’s serverless (short-lived functions), while this app is a **Streamlit** server (long-running process). Use one of the options below instead.

---

## Which is easiest? Streamlit Cloud vs Railway vs Render

| Platform | Easiest? | Why |
|----------|----------|-----|
| **Streamlit Community Cloud** | **Yes** | Built for Streamlit. Connect GitHub → choose `streamlit_app.py` → add `GROQ_API_KEY` → deploy. No Procfile, no port config. Free tier. |
| **Railway** | Medium | General PaaS. You add a Procfile (or set the start command) to run `streamlit run streamlit_app.py`, set env vars. One extra step. |
| **Render** | Medium | Same idea: create a Web Service, set build/start command, add env vars. Free tier; free instances spin down and have cold starts. |

**Recommendation:** Use **Streamlit Community Cloud** — it’s the easiest for this app and needs no extra config.

---

## Option 1: Streamlit Community Cloud (recommended)

**Free, minimal setup, made for Streamlit.**

1. Push your repo to **GitHub** (e.g. `yourusername/math-mentor`).
2. Go to **[share.streamlit.io](https://share.streamlit.io)** and sign in with GitHub.
3. Click **“New app”**:
   - **Repository**: `yourusername/math-mentor`
   - **Branch**: `main` (or your default)
   - **Main file path**: `streamlit_app.py`
   - **App URL**: e.g. `math-mentor`
4. Open **“Advanced settings”** and add **Secrets** (TOML):
   ```toml
   GROQ_API_KEY = "gsk_your_actual_key"
   ```
5. Deploy. First run can be slow (deps + RAG build). App URL: `https://math-mentor.streamlit.app` (or the name you set).

**Tips:**

- If the app lives in a subfolder (e.g. `Math_mentor_Project`), set **Root directory** to that folder.
- To pin Python 3.11, add `runtime.txt` in the project root with: `python-3.11`
- RAG is built at startup from `knowledge_base/` if that folder is in the repo.

---

## Option 2: Railway

1. Go to **[railway.app](https://railway.app)** and sign in (e.g. with GitHub).
2. **New project** → **Deploy from GitHub repo** → select your repo.
3. Add a **Procfile** in the project root (if not already present):
   ```
   web: streamlit run streamlit_app.py --server.port=$PORT --server.address=0.0.0.0
   ```
4. In the Railway dashboard, set **Variables**: `GROQ_API_KEY` = your key.
5. Deploy. Railway will detect Python and run the Procfile. Your app gets a URL like `https://your-app.up.railway.app`.

---

## Option 3: Render

1. Go to **[render.com](https://render.com)** and sign in (e.g. with GitHub).
2. **New** → **Web Service** → connect your repo.
3. Set:
   - **Build command**: `pip install -r requirements.txt`
   - **Start command**: `streamlit run streamlit_app.py --server.port=$PORT --server.address=0.0.0.0`
4. Under **Environment**, add `GROQ_API_KEY`.
5. Deploy. On the free tier, the service may sleep when idle (cold start when someone visits).

---

## Option 4: Hugging Face Spaces

1. **[huggingface.co](https://huggingface.co)** → create a **Space**.
2. **SDK**: Streamlit. Put your code in the Space (or clone and push).
3. If the Space expects `app.py`, you can rename `streamlit_app.py` to `app.py` in that repo, or set the Space’s app file to `streamlit_app.py` if the UI allows.
4. Add **Secrets**: `GROQ_API_KEY`.
5. App URL: `https://huggingface.co/spaces/yourusername/math-mentor`.

---

## Summary

| Goal | Use |
|------|-----|
| Easiest, no config | **Streamlit Community Cloud** |
| Same app on Railway | Add Procfile + env var |
| Same app on Render | Set start command + env var |
| Free Streamlit host with community | **Hugging Face Spaces** |

For this project, **Streamlit Community Cloud** is the simplest.
