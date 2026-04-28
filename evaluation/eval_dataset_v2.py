# evaluation/eval_dataset.py

ragas_eval_set = {
    "questions": [

        # ── AML Policy ────────────────────────────────────────────────────────

        {
            "id": "AML-01",
            "category": "aml_policy",
            "question": "Under what three conditions is a client classified as High-Risk under the AML policy?",
            "expected_answer": "A client is classified as High-Risk if they are a Politically Exposed Person (PEP), their source of wealth originates from a jurisdiction on the FATF watchlist, or they operate in a cash-intensive business sector such as currency exchange.",
            # RAG ASPECT: Multi-part retrieval — the answer requires the LLM to retrieve
            # and list all three conditions from a single chunk without omitting any.
            # Tests whether your chunking keeps the full enumerated list intact.
            "rag_aspect": "multi_part_retrieval",
            "ragas_metrics": ["faithfulness", "answer_relevancy", "context_precision", "context_recall"]
        },
        {
            "id": "AML-02",
            "category": "aml_policy",
            "question": "Who must employees report suspicious activity to, and what form must be used?",
            "expected_answer": "All employees must report suspicious activity to the designated Money Laundering Reporting Officer (MLRO) using Form SAR-INT-1.",
            # RAG ASPECT: Exact entity extraction — tests whether the RAG retrieves and
            # faithfully reproduces specific named entities (MLRO, SAR-INT-1) without
            # hallucinating a different role name or form number.
            "rag_aspect": "exact_entity_extraction",
            "ragas_metrics": ["faithfulness", "answer_relevancy", "context_precision", "context_recall"]
        },
        {
            "id": "AML-03",
            "category": "aml_policy",
            "question": "How does the firm classify Low-Risk clients under the AML policy?",
            "expected_answer": "Low-Risk clients are publicly traded, regulated entities in FATF-approved jurisdictions.",
            # RAG ASPECT: Noise resistance — the document contains definitions for Low,
            # Medium, and High risk in close proximity. Tests whether retrieval fetches
            # only the relevant chunk and the LLM doesn't blend in Medium/High risk
            # criteria into its answer.
            "rag_aspect": "noise_resistance",
            "ragas_metrics": ["faithfulness", "answer_relevancy", "context_precision", "context_recall"]
        },

        # ── Customer Onboarding ───────────────────────────────────────────────

        {
            "id": "ONB-01",
            "category": "onboarding",
            "question": "What forms are required for Enhanced Due Diligence (EDD) when onboarding a High-Risk customer?",
            "expected_answer": "EDD requires the ID Verification Form (IDV-50), the Source of Wealth Declaration Form (SOW-300), and a minimum of three external references.",
            # RAG ASPECT: Cross-document reasoning — answering correctly requires knowing
            # that a customer is High-Risk (defined in AML_policy.docx) and then looking
            # up the EDD form list (defined in Customer_Onboarding.docx). Tests whether
            # your retriever fetches relevant chunks from two different documents.
            "rag_aspect": "cross_document_reasoning",
            "ragas_metrics": ["faithfulness", "answer_relevancy", "context_precision", "context_recall"]
        },
        {
            "id": "ONB-02",
            "category": "onboarding",
            "question": "How long must EDD documents be retained after a client relationship ends?",
            "expected_answer": "All EDD documents must be retained for ten (10) years after the client relationship is terminated.",
            # RAG ASPECT: Numerical precision — tests whether the RAG faithfully returns
            # the exact retention period (10 years) without rounding, paraphrasing it
            # away, or confusing it with a different retention rule.
            "rag_aspect": "numerical_precision",
            "ragas_metrics": ["faithfulness", "answer_relevancy", "context_precision", "context_recall"]
        },
        {
            "id": "ONB-03",
            "category": "onboarding",
            "question": "What documentation is needed for Low or Medium Risk customer onboarding?",
            "expected_answer": "Low and Medium Risk customers require only a standard government-issued photo ID and the basic KYC Form (KYC-100).",
            # RAG ASPECT: Scope boundary — the question is about SDD, but EDD content
            # lives nearby in the same document. Tests whether the retriever returns the
            # SDD chunk specifically and whether the LLM avoids adding EDD requirements
            # that don't apply here.
            "rag_aspect": "scope_boundary",
            "ragas_metrics": ["faithfulness", "answer_relevancy", "context_precision", "context_recall"]
        },

        # ── Data Breach ───────────────────────────────────────────────────────

        {
            "id": "INC-01",
            "category": "data_breach",
            "question": "What must an employee do immediately upon identifying a suspected data breach?",
            "expected_answer": "The employee must immediately notify the Tier 1 help desk and complete initial report INC-RPT-1.",
            # RAG ASPECT: Procedural ordering — tests whether the RAG retrieves the
            # first step of a multi-step process and presents it as the immediate
            # action, rather than conflating it with later escalation steps.
            "rag_aspect": "procedural_ordering",
            "ragas_metrics": ["faithfulness", "answer_relevancy", "context_precision", "context_recall"]
        },
        {
            "id": "INC-02",
            "category": "data_breach",
            "question": "Within what timeframe must key contacts be notified for a Level 2 or Level 3 breach, and who are they?",
            "expected_answer": "If the breach involves more than 500 records or classified PII, Legal Counsel (Ms. R. Thompson), the Executive Director (Mr. A. Chen), and the Data Protection Officer (J. Patel) must all be contacted verbally within one hour.",
            # RAG ASPECT: Hallucination resistance on sensitive data — this chunk
            # contains real-looking names, extensions, and mobile numbers. Tests whether
            # the LLM faithfully reproduces them or fabricates plausible-sounding
            # replacements. A faithfulness score drop here is a red flag.
            "rag_aspect": "hallucination_resistance",
            "ragas_metrics": ["faithfulness", "answer_relevancy", "context_precision", "context_recall"]
        },
        {
            "id": "INC-03",
            "category": "data_breach",
            "question": "Within how many days must the IRT issue a final breach report, and who is the recipient?",
            "expected_answer": "The IRT must issue a final report to the Board of Directors within 30 days of incident closure.",
            # RAG ASPECT: Compound fact retrieval — the answer requires two distinct
            # facts (the deadline AND the recipient) to be present in the same response.
            # Tests whether the LLM answers both parts or silently drops one.
            "rag_aspect": "compound_fact_retrieval",
            "ragas_metrics": ["faithfulness", "answer_relevancy", "context_precision", "context_recall"]
        },

        # ── HR Policy — version conflict tests ───────────────────────────────
        # HR_policy.docx   = DOC 001, ARCHIVED, effective 2024-01-01 (v1)
        # HR_policy_v2.docx = DOC 002, ACTIVE,   effective 2025-01-01 (v2)
        # The correct answer differs between versions for all four questions below.
        # The RAG must retrieve from v2 only.

        {
            "id": "HR-01",
            "category": "hr_policy",
            "question": "How many days of unused PTO can an employee carry over to the next calendar year?",
            "expected_answer": "Under the current active policy (v2), a maximum of 40 hours (5 days) of unused PTO may be carried over. Any unused time over 40 hours is forfeited on January 1st.",
            # RAG ASPECT: Document versioning — v1 says 3 days carryover, v2 says 5 days.
            # Tests whether your metadata filtering (status=ACTIVE / is_latest=Yes)
            # correctly excludes the archived document at retrieval time. If the RAG
            # returns "3 days" it has retrieved from the wrong version.
            "rag_aspect": "document_versioning",
            "ragas_metrics": ["faithfulness", "answer_relevancy", "context_precision", "context_recall"]
        },
        {
            "id": "HR-02",
            "category": "hr_policy",
            "question": "How much advance notice must an employee give when requesting PTO?",
            "expected_answer": "Under the current active policy (v2), employees must submit PTO requests at least two (2) weeks in advance through the HRIS Portal (Form TMO-100).",
            # RAG ASPECT: Document versioning — v1 says 1 week notice, v2 says 2 weeks.
            # A second check on whether the retriever is version-aware. The phrasing
            # of both versions is similar enough that a naive vector search may rank
            # v1 equally or higher.
            "rag_aspect": "document_versioning",
            "ragas_metrics": ["faithfulness", "answer_relevancy", "context_precision", "context_recall"]
        },
        {
            "id": "HR-03",
            "category": "hr_policy",
            "question": "Is an employee required to use their accrued PTO concurrently with FMLA leave?",
            "expected_answer": "Yes. Under the current active policy (v2), the company requires employees to use any available accrued PTO or sick leave concurrently with FMLA leave, applying the paid leave first until exhaustion. The remainder of the FMLA period will then be unpaid.",
            # RAG ASPECT: Policy inversion across versions — v1 says PTO substitution is
            # optional ("does not require, but allows"), v2 says it is mandatory
            # ("requires"). This is a direct contradiction. Tests whether the LLM
            # correctly answers "required" and not "optional", which would indicate it
            # retrieved from the wrong document.
            "rag_aspect": "policy_inversion",
            "ragas_metrics": ["faithfulness", "answer_relevancy", "context_precision", "context_recall"]
        },
        {
            "id": "HR-04",
            "category": "hr_policy",
            "question": "What are the FMLA eligibility criteria for US employees?",
            "expected_answer": "To be eligible for FMLA leave, a US employee must have worked for the company for at least 12 months, completed at least 1,250 hours of service in the preceding 12-month period, and work at a site where the company employs at least 50 employees within 75 miles.",
            # RAG ASPECT: Multi-condition completeness — the correct answer requires all
            # three eligibility conditions. Tests whether the retriever fetches the full
            # eligibility section and whether the LLM reproduces all conditions without
            # dropping the "50 employees within 75 miles" clause, which is the most
            # commonly omitted detail.
            "rag_aspect": "multi_condition_completeness",
            "ragas_metrics": ["faithfulness", "answer_relevancy", "context_precision", "context_recall"]
        },

        # ── Compensation & Benefits ───────────────────────────────────────────

        {
            "id": "COMP-01",
            "category": "compensation",
            "question": "What is the 401(k) company match for a Tier 2 employee (3+ years of service) and what is the annual cap?",
            "expected_answer": "For Tier 2 employees (3+ years of service), the company matches dollar-for-dollar up to 4% of the employee's base salary, with an annual match cap of $6,000 USD.",
            # RAG ASPECT: Table retrieval and row disambiguation — the answer lives inside
            # a 3-row table. Tests whether your chunking preserves tabular structure and
            # whether the LLM picks the correct row (Tier 2) without mixing in Tier 1
            # or Executive figures.
            "rag_aspect": "table_retrieval",
            "ragas_metrics": ["faithfulness", "answer_relevancy", "context_precision", "context_recall"]
        },
        {
            "id": "COMP-02",
            "category": "compensation",
            "question": "When do company 401(k) matching contributions become fully vested?",
            "expected_answer": "Company matching contributions vest on a 4-year graded schedule at 25% per year. Full vesting (100%) occurs after four years of continuous employment. Employee contributions are immediately 100% vested.",
            # RAG ASPECT: Contrast within a single chunk — both employee contributions
            # (immediate vesting) and company contributions (4-year graded) are described
            # in the same section. Tests whether the LLM correctly distinguishes between
            # the two and answers only about company contributions without conflating them.
            "rag_aspect": "intra_chunk_contrast",
            "ragas_metrics": ["faithfulness", "answer_relevancy", "context_precision", "context_recall"]
        },

    ]
}