# Author: MilanWoj
from datetime import date
from app.core.llm_client import complete_once, LLMError

REWRITE_SYSTEM_PROMPT = """Tu es un outil de reformulation de requêtes pour un moteur de recherche web. Nous sommes le {today}.

Réponds sur EXACTEMENT deux lignes, sans rien d'autre :
Ligne 1 : la requête de recherche reformulée (5 à 10 mots-clés concrets, noms propres et termes factuels uniquement). N'utilise JAMAIS de mots interrogatifs seuls comme "quel", "qui", "comment" en début de requête : reformule en affirmation ou en groupe nominal (ex: "qui a gagné X" -> "vainqueur X", pas "quel est le gagnant de X").
Ligne 2 : une fenêtre temporelle parmi day, week, month, year, ou none si la question ne porte pas sur un événement récent/actuel.

Exemple :
Question : "quel est le gagnant de la dernière coupe du monde ?"
Réponse :
vainqueur coupe du monde football 2026 résultat final
month
"""


async def rewrite_for_search(query: str) -> tuple[str, str | None]:
    system = REWRITE_SYSTEM_PROMPT.format(today=date.today().isoformat())
    messages = [{"role": "system", "content": system}, {"role": "user", "content": query}]

    try:
        result = await complete_once(messages, max_tokens=60)
    except LLMError:
        return query, None

    lines = [line.strip() for line in result.strip().splitlines() if line.strip()]
    if not lines:
        return query, None

    rewritten_query = lines[0].strip('"').strip("'") or query
    time_range = lines[1].lower() if len(lines) > 1 else "none"
    time_range = time_range if time_range in {"day", "week", "month", "year"} else None

    return rewritten_query, time_range
