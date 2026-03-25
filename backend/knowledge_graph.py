"""
Knowledge graph — Python dict implementation.
In production this would be Neo4j.
Handles all graph traversal for recommendations.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.mock_data import PRODUCTS, USERS, INGREDIENT_BIOMARKER_MAP, POPULAR_BY_GOAL


def get_user(user_id: str) -> dict:
    return USERS.get(user_id, {})


def get_product(product_id: str) -> dict:
    return PRODUCTS.get(product_id, {})


def get_user_goals(user_id: str) -> list:
    user = get_user(user_id)
    return user.get("goals", [])


def get_user_purchases(user_id: str) -> list:
    user = get_user(user_id)
    return user.get("purchases", [])


def get_user_subscriptions(user_id: str) -> list:
    user = get_user(user_id)
    return user.get("subscriptions", [])


def get_products_for_goals(goals: list, exclude_product_ids: list = []) -> list:
    """
    Core graph traversal: goals → products.
    This is the cold start path — works with quiz answers alone,
    no purchase history needed.
    """
    scored = {}
    for product_id, product in PRODUCTS.items():
        if product_id in exclude_product_ids:
            continue
        # Count how many of the user's goals this product targets
        overlap = len(set(goals) & set(product.get("health_goals", [])))
        if overlap > 0:
            scored[product_id] = overlap

    # Sort by relevance score descending
    ranked = sorted(scored.items(), key=lambda x: x[1], reverse=True)
    return [pid for pid, _ in ranked]


def get_stack_gaps(user_id: str) -> list:
    """
    Stack gap detection: given what a user already takes,
    what products would complete their stack for their goals?
    Only runs when user has 2+ purchases AND goals set.
    """
    user = get_user(user_id)
    goals = user.get("goals", [])
    purchases = user.get("purchases", [])
    subscriptions = user.get("subscriptions", [])
    already_owns = set(purchases + subscriptions)

    if len(purchases) < 2 or not goals:
        return []

    # Get all products relevant to user goals
    relevant = get_products_for_goals(goals, exclude_product_ids=list(already_owns))

    # Get ingredients the user already covers
    covered_ingredients = set()
    for pid in already_owns:
        product = get_product(pid)
        covered_ingredients.update(product.get("ingredients", []))

    # Prioritise products that add NEW ingredients (not already covered)
    gaps = []
    for pid in relevant:
        product = get_product(pid)
        new_ingredients = set(product.get("ingredients", [])) - covered_ingredients
        if new_ingredients:
            gaps.append(pid)

    return gaps[:5]


def get_biomarker_recommendations(user_id: str) -> list:
    """
    Biomarker-aware recommendations for Zone members.
    Deficient or elevated biomarker → find ingredient that addresses it
    → find product containing that ingredient.
    """
    user = get_user(user_id)
    if not user.get("zone_member") or not user.get("biomarkers"):
        return []

    biomarkers = user.get("biomarkers", {})
    purchases = set(user.get("purchases", []))
    recommendations = []

    for biomarker_name, data in biomarkers.items():
        if data["status"] in ["deficient", "elevated", "suboptimal"]:
            # Find ingredients that address this biomarker
            addressing_ingredients = [
                ing for ing, bm in INGREDIENT_BIOMARKER_MAP.items()
                if bm == biomarker_name
            ]

            # Find products containing those ingredients
            for product_id, product in PRODUCTS.items():
                if product_id in purchases:
                    continue
                product_ingredients = set(product.get("ingredients", []))
                if product_ingredients & set(addressing_ingredients):
                    recommendations.append({
                        "product_id": product_id,
                        "reason": f"Your {biomarker_name} is {data['status']} "
                                  f"({data['value']} {data['unit']}). "
                                  f"This product directly addresses that.",
                        "biomarker": biomarker_name,
                        "status": data["status"]
                    })

    # Deduplicate by product_id
    seen = set()
    unique = []
    for rec in recommendations:
        if rec["product_id"] not in seen:
            seen.add(rec["product_id"])
            unique.append(rec)

    return unique


def get_why_right_for_you(user_id: str, product_id: str) -> str:
    """
    Generate a personal reason why a product is right for a specific user.
    Used on the product detail page.
    Three tiers: biomarker > goal-based > social proof.
    """
    user = get_user(user_id)
    product = get_product(product_id)

    if not user or not product:
        return ""

    # Tier 1: Zone member with relevant biomarker
    if user.get("zone_member") and user.get("biomarkers"):
        for ingredient in product.get("ingredients", []):
            biomarker_name = INGREDIENT_BIOMARKER_MAP.get(ingredient)
            if biomarker_name and biomarker_name in user["biomarkers"]:
                bm = user["biomarkers"][biomarker_name]
                if bm["status"] in ["deficient", "elevated", "suboptimal"]:
                    return (
                        f"Your last test showed {biomarker_name} at "
                        f"{bm['value']} {bm['unit']} — {bm['status']}. "
                        f"This product directly addresses that."
                    )

    # Tier 2: Goal-based match
    user_goals = user.get("goals", [])
    product_goals = product.get("health_goals", [])
    matching_goals = list(set(user_goals) & set(product_goals))
    if matching_goals:
        return (
            f"Your goal is {matching_goals[0].lower()}. "
            f"{product['name']} directly supports that — "
            f"{product['benefits'].lower()}."
        )

    # Tier 3: Cold start — social proof
    popular_products = []
    for goal_products in POPULAR_BY_GOAL.values():
        if product_id in goal_products:
            popular_products.append(product_id)

    if popular_products:
        return f"One of Healf's most popular products for wellbeing this month."

    return ""


def get_complementary_products(user_id: str, product_id: str) -> list:
    """
    Products that work well together with the current product,
    given user goals. Only shown when user has 2+ purchases.
    Experience 4 — never shown for cold start.
    """
    user = get_user(user_id)
    purchases = user.get("purchases", [])

    # Only show when we have enough signal
    if len(purchases) < 2:
        return []

    already_owns = set(purchases + [product_id])
    goals = user.get("goals", [])

    if not goals:
        return []

    # Find products that share goals with this product AND user goals
    current_product = get_product(product_id)
    current_goals = set(current_product.get("health_goals", []))
    user_goal_set = set(goals)
    shared_context = current_goals & user_goal_set

    if not shared_context:
        return []

    scored = {}
    for pid, product in PRODUCTS.items():
        if pid in already_owns:
            continue
        overlap = len(set(product.get("health_goals", [])) & shared_context)
        if overlap > 0:
            scored[pid] = overlap

    ranked = sorted(scored.items(), key=lambda x: x[1], reverse=True)
    return [pid for pid, _ in ranked[:3]]


def get_popular_for_goal(goal: str, exclude: list = []) -> list:
    """Social proof fallback for cold start users."""
    products = POPULAR_BY_GOAL.get(goal, [])
    return [p for p in products if p not in exclude][:3]
