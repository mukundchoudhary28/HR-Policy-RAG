
# Create a comprehensive RAGAS evaluation set with detailed questions
# Each question is designed to test specific RAGAS metrics

ragas_eval_set = {
    "questions": [
        {
            "id": 1,
            "category": "Retrieval Accuracy - Exact Extraction",
            "question": "What is the specific Document ID and effective date of the current active HR Policy document that governs leave policies?",
            "expected_answer": "Document ID: DOC 002. Effective Date: 2025-01-01. The current active HR Policy document is Version 2/3 (DOC 002), which supersedes the archived Version 1 (DOC 001).",
            "ragas_metrics": ["faithfulness", "answer_relevancy"],
            "test_focus": "Exact document identification and metadata extraction from multiple document versions",
            "difficulty": "basic",
            "context_required": ["HR Policy v2/v3 metadata", "HR Policy v1 archived status"]
        },
        {
            "id": 2,
            "category": "Numerical Precision - Table Extraction",
            "question": "According to the Q3 Compensation and Benefits Policy, what is the exact company match percentage for Tier 2 employees (3+ years of service), and what is the corresponding Annual Match Cap in USD?",
            "expected_answer": "For Tier 2 (3+ years): Company Match is dollar-for-dollar up to 4% of salary, with an Annual Match Cap of $6,000 USD. Employee contributes 6% of base salary.",
            "ragas_metrics": ["faithfulness", "context_precision"],
            "test_focus": "Precise numerical extraction from tiered tables with multiple data points",
            "difficulty": "intermediate",
            "context_required": ["Q3 Compensation Policy Chapter 3 table", "Understanding of tier definitions"]
        },
        {
            "id": 3,
            "category": "Conflict Detection & Resolution",
            "question": "When evaluating sick leave allocation, there is a direct numerical conflict between HR Policy v2/v3 and US Leave Policy 2024. what is the specific discrepancy, and which document should be considered authoritative?",
            "expected_answer": "The conflict is: HR Policy v2/v3 states 5 days (40 hours) of paid sick leave annually, while US Leave Policy 2024 states 10 days of paid sick leave annually. Both documents are marked ACTIVE and 'Is Latest: Yes'. HR Policy v2/v3 has Effective Date 2025-01-01, while US Leave Policy 2024 has Effective Date 2024-01-01. The resolution requires determining policy hierarchy based on: (1) Effective dates (later date may indicate more recent policy), (2) Document status (ACTIVE vs ARCHIVED), (3) Regional applicability (US vs US/Canada), and (4) Specific policy type (general leave policy vs specific leave policy).",
            "ragas_metrics": ["faithfulness", "answer_relevancy", "context_recall"],
            "test_focus": "Detecting and reasoning through conflicting information across parallel policy documents",
            "difficulty": "advanced",
            "context_required": ["HR Policy v2/v3 sick leave section", "US Leave Policy 2024 sick leave section", "Document metadata for both (effective dates, status, regions)"]
        },
        {
            "id": 4,
            "category": "Multi-Hop Reasoning - Cross Document",
            "question": "An employee was onboarded as High-Risk under AML Policy CMP-AML-2.0 six months ago. If an audit is conducted today, what specific forms must be present in their EDD file according to the Customer Onboarding Policy, and how long must these records be retained?",
            "expected_answer": "According to Customer Onboarding Forms & Procedures (PRO-ONB-1.5), Enhanced Due Diligence (EDD) for High-Risk customers requires: (1) ID Verification Form (IDV-50), (2) Source of Wealth Declaration Form (SOW-300), and (3) minimum of three (3) external references. Per Section 5.0 of the same document, EDD documents retention requirement is 10 years after client relationship termination. This requires connecting AML Policy risk classification to Customer Onboarding procedural requirements and retention policies.",
            "ragas_metrics": ["faithfulness", "context_recall", "answer_relevancy"],
            "test_focus": "Chaining information across AML Policy (risk classification) and Customer Onboarding (procedures and retention)",
            "difficulty": "advanced",
            "context_required": ["AML Policy CMP-AML-2.0 Section 3.3 (High-Risk criteria)", "Customer Onboarding Section 4.2 (EDD requirements)", "Customer Onboarding Section 5.0 (retention)"]
        },
        {
            "id": 5,
            "category": "Temporal Reasoning - Effective Dates",
            "question": "The Data Breach Response Protocol (INC-REP-500) became effective on February 15, 2025. If a data breach occurred on February 10, 2025, which policy version would apply to the incident response, and why?",
            "expected_answer": "The Data Breach Response Protocol effective 2025-02-15 would NOT apply to a February 10, 2025 incident because the effective date is after the incident date. The organization would need to check if a previous version existed with earlier effective date, or determine if the protocol was in draft/review status as of February 10, 2025. The current active version (INC-REP-500, V1.2, Status: ACTIVE, Is Latest: Yes) would govern the response. This tests temporal reasoning and understanding of when policies become enforceable.",
            "ragas_metrics": ["faithfulness", "context_precision"],
            "test_focus": "Understanding policy effective dates and version applicability",
            "difficulty": "intermediate",
            "context_required": ["Data Breach Response Protocol effective date metadata", "Incident date context"]
        },
        {
            "id": 6,
            "category": "Procedural Specificity - Forms & Contacts",
            "question": "According to the Data Breach Response Protocol, if a Level 3 breach affecting 750 records is confirmed at 9:00 AM, by what specific time must the Legal Counsel, Executive Director, and DPO be verbally notified, and what are their exact contact details?",
            "expected_answer": "Notification must be completed by 10:00 AM (within 1 hour of confirmation). Contacts: Legal Counsel (Primary): Ms. R. Thompson, Ext. 4501, Mobile: 555-888-9999; Executive Director (Primary): Mr. A. Chen, Mobile: 555-777-1111; Data Protection Officer (DPO): J. Patel, Ext. 4503. Source: Chapter 3, Section 3.1 of Data Breach Response Protocol (INC-REP-500).",
            "ragas_metrics": ["faithfulness", "context_precision", "answer_relevancy"],
            "test_focus": "Precise extraction of procedural requirements: timelines, specific contact information, and escalation paths",
            "difficulty": "advanced",
            "context_required": ["Data Breach Response Protocol Chapter 3 Section 3.1 (contacts and timeline)", "Understanding of Level 3 breach definition (>500 records)"]
        },
        {
            "id": 7,
            "category": "Hierarchical Policy Application",
            "question": "For a new employee in their first year of service, which specific policy document contains the governing rules for: (1) PTO accrual rate per pay period, (2) PTO usage eligibility timing, and (3) Carryover limits? Provide specific section references.",
            "expected_answer": "HR Policy v2/v3 (DOC 002, Status: ACTIVE, Is Latest: Yes, Effective: 2025-01-01) governs all three aspects: (1) Section 4.1.1: Accrual rate is 3.08 hours per 80-hour pay period for employees with less than 1 year of service, (2) Section 4.1.1: New employees eligible to use accrued PTO after successfully completing 90-day probationary period, (3) Section 4.1.3: Carryover limit is maximum 40 hours (5 days) of unused PTO. Note: HR Policy v1 (DOC 001) is ARCHIVED and should not be used for current guidance.",
            "ragas_metrics": ["faithfulness", "context_recall", "answer_relevancy"],
            "test_focus": "Correctly identifying the hierarchical governing policy among multiple versions and applying specific sections to employee scenarios",
            "difficulty": "intermediate",
            "context_required": ["HR Policy v2/v3 Chapter 4 Sections 4.1.1, 4.1.2, 4.1.3", "Document status and effective date metadata", "Understanding of archived vs. active documents"]
        },
        {
            "id": 8,
            "category": "Granular Detail Extraction - Vesting Schedules",
            "question": "Under the Q3 Compensation Policy, an employee has contributed to their 401(k) for 2.5 years. What percentage of the Company Match is currently vested, and what specific Section governs this calculation?",
            "expected_answer": "After 2.5 years (2 years + 6 months), the employee has completed 2 full years of the 4-year graded vesting schedule. At 2 years: 50% vested (25% per year × 2 years). The specific governing section is Chapter 4, Section 4.2: 'Company matching contributions vest according to a 4-year graded schedule (25% per year). Full vesting (100%) occurs after four years of continuous employment.'",
            "ragas_metrics": ["faithfulness", "context_precision"],
            "test_focus": "Precise calculation of graded vesting status based on employment duration and specific policy section identification",
            "difficulty": "intermediate",
            "context_required": ["Q3 Compensation Policy Chapter 4 Section 4.2 (vesting schedule details)", "Employment tenure calculation", "Understanding of graded vs. immediate vesting"]
        },
        {
            "id": 9,
            "category": "Edge Case Handling - Literal vs. Intended",
            "question": "The current HR Policy (v2/v3) states that part-time employees working '999 hours or more per week' accrue PTO on a prorated basis. What is the apparent Typo in this requirement, what is the likely intended Meaning, and what does literal interpretation imply for compliance purposes?",
            "expected_answer": "Literal text states '999 hours or more per week.' This appears to be a typo where '999' likely intends to represent '20' or '30+' hours (standard part-time thresholds), but the document literally specifies 999. For compliance purposes, the literal interpretation (999+ hours/week) would mean almost no part-time employees qualify, while the intended interpretation (20-30+ hours/week) aligns with standard HR practice. This tests whether the system recognizes document errors versus intended policy.",
            "ragas_metrics": ["faithfulness", "answer_relevancy"],
            "test_focus": "Handling ambiguous or erroneous text while inferring intended meaning from context",
            "difficulty": "advanced",
            "context_required": ["HR Policy v2/v3 Section 4.1.1 (part-time threshold text)", "Understanding of standard HR part-time practices", "Ability to recognize potential documentation errors"]
        },
        {
            "id": 10,
            "category": "Form & Procedure Identification",
            "question": "What is the Complete Step-by-Step Process for Submitting a PTO Request under the Current HR Policy (v2/v3), including: (1) Form Name/Number, (2) Submission Method, (3) Advance Notice Requirement, (4) Minimum Usage Increment, and (5) Manager Approval Requirements?",
            "expected_answer": "Complete PTO Request Process under HR Policy v2/v3: (1) Form: TMO-100, (2) Submission: Through HRIS Portal to direct manager, (3) Advance Notice: At least two (2) weeks in advance per Section 4.1.2, (4) Minimum Usage: No less than four (4) hours per Section 4.1.2, (5) Manager Approval: Subject to managerial approval based on departmental staffing needs; approval may be denied during peak financial reporting periods (Jan 1-15, July 1-15) per Section 4.1.2. Source: HR Policy v2/v3, Chapter 4, Sections 4.1.2 and 4.1.1.",
            "ragas_metrics": ["faithfulness", "context_recall", "answer_relevancy"],
            "test_focus": "Comprehensive extraction of procedural steps, form identifiers, and conditional requirements",
            "difficulty": "intermediate",
            "context_required": ["HR Policy v2/v3 Chapter 4 Sections 4.1.1 and 4.1.2", "Understanding of form TMO-100", "Manager discretion clauses"]
        },
        {
            "id": 11,
            "category": "Geographic & Jurisdictional Specificity",
            "question": "Which Policy Document contains the 63-week Parental Leave entitlement for Canadian employees, and under what specific conditions can US employees in Canada access this Benefit?",
            "expected_answer": "The 63-week Parental Leave entitlement for Canadian employees is found in HR Policy v2/v3 (DOC 002), Section 4.3.5: Canadian Parental Leave. US employees working in Canada may be eligible under specific jurisdictional requirements or company international assignment policies, but the 63-week provision is specific to Canadian provincial standards referenced in that section. This requires distinguishing between geographic variations in the same base Policy Document.",
            "ragas_metrics": ["faithfulness", "context_recall"],
            "test_focus": "Geographic policy variations and jurisdiction-specific benefit applicability",
            "difficulty": "intermediate",
            "context_required": ["HR Policy v2/v3 Section 4.3.5 (Canadian Parental Leave)", "Understanding of geographic applicability within unified policy documents"]
        },
        {
            "id": 12,
            "category": "Risk-Based Classification Logic",
            "question": "According to AML Policy CMP-AML-2.0, a Prospective Client operates a Currency Exchange Business in a Jurisdiction on the FATF Watchlist, and the Ultimate Beneficial Owner is a Politically Exposed Person (PEP). What is the Risk Classification, and what specific Enhanced Due Diligence forms are required per the Customer Onboarding Policy?",
            "expected_answer": "Risk Classification: HIGH-RISK (meets 2 of 3 criteria: PEP + FATF watchlist jurisdiction + cash-intensive business sector). Required EDD Forms per Customer Onboarding Policy Section 4.2: (1) ID Verification Form (IDV-50), (2) Source of Wealth Declaration Form (SOW-300), (3) Minimum three (3) external references. This requires connecting AML risk criteria to Customer Onboarding procedural requirements across two distinct Policy Documents.",
            "ragas_metrics": ["faithfulness", "context_recall", "answer_relevancy"],
            "test_focus": "Applying risk classification logic from AML Policy to procedural requirements in Customer Onboarding Policy",
            "difficulty": "advanced",
            "context_required": ["AML Policy CMP-AML-2.0 Section 3.3 (High-Risk criteria)", "Customer Onboarding Policy Section 4.2 (EDD requirements)", "Ability to apply logical AND/OR conditions across criteria"]
        },
        {
            "id": 13,
            "category": "Incident Response Authority & Timelines",
            "question": "Under the Data Breach Response Protocol (INC-REP-500), for a Level 2 Breach affecting 600 records with Classified PII: (1) What is the Maximum Response Time for Initial Notification, (2) Who has Authority to Disconnect Systems for Containment, and (3) What Form Documents the Chain of Custody?",
            "expected_answer": "For Level 2 breach (600 records > 500, classified PII involved): (1) Initial notification to Legal Counsel, Executive Director, and DPO must be within ONE HOUR per Chapter 3, Section 3.1, (2) Authority to disconnect systems: IRT Lead (CISO) per Chapter 3, Section 3.2, regardless of operational impact, (3) Chain of custody documentation: Form INC-COC-01 per Chapter 4, Section 4.1. This requires precise extraction of timeline, Authority, and Form references from the Data Breach Response Protocol.",
            "ragas_metrics": ["faithfulness", "context_precision", "context_recall"],
            "test_focus": "Precise extraction of incident response timelines, authority levels, and documentation requirements",
            "difficulty": "advanced",
            "context_required": ["Data Breach Response Protocol Chapter 3 Sections 3.1 and 3.2", "Data Breach Response Protocol Chapter 4 Section 4.1", "Understanding of Level 2 breach thresholds (>500 records)"]
        },
        {
            "id": 14,
            "category": "Policy Evolution & Version Differences",
            "question": "How does the FMLA Substitution of Paid Leave requirement differ between the Archived HR Policy v1 and the Current HR Policy v2/v3, and what specific Language indicates this Policy Change?",
            "expected_answer": "HR Policy v1 (Archived): States in Section 4.3.3 'The Company does not require, but allows employees to use any available accrued PTO or sick leave concurrently with FMLA leave. The employee may choose to keep their paid leave and take the FMLA period as unpaid.' HR Policy v2/v3 (Current): States in Section 4.3.3 'The Company requires employees to use any available accrued PTO or sick leave concurrently with FMLA leave, applying the paid leave first until exhaustion. The remainder of the FMLA period will be unpaid.' The critical difference: v1 uses 'does not require, but allows' (optional substitution), while v2/v3 uses 'requires' (mandatory substitution). This represents a significant Policy evolution from optional to mandatory paid leave substitution.",
            "ragas_metrics": ["faithfulness", "context_recall", "answer_relevancy"],
            "test_focus": "Detecting Policy language differences that indicate substantive changes between Document Versions",
            "difficulty": "advanced",
            "context_required": ["HR Policy v1 Section 4.3.3", "HR Policy v2/v3 Section 4.3.3", "Comparison of Optional vs Mandatory Language"]
        },
        {
            "id": 15,
            "category": "Metadata & Classification Accuracy",
            "question": "What is the Document Type classification for the Data Breach Response Protocol (INC-REP-500), and how does this differ from the Document Type of the Q3 Compensation and Benefits Policy (HR-COMP-Q3)?",
            "expected_answer": "Data Breach Response Protocol (INC-REP-500) Document Type: 'work' (per document metadata table). Q3 Compensation and Benefits Policy (HR-COMP-Q3) Document Type: 'payroll'. This distinction is important for Document classification accuracy and understanding that 'work' type documents contain Incident Response protocols, while 'payroll' type documents contain Compensation and benefits administration rules.",
            "ragas_metrics": ["faithfulness", "context_precision"],
            "test_focus": "Accurate extraction and distinction of Document Type metadata across different Policy Documents",
            "difficulty": "basic",
            "context_required": ["Data Breach Response Protocol metadata table", "Q3 Compensation Policy metadata table", "Understanding of Document Type taxonomy"]
        },
        {
            "id": 16,
            "category": "SAR Reporting Specificity",
            "question": "Under the AML Policy CMP-AML-2.0: (1) To whom must Suspicious Activity be Reported, (2) What is the Specific Form Name/Number for Reporting, and (3) What is the Classification of this Form Type?",
            "expected_answer": "Per Section 4.0 of AML Policy CMP-AML-2.0: (1) Suspicious Activity must be reported to the designated Money Laundering Reporting Officer (MLRO), (2) Form Name/Number: SAR-INT-1, (3) This is a Suspicious Activity Report (SAR) form, which is a standard regulatory compliance document type. This requires exact extraction of: reporting chain of command, specific form identifier, and understanding of SAR as a specific compliance form category.",
            "ragas_metrics": ["faithfulness", "context_precision"],
            "test_focus": "Precise extraction of reporting obligations, form identifiers, and regulatory compliance categories",
            "difficulty": "intermediate",
            "context_required": ["AML Policy CMP-AML-2.0 Section 4.0", "Understanding of MLRO role", "Form SAR-INT-1 identification"]
        },
        {
            "id": 17,
            "category": "Complex Multi-Document Integration",
            "question": "An employee with 4 Years of Service (Tier 2) experiences a Level 2 Data Breach (600 Records, Classified PII) during their FMLA leave (12 weeks for serious health condition). They were Onboarded as High-Risk 6 months ago under AML Policy CMP-AML-2.0. Outline: (A) All applicable Policy Documents, (B) Specific Sections governing this scenario, (C) Required Actions and Forms, (D) Relevant Timelines, and (E) Retention Requirements that survive the incident.",
            "expected_answer": "This scenario requires Integration across Four Policy Documents: (1) HR Policy v2/v3 (DOC 002, ACTIVE): Governs PTO accrual (4.62 hours/pay period for Tier 2), Sick Leave availability (5 days), FMLA mandatory substitution of paid leave (Section 4.3.3), Probationary status (ineligible for FMLA if <12 months employment). (2) AML Policy CMP-AML-2.0: High-Risk classification triggered EDD requirements during Onboarding (IDV-50, SOW-300, 3 References - Section 3.3 and Customer Onboarding Section 4.2). Retention: 10 years (Customer Onboarding Section 5.0). (3) Data Breach Response Protocol INC-REP-500: Level 2 breach (600 records > 500) requires 1-hour notification (Chapter 3 Section 3.1), CISO disconnection authority (Chapter 3 Section 3.2), Chain of Custody Form INC-COC-01 (Chapter 4 Section 4.1), Final Report to Board within 30 days (Chapter 4 Section 4.2). (4) FMLA Specifics: Form FML-200 to HR Department (Section 4.3.4), 30-day notice for foreseeable leave (Section 4.3.4). This is the most Complex Question requiring Multi-Hop reasoning across all Four Documents with precise Timeline, Authority, and Form identification.",
            "ragas_metrics": ["faithfulness", "context_recall", "context_precision", "answer_relevancy"],
            "test_focus": "Maximum Complexity: Chained reasoning across HR Policy, AML Policy, Customer Onboarding, and Data Breach Protocol with Timeline and Retention integration",
            "difficulty": "advanced",
            "context_required": ["All Four Policy Documents: HR Policy v2/v3, AML Policy CMP-AML-2.0, Customer Onboarding PRO-ONB-1.5, Data Breach Response INC-REP-500", "Cross-reference tables for tier/level definitions", "FMLA eligibility criteria (12 months employment, 1,250 hours)"]
        }
    ]
}
