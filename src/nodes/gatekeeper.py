from semantic_router import Route
from ..settings.config import LLMFactory, get_settings
import logging 

logger = logging.getLogger(__name__)

#Router settings
medical_route = Route(
    name="medical",
    score_threshold=0.3,
    utterances=[
        # --- 1. Diseases  ---
        "how to cure flu and cold naturally",
        "early symptoms of diabetes type 2",
        "treatment options for chronic inflammation",
        "causes of high blood pressure and hypertension",
        "autoimmune disease triggers and diet",
        "warning signs of heart disease",
        "identifying stroke symptoms",
        "dealing with chronic fatigue syndrome",

        # --- 2. Medicals ---
        "health benefits of vitamin c and d",
        "is ashwagandha safe for long term use",
        "side effects of creatine monohydrate",
        "best magnesium supplements for sleep",
        "do nootropics actually improve brain function",
        "how ssri antidepressants work in the brain",
        "dangers of mixing supplements with medication",

        # --- 3. Diet ---
        "doctor advice on ketogenic and paleo diet",
        "negative health effects of processed sugar",
        "intermittent fasting schedule for weight loss",
        "how to improve gut microbiome health",
        "foods that lower cortisol and stress",
        "insulin resistance and metabolic syndrome",
        "impact of alcohol on liver health",

        # --- 4. Biohacking---
        "biohacking protocols for longevity and anti-aging",
        "benefits of sauna and cold plunge therapy",
        "optimizing circadian rhythm for better sleep",
        "increasing mitochondrial density and energy",
        "measuring hrv and sleep quality",
        "science of red light therapy",

        # --- 5. Psycho ---
        "coping strategies for anxiety and depression",
        "meditation effects on the brain structure",
        "adhd symptoms in adults",
        "psychology of trauma and healing",
        "neuroplasticity and brain training exercises",
        "impact of social media on mental health",

        # --- 6. Phisio ---
        "exercises for lower back pain relief",
        "how to fix bad posture and neck pain",
        "recovering from acl knee injury",
        "science of muscle hypertrophy and growth",
        "stretching routine for flexibility",
        "preventing common running injuries",

        # --- 7. Science ---
        "breakdown of recent clinical trials",
        "peer-reviewed studies on cancer treatment",
        "meta-analysis of nutritional data",
        "understanding statistical significance in studies"
        
        #--- 8. Myths and fakes 
        "debunking common medical myths and misconceptions",
        "why vaccines do not cause autism",
        "truth about detox teas and cleanses",
        "scientific fact checking of health claims",
        "is msg actually bad for your health",
        "misconceptions about drinking water requirements",
        "doctors reacting to tiktok health trends",
        "separating pseudoscience from evidence based medicine",
        "dangers of alternative medicine and homeopathy",
        "lies about weight loss and metabolism",
        "correcting false health information",
        "analyzing fake medical news"
    ],
)

from functools import lru_cache

@lru_cache(maxsize=1)
def get_cached_router():
    return LLMFactory.get_semantic_router(routes=[medical_route])

def gatekeeper_node(state):
    """Node handling state after ingesting. Handling whole text lookup and looking for semantic match to the medical topic"""
    if isinstance(state, dict):
        list_transcripted_chunks = state.get("transcript_chunks", [])
    else:
        list_transcripted_chunks = getattr(state, "transcript_chunks", [])
    
    settings = get_settings()
    chunk_size = settings.EMBEDDING_CHUNK_SIZE_ROUTER
    
    router = get_cached_router()

    for chunk_transcripted in list_transcripted_chunks:
        for i in range(0, len(chunk_transcripted), chunk_size):
            sub_chunk = chunk_transcripted[i:i+chunk_size]
            
            if len(sub_chunk) < 50:
                continue
                
            decision = router(sub_chunk)
            
            if isinstance(decision, list):
                decision = decision[0]
            
            if decision.name == "medical":
                logger.info(f"Gatekeeper: Found relevant medical content. ({decision.similarity_score:.2f})")
                return {"gatekeeper_verdict": "pass"}
    logger.info(f"Gatekeeper: REJECT")
    return {"gatekeeper_verdict": "reject"}