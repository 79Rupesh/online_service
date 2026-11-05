"""Database connection and initialization module for SQLite.
MP Suvidha: Madhya Pradesh Digital Services Portal.
"""
import json
import sqlite3
import uuid
from datetime import datetime, timezone
from werkzeug.security import generate_password_hash
from backend.config import Config

def now_iso() -> str:
    """Returns the current UTC timestamp formatted as ISO-8601 string."""
    return datetime.now(timezone.utc).isoformat(timespec="seconds")

class ClosingConnection(sqlite3.Connection):
    """Commits or rolls back transaction and closes the SQLite connection safely."""
    def __exit__(self, exc_type, exc_value, traceback):
        try:
            return super().__exit__(exc_type, exc_value, traceback)
        finally:
            self.close()

def connect_db() -> sqlite3.Connection:
    """Returns a new SQLite connection with Row factory and foreign keys enabled."""
    conn = sqlite3.connect(Config.DB_PATH, factory=ClosingConnection)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def row_dict(row: sqlite3.Row | None) -> dict | None:
    """Converts a sqlite3.Row into a Python dictionary."""
    return dict(row) if row is not None else None

def init_db() -> None:
    """Initializes tables and seeds initial demo data if tables are empty."""
    with connect_db() as db:
        db.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                mobile TEXT NOT NULL DEFAULT '',
                password_hash TEXT NOT NULL,
                address TEXT NOT NULL DEFAULT '',
                role TEXT NOT NULL DEFAULT 'citizen',
                department TEXT NOT NULL DEFAULT '',
                active INTEGER NOT NULL DEFAULT 1,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS categories (
                name TEXT PRIMARY KEY,
                name_hi TEXT NOT NULL DEFAULT '',
                icon TEXT NOT NULL DEFAULT '📁',
                description TEXT NOT NULL DEFAULT '',
                description_hi TEXT NOT NULL DEFAULT ''
            );

            CREATE TABLE IF NOT EXISTS services (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                name_hi TEXT NOT NULL DEFAULT '',
                department TEXT NOT NULL,
                department_hi TEXT NOT NULL DEFAULT '',
                category TEXT NOT NULL,
                description TEXT NOT NULL,
                description_hi TEXT NOT NULL DEFAULT '',
                eligibility TEXT NOT NULL,
                eligibility_hi TEXT NOT NULL DEFAULT '',
                documents TEXT NOT NULL,
                documents_hi TEXT NOT NULL DEFAULT '[]',
                fee TEXT NOT NULL DEFAULT 'Free',
                fee_hi TEXT NOT NULL DEFAULT 'निःशुल्क',
                processing_time TEXT NOT NULL,
                processing_time_hi TEXT NOT NULL DEFAULT '',
                instructions TEXT NOT NULL DEFAULT '',
                instructions_hi TEXT NOT NULL DEFAULT '',
                availability TEXT NOT NULL DEFAULT 'Available',
                application_type TEXT NOT NULL DEFAULT 'Online',
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS applications (
                id TEXT PRIMARY KEY,
                citizen_id INTEGER NOT NULL REFERENCES users(id),
                service_id TEXT NOT NULL REFERENCES services(id),
                applicant TEXT NOT NULL,
                documents TEXT NOT NULL DEFAULT '[]',
                submitted_at TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'Submitted',
                department TEXT NOT NULL,
                officer_remarks TEXT NOT NULL DEFAULT '',
                updated_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS application_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                application_id TEXT NOT NULL REFERENCES applications(id),
                status TEXT NOT NULL,
                remarks TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS announcements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                title_hi TEXT NOT NULL DEFAULT '',
                body TEXT NOT NULL,
                body_hi TEXT NOT NULL DEFAULT '',
                kind TEXT NOT NULL DEFAULT 'Notice',
                published_at TEXT NOT NULL,
                active INTEGER NOT NULL DEFAULT 1
            );

            CREATE TABLE IF NOT EXISTS certificates (
                number TEXT PRIMARY KEY,
                application_id TEXT NOT NULL UNIQUE REFERENCES applications(id),
                applicant_name TEXT NOT NULL,
                service_name TEXT NOT NULL,
                issue_date TEXT NOT NULL,
                department TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'Valid'
            );

            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL DEFAULT 'Anonymous',
                stakeholder TEXT NOT NULL DEFAULT 'Citizen',
                portal_name TEXT NOT NULL DEFAULT 'MP Suvidha',
                rating INTEGER NOT NULL,
                ease_rating INTEGER NOT NULL,
                service_rating INTEGER NOT NULL,
                suggestions TEXT NOT NULL,
                complaint TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS evaluations (
                id TEXT PRIMARY KEY,
                portal_name TEXT NOT NULL,
                portal_url TEXT NOT NULL DEFAULT '',
                department TEXT NOT NULL DEFAULT '',
                description TEXT NOT NULL DEFAULT '',
                evaluation_date TEXT NOT NULL,
                evaluator_group TEXT NOT NULL DEFAULT '',
                scores TEXT NOT NULL,
                strengths TEXT NOT NULL DEFAULT '',
                limitations TEXT NOT NULL DEFAULT '',
                technical_issues TEXT NOT NULL DEFAULT '',
                user_difficulties TEXT NOT NULL DEFAULT '',
                improvements TEXT NOT NULL DEFAULT '',
                priority TEXT NOT NULL DEFAULT 'Medium',
                expected_benefits TEXT NOT NULL DEFAULT '',
                recommendations TEXT NOT NULL DEFAULT '',
                evaluator TEXT NOT NULL,
                created_by INTEGER REFERENCES users(id),
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS evaluation_groups (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                leader TEXT NOT NULL,
                members TEXT NOT NULL DEFAULT '[]',
                tasks TEXT NOT NULL DEFAULT '[]',
                progress INTEGER NOT NULL DEFAULT 0,
                created_by INTEGER REFERENCES users(id),
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS evaluation_discussions (
                id TEXT PRIMARY KEY,
                group_id TEXT NOT NULL REFERENCES evaluation_groups(id) ON DELETE CASCADE,
                user_name TEXT NOT NULL,
                topic TEXT NOT NULL,
                message TEXT NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS evaluation_presentations (
                id TEXT PRIMARY KEY,
                group_id TEXT NOT NULL UNIQUE REFERENCES evaluation_groups(id) ON DELETE CASCADE,
                title TEXT NOT NULL,
                team_members TEXT NOT NULL DEFAULT '',
                summary TEXT NOT NULL DEFAULT '',
                key_findings TEXT NOT NULL DEFAULT '',
                recommendations TEXT NOT NULL DEFAULT '',
                updated_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL REFERENCES users(id),
                title TEXT NOT NULL,
                body TEXT NOT NULL,
                read INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL
            );

            CREATE INDEX IF NOT EXISTS idx_apps_citizen ON applications(citizen_id);
            CREATE INDEX IF NOT EXISTS idx_apps_status ON applications(status);
            """
        )
        seed_db(db)

def seed_db(db: sqlite3.Connection) -> None:
    """Populates the database with MP Suvidha categories, services, demo accounts, and notices."""
    
    # 12 Core Citizen Categories (Bilingual)
    categories = [
        ("Education and Scholarship", "शिक्षा एवं छात्रवृत्ति", "🎓", "Educational schemes, scholarships, and student registration services.", "शैक्षणिक योजनाएँ, छात्रवृत्ति एवं छात्र पंजीयन सेवाएँ।"),
        ("Health and Welfare", "स्वास्थ्य एवं जनकल्याण", "🏥", "Healthcare programs, health insurance, and public welfare assistance.", "स्वास्थ्य सेवाएँ, स्वास्थ्य बीमा एवं जनकल्याण सहायता।"),
        ("Certificates and Documents", "प्रमाणपत्र एवं दस्तावेज़", "📜", "Income, domicile, caste, birth and government certificates.", "आय, मूल निवासी, जाति, जन्म एवं अन्य आधिकारिक प्रमाणपत्र।"),
        ("Agriculture and Farmers", "कृषि एवं किसान कल्याण", "🌾", "Farmer crop compensation, subsidies, and agricultural schemes.", "फसल क्षतिपूर्ति, कृषि अनुदान एवं किसान कल्याण योजनाएँ।"),
        ("Employment and Skill Development", "रोज़गार एवं कौशल विकास", "💼", "Employment exchange registration, vocational training, and youth programs.", "रोज़गार पंजीयन, कौशल प्रशिक्षण एवं युवा रोज़गार योजनाएँ।"),
        ("Social Security and Pension", "सामाजिक सुरक्षा एवं पेंशन", "🛡️", "Old age, widow, disability pensions and social security benefits.", "वृद्धावस्था, विधवा, दिव्यांग पेंशन एवं सामाजिक सहायता योजनाएँ।"),
        ("Revenue and Land Records", "राजस्व एवं भू-अभिलेख", "🏛️", "Land records, Khasra-Khatauni, mutation, and revenue services.", "भू-अभिलेख, खसरा-खतौनी, नामांतरण एवं राजस्व सेवाएँ।"),
        ("Transport Services", "परिवहन सेवाएँ", "🚗", "Driving licenses, vehicle permits, and road safety services.", "ड्राइविंग लाइसेंस, वाहन परमिट एवं परिवहन विभाग की सेवाएँ।"),
        ("Municipal Services", "नगर निगम एवं नागरिक सेवाएँ", "🏘️", "Water connections, property tax, sanitation, and civic utility services.", "नल कनेक्शन, सम्पत्ति कर, स्वच्छता एवं शहरी निकाय सेवाएँ।"),
        ("Business and Entrepreneurship", "व्यापार एवं उद्योग संवर्धन", "🏢", "MSME support, trade licenses, single-window enterprise clearance.", "एमएसएमई सहायता, व्यापार लाइसेंस एवं एकल खिड़की स्वीकृति।"),
        ("Rural Development", "ग्रामीण विकास एवं पंचायती राज", "🏡", "Panchayat schemes, rural housing, and village infrastructure support.", "पंचायत योजनाएँ, ग्रामीण आवास एवं ग्रामीण बुनियादी ढाँचा।"),
        ("Other Public Services", "अन्य लोक सेवाएँ", "📋", "Citizen grievances, RTI information, and general public administration.", "नागरिक शिकायतें, आरटीआई सूचना एवं सामान्य लोक सेवाएँ।"),
    ]
    
    for cat in categories:
        db.execute(
            """INSERT INTO categories(name, name_hi, icon, description, description_hi)
               VALUES(?, ?, ?, ?, ?)
               ON CONFLICT(name) DO UPDATE SET
               name_hi=excluded.name_hi,
               icon=excluded.icon,
               description=excluded.description,
               description_hi=excluded.description_hi""",
            cat
        )

    # Core Citizen Services of Madhya Pradesh
    services = [
        (
            "SVC-001",
            "Income Certificate",
            "आय प्रमाण पत्र",
            "Revenue Department",
            "राजस्व विभाग",
            "Certificates and Documents",
            "Official certificate verifying household annual income for availing government subsidies, scholarships, and schemes.",
            "सरकारी योजनाओं, छात्रवृत्ति एवं रियायतों हेतु परिवार की वार्षिक आय प्रमाणित करने वाला आधिकारिक प्रमाण पत्र।",
            "Resident of Madhya Pradesh with valid proof of identity and income declaration.",
            "मध्य प्रदेश का मूल निवासी जिसके पास वैध पहचान पत्र एवं आय स्व-घोषणा हो।",
            ["Aadhaar Card", "Samagra ID", "Income Self-Declaration Affidavit", "Electricity Bill / Address Proof"],
            ["आधार कार्ड", "समग्र आईडी", "आय स्व-घोषणा शपथ पत्र", "बिजली बिल / निवास प्रमाण"],
            "₹20",
            "₹२०",
            "7 working days",
            "७ कार्य दिवस",
            "Ensure uploaded document copies are clearly legible. This is an informational demonstration workflow.",
            "कृपया सुनिश्चित करें कि अपलोड किए गए दस्तावेज़ स्पष्ट हैं। यह एक प्रदर्शन प्रक्रिया है।"
        ),
        (
            "SVC-002",
            "Caste Certificate (SC/ST/OBC)",
            "जाति प्रमाण पत्र (अ.जा./अ.ज.जा./अन्य पिछड़ा वर्ग)",
            "Revenue Department",
            "राजस्व विभाग",
            "Certificates and Documents",
            "Official certification of caste category for educational reservations, government schemes, and employment benefits.",
            "शैक्षणिक आरक्षण, सरकारी योजनाओं एवं रोज़गार लाभ हेतु जाति श्रेणी का आधिकारिक प्रमाण पत्र।",
            "Belonging to notified SC, ST, or OBC communities residing in Madhya Pradesh.",
            "मध्य प्रदेश के अधिसूचित अनुसूचित जाति, जनजाति अथवा अन्य पिछड़ा वर्ग से संबंधित निवासी।",
            ["Aadhaar Card", "Samagra ID", "Father's Caste Record / 1950/1984 Land Proof", "School Marksheet / Transfer Certificate"],
            ["आधार कार्ड", "समग्र आईडी", "पिता का जाति प्रमाण / भू-अभिलेख", "स्कूल अंकसूची / स्थानांतरण प्रमाण पत्र"],
            "₹20",
            "₹२०",
            "15 working days",
            "१५ कार्य दिवस",
            "Upload valid parental proof or historical land record verifying residency since relevant cutoff year.",
            "कटऑफ वर्ष से निवास प्रमाणित करने हेतु पिता का वैध प्रमाण पत्र या पैतृक भू-अभिलेख अपलोड करें।"
        ),
        (
            "SVC-003",
            "Domicile / Local Resident Certificate",
            "मूल निवासी प्रमाण पत्र",
            "Revenue Department",
            "राजस्व विभाग",
            "Certificates and Documents",
            "Certificate establishing permanent residency in Madhya Pradesh for state employment and academic quota.",
            "राज्य में रोज़गार एवं शैक्षणिक प्रवेश में स्थानीय आरक्षण हेतु मध्य प्रदेश का स्थायी मूल निवासी प्रमाण पत्र।",
            "Continuous residence in Madhya Pradesh for at least 10 years or born to permanent residents.",
            "मध्य प्रदेश में न्यूनतम १० वर्षों से निरंतर निवास अथवा मूल निवासी माता-पिता की संतान।",
            ["Aadhaar Card", "Samagra ID", "Proof of continuous residence (10-year education/voter card/ration card)", "Passport Photograph"],
            ["आधार कार्ड", "समग्र आईडी", "१० वर्ष का निरंतर निवास प्रमाण (शिक्षा/मतदाता कार्ड/राशन कार्ड)", "पासपोर्ट साइज़ फोटो"],
            "₹20",
            "₹२०",
            "7 working days",
            "७ कार्य दिवस",
            "Check that applicant name and address match across all submitted supporting records.",
            "जाँच लें कि आवेदक का नाम और पता सभी संलग्न प्रमाण पत्रों में एक समान हो।"
        ),
        (
            "SVC-004",
            "Birth Certificate Registration / Copy",
            "जन्म प्रमाण पत्र पंजीयन / प्रति",
            "Municipal Services",
            "नगर निगम एवं नगरीय प्रशासन",
            "Certificates and Documents",
            "Application for issuance or duplicate copy of an official birth certificate registered with municipal authorities.",
            "शहरी अथवा ग्रामीण निकाय में पंजीकृत जन्म प्रमाण पत्र की नवीन अथवा द्वितीयक प्रति प्राप्त करने हेतु आवेदन।",
            "Child born within Madhya Pradesh municipal corporation or rural local body jurisdiction.",
            "मध्य प्रदेश के किसी भी नगर निगम अथवा ग्राम पंचायत क्षेत्र में जन्मा बालक/बालिका।",
            ["Hospital Discharge Summary / Birth Slip", "Mother's and Father's Aadhaar Cards", "Samagra Family ID"],
            ["अस्पताल डिस्चार्ज स्लिप / जन्म सूचना प्रपत्र", "माता एवं पिता का आधार कार्ड", "समग्र परिवार आईडी"],
            "Free",
            "निःशुल्क",
            "5-7 working days",
            "५-७ कार्य दिवस",
            "Provide accurate date, time, and institution name as noted in medical hospital discharge reports.",
            "अस्पताल के रिकॉर्ड के अनुसार सही जन्म तिथि, समय एवं संस्था का नाम दर्ज करें।"
        ),
        (
            "SVC-005",
            "Post-Matric Student Scholarship",
            "पोस्ट-मैट्रिक छात्रवृत्ति योजना",
            "Education and Scholarship",
            "उच्च शिक्षा एवं जनजातीय कार्य विभाग",
            "Education and Scholarship",
            "State financial scholarship scheme providing tuition and maintenance allowance for post-secondary education.",
            "कक्षा ११वीं से उच्च शिक्षा में अध्ययनरत पात्र विद्यार्थियों हेतु शिक्षण शुल्क एवं निर्वाह भत्ता छात्रवृत्ति योजना।",
            "Enrolled student in recognized college/university in MP with family income within defined scheme threshold.",
            "मध्य प्रदेश में मान्यता प्राप्त महाविद्यालय/विश्वविद्यालय में नियमित अध्ययनरत छात्र, जिनकी पारिवारिक आय निर्धारित सीमा में हो।",
            ["Previous Year Marksheet", "College Admission Fee Receipt & Student ID", "Income Certificate", "Aadhaar Linked Bank Passbook"],
            ["गत वर्ष की अंकसूची", "महाविद्यालय प्रवेश रसीद एवं छात्र पहचान पत्र", "वैध आय प्रमाण पत्र", "आधार लिंक बैंक पासबुक"],
            "Free",
            "निःशुल्क",
            "20-30 working days",
            "२०-३० कार्य दिवस",
            "Ensure bank account is seeded with Aadhaar and Direct Benefit Transfer (DBT) is active.",
            "सुनिश्चित करें कि आपका बैंक खाता आधार से लिंक है और डीबीटी (DBT) सक्रिय है।"
        ),
        (
            "SVC-006",
            "Madhya Pradesh Rojgar Panjiyan (Employment)",
            "मध्य प्रदेश रोज़गार पंजीयन",
            "Employment and Skill Development",
            "तकनीकी शिक्षा एवं रोज़गार विभाग",
            "Employment and Skill Development",
            "Online registration on MP Employment Exchange portal for government and private recruitment eligibility.",
            "मध्य प्रदेश शासन की भर्तियों एवं निजी रोज़गार अवसरों हेतु राज्य रोज़गार पोर्टल पर अनिवार्य पंजीयन।",
            "Resident of MP aged 15 to 60 with minimum 10th standard qualification.",
            "मध्य प्रदेश का निवासी, आयु १५ से ६० वर्ष एवं न्यूनतम १०वीं उत्तीर्ण।",
            ["Aadhaar Card", "Educational Marksheets & Degree Certificates", "Samagra ID", "Mobile Number & Email"],
            ["आधार कार्ड", "शैक्षणिक योग्यता अंकसूची व उपाधि", "समग्र आईडी", "सक्रिय मोबाइल नंबर एवं ईमेल"],
            "Free",
            "निःशुल्क",
            "Instant (Online)",
            "तत्काल (ऑनलाइन)",
            "Keep registration number handy. Renewal is required every 3 years to maintain job seniority.",
            "पंजीयन क्रमांक सुरक्षित रखें। वरिष्ठता बनाए रखने हेतु प्रत्येक ३ वर्ष में नवीनीकरण अनिवार्य है।"
        ),
        (
            "SVC-007",
            "Mukhyamantri Kisan Kalyan Yojana",
            "मुख्यमंत्री किसान कल्याण योजना",
            "Agriculture and Farmers",
            "किसान कल्याण तथा कृषि विकास विभाग",
            "Agriculture and Farmers",
            "State supplementary financial support of ₹6,000 per year paid in three installments to eligible landholding farmers.",
            "पात्र भू-धारक किसान परिवारों को ₹६,००० प्रति वर्ष की अतिरिक्त वित्तीय सहायता तीन किस्तों में प्रदान करने की योजना।",
            "Farmer registered under PM-Kisan with operational agricultural landholding in Madhya Pradesh.",
            "मध्य प्रदेश में कृषि योग्य भूमि धारक किसान जो पीएम-किसान योजना में पंजीकृत हों।",
            ["Khasra/Khatauni Land Record Copy", "Aadhaar Card", "Aadhaar-Linked Bank Account", "Samagra Member ID"],
            ["खसरा/खतौनी की नकल", "आधार कार्ड", "आधार लिंक बैंक खाता", "समग्र सदस्य आईडी"],
            "Free",
            "निःशुल्क",
            "15-20 working days",
            "१५-२० कार्य दिवस",
            "Land records must be synchronized with PM-Kisan portal eKYC details for seamless benefit disbursement.",
            "लाभ प्राप्त करने हेतु भू-अभिलेख एवं ई-केवाईसी विवरण पीएम-किसान पोर्टल से अद्यतन होना आवश्यक है।"
        ),
        (
            "SVC-008",
            "Indira Gandhi National Old Age Pension",
            "इंदिरा गांधी राष्ट्रीय वृद्धावस्था पेंशन योजना",
            "Social Security and Pension",
            "सामाजिक न्याय एवं दिव्यांगजन सशक्तिकरण",
            "Social Security and Pension",
            "Monthly social security pension of ₹600 for senior citizens living below the poverty line.",
            "गरीबी रेखा से नीचे जीवनयापन करने वाले ६० वर्ष या अधिक आयु के वरिष्ठ नागरिकों हेतु ₹६०० प्रतिमाह पेंशन।",
            "Resident of Madhya Pradesh aged 60 years or above belonging to BPL household.",
            "मध्य प्रदेश का निवासी, न्यूनतम ६० वर्ष आयु एवं बीपीएल (BPL) परिवार से संबंधित।",
            ["Age Proof (Aadhaar / Voter ID / Birth Certificate)", "BPL Ration Card / Samagra ID", "Bank Passbook Copy", "Passport Photograph"],
            ["आयु प्रमाण पत्र (आधार / वोटर कार्ड)", "बीपीएल राशन कार्ड / समग्र आईडी", "बैंक पासबुक प्रति", "पासपोर्ट साइज़ फोटो"],
            "Free",
            "निःशुल्क",
            "15-30 working days",
            "१५-३० कार्य दिवस",
            "Pension is credited directly into beneficiary bank account via electronic Aadhaar payment bridge.",
            "पेंशन की राशि सीधे लाभार्थी के बैंक खाते में आधार पेमेंट ब्रिज के माध्यम से भेजी जाती है।"
        ),
        (
            "SVC-009",
            "Land Record Copy (Khasra / Khatauni / B-1)",
            "भू-अभिलेख नकल (खसरा / खतौनी / बी-१)",
            "Revenue and Land Records",
            "राजस्व विभाग (मध्य प्रदेश भू-अभिलेख)",
            "Revenue and Land Records",
            "Certified digital copy of village land ownership records, plot area, and cultivation rights.",
            "ग्राम के भूमि स्वामित्व, खसरा रकबा, फसल विवरण एवं अधिकारों का प्रमाणित डिजिटल भू-अभिलेख।",
            "Any landowner, authorized family member, or citizen verifying land title in MP.",
            "मध्य प्रदेश में भूमि का कोई भी स्वामी, अधिकृत परिजन अथवा भूमि स्वामित्व जाँचने वाला नागरिक।",
            ["Village, Tehsil, and District Name", "Khasra Number or Landowner Name", "Applicant Aadhaar Card"],
            ["ग्राम, तहसील एवं जिला का नाम", "खसरा क्रमांक अथवा खातेदार का नाम", "आवेदक का आधार कार्ड"],
            "₹20 per copy",
            "₹२० प्रति नकल",
            "Instant to 2 days",
            "तत्काल से २ दिवस",
            "Digitally signed khasra copies issued via this portal are valid for bank loans and agricultural claims.",
            "इस पोर्टल से प्राप्त डिजिटल हस्ताक्षरित खसरा प्रतिलिपि बैंक ऋण एवं कृषि कार्यों हेतु मान्य है।"
        ),
        (
            "SVC-010",
            "New Domestic Water Connection",
            "नवीन घरेलू नल कनेक्शन आवेदन",
            "Municipal Services",
            "लोक स्वास्थ्य यांत्रिकी एवं नगरीय निकाय",
            "Municipal Services",
            "Application for fresh municipal potable piped water supply connection for residential premises.",
            "शहरी अथवा आवासीय परिसर हेतु नगर निगम की पाइपलाइन से नवीन पेयजल कनेक्शन प्राप्त करने का आवेदन।",
            "Property owner with completed building construction in municipal pipeline zone.",
            "नगर निगम क्षेत्र में स्थित वैध भवन अथवा आवासीय संपत्ति का स्वामी।",
            ["Property Tax Receipt / Registry Papers", "Building Layout / Pipeline Route Plan", "Aadhaar Card", "Passport Photo"],
            ["सम्पत्ति कर रसीद / रजिस्ट्री दस्तावेज", "भवन नक्शा / पाइपलाइन लेआउट", "आधार कार्ड", "पासपोर्ट फोटो"],
            "₹500 (demo)",
            "₹५०० (डेमो)",
            "10-15 working days",
            "१०-१५ कार्य दिवस",
            "A municipal junior engineer schedules on-site pipeline inspection within 5 days of submission.",
            "आवेदन जमा करने के ५ दिनों के भीतर कनिष्ठ अभियंता द्वारा स्थल निरीक्षण निर्धारित किया जाएगा।"
        ),
        (
            "SVC-011",
            "Ayushman Bharat MP Health Card",
            "आयुष्मान भारत मध्य प्रदेश स्वास्थ्य कार्ड",
            "Health and Welfare",
            "लोक स्वास्थ्य एवं परिवार कल्याण विभाग",
            "Health and Welfare",
            "Comprehensive health protection card enabling free cashless medical treatment up to ₹5 Lakh per year.",
            "प्रति वर्ष ₹५ लाख तक का निःशुल्क कैशलेस अस्पताल उपचार प्रदान करने वाला आयुष्मान स्वास्थ्य सुरक्षा कार्ड।",
            "Families registered under NFSA / Samagra BPL or listed in SECC socio-economic database in MP.",
            "मध्य प्रदेश के राष्ट्रीय खाद्य सुरक्षा, समग्र बीपीएल अथवा एसईसीसी सूची में शामिल पात्र परिवार।",
            ["Samagra Family ID", "Aadhaar Card with Biometric/OTP eKYC", "Ration Card"],
            ["समग्र परिवार आईडी", "आधार कार्ड (ओटीपी/बायोमेट्रिक ई-केवाईसी)", "राशन कार्ड"],
            "Free",
            "निःशुल्क",
            "Instant (Online)",
            "तत्काल (ऑनलाइन)",
            "Generate instant e-card and present at empaneled government or private hospitals for cashless admissions.",
            "डिजिटल कार्ड तत्काल डाउनलोड करें और संबद्ध निजी या सरकारी अस्पताल में कैशलेस उपचार हेतु प्रस्तुत करें।"
        ),
        (
            "SVC-012",
            "Trade License & Shop Act Registration",
            "दुकान एवं स्थापना पंजीयन (ट्रेड लाइसेंस)",
            "Business and Entrepreneurship",
            "नगरीय विकास एवं श्रम विभाग",
            "Business and Entrepreneurship",
            "Mandatory municipal commercial license for running retail stores, enterprises, and business offices.",
            "दुकान, वाणिज्यिक प्रतिष्ठान एवं लघु उद्योग संचालन हेतु अनिवार्य शहरी निकाय व्यापार अनुज्ञप्ति।",
            "Proprietor, partner, or authorized director establishing commercial venture in municipal boundary.",
            "शहरी सीमा में व्यापार या व्यवसाय आरंभ करने वाला प्रोप्राइटर, साझेदार अथवा अधिकृत प्रतिनिधि।",
            ["Premises Ownership / Rental Agreement", "Electricity Connection Bill", "PAN Card & Aadhaar", "GST Registration (if applicable)"],
            ["दुकान स्वामित्व / किराया अनुबंध प्रपत्र", "विद्युत कनेक्शन बिल", "पैन कार्ड एवं आधार कार्ड", "जीएसटी पंजीयन (यदि लागू हो)"],
            "₹250 (demo)",
            "₹२५० (डेमो)",
            "7 working days",
            "७ कार्य दिवस",
            "Certificate must be displayed prominently at the entrance of the commercial establishment.",
            "प्राप्त लाइसेंस को व्यापार स्थल अथवा दुकान के मुख्य द्वार पर प्रदर्शित करना अनिवार्य है।"
        ),
    ]

    for s in services:
        db.execute(
            """INSERT INTO services
            (id, name, name_hi, department, department_hi, category, description, description_hi,
             eligibility, eligibility_hi, documents, documents_hi, fee, fee_hi,
             processing_time, processing_time_hi, instructions, instructions_hi,
             availability, application_type, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'Available', 'Online', ?)
            ON CONFLICT(id) DO UPDATE SET
            name=excluded.name, name_hi=excluded.name_hi,
            department=excluded.department, department_hi=excluded.department_hi,
            category=excluded.category,
            description=excluded.description, description_hi=excluded.description_hi,
            eligibility=excluded.eligibility, eligibility_hi=excluded.eligibility_hi,
            documents=excluded.documents, documents_hi=excluded.documents_hi,
            fee=excluded.fee, fee_hi=excluded.fee_hi,
            processing_time=excluded.processing_time, processing_time_hi=excluded.processing_time_hi,
            instructions=excluded.instructions, instructions_hi=excluded.instructions_hi""",
            (
                s[0], s[1], s[2], s[3], s[4], s[5], s[6], s[7],
                s[8], s[9], json.dumps(s[10]), json.dumps(s[11]),
                s[12], s[13], s[14], s[15], s[16], s[17], now_iso()
            )
        )

    # Demo Accounts (Bilingual support with both @mpsuvidha.demo and backwards-compatible @janseva.demo)
    demo_users = [
        ("Aarav Sharma", "citizen@mpsuvidha.demo", "9876500001", "Citizen@123", "Arera Colony, Bhopal, Madhya Pradesh", "citizen", ""),
        ("Priya Verma (Officer)", "officer@mpsuvidha.demo", "9876500002", "Officer@123", "Vallabh Bhawan, Bhopal, Madhya Pradesh", "officer", "Revenue Department"),
        ("MP Suvidha Administrator", "admin@mpsuvidha.demo", "9876500003", "Admin@123", "Mantralaya, Bhopal, Madhya Pradesh", "admin", "General Administration"),
        # Backward compatibility accounts
        ("Aarav Sharma", "citizen@janseva.demo", "9876500001", "Citizen@123", "Arera Colony, Bhopal, Madhya Pradesh", "citizen", ""),
        ("Priya Verma (Officer)", "officer@janseva.demo", "9876500002", "Officer@123", "Vallabh Bhawan, Bhopal, Madhya Pradesh", "officer", "Revenue Department"),
        ("MP Suvidha Administrator", "admin@janseva.demo", "9876500003", "Admin@123", "Mantralaya, Bhopal, Madhya Pradesh", "admin", "General Administration"),
    ]
    for name, email, mobile, password, address, role, dept in demo_users:
        db.execute(
            """INSERT INTO users(name, email, mobile, password_hash, address, role, department, created_at)
               VALUES(?, ?, ?, ?, ?, ?, ?, ?)
               ON CONFLICT(email) DO UPDATE SET
               name=excluded.name, mobile=excluded.mobile, address=excluded.address, role=excluded.role, department=excluded.department""",
            (name, email, mobile, generate_password_hash(password), address, role, dept, now_iso()),
        )

    # Citizen Announcements (Professional, Bilingual, Non-Academic)
    if db.execute("SELECT COUNT(*) FROM announcements").fetchone()[0] == 0:
        notices = [
            (
                "Welcome to MP Suvidha: Madhya Pradesh Digital Services Portal",
                "एमपी सुविधा पोर्टल में आपका स्वागत है: मध्य प्रदेश डिजिटल सेवाएँ",
                "MP Suvidha is an independent demonstration portal designed to showcase citizen-friendly public service discovery, transparent online applications, and end-to-end tracking.",
                "एमपी सुविधा पोर्टल नागरिकों को सुलभ लोक सेवाएँ खोजने, पारदर्शी ऑनलाइन आवेदन करने एवं स्थिति ट्रैक करने की सुविधा प्रदान करता है।",
                "Important"
            ),
            (
                "Faceless Delivery of Revenue & Local Resident Certificates",
                "राजस्व एवं मूल निवासी प्रमाण पत्रों की डिजिटल व्यवस्था",
                "Citizens can submit applications online for Income, Domicile, and Caste certificates with instant tracking via registered Application IDs.",
                "नागरिक अब आय, मूल निवासी एवं जाति प्रमाण पत्रों हेतु ऑनलाइन आवेदन कर सकते हैं तथा आवेदन क्रमांक द्वारा वास्तविक स्थिति देख सकते हैं।",
                "Service"
            ),
            (
                "Unified Application Tracking and Digital Demonstration Verification",
                "एकीकृत आवेदन ट्रैकिंग एवं डिजिटल सत्यापन सुविधा",
                "Track application workflows in real-time and verify demonstration certificates anytime using our fast verification engine.",
                "अपने आवेदन की प्रगति वास्तविक समय में जाँचें और जारी किए गए डेमो प्रमाण पत्रों की प्रामाणिकता तुरंत सत्यापित करें।",
                "Notice"
            ),
            (
                "Complete Bilingual Support (Hindi & English)",
                "पूर्ण द्विभाषी सुविधा (हिन्दी एवं अंग्रेज़ी)",
                "Use the language switcher at the top to toggle effortlessly between Hindi and English across all services, forms, and tracking dashboards.",
                "शीर्ष पर स्थित भाषा चयन विकल्प से सभी सेवाओं, प्रपत्रों एवं डैशबोर्ड को सहजता से हिन्दी अथवा अंग्रेज़ी में देखें।",
                "Update"
            ),
        ]
        db.executemany(
            """INSERT INTO announcements(title, title_hi, body, body_hi, kind, published_at)
               VALUES(?, ?, ?, ?, ?, ?)""",
            [(a, b, c, d, e, now_iso()) for a, b, c, d, e in notices]
        )

    # Initial Demonstration Applications
    citizen_user = db.execute("SELECT id FROM users WHERE email='citizen@mpsuvidha.demo'").fetchone()
    if citizen_user and db.execute("SELECT COUNT(*) FROM applications").fetchone()[0] == 0:
        citizen_id = citizen_user[0]
        samples = [
            ("MPS-2026-10482", "SVC-001", "Aarav Sharma", "Submitted", "Application received. Initial document review queued at Revenue Office, Bhopal."),
            ("MPS-2026-10219", "SVC-005", "Aarav Sharma", "Under Review", "Verification of college fee receipt and marksheet verification under process."),
            ("MPS-2026-09831", "SVC-003", "Aarav Sharma", "Approved", "Continuous residency verified. Digital demonstration certificate issued."),
        ]
        for app_id, service_id, name, status, remarks in samples:
            service = db.execute("SELECT department, name FROM services WHERE id=?", (service_id,)).fetchone()
            stamp = now_iso()
            applicant_json = json.dumps({"name": name, "email": "citizen@mpsuvidha.demo", "mobile": "9876500001", "address": "Bhopal, MP"})
            db.execute(
                """INSERT OR IGNORE INTO applications
                   (id, citizen_id, service_id, applicant, documents, submitted_at, status, department, officer_remarks, updated_at)
                   VALUES(?,?,?,?,?,?,?,?,?,?)""",
                (app_id, citizen_id, service_id, applicant_json, "[]", stamp, status, service["department"], remarks, stamp)
            )
            db.execute(
                "INSERT INTO application_history(application_id, status, remarks, created_at) VALUES(?,?,?,?)",
                (app_id, "Submitted", "Application submitted online via MP Suvidha.", stamp)
            )
            if status != "Submitted":
                db.execute(
                    "INSERT INTO application_history(application_id, status, remarks, created_at) VALUES(?,?,?,?)",
                    (app_id, status, remarks, stamp)
                )
            if status == "Approved":
                db.execute(
                    """INSERT OR IGNORE INTO certificates
                       (number, application_id, applicant_name, service_name, issue_date, department, status)
                       VALUES(?,?,?,?,?,?,?)""",
                    ("MPS-CERT-2026-09831", app_id, name, service["name"], stamp[:10], service["department"], "Valid")
                )

    db.commit()
