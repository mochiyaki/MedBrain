# MedBrain — Task Board

> Actionable work items for the team. Pick a task, create a branch (`feature/<task-short-name>`), and open a PR when ready.

---

## 🎨 FRONTEND

### Task 1: Landing Page
**Priority:** High  
**Estimated Effort:** 2–3 days

#### Description
Create an engaging landing page for MedBrain — the clinical AI reasoning platform.

#### Requirements
- Hero section with product value proposition (AI-powered clinical intelligence)
- Key features overview (Patient Management, Radiology Analysis, Smart Notes, AI Research)
- Call-to-action for sign-up / login
- Responsive design (mobile + desktop)
- Modern medical UI aesthetic (clean, trustworthy, professional)

#### Tech Stack
- React + TypeScript
- Tailwind CSS for styling
- Framer Motion for animations

#### Acceptance Criteria
- [ ] Landing page renders at `/`
- [ ] Responsive on mobile, tablet, desktop
- [ ] Links to login/signup flow
- [ ] Lighthouse performance score > 90
- [ ] Accessible (WCAG 2.1 AA)

---

### Task 2: Patient Dashboard with Add/Edit Patient Info
**Priority:** High  
**Estimated Effort:** 4–5 days

#### Description
Build a patient management dashboard where clinicians can view, add, and edit patient information.

#### Requirements
- Patient list view with search/filter functionality
- Patient detail view showing full medical profile
- Add New Patient form (demographics, medical history, allergies, medications)
- Edit Patient information inline or via modal
- Patient timeline showing visits, notes, and imaging history

#### UI Components
- Data table with sorting, pagination, and search
- Patient profile card (photo, name, DOB, MRN, contact info)
- Forms with validation for patient data entry
- Status indicators (active, discharged, critical)

#### Data Fields to Support
| Category | Fields |
|----------|--------|
| Demographics | Name, DOB, Gender, MRN, Contact, Insurance |
| Medical History | Conditions, Surgeries, Family History |
| Current | Medications, Allergies, Vitals |
| Visits | Date, Provider, Notes, Imaging |

#### Acceptance Criteria
- [ ] Patient list with search/filter/sort
- [ ] Add new patient form with validation
- [ ] Edit existing patient details
- [ ] Patient detail page with comprehensive view
- [ ] Loading states and error handling
- [ ] Responsive layout

---

### Task 3: Radiology Analysis Page
**Priority:** High  
**Estimated Effort:** 5–7 days

#### Description
Create a radiology analysis page where clinicians can upload, view, and get AI-powered analysis of medical imaging (X-rays, CT scans, MRIs).

#### Requirements
- DICOM/medical image viewer with pan, zoom, window/level controls
- Image upload interface (drag & drop, file picker)
- AI analysis panel showing findings, annotations, and confidence scores
- Side-by-side comparison view (previous vs current imaging)
- Report generation section with AI-suggested findings
- Annotation tools (draw ROI, measure, mark areas of interest)

#### Key Features
| Feature | Details |
|---------|---------|
| Upload | Support DICOM, PNG, JPG formats |
| Viewer | Pan, zoom, brightness/contrast, window/level presets |
| AI Analysis | Trigger analysis, show heatmaps/overlays of findings |
| Report | AI-generated preliminary report, editable by clinician |
| History | View previous imaging for same patient |

#### Acceptance Criteria
- [ ] Image upload with drag-and-drop
- [ ] Medical image viewer with basic controls (zoom, pan, window/level)
- [ ] AI analysis trigger button with loading state
- [ ] Results panel showing findings with confidence scores
- [ ] Report generation/editing interface
- [ ] Image comparison view

#### Dependencies
- Backend radiology analysis API (Task 8 — Deep Agent)
- Image storage service

---

### Task 4: Clinical Note-Taking Page with Audio Transcription
**Priority:** High  
**Estimated Effort:** 5–6 days

#### Description
Build a clinical note-taking interface with real-time audio transcription capabilities. This should support clinicians documenting patient encounters via voice or text.

#### Requirements
- Rich text editor for clinical notes (SOAP format support)
- Audio recording with real-time transcription display
- Session-based organization (each encounter = one session with timestamp)
- Note templates (SOAP, H&P, Progress Note, Discharge Summary)
- Patient association (link notes to specific patient)
- Search and filter past notes by date, patient, type

#### Audio Transcription Features
- Start/stop/pause recording controls
- Real-time transcription preview as audio is captured
- Post-recording editing of transcribed text
- Speaker diarization indicator (if multiple speakers)
- Audio playback synced with transcript

#### Note Organization
- Session list with date stamps
- Per-patient note history
- Tags and categories
- Quick-search across all notes

#### Mobile / Android Considerations
- Design mobile-first for the note-taking interface
- Consider PWA approach for cross-platform support
- Offline-capable note drafting with sync when connected

