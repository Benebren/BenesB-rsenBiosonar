# BenesBörsenBiosonar

Private Web-App für automatisierte Analysen (Aktien & Krypto) und ein Ranking nach deiner Buy-Formel.

## Struktur
- `backend/` → FastAPI + Indikatoren + Scoring
- `frontend/` → Next.js UI

## Lokaler Start
1) Backend
```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

2) Frontend
```bash
cd frontend
npm install
cp .env.local.example .env.local
# ggf. NEXT_PUBLIC_BACKEND_URL anpassen
npm run dev
```

## Deployment-Hinweise
- **Railway** (Backend): neues Projekt → Deploy from GitHub → Python → `pip install -r backend/requirements.txt` → Start command: `uvicorn main:app --host 0.0.0.0 --port 8000`
  - Set working directory to `backend`
- **Vercel** (Frontend): neues Projekt → Import from GitHub → Framework: Next.js → Env: `NEXT_PUBLIC_BACKEND_URL` auf Railway-URL setzen

## Scoring-Logik
Score zählt erfüllte Bedingungen (0–7) gemäß deiner Formel:
- EMA50 > EMA200
- RSI14 < 30
- MACD-Linie kreuzt Signal von unten
- Schlusskurs > oberes Bollinger-Band (20, 2)
- ADX14 > 25
- OBV im Aufwärtstrend (letzte 5 Perioden)
- Stochastik: %K kreuzt %D von unten in der 20-Zone

> Hinweise:
> - Die "Squeeze"-Prüfung bei Bollinger ist im MVP vereinfacht (Breakout über oberes Band).
> - Du kannst Gewichte je Bedingung vergeben oder Schwellen anpassen.