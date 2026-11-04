# JanSeva Connect – Digital E-Governance Web Portal

**An Independent Full-Stack College Mini-Project Inspired by Madhya Pradesh MP e-Services**  
*Curriculum Fulfillment: Unit 5 – Mini Projects: Evaluation of Local E-Governance Portals*

---

> **⚠️ Academic Demonstration Disclaimer:**  
> This project is an independent college mini-project built for educational evaluation. It is **not** an official government website, is **not** affiliated with the Government of Madhya Pradesh, and does not connect to actual government databases or external citizen verification servers. All seeded accounts, citizen records, applications, and certificates are fictional demonstration samples.

---

## 1. Project Overview & Objectives

**JanSeva Connect** provides a centralized, responsive, citizen-centric digital portal where users can:
- Explore public services across 12 government departments.
- Submit online applications with supporting document attachments (PDF, JPG, PNG up to 5 MB).
- Follow applications through a dynamic 4-stage visual timeline tracker.
- Verify simulated digital certificates and download high-resolution PDF certificates.
- Submit stakeholder feedback with 5-star ratings and ease-of-use metrics.
- Perform **Unit 5 College Syllabus Portal Evaluations** (evaluating portals like *MP-eServices*, *MPOnline*, *MP State Scholarship Portal*), rate 10 standardized criteria, manage student evaluation groups, conduct team discussions, and auto-generate a comprehensive 13-point structured PDF Evaluation Report for viva presentations.

---

## 2. Technology Stack & Architectural Decision

The user requested: **Frontend in HTML, CSS, JavaScript** and **Backend in Python**.

### Frontend
- **HTML5:** Semantic markup, accessible labels (`aria-*`), skip links, responsive viewport meta.
- **CSS3:** Modular design system using CSS custom properties (`variables.css`), responsive grids, modern flexbox, smooth transitions, and high-contrast accessibility mode (`body.large-text`).
- **JavaScript (ES6+):** Pure Vanilla JavaScript organized into modular ES6 modules (`api.js`, `auth.js`, `services.js`, `tracking.js`, `verify.js`, `evaluation.js`, `dashboard.js`, `i18n.js`, `app.js`). Zero heavy node-modules build steps required!
- **Internationalization (i18n):** Complete real-time bilingual switching between English and हिन्दी.

### Backend
- **Python 3.10+ & Flask:** Lightweight, robust, industry-standard REST API architecture.
- **SQLite 3:** Built directly into Python standard library with ACID transactions and foreign key integrity. Automatically initializes and seeds `instance/janseva.db` on first launch—zero external database server installation required.
- **Security & Sessions:** PBKDF2/Werkzeug salted password hashing and time-limited signed cryptographic bearer tokens via `itsdangerous`.
- **PDF Generation:** Pure Python standard library implementation (`pdf_service.py`) generating PDF 1.4 documents with Helvetica typography. Runs without third-party binary C-dependencies or external render engines.

---

## 3. Project Folder Structure

Every module in this project has been strictly separated and organized for clean architecture:

