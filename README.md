# Talking Tom Hackathon (Vue + FastAPI)

This is a hackathon-ready, core-loop clone inspired by the classic pet-care game.

## Requirements
- Node.js 18+
- Python 3.11+

## Backend (FastAPI)
```
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Frontend (Vue 3 + Vite)
```
cd frontend
npm install
npm run dev
```

## Notes
- API base defaults to `http://localhost:8000`. Override with `VITE_API_BASE`.
- Player data is stored in `backend/data.sqlite`.
- Asset credits are listed in `CREDITS.md`.
