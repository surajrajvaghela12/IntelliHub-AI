# 🌐 Live Deployment Guide for IntelliHub AI (Railway / Render / Vercel)

This repository is fully configured for **1-click automated deployment** on **Railway** and **Render.com**.

---

## Option 1: Render.com (Free & Easiest Recommended)

1. Go to **[https://dashboard.render.com](https://dashboard.render.com)** and sign in with your GitHub account (`surajrajvaghela12`).
2. Click **New +** -> **Web Service**.
3. Select your repository: `surajrajvaghela12/IntelliHub-AI`.
4. Render will automatically detect the settings from `render.yaml`:
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate`
   - **Start Command**: `gunicorn intellihub.wsgi:application`
5. Click **Deploy Web Service**!
6. Your live website URL will be live at `https://intellihub-ai.onrender.com`.

---

## Option 2: Railway.app (Fastest Cloud Deployment)

1. Go to **[https://railway.app](https://railway.app)** and log in with GitHub (`surajrajvaghela12`).
2. Click **New Project** -> **Deploy from GitHub repo**.
3. Select `surajrajvaghela12/IntelliHub-AI`.
4. Railway will auto-detect the `Procfile` and `requirements.txt`.
5. Click **Deploy Now**.
6. Under Settings -> Networking, click **Generate Domain** to get your public live URL (e.g. `https://intellihub-ai.up.railway.app`).

---

## Option 3: GitHub Push Commands for `surajrajvaghela12`

Run these 3 commands in your terminal inside the project directory to publish to GitHub:

```bash
git remote add origin https://github.com/surajrajvaghela12/IntelliHub-AI.git
git branch -M main
git push -u origin main
```
