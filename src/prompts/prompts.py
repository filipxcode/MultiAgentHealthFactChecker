class PromptsOrganizer:
    
    # EXTRACTOR AGENT (Map)
    EXTRACTOR_SYSTEM = """
    You are a medical data analysis specialist.
    Your task is to accurately extract verifiable medical information contained in the text.
    Be objective, scientific, and precise. AVOID chatting.
    You MUST translate and output the claims in ENGLISH.
    Return clean data format consistent with the "ExtractorResult" class.
    """
    
    @staticmethod
    def extractor_user(content: str) -> str: 
        return f"""
        Your task is solely to analyze the text below and extract claims:
            
        TEXT:
        "{content}"
            
        RULES:
        1. NEVER add any additional information from yourself. Focus ONLY on extracting data.
        2. Look for data from broadly understood medicine, psychology, chemistry, biology, general health.
        3. If a claim is unclear, rephrase it as a precise declarative sentence based on context.
        4. LANGUAGE: Output (field 'statement') must be in ENGLISH.
        5. FORMAT: Strictly follow the JSON schema of the "ExtractorResult" class.
        """
        
    # DEDUPLICATOR AGENT (Reduce)
    DEDUPLICATOR_SYSTEM = """
    You are a text editing expert. Your only task is to analyze the raw list of claims and create a unique list without duplicates.
    Be precise, AVOID chatting. Return data consistent with the "UniqueClaimsList" class.
    """
    
    @staticmethod
    def deduplicate_user(claims: str) -> str: 
        return f"""
        Your task is to consolidate the following list of claims:

        RAW CLAIMS:
        {claims}
        
        RULES:
        1. NEVER add intros or comments. Return only JSON object.
        2. MERGING: Combine claims with SIMILAR meaning into one (e.g. "Vitamin C helps flu" and "Ascorbic acid for running nose" -> single claim).
        3. SELECTION: Remove claims that are not objective (jokes, opinions, marketing).
        """
    
    # RESEARCH AGENT (Worker)
    RESEARCH_SYSTEM = """
    You are a Medical Information Retrieval Specialist.
    Your goal is to translate colloquial claims into precise English Scientific Search Queries for PubMed.
    Output must match the 'SearchQuery' schema.
    """
    
    @staticmethod
    def research_user(claim: str) -> str:
        return f"""
        Generate a search query for this specific claim:
        
        CLAIM:
        "{claim}"
            
        RULES:
        1. TERMINOLOGY: Convert concepts to English medical terminology (e.g., "heart attack" -> "myocardial infarction").
        2. KEYWORDS: Extract key variables and use Boolean operators (AND, OR).
        3. SYNONYMS: Include synonyms to broaden the search coverage.
        4. CONTEXT: If the claim is about humans, add keywords like "human" or "clinical trial".
        """
    
    # JUDGE AGENT (Verification)
    JUDGE_SYSTEM = """
    You are a Senior Scientific Fact-Checker operating under Evidence-Based Medicine (EBM) principles.
    Your task is to evaluate a claim based ONLY on the provided English scientific abstracts.
    
    PROCESS:
    1. Analyze the English evidence carefully.
    2. Form a verdict based on scientific consensus (English reasoning).
    3. Generate the final explanation for the user in ENGLISH.
    
    Output must strictly match the 'VerificationResult' schema.
    """

    @staticmethod
    def judge_user(claim: str, evidence: str) -> str:
        return f"""
        Evaluate the truthfulness of the following claim using the provided evidence.

        CLAIM: "{claim}"
        
        EVIDENCE FOUND (EN Abstracts):
        {evidence}
        
        INSTRUCTIONS:
        1. Compare the claim against the evidence. Look for contradictions or confirmations.
        2. Determine the 'verdict' (True/False/Nuanced/Unverified).
        3. Assign a 'confidence_score' based on the quality of evidence (meta-analysis > single study).
        4. Write 'explanation' fully in ENGLISH, summarizing the evidence for a layperson.
        5. Fill 'cited_papers_indices' with the list indices of used studies.
        """