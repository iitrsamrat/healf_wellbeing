# Healf Personalisation — ML System

Personalisation layer for Healf across two surfaces: the For You page and the Product Detail Page. Five experiences across three tiers: on-browser, backend real-time, and batch.

Read `ARCHITECTURE.md` first — it explains what's here and why.

---

## Setup (under 10 minutes)

**1. Clone and create environment**
```bash
git clone https://github.com/iitrsamrat/healf_wellbeing.git
cd healf_wellbeing
conda create -n healf python=3.11 -y
conda activate healf
pip install -r requirements.txt
```

**2. Start the backend**
```bash
uvicorn backend.main:app --reload
```
Backend runs at `http://localhost:8000`. Docs at `http://localhost:8000/docs`.

**3. Open the UI**

Open `browser/index.html` directly in your browser. No build step needed.

Switch between users in the top-right dropdown to see how each experience changes based on available signal.

**4. Run the batch pipeline**
```bash
python batch/retrain.py
```
Shows what runs overnight: profile updates, model training, biomarker delta analysis, dropout risk flagging.

---

## What to look at

| File | What it demonstrates |
|---|---|
| `browser/index.html` | On-browser intent model + all 5 experiences in the UI |
| `backend/main.py` | Real-time tier — 5 API endpoints, one per experience |
| `backend/knowledge_graph.py` | Graph traversal — cold start, gap detection, biomarker mapping |
| `batch/retrain.py` | Batch tier — model training, embeddings, Zone delta analysis |
| `data/mock_data.py` | 5 users at different signal stages, 20 products, biomarker snapshots |

---

## Five users — five stages of signal

| User | Signal available | What they see |
|---|---|---|
| Tom | Nothing — cold start | Bestsellers + quiz prompt |
| Sarah | Quiz + 1 purchase | Goal-ranked shelf, why-right-for-you |
| James | 3 purchases + subscription | Stack gaps, complementary products |
| Priya | Zone member, deficient biomarkers | Biomarker-aware recommendations |
| Elena | Zone member, cardiovascular pattern | Multi-biomarker risk, personalised PDP |

---

## API endpoints

```
GET  /helix/chips/{user_id}           — personalised Helix prompt chips
GET  /foryou/{user_id}                — ranked For You shelf
GET  /pdp/{user_id}/{product_id}/why  — why this product is right for you
GET  /pdp/{user_id}/{product_id}/stack — complementary stack products
POST /helix/recommend                 — four-agent Helix reasoning
```

---

## On the browser model

`browser/index.html` includes a lightweight session intent classifier that runs entirely in the browser — no server round-trip. It watches which products you view in the current session and infers your current pillar intent (Eat / Move / Mind / Sleep). The shelf re-ranks in real time based on this.

In production this would be a quantised ONNX model loaded via `onnxruntime-web`. Here the same interface and logic is implemented in JavaScript to demonstrate the tier boundary without requiring a build pipeline.

---

## Folder structure

```
healf_wellbeing/
├── ARCHITECTURE.md
├── README.md
├── requirements.txt
├── data/
│   └── mock_data.py
├── backend/
│   ├── main.py
│   └── knowledge_graph.py
├── batch/
│   └── retrain.py
└── browser/
    └── index.html
```
