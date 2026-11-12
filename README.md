# MP Suvidha – Madhya Pradesh Digital Services Portal

**One Portal. Multiple Services.**
*An independent digital service information and application demonstration platform for Madhya Pradesh.*

---

> **⚠️ Independent Demonstration Portal Disclaimer:**
> MP Suvidha is an independent demonstration and information portal designed to showcase citizen-friendly public service discovery and digital application tracking. It is **not** an official Government of Madhya Pradesh website, is **not** affiliated with the Government of Madhya Pradesh or any of its departments, and does not use official government emblems. All demonstration records, certificates, and sample applications are simulated.

---

## 1. Portal Overview

**MP Suvidha** provides a unified, modern, accessible digital services portal where citizens can:
- **Discover Services:** Browse across 12 public service categories covering revenue, municipal, education, agriculture, social security, and business.
- **Understand Requirements:** Review eligibility criteria, required documents checklists, estimated processing times, and demonstration fee schedules.
- **Online Applications:** Submit applications with multi-file uploads (PDF, JPG, PNG up to 5 MB per document).
- **Stage-by-Stage Tracking:** Follow live application progress (Submitted → Under Review → Verification → Approved/Rejected) using unique Application IDs (e.g., `MPS-2026-10482`).
- **Certificate Verification:** Verify demonstration certificates by Certificate Number (e.g., `MPS-CERT-2026-09831`) and download branded PDF certificates.
- **Complete Bilingual Interface:** Instant switching between English and हिन्दी with full interface translation.
- **Role-Based Access Control:** Dedicated dashboards for Citizens, Department Officers, and Administrators.

---

## 2. Technology Stack

- **Frontend:** HTML5, Modern CSS3 (Centralized Design System with MP Suvidha Brand Palette), Vanilla JavaScript (ES6 Modules).
- **Backend:** Python 3 & Flask REST APIs (Modular Flask Blueprints).
- **Database:** SQLite 3 (Auto-seeded with 12 MP categories and essential services).
- **Authentication & Security:** PBKDF2 password hashing, URLSafeTimedSerializer signed bearer tokens.
- **PDF Generation:** Python standard-library PDF 1.4 generation service.

---

## 3. Brand Color System

MP Suvidha uses a clean, light, professional design system:

| Element | Color Name | Hex Code |
| :--- | :--- | :--- |
| Primary Branding | Primary Navy Blue | `#123B63` |
| Primary Buttons & Links | Royal Blue | `#1769AA` |
| Highlights & Accents | Saffron Orange | `#F4A340` |
| Success & Verification | Teal Green | `#168C83` |
| Main Page Background | Light Background | `#F5F8FC` |
| Card & Container Surfaces | Pure White | `#FFFFFF` |
| Headings | Dark Slate | `#1F2937` |
| Body Text | Medium Slate | `#475569` |
| Borders & Dividers | Border Grey | `#E2E8F0` |

---

## 4. Quick Start & How to Run

### Method 1: Double-Click Launcher (Easiest)
Simply double-click the **`run.bat`** file in the project folder.

### Method 2: Running via Terminal / PowerShell
```powershell
# 1. Navigate to the project directory
cd c:\Users\hp\OneDrive\Desktop\online_service

# 2. Run with Python
python app.py
```

### Method 3: Running via Command Prompt (CMD)
```cmd
cd /d "c:\Users\hp\OneDrive\Desktop\online_service"
python app.py
```

Open your web browser and navigate to:  
👉 **http://127.0.0.1:5000**

---

## 5. Demonstration Accounts

The portal includes ready-to-test demonstration accounts:

| Role | Email Address | Password | Department / Description |
| :--- | :--- | :--- | :--- |
| **Citizen** | `citizen@mpsuvidha.demo` | `Citizen@123` | General Citizen: Submit applications, track status, download certificates |
| **Officer (Revenue)** | `officer@mpsuvidha.demo` | `Officer@123` | Revenue Department: Department-restricted application review and approval |
| **Officer (Municipal)** | `officer_municipal@mpsuvidha.demo` | `Officer@123` | Municipal Services: Department-restricted civic applications review |
| **Administrator** | `admin@mpsuvidha.demo` | `Admin@123` | General Administration: Full governance, services, categories, users, analytics |

---

## 6. Sample Application IDs for Testing

- **Application Tracking:**  
  - ID: `MPS-2026-10482` | Contact: `citizen@mpsuvidha.demo` (Status: *Submitted*)
  - ID: `MPS-2026-10219` | Contact: `citizen@mpsuvidha.demo` (Status: *Under Review*)
  - ID: `MPS-2026-09831` | Contact: `citizen@mpsuvidha.demo` (Status: *Approved*)

- **Certificate Verification:**  
  - Number: `MPS-CERT-2026-09831` (Demonstration Domicile Certificate)
