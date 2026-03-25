"""
Healf Personalisation — Backend real-time tier.
FastAPI service serving personalised recommendations within 200ms.
In production this would connect to Neo4j and a trained ranking model.
Here we use the mock knowledge graph with hand-crafted features.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import time

from backend.knowledge_graph import (
    get_user,
    get_product,
    get_user_goals,
    get_products_for_goals,
    get_stack_gaps,
    get_biomarker_recommendations,
    get_why_right_for_you,
    get_complementary_products,
    get_popular_for_goal,
)
from data.mock_data import PRODUCTS, POPULAR_BY_GOAL

app = FastAPI(title="Healf Personalisation API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─── Models ───────────────────────────────────────────────────────────────────

class HelixMessage(BaseModel):
    user_id: str
    message: str


class SessionSignal(BaseModel):
    user_id: Optional[str] = None
    viewed_products: list[str] = []
    pillar_intent: Optional[str] = None  # inferred by browser model


# ─── Experience 1 — Helix chips personalisation ───────────────────────────────

@app.get("/helix/chips/{user_id}")
def get_helix_chips(user_id: str):
    """
    Returns personalised Helix prompt chips.
    For new users: generic onboarding chips.
    For known users: chips based on their profile and recent activity.
    """
    user = get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    goals = user.get("goals", [])
    purchases = user.get("purchases", [])
    helix_profile = user.get("helix_profile", {})
    zone_member = user.get("zone_member", False)

    # Cold start — no data at all
    if not goals and not purchases:
        return {
            "chips": [
                "What's bringing you to Healf today?",
                "Help me find the right supplements",
                "I want to improve my sleep",
                "What should I take for more energy?"
            ],
            "context": "cold_start"
        }

    # Known user — personalise chips
    chips = []

    # Chip 1: based on their primary goal
    if goals:
        primary_goal = goals[0].lower()
        chips.append(f"How is your {primary_goal.replace('better ', '')} lately?")

    # Chip 2: based on what they're subscribed to
    subscriptions = user.get("subscriptions", [])
    if subscriptions:
        product_name = PRODUCTS.get(subscriptions[0], {}).get("name", "your supplement")
        chips.append(f"Is {product_name} working for you?")

    # Chip 3: Zone member — biomarker follow up
    if zone_member and user.get("biomarkers"):
        chips.append("Review my latest blood results")
    else:
        chips.append("What does my supplement stack look like?")

    # Chip 4: always useful
    chips.append("What am I missing from my stack?")

    return {
        "chips": chips[:4],
        "context": "personalised",
        "user_goals": goals
    }


# ─── Experience 2 — Ranked For You shelf ──────────────────────────────────────

@app.get("/foryou/{user_id}")
def get_for_you(user_id: str, pillar_intent: Optional[str] = None):
    """
    Returns personalised ranked product shelf.
    pillar_intent is passed from the browser model (on-browser tier).
    Falls back gracefully at each step.
    """
    start = time.time()
    user = get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    goals = user.get("goals", [])
    purchases = user.get("purchases", [])
    subscriptions = user.get("subscriptions", [])
    zone_member = user.get("zone_member", False)
    already_owns = set(purchases + subscriptions)

    # Cold start — no goals, no purchases
    if not goals and not purchases:
        popular = list(PRODUCTS.keys())[:8]
        return {
            "shelf_title": "Top picks this week",
            "context": "cold_start",
            "products": _format_products(popular),
            "message": "Take the quiz to get products picked for you",
            "latency_ms": round((time.time() - start) * 1000, 1)
        }

    # Zone member — biomarker-aware recommendations first
    biomarker_recs = []
    if zone_member:
        biomarker_recs = [r["product_id"] for r in get_biomarker_recommendations(user_id)]

    # Stack gap detection — only when we have purchase history
    stack_gaps = []
    if len(purchases) >= 2:
        stack_gaps = get_stack_gaps(user_id)

    # Goal-based ranking from knowledge graph
    goal_based = get_products_for_goals(goals, exclude_product_ids=list(already_owns))

    # Boost by browser session intent if available
    if pillar_intent:
        goal_based = _boost_by_pillar(goal_based, pillar_intent)

    # Merge: biomarker first, then gaps, then goal-based
    seen = set(already_owns)
    ranked = []
    for pid in (biomarker_recs + stack_gaps + goal_based):
        if pid not in seen:
            ranked.append(pid)
            seen.add(pid)

    shelf_title = "For you this week" if goals else "Top picks this week"

    return {
        "shelf_title": shelf_title,
        "context": "personalised" if goals else "cold_start",
        "products": _format_products(ranked[:10]),
        "signals_used": {
            "goals": goals,
            "biomarker_aware": len(biomarker_recs) > 0,
            "stack_gaps_detected": len(stack_gaps),
            "session_intent": pillar_intent
        },
        "latency_ms": round((time.time() - start) * 1000, 1)
    }


# ─── Experience 3 — Why this is right for you (PDP) ──────────────────────────

@app.get("/pdp/{user_id}/{product_id}/why")
def get_why_right(user_id: str, product_id: str):
    """
    Returns a personal reason why a product is right for this user.
    Three tiers: biomarker > goal-based > social proof.
    """
    user = get_user(user_id)
    product = get_product(product_id)

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    reason = get_why_right_for_you(user_id, product_id)

    return {
        "product_id": product_id,
        "product_name": product.get("name"),
        "why_right_for_you": reason,
        "show": bool(reason)
    }


# ─── Experience 4 — Complementary stack (PDP) ────────────────────────────────

@app.get("/pdp/{user_id}/{product_id}/stack")
def get_stack(user_id: str, product_id: str):
    """
    Returns products that complete the user's stack.
    Only shown when user has 2+ purchases. Empty for cold start.
    """
    user = get_user(user_id)
    purchases = user.get("purchases", []) if user else []

    # Experience 4 rule: only show when we have enough signal
    if len(purchases) < 2:
        return {
            "show": False,
            "reason": "not_enough_signal",
            "products": []
        }

    complementary = get_complementary_products(user_id, product_id)
    goals = user.get("goals", [])
    goal_label = goals[0] if goals else "your goals"

    return {
        "show": len(complementary) > 0,
        "section_title": f"Works well with your {goal_label.lower()} stack",
        "products": _format_products(complementary)
    }


# ─── Experience 5 — Four-agent Helix reasoning ───────────────────────────────

@app.post("/helix/recommend")
def helix_recommend(body: HelixMessage):
    """
    Four-agent reasoning: Eat, Move, Mind, Sleep agents each
    propose products. Where agents agree, confidence goes up.
    LLM judge (mocked here) checks for conflicts.
    """
    user = get_user(body.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    message = body.message.lower()
    purchases = set(user.get("purchases", []))

    # Each agent proposes products from their pillar
    agents = {
        "Eat": _agent_recommend("Eat", message, purchases),
        "Move": _agent_recommend("Move", message, purchases),
        "Mind": _agent_recommend("Mind", message, purchases),
        "Sleep": _agent_recommend("Sleep", message, purchases),
    }

    # Score by agent agreement — products multiple agents recommend get boosted
    product_votes = {}
    for agent_name, products in agents.items():
        for pid in products:
            if pid not in product_votes:
                product_votes[pid] = {"votes": 0, "agents": []}
            product_votes[pid]["votes"] += 1
            product_votes[pid]["agents"].append(agent_name)

    # Sort by votes — most agreed-upon products surface first
    ranked = sorted(product_votes.items(), key=lambda x: x[1]["votes"], reverse=True)

    # Mock LLM judge — check known conflicts
    CONFLICTS = {("p001", "p016")}  # Magnesium + Melatonin — mild overlap, flag it
    results = []
    seen = set()
    for pid, data in ranked[:5]:
        if pid in seen:
            continue
        conflict_flag = any(
            {pid, other} in CONFLICTS
            for other in [r["product_id"] for r in results]
        )
        product = get_product(pid)
        results.append({
            "product_id": pid,
            "product_name": product.get("name"),
            "brand": product.get("brand"),
            "price": product.get("price"),
            "agreed_by": data["agents"],
            "confidence": "high" if data["votes"] > 1 else "moderate",
            "conflict_flag": conflict_flag,
            "reason": _generate_reason(pid, data["agents"], message)
        })
        seen.add(pid)

    return {
        "user_message": body.message,
        "agent_outputs": {k: v for k, v in agents.items()},
        "recommendations": results
    }


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _format_products(product_ids: list) -> list:
    results = []
    for pid in product_ids:
        p = PRODUCTS.get(pid, {})
        if p:
            results.append({
                "product_id": pid,
                "name": p.get("name"),
                "brand": p.get("brand"),
                "pillar": p.get("pillar"),
                "price": p.get("price"),
                "benefits": p.get("benefits"),
                "health_goals": p.get("health_goals", [])
            })
    return results


def _boost_by_pillar(product_ids: list, pillar: str) -> list:
    """Move products matching browser-inferred pillar to the top."""
    pillar_matches = [
        pid for pid in product_ids
        if PRODUCTS.get(pid, {}).get("pillar") == pillar
    ]
    others = [pid for pid in product_ids if pid not in pillar_matches]
    return pillar_matches + others


def _agent_recommend(pillar: str, message: str, exclude: set) -> list:
    """Each agent returns products from their pillar relevant to the message."""
    KEYWORDS = {
        "Eat": ["eat", "energy", "fatigue", "tired", "vitamin", "mineral",
                "supplement", "gut", "digest", "immune", "inflammation"],
        "Move": ["train", "workout", "muscle", "strength", "recovery",
                 "performance", "exercise", "sport", "creatine"],
        "Mind": ["stress", "anxiety", "focus", "mood", "mental",
                 "calm", "concentrate", "brain"],
        "Sleep": ["sleep", "tired", "rest", "insomnia", "wake",
                  "night", "fatigue", "relax"]
    }

    keywords = KEYWORDS.get(pillar, [])
    relevant = any(kw in message for kw in keywords)
    if not relevant:
        return []

    pillar_products = [
        pid for pid, p in PRODUCTS.items()
        if p.get("pillar") == pillar and pid not in exclude
    ]
    return pillar_products[:3]


def _generate_reason(product_id: str, agents: list, message: str) -> str:
    product = get_product(product_id)
    name = product.get("name", "")
    benefits = product.get("benefits", "")
    agent_str = " and ".join(agents) if len(agents) > 1 else agents[0]
    return f"{name} was suggested by the {agent_str} pillar. {benefits}."


# ─── Run ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
