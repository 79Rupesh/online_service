/**
 * MP Suvidha: Comprehensive Bilingual English & Hindi Translations Engine
 * Madhya Pradesh Digital Services Portal
 */
const I18N = {
  currentLang: localStorage.getItem("mpsuvidha_lang") || localStorage.getItem("janseva_lang") || "en",

  // Localized dictionaries for dynamic database categories and departments
  categories: {
    "Education and Scholarship": "शिक्षा एवं छात्रवृत्ति",
    "Health and Welfare": "स्वास्थ्य एवं जनकल्याण",
    "Certificates and Documents": "प्रमाणपत्र एवं दस्तावेज़",
    "Agriculture and Farmers": "कृषि एवं किसान कल्याण",
    "Employment and Skill Development": "रोज़गार एवं कौशल विकास",
    "Social Security and Pension": "सामाजिक सुरक्षा एवं पेंशन",
    "Revenue and Land Records": "राजस्व एवं भू-अभिलेख",
    "Transport Services": "परिवहन सेवाएँ",
    "Municipal Services": "नगर निगम एवं नागरिक सेवाएँ",
    "Business and Entrepreneurship": "व्यापार एवं उद्योग संवर्धन",
    "Rural Development": "ग्रामीण विकास एवं पंचायती राज",
    "Other Public Services": "अन्य लोक सेवाएँ",
    // Legacy maps
    "Education and Learning": "शिक्षा एवं छात्रवृत्ति",
    "Certificates and Licenses": "प्रमाणपत्र एवं दस्तावेज़",
    "Employment and Entrepreneurship": "रोज़गार एवं कौशल विकास",
    "Agriculture and Rural Development": "कृषि एवं किसान कल्याण",
    "Social Welfare and Pension": "सामाजिक सुरक्षा एवं पेंशन",
    "Revenue and Administration": "राजस्व एवं भू-अभिलेख",
    "Transport and Infrastructure": "परिवहन सेवाएँ",
    "Business and Investment": "व्यापार एवं उद्योग संवर्धन",
    "Youth and Sports": "युवा एवं खेल कल्याण",
    "Tourism and Culture": "पर्यटन एवं संस्कृति"
  },

  departments: {
    "Revenue Department": "राजस्व विभाग",
    "Municipal Services": "नगर निगम एवं नगरीय प्रशासन",
    "Education Department": "शिक्षा विभाग",
    "Higher Education Department": "उच्च शिक्षा विभाग",
    "Employment Department": "तकनीकी शिक्षा एवं रोज़गार विभाग",
    "Agriculture Department": "किसान कल्याण तथा कृषि विकास विभाग",
    "Social Justice Department": "सामाजिक न्याय एवं दिव्यांगजन सशक्तिकरण",
    "Public Health Engineering Department": "लोक स्वास्थ्य यांत्रिकी विभाग",
    "Health and Welfare": "लोक स्वास्थ्य एवं परिवार कल्याण विभाग",
    "Industry Department": "नगरीय विकास एवं उद्योग विभाग",
    "Tourism and Culture Department": "पर्यटन एवं संस्कृति विभाग",
    "Transport and Infrastructure": "परिवहन विभाग",
    "Citizen Support": "नागरिक सहायता केंद्र",
    "General Administration": "सामान्य प्रशासन विभाग"
  },

  statuses: {
    "Submitted": { en: "Submitted", hi: "जमा किया गया" },
    "Under Review": { en: "Under Review", hi: "समीक्षाधीन" },
    "Documents Required": { en: "Documents Required", hi: "दस्तावेज़ प्रतीक्षित" },
    "Approved": { en: "Approved", hi: "स्वीकृत" },
    "Rejected": { en: "Rejected", hi: "अस्वीकृत" },
    "Completed": { en: "Completed", hi: "पूर्ण" },
    "Valid": { en: "Valid (Demonstration)", hi: "मान्य (प्रदर्शन रिकॉर्ड)" }
  },

  translations: {
    en: {
      // Branding & Metadata
      portal_name: "MP Suvidha",
      portal_subtitle: "Madhya Pradesh Digital Services",
      portal_tagline: "One Portal. Multiple Services.",
      demo_badge: "Demonstration Portal · Madhya Pradesh Digital Services",
      disclaimer_short: "MP Suvidha is an independent demonstration portal and is not affiliated with the Government of Madhya Pradesh.",
      
      // Header & Navigation
      nav_home: "Home",
      nav_services: "Services",
      nav_categories: "Categories",
      nav_track: "Track Application",
      nav_verify: "Verify Certificate",
      nav_about: "About Us",
      nav_help: "Help Centre",
      nav_dashboard: "My Dashboard",
      nav_profile: "My Profile",
      nav_evaluation: "Internal Evaluation",
      
      // Action Buttons
      btn_login: "Log In",
      btn_register: "Register ↗",
      btn_logout: "Sign Out",
      btn_apply_now: "Apply Now",
      btn_view_details: "View Details",
      btn_check_status: "Track Status",
      btn_verify: "Verify Certificate",
      btn_search: "Search",
      btn_save: "Save Changes",
      btn_submit: "Submit Application",
      btn_cancel: "Cancel",
      btn_close: "Close",
      btn_download_pdf: "Download Certificate (PDF)",
      btn_explore_services: "Explore Services",
      btn_how_it_works: "How It Works",
      btn_filter: "Filter",
      btn_reset: "Reset Filters",

      // Hero Section
      hero_eyebrow: "One Portal. Multiple Services.",
      hero_title: "All Essential Services, <span>One Digital Platform</span>",
      hero_subtitle: "Discover services, understand eligibility, submit applications and track your progress through one convenient platform.",
      hero_search_placeholder: "Search for services, certificates, or departments...",
      hero_popular: "Popular Searches:",
      tag_income: "Income Certificate",
      tag_caste: "Caste Certificate",
      tag_domicile: "Domicile Certificate",
      tag_khasra: "Land Record (Khasra)",
      tag_scholarship: "Scholarship",
      tag_rojgar: "Rojgar Panjiyan",

      // Quick Services Shortcuts
      quick_apply: "Apply for a Service",
      quick_apply_desc: "Discover eligibility and apply online",
      quick_track: "Track Application",
      quick_track_desc: "Real-time application status",
      quick_verify: "Verify Certificate",
      quick_verify_desc: "Check demo certificate validity",
      quick_categories: "Explore Categories",
      quick_categories_desc: "12 Citizen Service Clusters",

      // Statistics
      stat_services: "Active Services",
      stat_users: "Registered Citizens",
      stat_apps: "Total Applications",
      stat_approved: "Approved & Issued",

      // Service Categories Section
      cat_eyebrow: "Service Clusters",
      cat_title: "Explore by <span>Category</span>",
      cat_subtitle: "Discover government citizen services organized cleanly by department and domain.",
      cat_view_all: "View all services in this category →",

      // Popular Services Section
      pop_eyebrow: "Most Requested",
      pop_title: "Popular <span>Citizen Services</span>",
      pop_subtitle: "Frequently accessed digital applications for residents of Madhya Pradesh.",

      // Service Directory
      serv_eyebrow: "Service Directory",
      serv_title: "Comprehensive <span>Service Catalogue</span>",
      serv_subtitle: "Search, review prerequisite documents, fee details, and submit online applications.",
      serv_search_placeholder: "Type service name, keyword, or department...",
      serv_filter_all_cat: "All Categories",
      serv_filter_all_dept: "All Departments",
      serv_sort_az: "Name (A to Z)",
      serv_sort_za: "Name (Z to A)",
      serv_results_count: "Showing services",
      serv_no_results: "No services found matching your criteria.",
      serv_eligibility_label: "Eligibility:",
      serv_fee_label: "Fee:",
      serv_time_label: "Processing Time:",
      serv_dept_label: "Department:",
      serv_docs_label: "Required Documents:",
      serv_instructions_label: "Instructions:",

      // Application Tracking Section
      track_eyebrow: "Real-time Tracking",
      track_title: "Track Your <span>Application</span>",
      track_subtitle: "Enter your Application ID and registered email or mobile number to inspect live stage progress.",
      track_id_label: "Application ID",
      track_id_placeholder: "e.g., MPS-2026-10482",
      track_contact_label: "Registered Email or Mobile Number",
      track_contact_placeholder: "e.g., citizen@mpsuvidha.demo or 9876500001",
      track_btn_submit: "Track Status Now",
      track_stage_1: "Submitted",
      track_stage_2: "Under Review",
      track_stage_3: "Verification",
      track_stage_4: "Approved / Issued",
      track_officer_remarks: "Officer Remarks:",
      track_history_title: "Application Stage History",

      // Certificate Verification Section
      verify_eyebrow: "Instant Verification",
      verify_title: "Demonstration <span>Certificate Verification</span>",
      verify_subtitle: "Verify demonstration certificates issued by the MP Suvidha portal using the certificate number.",
      verify_number_label: "Certificate Number",
      verify_number_placeholder: "e.g., MPS-CERT-2026-09831",
      verify_btn_submit: "Verify Certificate",
      verify_result_title: "Certificate Verification Record",
      verify_issued_to: "Issued To:",
      verify_service: "Service:",
      verify_dept: "Department:",
      verify_date: "Date of Issue:",
      verify_status: "Status:",
      verify_demo_notice: "Demonstration Notice: This certificate was issued in demonstration mode on MP Suvidha and is not an official government statutory document.",

      // How It Works
      how_eyebrow: "Citizen Guide",
      how_title: "How It <span>Works</span>",
      how_subtitle: "Simple 4-step process to discover and complete citizen services online.",
      how_step1_title: "1. Find a Service",
      how_step1_desc: "Browse through 12 categories or use the instant search to locate your required service.",
      how_step2_title: "2. Read Requirements",
      how_step2_desc: "Review eligibility criteria, required documents, demonstration fees, and expected timelines.",
      how_step3_title: "3. Submit Application",
      how_step3_desc: "Fill in applicant details, upload supporting documents, and receive your unique Application ID.",
      how_step4_title: "4. Track Progress",
      how_step4_desc: "Follow stage-by-stage review by department officers and download your demonstration certificate.",

      // Announcements Section
      ann_eyebrow: "Updates & Alerts",
      ann_title: "Important <span>Notices & Announcements</span>",
      ann_subtitle: "Official portal notifications, service schedules, and digital governance updates.",

      // Feedback & Help Centre
      fb_eyebrow: "Citizen Voice",
      fb_title: "Feedback & <span>Citizen Support</span>",
      fb_subtitle: "Share your experience to help us improve the digital service experience for everyone.",
      fb_overall_rating: "Overall Experience Rating",
      fb_ease_rating: "Ease of Navigation Rating",
      fb_service_rating: "Service Information Rating",
      fb_name_label: "Your Name (Optional)",
      fb_role_label: "Stakeholder Category",
      fb_suggestions_label: "Your Suggestions & Experience",
      fb_suggestions_placeholder: "Tell us what worked well and what could be improved...",
      fb_complaint_label: "Grievance or Issue Description (Optional)",
      fb_btn_submit: "Submit Feedback",

      // About Us Section
      about_eyebrow: "About Portal",
      about_title: "About <span>MP Suvidha</span>",
      about_p1: "MP Suvidha is an independent digital service information and application demonstration portal designed to help citizens discover and access information about essential services in Madhya Pradesh.",
      about_p2: "The portal showcases a unified citizen experience: single-window discovery across 12 public service categories, paperless document upload simulation, transparent multi-stage application tracking, and verifiable demonstration certificates.",
      about_p3: "DISCLAIMER: MP Suvidha is an independent educational and demonstration portal. It is not affiliated with, authorized by, or an official website of the Government of Madhya Pradesh or any of its departments.",

      // Citizen Dashboard
      dash_title: "Citizen Dashboard",
      dash_welcome: "Welcome back,",
      dash_tab_applications: "My Applications",
      dash_tab_certificates: "My Certificates",
      dash_tab_notifications: "Notifications",
      dash_tab_profile: "Profile Settings",
      dash_col_id: "Application ID",
      dash_col_service: "Service Name",
      dash_col_dept: "Department",
      dash_col_date: "Submitted Date",
      dash_col_status: "Current Status",
      dash_col_action: "Actions",

      // Officer & Admin Dashboard
      dash_officer_title: "Department Officer Portal",
      dash_admin_title: "Portal Administration & Analytics",
      dash_total_apps: "Total Applications",
      dash_pending_review: "Pending Review",
      dash_approved_count: "Approved",
      dash_rejected_count: "Rejected",

      // Authentication Modals
      auth_login_title: "Log In to MP Suvidha",
      auth_register_title: "Create Citizen Account",
      auth_email_label: "Email Address",
      auth_password_label: "Password",
      auth_name_label: "Full Name",
      auth_mobile_label: "Mobile Number (10 digits)",
      auth_address_label: "Address (City / District)",
      auth_btn_login: "Log In",
      auth_btn_register: "Create Account",
      auth_quick_demo: "Quick Demo Logins:",
      auth_demo_citizen: "Citizen Login",
      auth_demo_officer: "Officer Login",
      auth_demo_admin: "Admin Login",

      // Application Submission Modal
      apply_modal_title: "Apply for",
      apply_step_info: "Applicant Information",
      apply_step_docs: "Document Upload",
      apply_demo_fee_notice: "Demonstration Notice: Fee payment is simulated in demonstration mode. No real payment is required.",
      apply_attach_label: "Attach Supporting Documents (PDF, JPG, PNG up to 5 MB)",
      apply_review_declaration: "I declare that the information provided is accurate for demonstration purposes.",

      // Footer
      footer_about_heading: "About MP Suvidha",
      footer_services_heading: "Citizen Services",
      footer_links_heading: "Quick Links",
      footer_help_heading: "Help & Support",
      footer_privacy: "Privacy Policy",
      footer_terms: "Terms & Conditions",
      footer_faq: "FAQ",
      footer_contact: "Contact Information",
      footer_rights: "All rights reserved. MP Suvidha is an independent demonstration portal."
    },

    hi: {
      // Branding & Metadata
      portal_name: "एमपी सुविधा",
      portal_subtitle: "मध्य प्रदेश डिजिटल सेवाएँ",
      portal_tagline: "एक पोर्टल · अनेक सेवाएँ",
      demo_badge: "प्रदर्शन पोर्टल · मध्य प्रदेश डिजिटल सेवाएँ",
      disclaimer_short: "एमपी सुविधा एक स्वतंत्र प्रदर्शन पोर्टल है और इसका मध्य प्रदेश शासन से कोई आधिकारिक संबंध नहीं है।",

      // Header & Navigation
      nav_home: "होम",
      nav_services: "सेवाएँ",
      nav_categories: "श्रेणियाँ",
      nav_track: "आवेदन ट्रैक करें",
      nav_verify: "प्रमाणपत्र सत्यापन",
      nav_about: "हमारे बारे में",
      nav_help: "सहायता केंद्र",
      nav_dashboard: "मेरा डैशबोर्ड",
      nav_profile: "मेरी प्रोफ़ाइल",
      nav_evaluation: "आंतरिक मूल्यांकन",

      // Action Buttons
      btn_login: "लॉग इन",
      btn_register: "पंजीकरण ↗",
      btn_logout: "लॉग आउट",
      btn_apply_now: "आवेदन करें",
      btn_view_details: "विवरण देखें",
      btn_check_status: "स्थिति देखें",
      btn_verify: "प्रमाणपत्र जाँचें",
      btn_search: "खोजें",
      btn_save: "सहेजें",
      btn_submit: "आवेदन जमा करें",
      btn_cancel: "रद्द करें",
      btn_close: "बंद करें",
      btn_download_pdf: "प्रमाणपत्र डाउनलोड करें (PDF)",
      btn_explore_services: "सभी सेवाएँ देखें",
      btn_how_it_works: "यह कैसे काम करता है",
      btn_filter: "फ़िल्टर",
      btn_reset: "रीसेट करें",

      // Hero Section
      hero_eyebrow: "एक पोर्टल · अनेक सेवाएँ",
      hero_title: "सभी आवश्यक सेवाएँ, <span>एक ही डिजिटल प्लेटफॉर्म पर</span>",
      hero_subtitle: "सेवाओं की जानकारी प्राप्त करें, पात्रता समझें, आवेदन करें और अपनी आवेदन स्थिति आसानी से देखें।",
      hero_search_placeholder: "सेवाएँ, प्रमाणपत्र या विभाग खोजें...",
      hero_popular: "लोकप्रिय खोज:",
      tag_income: "आय प्रमाण पत्र",
      tag_caste: "जाति प्रमाण पत्र",
      tag_domicile: "मूल निवासी प्रमाण पत्र",
      tag_khasra: "भू-अभिलेख (खसरा)",
      tag_scholarship: "छात्रवृत्ति योजना",
      tag_rojgar: "रोज़गार पंजीयन",

      // Quick Services Shortcuts
      quick_apply: "सेवा हेतु आवेदन",
      quick_apply_desc: "पात्रता जाँचें व ऑनलाइन आवेदन करें",
      quick_track: "आवेदन ट्रैक करें",
      quick_track_desc: "वास्तविक समय में आवेदन स्थिति",
      quick_verify: "प्रमाणपत्र सत्यापन",
      quick_verify_desc: "डेमो प्रमाणपत्र की वैधता जाँचें",
      quick_categories: "श्रेणियाँ देखें",
      quick_categories_desc: "१२ नागरिक सेवा वर्ग",

      // Statistics
      stat_services: "सक्रिय सेवाएँ",
      stat_users: "पंजीकृत नागरिक",
      stat_apps: "कुल आवेदन",
      stat_approved: "स्वीकृत एवं जारी",

      // Service Categories Section
      cat_eyebrow: "विभागीय वर्ग",
      cat_title: "श्रेणी अनुसार <span>सेवाएँ खोजें</span>",
      cat_subtitle: "मध्य प्रदेश शासन के विभिन्न विभागों की सेवाएँ सुव्यवस्थित श्रेणियों में प्राप्त करें।",
      cat_view_all: "इस श्रेणी की सभी सेवाएँ देखें →",

      // Popular Services Section
      pop_eyebrow: "अति आवश्यक",
      pop_title: "लोकप्रिय <span>नागरिक सेवाएँ</span>",
      pop_subtitle: "मध्य प्रदेश के नागरिकों द्वारा सर्वाधिक उपयोग की जाने वाली प्रमुख डिजिटल सेवाएँ।",

      // Service Directory
      serv_eyebrow: "सेवा निर्देशिका",
      serv_title: "समग्र <span>सेवा निर्देशिका</span>",
      serv_subtitle: "आवश्यक दस्तावेज़ों की सूची, पात्रता एवं शुल्क विवरण देखें और ऑनलाइन आवेदन करें।",
      serv_search_placeholder: "सेवा का नाम, विभाग या कीवर्ड दर्ज करें...",
      serv_filter_all_cat: "सभी श्रेणियाँ",
      serv_filter_all_dept: "सभी विभाग",
      serv_sort_az: "नाम (अ से ज्ञ / A-Z)",
      serv_sort_za: "नाम (विपरीत क्रम)",
      serv_results_count: "कुल सेवाएँ उपलब्ध",
      serv_no_results: "आपके खोज मानदंड के अनुरूप कोई सेवा नहीं मिली।",
      serv_eligibility_label: "पात्रता:",
      serv_fee_label: "शुल्क:",
      serv_time_label: "प्रसंस्करण समय:",
      serv_dept_label: "संबंधित विभाग:",
      serv_docs_label: "आवश्यक दस्तावेज़:",
      serv_instructions_label: "महत्वपूर्ण निर्देश:",

      // Application Tracking Section
      track_eyebrow: "लाइव ट्रैकिंग",
      track_title: "अपने आवेदन को <span>ट्रैक करें</span>",
      track_subtitle: "प्रक्रिया के विभिन्न चरणों की वास्तविक स्थिति देखने हेतु आवेदन क्रमांक एवं पंजीकृत संपर्क दर्ज करें।",
      track_id_label: "आवेदन क्रमांक (Application ID)",
      track_id_placeholder: "उदाहरण: MPS-2026-10482",
      track_contact_label: "पंजीकृत ईमेल अथवा मोबाइल नंबर",
      track_contact_placeholder: "उदाहरण: citizen@mpsuvidha.demo अथवा 9876500001",
      track_btn_submit: "स्थिति तुरंत देखें",
      track_stage_1: "आवेदन प्राप्त",
      track_stage_2: "समीक्षाधीन",
      track_stage_3: "सत्यापन प्रक्रिया",
      track_stage_4: "स्वीकृत / प्रमाणपत्र जारी",
      track_officer_remarks: "अधिकारी की टिप्पणी:",
      track_history_title: "आवेदन चरण इतिहास",

      // Certificate Verification Section
      verify_eyebrow: "त्वरित सत्यापन",
      verify_title: "डेमो <span>प्रमाणपत्र सत्यापन</span>",
      verify_subtitle: "एमपी सुविधा पोर्टल द्वारा जारी किए गए प्रदर्शन प्रमाणपत्रों की सत्यता क्रमांक द्वारा जाँचें।",
      verify_number_label: "प्रमाणपत्र क्रमांक (Certificate Number)",
      verify_number_placeholder: "उदाहरण: MPS-CERT-2026-09831",
      verify_btn_submit: "प्रमाणपत्र सत्यापित करें",
      verify_result_title: "प्रमाणपत्र सत्यापन विवरण",
      verify_issued_to: "आवेदक का नाम:",
      verify_service: "सेवा का नाम:",
      verify_dept: "जारीकर्ता विभाग:",
      verify_date: "जारी करने का दिनांक:",
      verify_status: "प्रमाणपत्र स्थिति:",
      verify_demo_notice: "प्रदर्शन सूचना: यह प्रमाणपत्र एमपी सुविधा पोर्टल द्वारा प्रदर्शन उद्देश्य से जारी किया गया है और यह शासकीय वैधानिक अभिलेख नहीं है।",

      // How It Works
      how_eyebrow: "नागरिक मार्गदर्शन",
      how_title: "यह कैसे <span>काम करता है</span>",
      how_subtitle: "डिजिटल सेवाओं का लाभ उठाने हेतु सरल चार-चरणीय प्रक्रिया।",
      how_step1_title: "१. सेवा खोजें",
      how_step1_desc: "१२ श्रेणियों में से अथवा सर्च बार का उपयोग करके अपनी वांछित सेवा का चयन करें।",
      how_step2_title: "२. आवश्यकताएँ समझें",
      how_step2_desc: "पात्रता नियम, आवश्यक दस्तावेज़ों की सूची एवं समय-सीमा का अवलोकन करें।",
      how_step3_title: "३. ऑनलाइन आवेदन करें",
      how_step3_desc: "आवेदक का विवरण भरें, दस्तावेज़ अपलोड करें और विशिष्ट आवेदन क्रमांक प्राप्त करें।",
      how_step4_title: "४. प्रगति ट्रैक करें",
      how_step4_desc: "विभागीय अधिकारी की समीक्षा प्रगति देखें और स्वीकृत होने पर प्रमाणपत्र डाउनलोड करें।",

      // Announcements Section
      ann_eyebrow: "सूचनाएँ व समाचार",
      ann_title: "महत्वपूर्ण <span>सूचनाएँ एवं समाचार</span>",
      ann_subtitle: "पोर्टल अपडेट, सेवा दिशा-निर्देश एवं डिजिटल सुशासन से संबंधित नवीनतम सूचनाएँ।",

      // Feedback & Help Centre
      fb_eyebrow: "नागरिक विचार",
      fb_title: "प्रतिक्रिया एवं <span>नागरिक सहायता</span>",
      fb_subtitle: "डिजिटल सेवा अनुभव को और अधिक सुगम बनाने हेतु अपने बहुमूल्य सुझाव साझा करें।",
      fb_overall_rating: "समग्र पोर्टल अनुभव रेटिंग",
      fb_ease_rating: "नेविगेशन व सुगमता रेटिंग",
      fb_service_rating: "सेवा जानकारी स्पष्टता रेटिंग",
      fb_name_label: "आपका नाम (ऐच्छिक)",
      fb_role_label: "हितधारक श्रेणी",
      fb_suggestions_label: "आपके सुझाव एवं अनुभव",
      fb_suggestions_placeholder: "हमें बताएँ कि क्या अच्छा रहा और कहाँ सुधार की आवश्यकता है...",
      fb_complaint_label: "शिकायत अथवा समस्या का विवरण (ऐच्छिक)",
      fb_btn_submit: "प्रतिक्रिया जमा करें",

      // About Us Section
      about_eyebrow: "पोर्टल परिचय",
      about_title: "एमपी सुविधा <span>के बारे में</span>",
      about_p1: "एमपी सुविधा मध्य प्रदेश से संबंधित विभिन्न आवश्यक लोक सेवाओं की जानकारी खोजने एवं ऑनलाइन आवेदन प्रक्रियाओं को समझने हेतु एक स्वतंत्र नागरिक सूचना व प्रदर्शन पोर्टल है।",
      about_p2: "यह पोर्टल एकल खिड़की व्यवस्था, १२ नागरिक सेवा श्रेणियों, डिजिटल दस्तावेज़ अपलोड, पारदर्शी आवेदन ट्रैकिंग एवं सत्यापन योग्य प्रमाणपत्रों का एक आधुनिक अनुभव प्रदान करता है।",
      about_p3: "अस्वीकरण: एमपी सुविधा एक स्वतंत्र शैक्षणिक एवं प्रदर्शन पोर्टल है। यह मध्य प्रदेश शासन अथवा इसके किसी भी विभाग का आधिकारिक पोर्टल नहीं है और न ही उनसे संबद्ध है।",

      // Citizen Dashboard
      dash_title: "नागरिक डैशबोर्ड",
      dash_welcome: "स्वागत है,",
      dash_tab_applications: "मेरे आवेदन",
      dash_tab_certificates: "मेरे प्रमाणपत्र",
      dash_tab_notifications: "सूचनाएँ",
      dash_tab_profile: "प्रोफ़ाइल सेटिंग",
      dash_col_id: "आवेदन क्रमांक",
      dash_col_service: "सेवा का नाम",
      dash_col_dept: "विभाग",
      dash_col_date: "जमा दिनांक",
      dash_col_status: "वर्तमान स्थिति",
      dash_col_action: "कार्यवाही",

      // Officer & Admin Dashboard
      dash_officer_title: "विभागीय अधिकारी पोर्टल",
      dash_admin_title: "पोर्टल प्रशासन एवं सांख्यिकी",
      dash_total_apps: "कुल आवेदन",
      dash_pending_review: "लंबित समीक्षा",
      dash_approved_count: "स्वीकृत",
      dash_rejected_count: "अस्वीकृत",

      // Authentication Modals
      auth_login_title: "एमपी सुविधा में लॉग इन करें",
      auth_register_title: "नया नागरिक खाता बनाएँ",
      auth_email_label: "ईमेल पता",
      auth_password_label: "पासवर्ड",
      auth_name_label: "पूरा नाम",
      auth_mobile_label: "मोबाइल नंबर (१० अंक)",
      auth_address_label: "पता (शहर / जिला)",
      auth_btn_login: "लॉग इन करें",
      auth_btn_register: "खाता बनाएँ",
      auth_quick_demo: "त्वरित डेमो लॉगिन:",
      auth_demo_citizen: "नागरिक लॉगिन",
      auth_demo_officer: "अधिकारी लॉगिन",
      auth_demo_admin: "एडमिन लॉगिन",

      // Application Submission Modal
      apply_modal_title: "आवेदन प्रपत्र:",
      apply_step_info: "आवेदक की जानकारी",
      apply_step_docs: "दस्तावेज़ संलग्न करें",
      apply_demo_fee_notice: "प्रदर्शन सूचना: यह प्रदर्शन मोड है। वास्तविक भुगतान की आवश्यकता नहीं है।",
      apply_attach_label: "समर्थक दस्तावेज़ संलग्न करें (PDF, JPG, PNG अधिकतम ५ MB)",
      apply_review_declaration: "मैं घोषणा करता/करती हूँ कि दी गई जानकारी प्रदर्शन परीक्षण हेतु सत्य है।",

      // Footer
      footer_about_heading: "एमपी सुविधा के बारे में",
      footer_services_heading: "नागरिक सेवाएँ",
      footer_links_heading: "त्वरित लिंक",
      footer_help_heading: "सहायता केंद्र",
      footer_privacy: "गोपनीयता नीति",
      footer_terms: "नियम एवं शर्तें",
      footer_faq: "सामान्य प्रश्न (FAQ)",
      footer_contact: "संपर्क सूत्र",
      footer_rights: "सर्वाधिकार सुरक्षित। एमपी सुविधा एक स्वतंत्र प्रदर्शन सूचना पोर्टल है।"
    }
  },

  t(key) {
    const dict = this.translations[this.currentLang] || this.translations.en;
    return dict[key] !== undefined ? dict[key] : (this.translations.en[key] || key);
  },

  translateCategory(name) {
    if (this.currentLang === "hi") {
      return this.categories[name] || name;
    }
    return name;
  },

  translateDepartment(dept) {
    if (this.currentLang === "hi") {
      return this.departments[dept] || dept;
    }
    return dept;
  },

  translateStatus(status) {
    const st = this.statuses[status];
    if (st) {
      return st[this.currentLang] || st.en || status;
    }
    return status;
  },

  setLanguage(lang) {
    if (lang !== "en" && lang !== "hi") lang = "en";
    this.currentLang = lang;
    localStorage.setItem("mpsuvidha_lang", lang);
    localStorage.setItem("janseva_lang", lang);
    document.documentElement.lang = lang;

    // Sync select dropdown
    const selectEl = document.getElementById("language-select");
    if (selectEl) selectEl.value = lang;

    // Update all elements with data-i18n
    document.querySelectorAll("[data-i18n]").forEach(el => {
      const key = el.getAttribute("data-i18n");
      const val = this.t(key);
      if (val) el.innerHTML = val;
    });

    // Update placeholders with data-i18n-placeholder
    document.querySelectorAll("[data-i18n-placeholder]").forEach(el => {
      const key = el.getAttribute("data-i18n-placeholder");
      const val = this.t(key);
      if (val) el.setAttribute("placeholder", val);
    });

    // Update tooltips / titles with data-i18n-title
    document.querySelectorAll("[data-i18n-title]").forEach(el => {
      const key = el.getAttribute("data-i18n-title");
      const val = this.t(key);
      if (val) el.setAttribute("title", val);
    });

    // Notify other components to refresh localized lists
    window.dispatchEvent(new CustomEvent("languageChanged", { detail: { lang } }));
  }
};
