import json, hashlib
from typing import Optional, Dict
import numpy as np
import streamlit as st
from client import get_openai_client

@st.cache_data(show_spinner=False)
def load_facts():
    with open("fact.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    for d in data:
        d["_search_text"] = " ".join([
            d.get("title",""), d.get("summary",""),
            " ".join(d.get("tags", [])),
            d.get("id",""), d.get("type","")
        ])
    return data

def _facts_checksum(facts):
    h = hashlib.sha256()
    for d in facts:
        h.update((d.get("id","") + d.get("title","") + d.get("summary","")).encode("utf-8"))
    return h.hexdigest()

@st.cache_resource(show_spinner=False)
def embed_facts(facts, model="text-embedding-3-small", _checksum=None):
    client = get_openai_client()
    texts = [d["_search_text"] for d in facts]
    embs = client.embeddings.create(model=model, input=texts).data
    import numpy as _np
    M = _np.vstack([_np.array(e.embedding, dtype=_np.float32) for e in embs])
    return M

def cosine_sim(a, B):
    a = a / (np.linalg.norm(a) + 1e-9)
    B = B / (np.linalg.norm(B, axis=1, keepdims=True) + 1e-9)
    return B @ a

def make_query_text(persona_info: Dict, project_description: str, user_message: str = ""):
    place = persona_info.get('place') or persona_info.get('Place') or ""
    tags = [
        persona_info.get('values') or persona_info.get('personal_values') or "",
        persona_info.get('reasons') or persona_info.get('reason_for_visiting') or "",
    ]
    return " | ".join([place, project_description, user_message] + [str(t) for t in tags if t])

def _guess_area_code(place: str) -> Optional[str]:
    if not place:
        return None
    p = place.lower()
    if any(x in p for x in ["floridsdorf", "florisdorf", "1210", "21st", "21.", "xxi"]): return "FLR"
    if "karlsplatz" in p or "karls" in p: return "KAR"
    if "praterstern" in p or "prater" in p or "leopoldstadt" in p or "1020" in p or "2nd" in p or "2." in p: return "PRT"
    if "donaukanal" in p: return "DNK"
    return None

def retrieve_facts(facts, fact_embs, persona_info, project_description, user_message="", k=5):
    client = get_openai_client()
    qtext = make_query_text(persona_info, project_description, user_message)
    qemb = client.embeddings.create(model="text-embedding-3-small", input=qtext).data[0].embedding
    qemb = np.array(qemb, dtype=np.float32)

    sims = cosine_sim(qemb, fact_embs)

    place = (persona_info.get('place') or persona_info.get('Place') or "").lower()
    boosts = []
    for d in facts:
        t = (d["_search_text"] + " " + d.get("summary","")).lower()
        b = 0.0
        if place and place in t: b += 0.15
        if any(tag.lower() in qtext.lower() for tag in d.get("tags", [])): b += 0.1
        boosts.append(b)
    boosts = np.array(boosts, dtype=np.float32)
    scores = sims + boosts

    area = _guess_area_code(persona_info.get('place') or persona_info.get('Place') or "")
    if area:
        mask = np.array([
            1.0 if (str(d.get("id","")).upper().startswith(f"VIE-{area}-")
                    or area.lower() in " ".join(d.get("tags", [])).lower())
            else 0.0
            for d in facts
        ], dtype=np.float32)
        if mask.sum() > 0:
            scores = np.where(mask > 0, scores + 0.5, -1e9)

    top_idx = scores.argsort()[::-1][:k]
    return [facts[i] for i in top_idx]