```text
janseva-connect/
│
├── backend/                       # Python Backend Modules
│   ├── config.py                  # Environment paths, upload limits, secret keys
│   ├── database.py                # SQLite schema, tables, indices, and sample seed data
│   ├── auth.py                    # Token generation, session decorator, password verification
│   ├── pdf_service.py             # Pure Python PDF engine for Certificates & Unit 5 Reports
│   └── routes/                    # Modular Flask Route Blueprints
│       ├── __init__.py
│       ├── auth_routes.py         # Registration, login, profile endpoints (/api/auth/*)
│       ├── service_routes.py      # Directory search, category filters, CRUD (/api/services/*)
│       ├── application_routes.py  # Application submissions, tracking, file uploads
│       ├── certificate_routes.py  # Simulated verification and PDF certificate download
│       ├── evaluation_routes.py   # Unit 5 evaluations, rubric scoring, groups & PDF report
│       ├── feedback_routes.py     # Citizen ratings and feedback summaries (/api/feedback)
│       ├── announcement_routes.py # Homepage public notices & alerts (/api/announcements)
│       └── admin_routes.py        # User control (RBAC), analytics, metrics (/api/admin/*)
│
├── static/                        # Frontend Static Assets
│   ├── css/                       # Modular CSS Design System
│   │   ├── variables.css          # Government color tokens, typography, radii, shadows
│   │   ├── base.css               # Typography, resets, buttons, inputs, status pills
│   │   ├── layout.css             # Utility bar, sticky header, mobile drawer, footer
│   │   ├── components.css         # Hero search, category cards, service cards, modals, toast
│   │   ├── dashboard.css          # Citizen, Officer, and Administrator dashboard tables
│   │   ├── evaluation.css         # Unit 5 criteria rubric, SWOT cards, discussion feed
│   │   └── styles.css             # Master CSS importing all modular stylesheets
│   │
│   └── js/                        # Modular Frontend JavaScript
│       ├── i18n.js                # Full English / Hindi dictionary and dynamic translator
│       ├── state.js               # Global state container, toast helper, date formatters
│       ├── api.js                 # Fetch REST client with Bearer authorization
│       ├── auth.js                # Sign in, registration, session restore, profile editing
│       ├── services.js            # Directory search, filters, pagination, application modal
│       ├── tracking.js            # 4-stage visual status timeline tracking engine
│       ├── verify.js              # Certificate lookup and PDF download trigger
│       ├── evaluation.js          # 10 criteria rating, SWOT inputs, group workspace & PDF
│       ├── feedback.js            # 5-star interactive rating and testimonials
│       ├── dashboard.js           # Citizen hub, Officer review queue, Admin RBAC & analytics
│       └── app.js                 # Event routing, DOMContentLoaded bootstrap, accessibility
│
├── templates/
│   └── index.html                 # Complete, accessible, semantic Single-Page Application
│
├── instance/                      # Created on launch; holds SQLite database (janseva.db)
├── uploads/                       # Stores randomized document uploads (PDF, JPG, PNG)
├── app.py                         # Application factory and Flask runner
├── requirements.txt               # Backend dependencies (Flask, python-dotenv)
├── .env.example                   # Environment variable template
├── .gitignore                     # Git exclusions (.venv, instance/, uploads/, etc.)
└── README.md                      # Comprehensive project documentation
```

---

## 4. Permanent Cyber-Gov Dark Mode Design System

As per user requirements, **JanSeva Connect is permanently styled in a modern, sleek Cyber-Gov Dark Mode theme**. Light mode has been completely replaced with a dark aesthetic designed for high contrast and visual appeal:

| Color Role | Hex Code | Visual Preview / Usage |
|---|---|---|
| **Deep Space Main BG** | `#070B19` | Deepest midnight background for body and viewport |
| **Secondary Dark BG** | `#0D1527` | Alternate section background, cards container |
| **Card Surface Surface** | `#131E36` | Elevated cards, dialog surfaces, panels |
| **Card Hover Surface** | `#182747` | Subtle glowing card hover elevation |
| **Input Background** | `#0B1224` | Form inputs, dropdowns, and search controls |
| **Crisp White Text** | `#F8FAFC` | Primary headings, brand names, button text |
| **High-Contrast Body** | `#CBD5E1` | Primary readable paragraphs, table cells |
| **Muted Slate Text** | `#94A3B8` | Subtitles, labels, metadata dates |
| **Electric Sky Blue** | `#38BDF8` | Primary interactive buttons, focus rings, links |
| **Radiant Gold Saffron**| `#F59E0B` | Status alerts, pending tags, star ratings |
| **Emerald Mint Teal** | `#10B981` | Approved pills, verified seal, live engine dot |
| **Coral Error Red** | `#EF4444` | Rejections, validation error messages |

---

## 5. How to Run on Windows PowerShell

### Prerequisites
- Python 3.10 or higher installed (`python --version`)

### Step-by-Step Commands

1. Open **Windows PowerShell** and navigate to your project directory:
   ```powershell
   cd "C:\Users\hp\Desktop\New folder"
   ```

2. *(Optional)* Create and activate a Python virtual environment:
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

3. Install required Python packages:
   ```powershell
   python -m pip install -r requirements.txt
   ```

4. Create environment configuration (or copy example):
   ```powershell
   Copy-Item .env.example .env
   ```

5. Run the application:
   ```powershell
   python app.py
   ```

6. Open your browser and navigate to:  
   👉 **http://127.0.0.1:5000**

