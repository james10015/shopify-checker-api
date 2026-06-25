# Shopify API — Northflank Deployment

## 🚀 Deploy (3 Steps)

1. Push this folder to a GitHub/GitLab repo
2. Go to Northflank → Create Service → Select your repo
3. Done. Northflank auto-detects the Dockerfile and deploys.

## ⚙️ Auto-Detected Settings
- **Dockerfile** → Northflank picks it up automatically
- **Port** → 8080 (set in Dockerfile, Northflank maps it)
- **Gunicorn** → Production WSGI server (2 workers, 4 threads)
- **Health Check** → `/health` endpoint available

## 📁 Files
```
├── app.py              # Main Flask application
├── Dockerfile          # Auto-detected by Northflank
├── Procfile            # Fallback (Heroku-style)
├── requirements.txt    # Python dependencies
├── .dockerignore
└── .gitignore
```
