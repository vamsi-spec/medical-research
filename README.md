> **AI-powered medical literature research assistant with evidence-based answers from 5,000+ PubMed abstracts**

An intelligent medical research assistant that retrieves, ranks, and synthesizes peer-reviewed medical literature to provide evidence-based answers with confidence scoring, safety mechanisms, and real-time medical API integrations.


## ✨ **Key Features**

### 🔬 **Core Capabilities**
- **Hybrid Retrieval System**: BM25 (lexical) + FAISS (semantic) for optimal precision
- **Evidence-Based Ranking**: Prioritizes Meta-Analyses > Systematic Reviews > RCTs > Clinical Trials
- **Confidence Scoring**: 5-factor confidence assessment (retrieval, evidence, consistency, completeness, recency)
- **Safety Layer**: Detects and refuses unsafe queries (diagnosis, treatment, dosage, emergencies)
- **Hallucination Detection**: Validates citations and detects uncited claims

### 🛠️ **Medical Tools** (Real APIs)
- **Drug Interaction Checker**: RxNav API (NLM/NIH) - 100,000+ drug pairs
- **Clinical Trials Search**: ClinicalTrials.gov API - recruiting trials nationwide
- **Medical Code Lookup**: ICD-10 (70,000+ codes) & CPT via NLM ClinicalTables API

### 🎨 **Frontend Features**
- Professional chat interface with real-time Q&A
- Citation management with PubMed links
- Evidence badges (Level A/B/C)
- Dark mode support
- Chat history & bookmarks
- Export (PDF, Text, BibTeX)
- Voice input (Chrome/Edge)
- Keyboard shortcuts
- PWA (installable app)
- Medical disclaimer

---

## 🏗️ **System Architecture**
```
┌─────────────────────────────────────────────────────────────────┐
│                         FRONTEND (React)                         │
│  Chat UI │ Tools │ History │ Export │ Settings │ Voice Input   │
└───────────────────────────┬─────────────────────────────────────┘
                            │ HTTP/REST
┌───────────────────────────▼─────────────────────────────────────┐
│                   BACKEND API (FastAPI)                          │
│  /ask │ /drug-interaction │ /clinical-trials │ /medical-code   │
└───────────────────────────┬─────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
┌───────▼────────┐  ┌──────▼──────┐  ┌────────▼─────────┐
│ SAFETY LAYER   │  │  RAG ENGINE │  │  EXTERNAL APIs   │
│ - Detect Unsafe│  │  - Hybrid   │  │  - RxNav (NLM)   │
│ - Hallucination│  │    Retrieval│  │  - ClinicalTrials│
│ - Validation   │  │  - Evidence │  │  - NLM Codes     │
│                │  │    Ranking  │  │                  │
└────────────────┘  └──────┬──────┘  └──────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
┌───────▼────────┐ ┌──────▼──────┐  ┌───────▼────────┐
│ BM25 INDEX     │ │ FAISS INDEX │  │ LLM (Ollama)   │
│ (Lexical)      │ │ (Semantic)  │  │ llama3.1:8b    │
│ 5000+ abstracts│ │ 384-dim     │  │ llama3.2       │
└────────────────┘ └─────────────┘  └────────────────┘
                           │
                  ┌────────▼────────┐
                  │ PUBMED DATABASE │
                  │ 5000+ Abstracts │
                  └─────────────────┘
```

---

## 🛠️ **Tech Stack**

### **Backend**
- **Framework**: FastAPI 0.104+ (Python 3.10+)
- **Database**: PostgreSQL + SQLAlchemy ORM
- **Retrieval**: 
  - BM25 (Rank-BM25) for lexical matching
  - FAISS for semantic similarity
- **LLM**: Ollama (llama3.1:8b for answers, llama3.2 for embeddings)
- **APIs**: 
  - PubMed Entrez (NCBI)
  - RxNav (NLM)
  - ClinicalTrials.gov
  - NLM ClinicalTables

### **Frontend**
- **Framework**: React 18.2 + Vite
- **Styling**: Tailwind CSS v3
- **State**: Zustand
- **UI Components**: Custom + Lucide React icons
- **Features**: 
  - React Markdown
  - React Hot Toast
  - jsPDF for export
  - Voice input (Web Speech API)
  - PWA (Service Worker)


## 🚀 **Quick Start**

### **Prerequisites**
```bash
# Required
- Python 3.10+
- Node.js 18+
- PostgreSQL 14+
- Ollama (for LLM)

# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Pull models
ollama pull llama3.1:8b
ollama pull llama3.2
```

### **1. Clone Repository**
```bash
git clone https://github.com/yourusername/medical-research-assistant.git
cd medical-research-assistant
```

### **2. Backend Setup**
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env with your settings

# Initialize database
python scripts/init_db.py

# Download PubMed data (5000 abstracts)
python scripts/data_ingestion/pubmed_fetcher.py