#### Acceptance Criteria
- [ ] Rich text editor with medical note templates
- [ ] Audio recording with start/stop/pause
- [ ] Real-time transcription display
- [ ] Session organization with timestamps
- [ ] Patient-linked notes
- [ ] Search/filter functionality
- [ ] Mobile-responsive design

#### Dependencies
- Backend transcription API (Task 7)
- Database schema for notes (Task 5)

---

## ⚙️ BACKEND

### Task 5: Design and Implement Database Schema
**Priority:** High (Foundation — start here)  
**Estimated Effort:** 3–4 days

#### Description
Design and implement the core database schema for MedBrain covering patients, notes, imaging, sessions, and AI interactions.

#### Schema Design

**Core Tables**
```
patients          — Demographics, MRN, contact info, insurance
medical_history   — Conditions, surgeries, family history (FK → patients)
medications       — Current and past medications with dosage/frequency
allergies         — Patient allergies and reactions
vitals            — Time-series vital signs
```

**Clinical Notes**
```
sessions          — Clinical encounter sessions (date, provider, patient, type)
notes             — Rich text notes linked to sessions (with audio_url reference)
transcriptions    — Raw transcription data with timestamps and speaker info
```

**Imaging**
```
imaging_studies   — Uploaded imaging metadata (patient, date, modality, body part)
imaging_files     — File references (S3/storage paths, DICOM metadata)
ai_analyses       — AI analysis results linked to imaging studies
annotations       — Clinician/AI annotations on images
```

**AI & Context**
```
agent_sessions    — AI agent interaction logs
research_results  — Cached deep research results
context_snapshots — Serialized context graph snapshots
```

#### Technical Requirements
- PostgreSQL with proper indexing strategy
- Soft deletes (`deleted_at` timestamps)
- Audit trail (`created_by`, `updated_by`, timestamps on all tables)
- Multi-tenancy support (`organization_id`)
- HIPAA-compliant data handling considerations
- Database migrations via Alembic

#### Deliverables
- [ ] ER diagram / schema documentation
- [ ] Migration files for all tables
- [ ] Seed data for development
- [ ] Index strategy document
- [ ] README for database setup

---

### Task 6: Build Context Graph for Agent Memory
**Priority:** High  
**Estimated Effort:** 5–7 days

#### Description
Implement a knowledge/context graph that serves as the AI agent's memory system. This graph stores patient relationships, clinical facts, temporal data, and enables the agent to reason over historical context.

#### Graph Structure
| Element | Examples |
|---------|----------|
| Nodes | Patients, Conditions, Medications, Providers, Encounters, Lab Results, Imaging |
| Edges | Relationships with temporal metadata (`valid_from`, `valid_to`) |
| Episodes | Grouped related clinical events into episodes of care |
| Facts | Atomic clinical facts extracted from notes/records |

#### Key Capabilities
- Add/update/query facts about patients
- Temporal reasoning (what was true at time T?)
- Relationship traversal (patient → conditions → medications → interactions)
- Context window management (retrieve relevant context for AI agent)
- Similarity search over embedded clinical facts

#### Memory Types
| Type | Purpose | Storage |
|------|---------|---------|
| Short-term | Current session context, recent interactions | Redis |
| Long-term | Persistent patient facts, clinical history | Graph DB |
| Episodic | Grouped encounters and care episodes | Graph DB |
| Semantic | Embedded clinical knowledge for similarity retrieval | Vector DB |

#### Tech Stack
- Neo4j or Zep for graph storage
- Vector embeddings for semantic search (pgvector or Pinecone)
- LangGraph for agent-graph interaction patterns
- Redis for short-term/session memory caching

#### Acceptance Criteria
- [ ] Graph schema defined with node/edge types
- [ ] CRUD operations for facts and relationships
- [ ] Temporal query support (point-in-time queries)
- [ ] Context retrieval API (given patient + query → relevant context)
- [ ] Embedding pipeline for clinical text
- [ ] Integration tests with sample patient data

---

### Task 7: Note-Taking Service with Audio Transcription & AI Storage
**Priority:** High  
**Estimated Effort:** 5–6 days

#### Description
Build the backend service for clinical note-taking that handles audio transcription, AI-powered note processing, and persistent storage with session timestamps.

#### Audio Transcription Pipeline
- Accept audio uploads (WAV, MP3, WebM formats)
- Real-time streaming transcription via WebSocket (for live recording)
- Batch transcription for uploaded audio files
- Speaker diarization (identify different speakers)
- Medical vocabulary enhancement for accuracy

#### AI Note Processing
- Parse transcribed text into structured clinical notes
- Extract key medical entities (conditions, medications, procedures)
- Auto-generate SOAP note sections from free-text
- Summarize long transcriptions into concise notes
- Identify and flag action items (orders, follow-ups, referrals)

