Proposal: New Feature Enhancements for AgriTech

Overview
- Purpose: Add four major features to AgriTech to increase farmer adoption and provide actionable, expert-backed guidance.
- Features:
  1. AI Fertilizer Recommendation System
  2. Weather Forecast Dashboard Integration
  3. Expert Q&A Forum (Community Upgrade)
  4. Farm Progress Tracker

Scope & Goals
- Deliver production-ready backend APIs, minimal frontend components, and integration points for ML and third-party APIs.
- Keep changes incremental and backward-compatible with existing `crop_recommendation` module and `dashboard.html`.

1. AI Fertilizer Recommendation System
- Goal: Suggest fertilizer types and application rates based on soil pH, crop type, and weather conditions.
- Inputs: soil_pH, crop_type, growth_stage (optional), recent_weather (temp, rainfall).
- Output: fertilizer recommendation object {fertilizer_name, NPK_ratio, application_rate, notes}
- Implementation approach:
  - Train a lightweight ML model (scikit-learn or TensorFlow/Keras) using historical fertilizer-response datasets.
  - Integrate model inference into `crop_recommendation` module (e.g., new function `recommend_fertilizer()`).
  - Expose API route: `GET /api/recommend/fertilizer` (query params or POST JSON payload).
  - Validate inputs and return confidence score.
  - Model storage: add `/models/fertilizer_model.*` and versioning metadata in `ipm_config.json` or `ml-model-versioning-implementation.md`.
- Testing: unit tests for inference wrapper, integration tests for API route.

2. Weather Forecast Dashboard Integration
- Goal: Provide real-time weather updates on dashboard using OpenWeatherMap API.
- Backend:
  - New API route: `GET /api/weather?lat={lat}&lon={lon}` — server fetches OpenWeatherMap 5-day/3-hour forecast and caches for short TTL (e.g., 10 minutes).
  - Config: use env var `OPENWEATHER_API_KEY` and `WEATHER_CACHE_TTL`.
  - Rate limiting & error handling for API failures.
- Frontend:
  - Add a weather widget to `dashboard.html` (or `dashboard` component) showing current conditions, 3-day summary, and an icon set.
  - Use existing `index.js`/`dashboard.js` pattern. Minimal UI with optional Chart.js sparkline for temp/precip.

3. Expert Q&A Forum (Community Upgrade)
- Goal: Allow verified experts to answer farmer queries, with role-based access control.
- Auth & Roles:
  - Add roles: `admin`, `farmer`, `expert`.
  - Use JWT-based authentication. Extend current `auth_utils.py` to support roles in token claims and role-check decorators.
  - Endpoints:
    - `POST /api/questions` — create question (farmer)
    - `GET /api/questions/:id` — view question and answers
    - `POST /api/questions/:id/answers` — add answer (expert only)
    - `GET /api/questions` — list (paginated)
  - Verification flow: admin can mark a user as `expert` via `PUT /api/users/:id/role` or via DB flag.
- DB changes:
  - `questions` table: id, user_id, title, body, tags, created_at, status
  - `answers` table: id, question_id, user_id, body, created_at, upvotes
- Frontend:
  - Update forum UI pages (`community_forum.html` or `forum.js`) to show expert answers with badge and allow filtering by `expert`.

4. Farm Progress Tracker
- Goal: Farmers log crop activities and view visual progress insights.
- Data model:
  - `activities` table: id, user_id, farm_id, crop_id, activity_type (sowing, irrigation, fertilizing, harvesting), date, notes, attachments
  - `crop_progress` aggregated view/table to compute GDDs, days since sowing, expected harvest window.
- API:
  - `POST /api/activities` — log activity
  - `GET /api/activities?user_id=&farm_id=&crop_id=` — list activities
  - `GET /api/activities/summary` — summarized metrics for charts
- Frontend:
  - New `farm_progress.html` or widget for `dashboard.html` with charts (Chart.js) showing activity timeline, irrigation frequency, and expected harvest.

Security & Auth
- Extend JWT tokens to include `role` claim.
- Use `auth_utils.py` to implement `@requires_role('expert')` and `@requires_role('admin')` decorators.
- Store sensitive keys in environment variables; do not commit API keys.

Data & Schema Migration
- Add migration scripts (SQL or a small migration helper) to create `roles`, `questions`, `answers`, `activities` tables.
- Backward-compatible migrations: add new columns with defaults where possible.

Integration Points & Files to Modify
- Backend:
  - `app.py` — register new blueprints/routes for `/api/recommend/fertilizer`, `/api/weather`, `/api/questions`, `/api/activities`.
  - `auth_utils.py` — JWT role support and decorators.
  - `agri_utils.py` or `crop_recommendation` module — add `recommend_fertilizer()` wrapper and model loader.
- Frontend:
  - `dashboard.html` and `dashboard.js` (or `farm_dashboard.html` / `farm_dashboard.js`) — add weather and progress widgets.
  - `community_forum.html` and `forum.js` — expert Q&A UI updates.
  - Add Chart.js to `index.html` or per-page scripts (use CDN in prototype).

ML Model Notes
- Prototype with scikit-learn (RandomForest) or a small neural net with Keras depending on dataset size.
- Provide training notebook in `/ml/` with dataset preprocessing steps, reproducible training and eval.
- Maintain model metadata: version, training_date, metrics.

Timeline & Milestones (Suggested)
- Week 1: Design data model, auth roles, and API contracts; create migrations.
- Week 2: Implement JWT roles and forum endpoints; basic frontend for Q&A.
- Week 3: Implement activities API and farm progress UI; basic charts.
- Week 4: Integrate OpenWeatherMap API; add weather widget and caching.
- Week 5: Train POC fertilizer model, integrate into `crop_recommendation` and expose API; testing and polish.

Testing & QA
- Unit tests for new API routes and auth decorators.
- Integration tests for end-to-end flows (question->answer, activity->chart)
- ML model CI: add smoke test ensuring model loads and returns expected output format.

Deliverables
- `PROPOSAL_FEATURE_ENHANCEMENTS.md` (this file)
- New API routes registered in `app.py` and helper modules
- Minimal frontend components wired into existing pages
- Migration scripts and sample data
- ML training notebook and model artifact

Open Questions / Decisions
- Choice of ML framework (scikit-learn vs TensorFlow) — dataset dependent.
- Whether to persist cached weather in DB or memory cache (Redis recommended for scale).
- Expert verification workflow (manual admin vs third-party verification).

Next Steps
- Review proposal and approve scope.
- I can scaffold the API routes, add DB migrations, and scaffold frontend widgets next — which would you like me to start with?