To stop the server, press `Ctrl + C` in the PowerShell window.

---

## 6. Demo Accounts & Credentials

For quick testing and grading, pre-configured demo accounts are seeded into SQLite:

| Role | Email Address | Password | Permissions & Available Features |
|---|---|---|---|
| **Citizen** | `citizen@janseva.demo` | `Citizen@123` | Submit applications, upload documents, track status, download demo certificates, update profile. |
| **Department Officer** | `officer@janseva.demo` | `Officer@123` | Access Department Queue, inspect citizen uploaded files, update application status with remarks, issue approvals. |
| **Administrator** | `admin@janseva.demo` | `Admin@123` | Manage user roles (RBAC), activate/deactivate accounts, publish directory services, broadcast notices, review feedback & analytics. |

> **Pro Tip:** In the Login Modal, click the one-touch **Citizen**, **Officer**, or **Admin** buttons to automatically fill and log in with sample credentials!

---

## 7. Key Features Implemented

### A. Citizen Service Directory
- 17 realistic demonstration services across 12 public departments.
- Live keyword search with instant debouncing.
- Dropdown filters for Category, Department, and alphabetical sorting (A-Z / Z-A).
- Pagination controls with total matching record count.
- Service details modal showing prerequisite criteria, fees, processing turnaround, and document checklist.

### B. Online Application & Document Uploads
- Multi-step modal flow: Service selection → applicant information → local document upload (PDF, JPG, PNG up to 5 MB per file) → declaration checkbox → submission.
- Generates a unique tracking ID (e.g., `JS-2026-10482`).

### C. Live Application Tracking (4-Stage Visual Timeline)
- Public tracking requiring Application ID + registered Email/Mobile.
- 4-stage visual timeline:
  1. *Application Submitted*
  2. *Under Review*
  3. *Document Verification*
  4. *Approved / Rejected*
- Displays department officer remarks, audit history timestamps, and certificate download link upon approval.

### D. Simulated Certificate Verification
- Verifies certificate numbers (e.g., `JSC-2026-00831`).
- Displays certificate badge with masked applicant name (`A•••• D••••`) for privacy compliance.
- Download verified demonstration certificate as a formatted PDF.

### E. College Syllabus Unit 5: E-Governance Evaluation Module
- **Portal Selection:** MP-eServices, MPOnline, MP-eDistrict, MP State Scholarship Portal, etc.
- **10 Standardized Evaluation Criteria (1 to 5 ratings):**
  1. User Friendliness
  2. Navigation and Interface
  3. Accessibility
  4. Service Availability
  5. Application Process
  6. Application Tracking
  7. Information Accuracy
  8. Security and Privacy
  9. Mobile Responsiveness
  10. Overall User Experience
- **SWOT Analysis:** Strengths, Limitations, Technical Issues, User Difficulties.
- **Improvement Potential:** Suggested Improvements, Priority (Low/Medium/High), Expected Benefits, Technical Recommendations.
- **Structured 13-Point PDF Evaluation Report:** Generates a formatted academic PDF report directly from the browser via `/api/evaluations/<id>/report.pdf`.
- **Student Group Collaboration:** Create groups, assign leader, list members, set evaluation tasks, and track percentage progress.
- **Team Discussion Board:** Real-time in-app discussion feed for group observations.
- **Presentation Support Desk:** Dedicated workspace to record viva presentation titles, team members, summary, and key findings.

### F. Accessibility & Internationalization (i18n)
- **Bilingual Interface:** Real-time toggle between English and हिन्दी.
- **Text Size Adjustment:** A- / A / A+ accessibility buttons.
- Fully responsive across mobile, tablet, and desktop viewports.

---

