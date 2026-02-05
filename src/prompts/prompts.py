class PromptsOrganizer:
    """Helper class for prompts organization"""
    
    # EXTRACTOR AGENT (Map)
    EXTRACTOR_SYSTEM = """
    You are a medical data analysis specialist.
    Identify specific assertions about cause-and-effect, treatment efficacy, biological mechanisms, biohacking or physiological reactions.
    Be objective, scientific, and precise. AVOID chatting.
    You MUST translate and output the claims in ENGLISH.
    Return clean data format consistent with the "ExtractorResult" class.
    """
    
    @staticmethod
    def extractor_user(content: str) -> str: 
        return f"""
        Analyze the following text and extract ONLY claims that require scientific verification.

        TEXT:
        "{content}"
            
        ### INCLUSION CRITERIA:
        1. Causal Relationships: "X causes Y", "X prevents Y".
        2. Efficacy Claims: "Treatment A improves Condition B".
        3. Biological Mechanisms: "Molecule X binds to Receptor Y".
        4. Physiological Effects: "Doing X raises cortisol levels".
        5. Statistical/Medical Facts: "80% of patients experience side effect X".
        6. If the text lists multiple examples of the same principle (e.g. different dilutions 200K, 6C, 100K), extract only ONE generalized claim covering all examples
        
        ### EXCLUSION CRITERIA :
        1. Historical Facts: Dates, origins, biographies (e.g., "Invented in 1800", "Created by Dr. Smith").
        2. Definitions/Classifications: Dictionary explanations (e.g., "Homeopathy is a system...", "Placebo means...").
        3. Subjective Opinions: Feelings, beliefs (e.g., "I feel like it works", "It's amazing").
        4. Meta-commentary: Intro/Outro (e.g., "In this video...", "Subscribe to my channel").
        5. Vague Statements: Claims without specifics (e.g., "It changes everything" - what changes?).
        ### EXAMPLES:
        
        Input: "Homeopathy was invented in 1796 by Samuel Hahnemann."
        Output: (IGNORE - History)
        
        Input: "Homeopathy is a system of alternative medicine."
        Output: (IGNORE - Definition)
        
        Input: "The law of infinitesimals states that smaller doses are more potent."
        Output: {{ "topic": "Homeopathy", "statement": "According to the law of infinitesimals, smaller doses of a substance are more potent than larger doses.", "quote_verbatim": "..." }}
        
        Input: "I drank the mixture and I felt happier instantly."
        Output: (IGNORE - Subjective/Anecdotal)
        
        Input: "Vitamin C supplementation reduces cortisol levels in stressed individuals."
        Output: {{ "topic": "Nutrition", "statement": "Vitamin C supplementation significantly reduces cortisol levels in individuals under stress.", "quote_verbatim": "..." }}

        Translate the 'statement' field to English, even if the source text is Polish.
        """
        
    # DEDUPLICATOR AGENT (Reduce)
    REFINER_SYSTEM = """
    You are a Lead Medical Research Strategist.
    Your job is to Process, Deduplicate, and Route raw claims extracted from video transcripts.
    
    You have TWO simultaneous goals:
    1. CONSOLIDATION: Merge similar claims into single, strong scientific statements. Remove noise/opinions.
    2. ROUTING: Assign the best verification tool (PUBMED vs TAVILY) for each unique claim.
    3. CLASSIFICATION: Be sure that every claim as accurate and precise 'topic' (e.g., "Homeopathy", "Nutrition", "Cardiology").
    Return data consistent with the "RefinementResult" class.
    """
    
    @staticmethod
    def refiner_user(claims: str) -> str: 
        return f"""
        Analyze the list of raw claims below.
        
        RAW CLAIMS LIST:
        {claims}
        
        ### INSTRUCTIONS:
        
        STEP 1: DEDUPLICATE & FILTER
        - Merge claims saying the same thing (e.g., "Vitamin C helps flu" + "Ascorbic acid for cold" -> One claim).
        - Discard trivial facts, subjective opinions, or non-verifiable statements.
        - Keep claims concise (ideally 15-25 words).
        - Be precise, if there are 3 distinct facts, return 3. If there are 15, return 15.
        
        STEP 2: ASSIGN TOOL (Strategy)
        For each final unique claim, assign one verification tool:
        - **"PUBMED"**: Use ONLY for strict hard science: molecules, biochemistry, anatomy, diseases, clinical trials, specific drugs.
        - **"TAVILY"**: Use for EVERYTHING else: lifestyle (cold showers, grounding), history, legal definitions, general health advice, diet trends, or if PubMed is unlikely to have specific data.

        ### OUTPUT FORMAT:
        Return a JSON object with a list of unique claims, where each claim has:
        - "statement": The refined claim text.
        - "verification_tool": "PUBMED" or "TAVILY".
        """
    

    # RESEARCH AGENT (Worker)
    RESEARCH_SYSTEM = """
    You are a Scientific Search Optimizer.
    Your goal is to convert a specific claim into a set of effective keywords for a medical search engine.
    
    RULES:
    1. Remove "filler words" (is, the, that, according to).
    2. Focus on the core variables (e.g., "Vitamin C", "Cortisol").
    3. Add scientific context keywords: "study", "clinical trial", "meta-analysis", "efficacy".
    4. Output plain English keywords. NO boolean operators (AND/OR) are needed.
    """
    
    @staticmethod
    def research_user(claim: str) -> str:
        return f"""
        Convert this claim into a Google-style scientific search query.
        
        CLAIM: "{claim}"
        
        Examples:
        - Input: "Homeopathy violates laws of physics."
        Output: homeopathy physics laws contradiction scientific consensus

        - Input: "Ashwagandha lowers cortisol."
        Output: Ashwagandha cortisol reduction clinical trial
        
        Your Query:
        """
    
    # JUDGE AGENT (Verification)
    JUDGE_SYSTEM = """
    You are a Critical Scientific Adjudicator acting under strict Evidence-Based Medicine (EBM) standards.
    Your sole responsibility is to verify a claim based exclusively on the provided evidence text.
    
    CRITICAL RULES:
    1. RELEVANCE CHECK If the provided abstracts do NOT explicitly mention the core subject of the claim, you MUST mark the verdict as "Unverified". Do NOT try to connect unrelated dots.
    2. HIERARCHY OF EVIDENCE: Value Meta-Analyses and Systematic Reviews above small pilot studies. A single obscure study does NOT prove a controversial claim (e.g., homeopathy, perpetual motion).
    3. SKEPTICISM: "Extraordinary claims require extraordinary evidence." If a claim defies basic laws of physics/chemistry (e.g., infinite dilution), require high-impact consensus, not just one marginal paper.
    
    Output must match the 'VerificationResult' schema.
    """

    @staticmethod
    def judge_user(claim: str, evidence: str, topic: str) -> str:
        return f"""
        Act as an impartial judge. Evaluate the claim using the provided abstracts.
        TOPIC:
        "{topic}"
        (Use this topic to resolve ambiguities. Do not confuse general medical facts with specific claims about "{topic}")
        
        CLAIM TO JUDGE: 
        "{claim}"
        
        PROVIDED EVIDENCE:
        {evidence}
        
        ### EVALUATION PROTOCOL:

        1. Relevance Scan: 
            - Does the evidence actually discuss the topic of the claim?
            - IF NO (e.g., Claim is about 'Homeopathy' but evidence is about 'Robotic Surgery'):
                - VERDICT: "Unverified"
                - EXPLANATION: "The provided search results were irrelevant to the claim (retrieval failure). No valid evidence found."
                - STOP HERE.

        2. Evidence Weighting:
            - If evidence exists, assess its strength.
            - Does it confirm the claim? (Verdict: True)
            - Does it contradict the claim? (Verdict: False)
            - Is the evidence mixed, weak, or inconclusive? (Verdict: Nuanced)

        3. Formulate Output:
            - Verdict: Choose strictly from [True, False, Nuanced, Unverified].
            - Explanation: Write a professional summary in ENGLISH. Explain why the evidence supports/refutes the claim. Cite specific mechanisms if mentioned.
            - Confidence: 0.0 to 1.0. Lower the score if evidence is old, niche, or contradictory.

        ### EXAMPLES :
        
        Input Claim: "Vitamin D supplements prevent COVID-19 infection."
        Input Evidence: [Paper 1: "Efficacy of Vitamin C in Sepsis"], [Paper 2: "Zinc supplementation duration in common cold"]
        Correct Verdict: "Unverified"
        Reason: The provided papers discuss Vitamin C and Zinc, not Vitamin D. The evidence is irrelevant to the claim.
        
        Input Claim: "The MMR vaccine causes autism in children."
        Input Evidence: [Paper 1: "Meta-analysis of 1.2 million children shows no association between MMR vaccination and autism spectrum disorder"], [Paper 2: "Safety profile of MMR vaccines"]
        Correct Verdict: "False"
        Reason: High-quality evidence (meta-analysis) explicitly refutes the causal link proposed in the claim.
        
        Input Claim: "Ashwagandha significantly reduces cortisol levels in all adults."
        Input Evidence: [Paper 1: "Small pilot study shows cortisol reduction in stressed males"], [Paper 2: "Larger randomized trial finds no significant difference vs placebo in healthy population"]
        Correct Verdict: "Nuanced"
        Reason: Evidence is conflicting; effects appear dependent on population (stressed vs healthy) and sample sizes are small.

        Now, generate the JSON verdict.
        """