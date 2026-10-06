# Author: MilanWoj
from app.core.llm_client import complete_once, LLMError

CLARIFY_SYSTEM_PROMPT = """Tu évalues si une question est trop ambiguë pour être recherchée efficacement sur le web ou dans des documents.

Une question est ambiguë UNIQUEMENT si elle contient un pronom ou une référence démonstrative sans antécédent DANS LA QUESTION ELLE-MÊME (ex: "il a gagné combien de fois ?" sans dire qui, "cette entreprise" sans jamais la nommer, "la meilleure méthode" sans dire pour quoi).

Un nom propre, un acronyme, un titre de projet ou un terme technique que TU ne reconnais pas n'est PAS une ambiguïté : ce n'est pas à toi de le connaître, c'est le rôle de la recherche (web ou documents) de le retrouver. Ne demande JAMAIS de clarification sur un nom propre inconnu (ex: "LunarNav", "le rover", "le second document" cité dans une question qui contient déjà assez de contexte pour être recherchée tels quels).

Une question n'est PAS ambiguë si elle est autonome et compréhensible telle quelle, même si elle porte sur un sujet pointu ou inconnu de toi (ex: "quelle est la capitale de la France", "explique le RAG", "quelle précision vise le projet LunarNav ?", "quels capteurs le rover utilise-t-il ?").

Réponds sur une seule ligne :
- Si la question est claire : réponds exactement "CLEAR"
- Si la question est ambiguë : réponds par UNE question de clarification concise, en français, qui aide l'utilisateur à préciser sa demande.
"""


async def check_ambiguity(query: str) -> str | None:
    messages = [{"role": "system", "content": CLARIFY_SYSTEM_PROMPT}, {"role": "user", "content": query}]
    try:
        result = await complete_once(messages, max_tokens=60)
    except LLMError:
        return None

    result = result.strip()
    if result.upper().startswith("CLEAR"):
        return None
    return result