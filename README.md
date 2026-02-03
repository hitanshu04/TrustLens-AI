## Scam Detection API (FastAPI)

Real-time Scam Detection API built with **FastAPI**, designed to be **production-ready** and **ML-ready**.  
The core engine combines keyword-based rules, URL reputation heuristics, and a placeholder for behavioral/ML signals.

---

### Features

- **POST `/api/v1/analyze`**
  - Accepts **raw message text** and optional **behavioral metadata**
  - Returns **`scam_risk_score`** (0–100) and **human-readable reasons**
- **Rule-based risk engine**
  - Keyword/NLP heuristics for common scam patterns
  - URL reputation checks, with emphasis on **shortened links** (e.g. `bit.ly`, `tinyurl.com`)
  - Behavioral signal **placeholder** for future models (metadata field)
- **ML-ready design**
  - Pluggable `RiskComponent` interface for rule-based and ML components
  - `MlModelComponent` stub ready for hooking up a classifier
- **Modular architecture**
  - `routers/` for API endpoints
  - `services/` for risk engine & utilities
  - `models/` for Pydantic schemas
  - `core/` for configuration

---

### Project Structure

```text
scam-risk-engine/
  main.py                 # FastAPI app + uvicorn entrypoint
  requirements.txt
  README.md
  app/
    __init__.py
    core/
      config.py           # Settings (host, port, URL reputation config, etc.)
    models/
      __init__.py
      schemas.py          # Request/response schemas and Reason model
    services/
      __init__.py
      risk_engine.py      # Pluggable risk engine and rule components
      url_reputation.py   # URL extraction + reputation heuristics
    routers/
      __init__.py
      analyze.py          # /api/v1/analyze endpoint
```

---

### Installation

From the project root (`scam-risk-engine`):

```bash
python -m venv .venv
.venv\Scripts\activate  # On Windows
# source .venv/bin/activate  # On macOS/Linux

pip install -r requirements.txt
```

---

### Running the API (uvicorn)

From the project root:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

Or using the built-in entrypoint:

```bash
python main.py
```

By default the API will be available at:

- Base URL: `http://localhost:8000`
- Docs (Swagger UI): `http://localhost:8000/docs`

---

### API: POST `/api/v1/analyze`

- **URL**: `/api/v1/analyze`
- **Method**: `POST`
- **Request body** (`application/json`):

```json
{
  "message": "Congratulations! You have won a $1,000 gift card. Click https://bit.ly/abc123 to claim now.",
  "metadata": {
    "channel": "sms",
    "recipient_country": "US",
    "sender_is_new": true
  }
}
```

- **Response** (`200 OK`):

```json
{
  "scam_risk_score": 87,
  "reasons": [
    {
      "type": "keyword",
      "description": "Detected high-risk phrases associated with common scam patterns: congratulations, gift card, you have won",
      "weight": 0.7
    },
    {
      "type": "url_reputation",
      "description": "Detected shortened URL using domain 'bit.ly', which is commonly used to obscure final destinations in scam messages.",
      "weight": 0.3
    }
  ],
  "url_indicators": ["https://bit.ly/abc123"]
}
```

> **Note**: Exact scores and weights will vary based on message content and engine tuning.

---

### Detection Engine Design

- **Keyword-based NLP rules**

  - Implemented in `KeywordRuleComponent` within `app/services/risk_engine.py`
  - Uses weighted phrases like `"wire transfer"`, `"gift card"`, `"you have won"`, `"verification code"`, etc.
  - Each match contributes to a normalized risk score (0–1), then mapped to 0–100.

- **URL reputation**

  - Implemented in `UrlReputationComponent` and `app/services/url_reputation.py`
  - Extracts URLs with a regex and checks them against `SUSPICIOUS_SHORT_DOMAINS` from `core/config.py`
  - Shortened links (e.g., `bit.ly`, `tinyurl.com`, `t.co`) contribute a higher risk score and explicit reasons.

- **Behavioral signals (placeholder)**

  - `AnalyzeRequest.metadata` is a **free-form dict** intended for contextual/behavioral data:
    - Channel (SMS, email, chat)
    - Sender history
    - Message frequency, etc.
  - `BehavioralSignalComponent` currently returns **neutral** scores, but documents where future logic should go.

- **ML-ready integration**
  - `RiskComponent` protocol defines a simple `analyze(message, metadata) -> (score, reasons)` interface.
  - `RiskEngine` composes multiple components:
    - `KeywordRuleComponent`
    - `UrlReputationComponent`
    - `BehavioralSignalComponent`
    - `MlModelComponent` (stub)
  - To plug in a real ML model:
    - Implement a new component (or enable `MlModelComponent`) that:
      - Loads your model (e.g., from a serialized file or remote service)
      - Computes a probability / risk score in \[0, 1\]
      - Returns a list of `Reason` objects explaining the model's decision (when possible).
    - Add it to the `RiskEngine` components list.

---

### Extending the Engine

- **Add new rules**

  - Edit `KeywordRuleComponent.KEYWORD_WEIGHTS` to add/remove phrases or adjust weights.
  - Extend URL heuristics in `url_reputation.py` (e.g., blocklists, suspicious TLDs, external reputation APIs).

- **Add a real ML model**
  - Implement a new class that conforms to `RiskComponent`:
    - Accepts `message` and optional `metadata`
    - Returns a normalized score \[0, 1\] and `Reason` list
  - Plug it into `RiskEngine` by passing a custom `components` list or modifying the default.

---

### Example `curl` Request

```bash
curl -X POST "http://localhost:8000/api/v1/analyze" \
  -H "Content-Type: application/json" \
  -d '{
        "message": "URGENT: Your bank account is locked. Visit https://tinyurl.com/fake-bank to verify immediately.",
        "metadata": {
          "channel": "sms",
          "sender_is_new": true
        }
      }'
```

---

### Production Notes

- Run behind a proper ASGI server setup (e.g. `uvicorn` or `gunicorn` + `uvicorn.workers.UvicornWorker`)
- Use environment variables or `.env` to configure:
  - `HOST`, `PORT`, `RELOAD`
  - URL reputation lists and any API keys for external services
- Add logging, monitoring, and rate limiting in front of the API (e.g. via API gateway or reverse proxy).