#### Storage & Organization
- Store notes per session with timestamps (`created_at`, `session_date`)
- Link notes to patient records
- Version history for edited notes
- Audio file storage (S3/object storage)
- Full-text search across notes

#### API Endpoints
```
POST   /api/notes/sessions          — Create new note session
GET    /api/notes/sessions/:id      — Get session with notes
POST   /api/notes/transcribe        — Upload audio for transcription
WS     /api/notes/transcribe/stream — Real-time transcription stream
POST   /api/notes/:id/process       — AI process a note (extract entities, generate SOAP)
GET    /api/notes/patient/:id       — Get all notes for patient
GET    /api/notes/search            — Full-text search notes
```

#### Tech Stack
- FastAPI for REST + WebSocket endpoints
- Whisper / Deepgram / AssemblyAI for transcription
- LangChain for AI note processing
- PostgreSQL for structured storage
- S3-compatible storage for audio files
- Elasticsearch for full-text search (optional)

#### Acceptance Criteria
- [ ] Audio upload and batch transcription working
- [ ] WebSocket streaming transcription endpoint
- [ ] Notes stored with session timestamps
- [ ] AI extracts medical entities from transcribed text
- [ ] SOAP note auto-generation from free text
- [ ] Patient-linked note retrieval
- [ ] Full-text search across notes

---

### Task 8: Deep Agent Harness for Context Management & Online Research
**Priority:** High  
**Estimated Effort:** 7–10 days

#### Description
Build a deep AI agent harness that manages clinical context and performs deep research from online medical content (PubMed, clinical guidelines, drug databases, etc.). This is the core "Brain" in MedBrain.

#### Agent Architecture
- Multi-step reasoning agent using LangGraph
- Tool-use capabilities (search, retrieve, analyze, summarize)
- Context window management (prioritize relevant info)
- Chain-of-thought clinical reasoning
- Fallback and error handling for failed tool calls

#### Context Management
- Pull relevant patient context from the context graph (Task 6)
- Manage conversation history with smart truncation
- Priority ranking of context items (recent > old, relevant > tangential)
- Dynamic context assembly based on query intent
- Memory consolidation (summarize old context periodically)

#### Deep Research Capabilities
| Capability | Source |
|------------|--------|
| Medical Literature | PubMed / NCBI APIs |
| Clinical Trials | ClinicalTrials.gov |
| Drug Info & Interactions | OpenFDA, DrugBank |
| Clinical Guidelines | WHO/CDC, specialty societies |
| Lab Interpretation | Reference ranges, clinical significance |
| Differential Diagnosis | Symptom → ranked DDx with evidence |

#### API Endpoints
```
POST   /api/agent/query              — Submit a clinical query
POST   /api/agent/research           — Trigger deep research on a topic
GET    /api/agent/research/:id       — Get research results
POST   /api/agent/context/assemble   — Assemble context for a patient query
GET    /api/agent/sessions/:id       — Get agent session history
POST   /api/agent/differential       — Generate differential diagnosis
```

#### Tech Stack
- LangGraph for agent orchestration
- LangChain tools for search/retrieval
- Fireworks AI / OpenAI for LLM inference
- Tavily or Serper for web search
- BioPython for PubMed integration
- Redis for caching research results

#### Acceptance Criteria
- [ ] LangGraph agent with multi-step reasoning
- [ ] Context assembly from patient graph + session history
- [ ] PubMed search and summarization tool
- [ ] Drug interaction checking tool
- [ ] Clinical guideline retrieval
- [ ] Research results caching and retrieval
- [ ] Streaming responses for real-time UI updates
- [ ] Error handling and fallback strategies

---

## 📋 Task Dependency Graph

```
Task 5 (DB Schema) ──────────┐
                              ├──→ Task 2 (Patient Dashboard)
Task 6 (Context Graph) ──────┤
                              ├──→ Task 7 (Note-Taking Backend) ──→ Task 4 (Notes Frontend)
                              │
                              └──→ Task 8 (Deep Agent) ──→ Task 3 (Radiology Frontend)

Task 1 (Landing Page) — Independent, can start immediately
```

## 🚀 Suggested Workflow

1. **Start immediately (no dependencies):** Task 1 (Landing Page), Task 5 (DB Schema)
2. **After DB Schema:** Task 2 (Patient Dashboard), Task 6 (Context Graph)
3. **After Context Graph:** Task 7 (Note-Taking Backend), Task 8 (Deep Agent)
4. **After Backend APIs:** Task 3 (Radiology Page), Task 4 (Notes Page)

## 🛠️ Project Setup (Do First)

Before starting any task, the repo needs initial scaffolding:
```bash
# Frontend (React + TypeScript + Vite + Tailwind)
npm create vite@latest frontend -- --template react-ts

# Backend (FastAPI + Python)
mkdir backend && cd backend
python -m venv venv
pip install fastapi uvicorn sqlalchemy alembic langchain langgraph
```

---

*Last updated: 2026-05-23*