# Build indices
python scripts/build_indices.py

# Start backend
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

### **3. Frontend Setup**
```bash
cd medical-assistant-frontend

# Install dependencies
npm install

# Create .env
echo "VITE_API_BASE_URL=http://localhost:8000/api/v1" > .env

# Start frontend
npm run dev
```

### **4. Access Application**
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

---

## 📖 **Usage Guide**

### **Basic Query**
```
Q: What is the first-line treatment for type 2 diabetes?

A: The first-line treatment for type 2 diabetes is metformin, 
   combined with lifestyle modifications including diet and exercise...
   
   [1] [2] [3]  ← Citations linked to PubMed
   
   Confidence: 87%
   Evidence: 3 Level A, 2 Level B
```

### **Using Medical Tools**

#### **1. Drug Interaction Checker**
```
Drug 1: warfarin
Drug 2: aspirin
→ Major interaction detected
→ Increased bleeding risk
→ Clinical recommendation provided
```

#### **2. Clinical Trials Search**
```
Condition: type 2 diabetes
→ 10+ recruiting trials
→ Locations, phases, enrollment info
→ Direct links to ClinicalTrials.gov
```

#### **3. Medical Codes Lookup**
```
Search: diabetes (ICD-10)
→ E11.9: Type 2 diabetes without complications
→ E11.65: Type 2 diabetes with hyperglycemia
→ Billable status, categories
```

### **Export & Collaboration**
- **Export as PDF**: Full conversation with citations
- **Export as Text**: Plain text format
- **Export Citations**: BibTeX format for reference managers
- **Bookmark Answers**: Save important findings

---

## 🧪 **Evaluation & Benchmarking**

### **Run Benchmark**
```bash
# Full evaluation (30 queries)
python scripts/evaluation/run_benchmark.py

# Compare retrievers
python scripts/evaluation/compare_retrievers.py

# Generate PDF report
python scripts/evaluation/generate_report.py
```

### **Benchmark Categories**
- **Treatment**: 8 queries (first-line therapies, management)
- **Pharmacology**: 5 queries (mechanism of action, drug info)
- **Diagnosis**: 5 queries (criteria, screening)
- **Pathophysiology**: 5 queries (disease mechanisms)
- **Prevention**: 4 queries (risk reduction, lifestyle)
- **Adverse Effects**: 3 queries (side effects, complications)

### **Performance by Difficulty**
| Difficulty | Avg Confidence | Avg Response Time |
|------------|----------------|-------------------|
| Easy (10)  | 86.7% | 2.12s |
| Medium (13)| 81.4% | 2.38s |
| Hard (7)   | 74.2% | 2.89s |

---

## 🔒 **Safety & Compliance**

### **Safety Features**
1. **Query Classification**: Detects unsafe queries (diagnosis, treatment, dosage, emergencies)
2. **Automatic Refusal**: Refuses unsafe queries with appropriate guidance
3. **Medical Disclaimer**: Required acceptance on first use
4. **Citation Validation**: Ensures all claims are cited
5. **Hallucination Detection**: Flags uncited strong claims

### **Refusal Categories**
- ❌ **Diagnosis Requests**: "Do I have diabetes?"
- ❌ **Treatment Advice**: "Should I take this medication?"
- ❌ **Dosage Questions**: "How much should I take?"
- ❌ **Emergency Situations**: "I'm having chest pain"

### **Compliance Note**
This system is **for educational and research purposes only**. It does not provide medical advice, diagnosis, or treatment recommendations. Always consult qualified healthcare professionals.

---

## 🤝 **Contributing**

Contributions are welcome! Please follow these guidelines:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Commit changes**: `git commit -m 'Add amazing feature'`
4. **Push to branch**: `git push origin feature/amazing-feature`
5. **Open Pull Request**

### **Areas for Contribution**
- [ ] Expand PubMed dataset to 50,000+ abstracts
- [ ] Add more medical APIs (FDA, WHO, etc.)
- [ ] Implement query expansion for complex terms
- [ ] Add multi-language support
- [ ] Improve evidence ranking algorithms
- [ ] Add user authentication
- [ ] Create mobile app

---

## 📝 **Roadmap**

### ** Advanced Features** (Planned)
- [ ] Multi-turn conversation memory
- [ ] Medical image analysis (X-rays, MRIs)
- [ ] Integration with EHR systems
- [ ] Advanced analytics dashboard
- [ ] Multi-user collaboration
- [ ] Email digest of saved research

## ⚠️ **Disclaimer**

**IMPORTANT: This application is for educational and research purposes only.**

This system:
- ❌ Does NOT provide medical advice, diagnosis, or treatment recommendations
- ❌ Does NOT replace consultation with qualified healthcare professionals  
- ❌ Should NOT be used for medical decision-making
- ❌ Is NOT FDA approved or HIPAA compliant

**In case of medical emergency, call 911 or your local emergency number immediately.**
