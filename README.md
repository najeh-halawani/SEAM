# SEAM Assessment Chatbot

**AI-Augmented Organizational Diagnosis using the Socio-Economic Approach to Management**

An AI-powered diagnostic chatbot for conducting bilingual (Arabic/English) semi-structured interviews, anonymizing responses, categorizing field notes into SEAM dysfunction areas, and clustering similar expressions for organizational diagnosis.

## Quick Start

### 1. Install Dependencies

```bash
cd D:\Projects\SEAM
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### 2. Configure Environment

Copy `.env.example` to `.env` and add your OpenAI API key:

```bash
copy .env.example .env
# Edit .env and set OPENAI_API_KEY
```

### 3. Run the Server

```bash
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

### 4. Access the App

| Page | URL |
|------|-----|
| Landing | http://localhost:8000 |
| Interview Chatbot | http://localhost:8000/interview.html |
| Consultant Dashboard | http://localhost:8000/dashboard.html |

**Dashboard password** (default): `admin123`

## Architecture

```
backend/
├── main.py              # FastAPI app
├── config.py            # Settings (.env)
├── database.py          # SQLite + SQLAlchemy
├── models.py            # ORM models
├── schemas.py           # Pydantic schemas
├── routers/             # API endpoints
│   ├── auth.py          # JWT authentication
│   ├── interview.py     # Chat interview flow
│   └── dashboard.py     # Analytics & export
├── services/            # AI/NLP pipeline
│   ├── interview_engine.py   # GPT conversation
│   ├── anonymizer.py         # NER + rules
│   ├── categorizer.py        # SEAM classification
│   ├── clusterer.py          # Semantic clustering
│   └── language_detector.py  # Arabic/English
└── seam/                # Domain knowledge
    ├── categories.py    # 6 dysfunction areas
    ├── questions.py     # Bilingual Q bank
    └── prompts.py       # GPT system prompts
frontend/
├── index.html           # Landing page
├── interview.html       # Chatbot UI
├── dashboard.html       # Consultant dashboard
├── css/styles.css       # Design system
└── js/                  # Client logic
```

## SEAM Dysfunction Categories

1. **Strategic Implementation** — vision, priorities, strategy-execution alignment
2. **Working Conditions** — environment, tools, workload, well-being
3. **Work Organization** — roles, processes, authority, structure
4. **Time Management** — scheduling, interruptions, deadlines
5. **Communication, Coordination & Cooperation (3Cs)** — information flow, teamwork
6. **Integrated Training** — skills, onboarding, continuous learning

## Designed by

Dr. Karim Shaarani — Doctor in Business Administration, SEAM Expert
