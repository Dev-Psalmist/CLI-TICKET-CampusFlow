# CampusFlow
### Intelligent Campus Support & Ticket Management System

**A smarter way to report, track, prioritise and resolve campus issues.**

CampusFlow is a Streamlit-based campus support and ticket management application. It gives students and campus users a central place to report problems, while helping support teams organise requests, identify urgent issues, monitor workloads and understand how effectively problems are being resolved.

The project combines a ticket-management workflow with AI-assisted ticket classification, troubleshooting guidance and a conversational campus support assistant. It is designed around common university support needs such as network access, hardware, software and campus facilities.

---

## Why CampusFlow?

Campus issues are often reported through scattered conversations, emails or informal channels. This makes it difficult to track requests, identify repeated problems, decide what needs attention first and understand which departments are overloaded.

CampusFlow brings those activities into one dashboard. Each issue can be recorded as a ticket, reviewed, assigned to a responsible department or staff member, tracked through its status and included in operational reports.

AI features help interpret ticket descriptions and suggest next steps. They support the workflow; they do not replace the judgement or actions of university support staff.

---

## Features

### 1. Campus Support Dashboard
A central overview of the support operation, including:
- Total, resolved and outstanding tickets.
- Ticket classification and priority indicators.
- Department workload and performance.
- Recent ticket activity.
- Ticket insight visualisations.
- Campus information, photo gallery and education/library news content.
- World clock and global events information panels.

### 2. Create Support Tickets
Users can submit a campus issue with a title and description. The application generates a ticket ID and stores the new ticket so it can be followed up through the management workflow.

### 3. AI Ticket Intelligence
The AI assistant can analyse a ticket description and recommend:
- A ticket category: Network, Hardware, Software, Facilities or Other.
- A priority: Critical, High, Medium or Low.
- The likely responsible department.
- The reason for the classification.
- A recommended action.

This helps support staff triage incoming issues more consistently. AI classifications should be reviewed by a human, especially for urgent or safety-related incidents.

### 4. Duplicate Ticket Detection
Before a new issue is submitted, CampusFlow can compare its title and description with existing tickets. It uses keyword overlap and wording similarity to identify possible duplicates, helping teams spot repeated reports of the same problem.

A similarity match is a warning for review, not proof that two reports describe the same incident.

### 5. Ticket Management
The management area supports operational follow-up, including:
- Viewing and filtering saved tickets.
- Reviewing individual ticket details.
- Updating ticket status.
- Assigning staff and monitoring staff workloads.
- Reviewing ticket priority, category and department information.

### 6. AI Troubleshooting Suggestions
Users and support staff can request structured troubleshooting guidance. Suggestions explain the likely issue, possible causes, practical steps, when to escalate and how recurrence may be prevented.

The assistant is instructed not to request passwords, bypass university security or claim that it has fixed an issue.

### 7. CampusFlow AI Chatbot
A conversational assistant for campus support questions. It can explain the ticket workflow, provide troubleshooting guidance and use recent saved ticket records as context when answering relevant questions.

The chatbot provides information and guidance; it does not independently create, assign, update or resolve tickets.

### 8. Reports and Analytics
The reports area turns saved tickets into operational summaries, including:
- Ticket totals and classification coverage.
- Open, in-progress and resolved ticket counts.
- Overall resolution rate.
- Ticket category and priority distributions.
- Department workload.
- Department-level resolution performance.

### 9. Campus Gallery and Information
The project includes a campus photograph gallery and supporting campus information sections. The gallery images are stored in the repository under `assets/campus/`.

### 10. Education and Library News
The news feed retrieves recent library-related headlines from Google News RSS feeds, including library services, books and publishing, reading and literacy, and digital or research libraries. Results are cached to reduce repeated requests.

---

## AI providers

The AI provider selector currently exposes these options:

| Provider | Purpose |
|---|---|
| Google Gemini | Ticket intelligence, troubleshooting and chatbot responses. |
| Groq | Alternative AI inference provider. |
| OpenRouter | Access to supported models through the OpenRouter API. |

The available model choices are configured in `ai_assistant.py`. A valid API key is required for whichever provider is selected. Model availability, rate limits and charges depend on the provider and the account being used.

### Environment variables

Configure the keys you intend to use:

| Variable | Used for |
|---|---|
| `GEMINI_API_KEY` | Google Gemini requests. |
| `GROQ_API_KEY` | Groq requests. |
| `OPENROUTER_API_KEY` | OpenRouter requests. |

For local development, create a `.env` file only if your environment loader or deployment setup is configured to load it. The application reads environment variables and Streamlit secrets; do not commit real API keys to GitHub.

For Streamlit Community Cloud or another Streamlit deployment that supports secrets, configure the required values in the app's secrets settings, for example:

```toml
GEMINI_API_KEY = "your-gemini-api-key"
GROQ_API_KEY = "your-groq-api-key"
OPENROUTER_API_KEY = "your-openrouter-api-key"
```

Only add the keys you actually use. Keep secrets private.

---

## Technology

