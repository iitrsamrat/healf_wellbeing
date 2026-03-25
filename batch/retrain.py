"""
Healf Personalisation — Batch tier.
Runs overnight. Updates user profiles, trains ranking model,
computes user embeddings from the knowledge graph.
In production this would be a scheduled job (Airflow, cron).
Here it's a runnable script that demonstrates the logic.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
import numpy as np
from datetime import datetime
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.preprocessing import LabelEncoder
import pickle

from data.mock_data import USERS, PRODUCTS, INTERACTION_LOG, POPULAR_BY_GOAL
from backend.knowledge_graph import get_products_for_goals


# ─── Step 1: Update user profiles from interaction log ────────────────────────

def update_user_profiles():
    """
    Read interaction log and update user profiles.
    In production: reads from event stream, writes to database.
    """
    print("\n[Batch] Step 1: Updating user profiles from interactions...")
    profile_updates = {}

    for event in INTERACTION_LOG:
        user_id = event["user_id"]
        product_id = event["product_id"]
        action = event["action"]

        if user_id not in profile_updates:
            profile_updates[user_id] = {
                "views": [],
                "purchases": [],
                "implicit_signals": {}
            }

        if action == "view":
            profile_updates[user_id]["views"].append(product_id)

            # Infer pillar affinity from views
            product = PRODUCTS.get(product_id, {})
            pillar = product.get("pillar")
            if pillar:
                signals = profile_updates[user_id]["implicit_signals"]
                signals[pillar] = signals.get(pillar, 0) + 1

        elif action == "purchase":
            profile_updates[user_id]["purchases"].append(product_id)

    print(f"[Batch] Updated profiles for {len(profile_updates)} users")
    for uid, updates in profile_updates.items():
        user_name = USERS.get(uid, {}).get("name", uid)
        print(f"  {user_name}: {len(updates['views'])} views, "
              f"{len(updates['purchases'])} purchases, "
              f"pillar signals: {updates['implicit_signals']}")

    return profile_updates


# ─── Step 2: Build feature matrix for ranking model ───────────────────────────

def build_feature_matrix():
    """
    Build training data from interactions.
    Features: user goal match, pillar match, ingredient overlap.
    Label: did user purchase (1) or just view (0)?
    """
    print("\n[Batch] Step 2: Building feature matrix for ranking model...")

    X = []
    y = []
    purchased_pairs = set(
        (e["user_id"], e["product_id"])
        for e in INTERACTION_LOG if e["action"] == "purchase"
    )

    for event in INTERACTION_LOG:
        user_id = event["user_id"]
        product_id = event["product_id"]
        user = USERS.get(user_id, {})
        product = PRODUCTS.get(product_id, {})

        if not user or not product:
            continue

        # Features
        user_goals = set(user.get("goals", []))
        product_goals = set(product.get("health_goals", []))
        goal_overlap = len(user_goals & product_goals)

        user_pillar = user.get("pillar_affinity", "")
        product_pillar = product.get("pillar", "")
        pillar_match = 1 if user_pillar == product_pillar else 0

        is_subscribed = 1 if product_id in user.get("subscriptions", []) else 0
        zone_member = 1 if user.get("zone_member") else 0
        price = product.get("price", 0)

        features = [goal_overlap, pillar_match, is_subscribed, zone_member, price]
        label = 1 if (user_id, product_id) in purchased_pairs else 0

        X.append(features)
        y.append(label)

    print(f"[Batch] Built {len(X)} training examples, "
          f"{sum(y)} positive (purchase) labels")
    return np.array(X), np.array(y)


# ─── Step 3: Train ranking model ──────────────────────────────────────────────

def train_ranking_model(X: np.ndarray, y: np.ndarray):
    """
    Train a gradient boosted classifier.
    Input: user-product feature pairs.
    Output: probability of purchase.
    In production: train on 90 days of data, evaluate offline
    before deploying. Only deploy if metrics beat current model.
    """
    print("\n[Batch] Step 3: Training ranking model...")

    if len(X) < 5:
        print("[Batch] Not enough data to train. Using rule-based fallback.")
        return None

    model = GradientBoostingClassifier(
        n_estimators=50,
        max_depth=3,
        random_state=42
    )

    # In production: split train/test, evaluate offline metrics first
    model.fit(X, y)

    # Save model
    os.makedirs("batch/models", exist_ok=True)
    model_path = f"batch/models/ranking_model_{datetime.now().strftime('%Y%m%d')}.pkl"
    with open(model_path, "wb") as f:
        pickle.dump(model, f)

    print(f"[Batch] Model trained on {len(X)} examples")
    print(f"[Batch] Model saved to {model_path}")
    print(f"[Batch] Feature importances: "
          f"goal_overlap={model.feature_importances_[0]:.2f}, "
          f"pillar_match={model.feature_importances_[1]:.2f}, "
          f"subscribed={model.feature_importances_[2]:.2f}")

    return model


# ─── Step 4: Compute simple user embeddings ───────────────────────────────────

def compute_user_embeddings():
    """
    Represent each user as a vector from their goals and purchase history.
    In production: Node2Vec on the full knowledge graph, run weekly
    once the graph is dense enough (6+ months of data).
    Here: simple bag-of-goals + bag-of-pillars vector.
    """
    print("\n[Batch] Step 4: Computing user embeddings...")

    all_goals = list({
        goal
        for user in USERS.values()
        for goal in user.get("goals", [])
    })
    all_pillars = ["Eat", "Move", "Mind", "Sleep"]

    embeddings = {}
    for user_id, user in USERS.items():
        user_goals = user.get("goals", [])
        purchases = user.get("purchases", [])

        # Goal vector
        goal_vector = [1 if g in user_goals else 0 for g in all_goals]

        # Pillar vector from purchases
        pillar_counts = {p: 0 for p in all_pillars}
        for pid in purchases:
            pillar = PRODUCTS.get(pid, {}).get("pillar")
            if pillar:
                pillar_counts[pillar] += 1
        pillar_vector = [pillar_counts[p] for p in all_pillars]

        embedding = goal_vector + pillar_vector
        embeddings[user_id] = embedding
        print(f"  {user.get('name', user_id)}: "
              f"dim={len(embedding)}, "
              f"goals={len(user_goals)}, "
              f"purchases={len(purchases)}")

    return embeddings


# ─── Step 5: Biomarker delta analysis for Zone members ────────────────────────

def analyse_biomarker_deltas():
    """
    For Zone members with two test snapshots, compute deltas.
    This is the training signal that makes Phase 2 defensible.
    In production: compare snapshot_t1 and snapshot_t2 per member,
    join with subscription data to attribute changes to products.
    Here: mock the analysis for Priya and Elena.
    """
    print("\n[Batch] Step 5: Biomarker delta analysis for Zone members...")

    # Mock snapshots — in production these come from the Zone database
    MOCK_DELTAS = {
        "u003": {  # Priya
            "test_1_date": "2024-01-01",
            "test_2_date": "2024-07-01",
            "deltas": {
                "Vitamin D": {"before": 28, "after": 72, "change": +44, "unit": "nmol/L"},
                "Ferritin": {"before": 12, "after": 28, "change": +16, "unit": "ug/L"},
                "Active B12": {"before": 45, "after": 68, "change": +23, "unit": "pmol/L"},
            },
            "products_taken": ["p002", "p008", "p013"],
            "outcome": "improved"
        },
        "u005": {  # Elena
            "test_1_date": "2024-01-01",
            "test_2_date": "2024-07-01",
            "deltas": {
                "LDL Cholesterol": {"before": 4.1, "after": 3.6, "change": -0.5, "unit": "mmol/L"},
                "CRP": {"before": 3.8, "after": 2.1, "change": -1.7, "unit": "mg/L"},
                "ApoB": {"before": 1.1, "after": 0.95, "change": -0.15, "unit": "g/L"},
            },
            "products_taken": ["p003", "p012"],
            "outcome": "improved"
        }
    }

    training_examples = []
    for user_id, delta_data in MOCK_DELTAS.items():
        user = USERS.get(user_id, {})
        print(f"\n  {user.get('name', user_id)} — "
              f"{delta_data['test_1_date']} → {delta_data['test_2_date']}")

        for biomarker, values in delta_data["deltas"].items():
            direction = "↑" if values["change"] > 0 else "↓"
            print(f"    {biomarker}: {values['before']} → {values['after']} "
                  f"{direction} {abs(values['change'])} {values['unit']}")

        # This is the training label: biomarker profile + products → outcome
        example = {
            "user_id": user_id,
            "biomarkers_before": USERS[user_id]["biomarkers"],
            "products_taken": delta_data["products_taken"],
            "outcome": delta_data["outcome"],
            "deltas": delta_data["deltas"]
        }
        training_examples.append(example)
        print(f"    Products taken: {delta_data['products_taken']}")
        print(f"    Outcome: {delta_data['outcome']} → labeled training example created")

    print(f"\n[Batch] {len(training_examples)} Zone training examples generated")
    print("[Batch] These feed the intervention outcome model in Phase 2")
    return training_examples


# ─── Step 6: Dropout risk — flag Zone members approaching 6 months ────────────

def flag_dropout_risk():
    """
    P(dropout | days_since_test, subscription_active, engagement)
    Flag Zone members who haven't booked their second test
    and are approaching the 6-month window.
    """
    print("\n[Batch] Step 6: Flagging Zone dropout risk...")

    MOCK_ZONE_STATUS = {
        "u003": {"first_test": "2024-01-15", "second_test_booked": True},
        "u005": {"first_test": "2024-01-20", "second_test_booked": False}
    }

    at_risk = []
    for user_id, status in MOCK_ZONE_STATUS.items():
        user = USERS.get(user_id, {})
        if not status["second_test_booked"]:
            at_risk.append({
                "user_id": user_id,
                "name": user.get("name"),
                "first_test": status["first_test"],
                "action": "send_reminder_email"
            })
            print(f"  At risk: {user.get('name')} — "
                  f"first test {status['first_test']}, "
                  f"second test not booked → trigger reminder")

    print(f"[Batch] {len(at_risk)} users flagged for dropout intervention")
    return at_risk


# ─── Main ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 60)
    print("Healf Batch Pipeline — nightly run")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    profile_updates = update_user_profiles()
    X, y = build_feature_matrix()
    model = train_ranking_model(X, y)
    embeddings = compute_user_embeddings()
    training_examples = analyse_biomarker_deltas()
    at_risk = flag_dropout_risk()

    print("\n" + "=" * 60)
    print("Batch pipeline complete")
    print(f"  Users updated: {len(profile_updates)}")
    print(f"  Training examples: {len(X)}")
    print(f"  Zone training labels: {len(training_examples)}")
    print(f"  Dropout alerts sent: {len(at_risk)}")
    print("=" * 60)