## 8. REST API Reference

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `GET` | `/api/health` | Service health status | Public |
| `GET` | `/api/services` | Search & filter services | Public |
| `GET` | `/api/services/<id>` | Single service details | Public |
| `POST` | `/api/services` | Add new service | Admin |
| `PUT` | `/api/services/<id>` | Update service / toggle | Admin |
| `GET` | `/api/categories` | Categories and counts | Public |
| `GET` | `/api/departments` | Distinct departments list | Public |
| `POST` | `/api/auth/register` | Register new citizen | Public |
| `POST` | `/api/auth/login` | Sign in & get bearer token | Public |
| `GET` | `/api/auth/me` | Fetch active user profile | Bearer Token |
| `PATCH` | `/api/auth/profile` | Update profile information | Bearer Token |
| `POST` | `/api/applications` | Submit application (multipart) | Citizen / Any |
| `GET` | `/api/applications/my` | View logged-in user applications | Bearer Token |
| `POST` | `/api/applications/track` | Public tracking lookup | Public |
| `GET` | `/api/applications` | Officer application queue | Officer / Admin |
| `PATCH` | `/api/applications/<id>/status` | Update status & remarks | Officer / Admin |
| `GET` | `/api/certificates/verify/<num>` | Verify certificate | Public |
| `GET` | `/api/certificates/<num>/download`| Download certificate PDF | Public |
| `GET` | `/api/evaluations` | List portal evaluations | Public |
| `POST` | `/api/evaluations` | Save new portal evaluation | Bearer Token |
| `GET` | `/api/evaluations/<id>/report.pdf`| Download Unit 5 PDF report | Public |
| `GET` | `/api/evaluation-groups` | List student groups | Bearer Token |
| `POST` | `/api/evaluation-groups` | Create student group | Bearer Token |
| `GET` | `/api/feedback` | Feedback summary & testimonials | Public |
| `POST` | `/api/feedback` | Submit citizen feedback | Public |
| `GET` | `/api/announcements` | Active homepage notices | Public |
| `POST` | `/api/announcements` | Publish new notice | Admin |
| `GET` | `/api/admin/users` | User management list | Admin |
| `PATCH` | `/api/admin/users/<id>` | Change user role or active state | Admin |
| `GET` | `/api/admin/analytics` | Category & status statistics | Admin |

---

## 9. Testing & Grading Workflow

To verify all features during your college viva or evaluation:

1. **Test Public Service Discovery:**
   - Search for "income" in the hero search bar; verify smooth filtering and service cards display.
   - Switch language to **हिन्दी** in the top utility bar; observe interface labels switching dynamically.
   - Test font size increase with the **A+** button.

2. **Test Citizen Journey:**
   - Click **Log In** and choose the **Citizen** demo account.
   - Click **Apply Now** on *Income Certificate*. Fill the form and attach a sample image/PDF.
   - Note the generated Application ID (e.g., `JS-2026-XXXXXX`).
   - Go to **Track Application**, enter the ID and `citizen@janseva.demo`, and inspect the live status timeline.

3. **Test Department Officer Workflow:**
   - Sign out and log in with the **Officer** demo account (`officer@janseva.demo`).
   - In the dashboard, navigate to the **Department Officer Queue**.
   - Locate the submitted application, click **Review & Update Status**, download the uploaded document proof, change status to **Approved**, and enter remarks.
   - Save decision; notice the automated issuance of a demonstration certificate.

4. **Test Certificate Verification:**
   - Navigate to **Verify Certificate**, enter `JSC-2026-00831` (or the newly generated number), and click **Verify Certificate**.
   - Click **Download Demo Certificate (PDF)** and inspect the generated PDF document.

5. **Test Unit 5 College Syllabus Evaluation Module:**
   - Scroll to **E-Governance Evaluation**.
   - Select *MP-eServices*, rate all 10 criteria (1 to 5), input strengths and limitations, and click **Save Evaluation & Download Report (PDF)**.
   - Confirm that a 13-point structured PDF evaluation report opens automatically.
   - Click **Form Student Team** to create a student research group, open the **Team Workspace**, and add an observation to the **Discussion Board**.

6. **Test Administrator Operations:**
   - Sign in as **Admin** (`admin@janseva.demo`).
   - Inspect the **User Accounts (RBAC)** tab to adjust roles or deactivate accounts.
   - Publish a new announcement and verify it appears on the homepage notice board.
   - Review category-wise and status-wise distribution bars in the **Portal Analytics** tab.

---

## 10. Resetting Demo Records

To restore fresh demo data at any time:
1. Stop the server (`Ctrl + C`).
2. Delete the `instance/janseva.db` file.
3. Restart the server (`python app.py`). The database schema and fictional demo records will be re-seeded automatically.
"# online_service" 