- **Python** — application logic and supporting modules.
- **Streamlit** — interactive web application.
- **Plotly** — dashboard charts and visual analytics.
- **Google Gen AI SDK** — Gemini integration.
- **Groq SDK** — Groq integration.
- **HTTP/JSON APIs** — OpenRouter requests and external news retrieval.
- **JSON** — local ticket data storage.
- **pytest-compatible tests** — automated checks for selected application modules.

---

## Repository structure

The GitHub repository contains the application inside the `CampusFlow-Ticket-Creator/` directory.

```text
CLI-TICKET-CampusFlow/
├── README.md
├── tickets.json
└── CampusFlow-Ticket-Creator/
    ├── app.py                    # Main Streamlit web application
    ├── main.py                   # Original command-line ticket workflow
    ├── ai_assistant.py           # AI providers, intelligence, suggestions and chatbot
    ├── ticket_manager.py         # Ticket ID generation
    ├── storage.py                # JSON ticket storage
    ├── validation.py             # Input validation for CLI workflow
    ├── duplicate_detector.py     # Possible duplicate detection
    ├── historical_classifier.py  # AI classification of unclassified tickets
    ├── reports.py                # Dashboard and reporting calculations
    ├── news_feed.py              # Library and education news feeds
    ├── campus_gallery.py         # Campus photo gallery
    ├── assets/
    │   └── campus/               # Campus photographs and photo credits
    ├── tickets.json              # Application ticket data
    ├── requirements.txt          # Python dependencies
    ├── test_duplicates.py
    ├── test_intelligence.py
    └── test_reports.py
```

---

## Run CampusFlow locally

### Requirements
- Python 3.10 or later (Python 3.12 is suitable).
- pip.
- An internet connection for AI provider calls and live news retrieval.
- An API key for an AI provider if you want to use AI features.

### 1. Clone the repository

```bash
git clone https://github.com/Dev-Psalmist/CLI-TICKET-CampusFlow.git
cd CLI-TICKET-CampusFlow
```

### 2. Enter the application directory

The Streamlit application and its requirements file are inside the project subdirectory:

```bash
cd CampusFlow-Ticket-Creator
```

### 3. Create a virtual environment

Linux / macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 4. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 5. Configure an AI provider

Set the API key for the provider you want to use.

Linux / macOS example:

```bash
export GEMINI_API_KEY="your-gemini-api-key"
```

Windows PowerShell example:

```powershell
$env:GEMINI_API_KEY="your-gemini-api-key"
```

You can alternatively configure the key through Streamlit secrets in a supported deployment.

### 6. Start the application

From inside `CampusFlow-Ticket-Creator/`, run:

```bash
streamlit run app.py
```

Streamlit will display a local address, usually:

```text
http://localhost:8501
```

Open that address in your browser.

---

## Run the original command-line version

The repository also retains an introductory command-line ticket workflow in `main.py`. From inside `CampusFlow-Ticket-Creator/`:

```bash
python main.py
```

The command-line workflow collects and validates a ticket title and description, generates an ID, saves the ticket and requests AI suggestions. The full-featured user interface is the Streamlit application launched with `streamlit run app.py`.

---

## Data storage

CampusFlow currently stores ticket records in JSON files. The Streamlit app uses `storage.py`, which reads and writes `tickets.json` in its configured data directory. The default is the current working directory; deployments can set `CAMPUSFLOW_DATA_DIR` to choose a persistent data location.

For local use, make sure the application is started from the `CampusFlow-Ticket-Creator/` directory so its relative data and asset paths resolve as expected.

JSON storage is straightforward for a learning project, prototype or small single-instance deployment. For concurrent users, larger deployments or stronger data integrity requirements, a managed database would be a more suitable next step. Persistent disk or external storage must be configured on hosting platforms if ticket data needs to survive redeployments.

---

## Tests

From inside `CampusFlow-Ticket-Creator/`, install the dependencies and run the available tests:

```bash
pytest
```

The repository includes tests for duplicate detection, AI ticket intelligence and reporting calculations. These tests cover selected modules; they do not by themselves guarantee every page, external API integration or deployment configuration is error-free.

---

## Important notes and limitations

- AI-generated classifications, priorities and recommendations can be incorrect. Review them before acting.
- AI functionality depends on valid provider credentials, network access, provider availability and model limits.
- News articles depend on external RSS sources and internet connectivity; feeds may occasionally be unavailable or omit article images.
- Ticket records are stored as JSON rather than in a multi-user database. Configure persistent storage when deploying.
- The project repository includes sample ticket data. Treat it as demonstration data, not as a live institutional service record.
- Do not store passwords, payment information or unnecessary sensitive personal information in ticket descriptions.
- This repository does not establish that the application is officially operated, endorsed or supported by the University of Jos. It is a campus-support project with University of Jos-oriented campus content.

---

## Project goal

CampusFlow aims to make campus support more organised, transparent and responsive by connecting issue reporting, ticket tracking, AI-assisted triage, troubleshooting and performance reporting in one application.

**Report clearly. Prioritise intelligently. Resolve transparently.**

---

## License

No license file is currently included in this repository. Until a license is added, the default copyright rules apply; reuse and redistribution are not automatically granted.
