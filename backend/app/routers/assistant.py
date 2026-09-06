from __future__ import annotations

import asyncio
import os
from typing import Annotated, Any

import httpx
from fastapi import APIRouter, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import BaseModel, Field

from ..core.security import get_current_user
from ..db.mongo import get_database


router = APIRouter(prefix="/assistant", tags=["assistant"])

GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-3.6-flash")

# Grounding rules for the LLM path. The model may only use the numbers in the
# supplied context and the app's published factor ranges — it must never
# invent emission factors, claim verified reductions, or contradict the
# planning-guidance framing used across the product.
GEMINI_SYSTEM_PROMPT = (
    "You are the CarbonSense climate assistant. CarbonSense estimates a personal "
    "monthly carbon footprint two ways: an XGBoost model over a 15-question survey, "
    "and a transparent baseline computed from cited emission factors (Ember 2025 grid "
    "factors, IPCC fuel chemistry, Scarborough 2023 diet bands, OWID air-travel bands, "
    "EEA clothing, IPCC waste). India/US/UK grids; shared lines divide by household size. "
    "You are chatting with one signed-in user. Rules: (1) Use ONLY the user-specific "
    "numbers in the provided context — never invent or convert emission factors. "
    "(2) Every estimate is planning guidance, not a verified or measured reduction; "
    "never claim certainty. (3) Answers are short: at most 4 sentences or 3 bullet "
    "points. (4) When useful, reference the user's own top contributors or goal from "
    "the context. (5) If asked something outside carbon-footprint planning, answer "
    "briefly and steer back to CarbonSense topics."
)


async def gemini_reply(message: str, context: dict[str, Any]) -> str | None:
    """Ask Gemini for a grounded reply. Returns None on ANY failure so the
    rule-based assistant can take over (missing key, quota, timeout, error)."""
    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not api_key:
        return None
    payload = {
        "contents": [
            {"role": "user", "parts": [{"text": (
                f"User context (already computed by CarbonSense; use only these numbers):\n"
                f"{context}\n\nUser question: {message}"
            )}]},
        ],
        "systemInstruction": {"parts": [{"text": GEMINI_SYSTEM_PROMPT}]},
        # No-thinking mode: thinkingLevel low keeps this model from emitting
        # hidden reasoning parts, cutting grounded replies from ~30s to ~5s.
        "generationConfig": {
            "temperature": 0.4,
            "maxOutputTokens": 2048,
            "thinkingConfig": {"thinkingLevel": "low"},
        },
    }
    try:
        async with httpx.AsyncClient(timeout=25.0) as client:
            response = await client.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent",
                params={"key": api_key},
                json=payload,
            )
            if response.status_code != 200:
                return None
            body = response.json()
            if body.get("candidates", [{}])[0].get("finishReason") == "QUOTA_EXCEEDED":
                return None
            parts = body.get("candidates", [{}])[0].get("content", {}).get("parts", [])
            text = "".join(part.get("text", "") for part in parts).strip()
            return text or None
    except Exception:
        return None


class AssistantRequest(BaseModel):
    message: str = Field(min_length=1, max_length=1000)


# ---------------------------------------------------------------------------
# Expanded keyword→response mapping
# ---------------------------------------------------------------------------

TIPS = {
    "transport": {
        "keywords": ["transport", "car", "drive", "driving", "vehicle", "commute", "bus", "train", "flight", "fly", "travel"],
        "title": "Transport tips",
        "suggestions": [
            "Consider carpooling or using public transport for short commutes — even 2 trips per week can cut transport emissions significantly.",
            "For longer journeys, trains typically produce fewer emissions per km than flying. Check local options.",
            "If you drive, combining errands into a single trip reduces fuel use. Keeping tyres at the right pressure also helps.",
        ],
        "recommendation_key": "transit_two_trips",
    },
    "electricity": {
        "keywords": ["electricity", "electric", "energy", "power", "heating", "solar", "grid", "renewable"],
        "title": "Energy tips",
        "suggestions": [
            "Switching to a renewable energy tariff can reduce your electricity-related footprint without changing daily habits.",
            "Reducing standby power consumption and using LED bulbs are small steps with measurable cumulative impact.",
            "If available, a smart thermostat can help reduce heating energy without sacrificing comfort.",
        ],
        "recommendation_key": "cleaner_energy",
    },
    "diet": {
        "keywords": ["diet", "food", "meal", "meat", "chicken", "beef", "vegan", "vegetarian", "dairy", "protein"],
        "title": "Diet tips",
        "suggestions": [
            "Replacing one meat-based meal per day with a plant-based option can reduce diet-related emissions noticeably.",
            "Reducing food waste is one of the most impactful actions — plan meals and use leftovers creatively.",
            "If you eat dairy, consider trying oat or soy milk as an alternative — they typically have lower footprints.",
        ],
        "recommendation_key": "lower_impact_meals",
    },
    "fuel": {
        "keywords": ["fuel", "gas", "petrol", "diesel", "oil", "heating fuel"],
        "title": "Fuel tips",
        "suggestions": [
            "Combining journeys and reducing unnecessary trips is the simplest way to cut fuel use.",
            "If you use fuel for heating, improving insulation can significantly reduce consumption over time.",
            "Monitoring your fuel consumption over time helps identify patterns and reduction opportunities.",
        ],
        "recommendation_key": "fuel_efficiency",
    },
    "goals": {
        "keywords": ["goal", "target", "aim", "reduce", "reduction"],
        "title": "Goals & targets",
        "suggestions": [
            "Setting a specific reduction target helps focus your actions. A realistic goal is better than an ambitious one you can't sustain.",
            "Your CarbonSense goals track progress against a baseline — revisit them as your habits change.",
            "Breaking a long-term target into monthly milestones makes progress more visible and motivating.",
        ],
    },
    "forecast": {
        "keywords": ["forecast", "predict", "future", "projection", "trend"],
        "title": "Forecasting",
        "suggestions": [
            "Your forecast uses activity history to project a directional future range. It's indicative, not a certainty.",
            "The more activity entries you record, the more useful your forecast becomes for spotting patterns.",
            "Forecasts are most helpful when used for planning, not as precise predictions of future emissions.",
        ],
    },
    "quest": {
        "keywords": ["quest", "streak", "badge", "score", "gamification", "challenge"],
        "title": "CarbonQuest",
        "suggestions": [
            "CarbonQuest rewards recorded participation and verified actions. Complete estimates and track activities to build your score.",
            "Badges recognise milestones — your first estimate, verified action completions, and sustained streaks.",
            "The leaderboard uses privacy-aware aggregate data only. Individual names are never exposed.",
        ],
    },
    "recommendation": {
        "keywords": ["recommendation", "action", "advice", "tip", "suggestion", "step"],
        "title": "Recommendations",
        "suggestions": [
            "Result-led recommendations are matched to your completed AI prediction and baseline — they target your specific profile.",
            "Your organization can also assign custom recommendations. Check 'My Recommendations' for any assigned actions.",
            "Accepting a recommendation is a commitment — complete it and record the change to earn recognition.",
        ],
    },
    "organization": {
        "keywords": ["organization", "organisation", "team", "group", "member", "invite"],
        "title": "Organization",
        "suggestions": [
            "Create an organization to invite team members, or join one using an invite code from your administrator.",
            "Organization admins can send reminders to members, assign recommendations, and view aggregate stats.",
            "Your organization role determines what you can see and do — admins have full management access.",
        ],
    },
    "baseline": {
        "keywords": ["baseline", "formula", "calculation", "reference", "audit"],
        "title": "Baseline calculation",
        "suggestions": [
            "The transparent baseline uses the same v2.5-aligned cited factors as the AI model (Ember 2025 grid, IPCC fuel chemistry, Scarborough diet bands) to calculate an auditable estimate.",
            "Compare your AI prediction against the baseline to see how your profile differs from reference values.",
            "Both estimates are indicative — they support planning and comparison, not certified emissions reporting.",
        ],
    },
    "privacy": {
        "keywords": ["privacy", "data", "share", "opt", "consent", "private"],
        "title": "Privacy & data",
        "suggestions": [
            "Your account-scoped records are private by default. Only you can see your prediction history and activity.",
            "Aggregate sharing is opt-in — toggling it on allows your organization to see anonymised cohort statistics.",
            "No individual records are ever exposed in aggregate views. The system enforces consent-based boundaries.",
        ],
    },
    "hello": {
        "keywords": ["hello", "hi", "hey", "good morning", "good afternoon", "help"],
        "title": "Greeting",
        "suggestions": [
            "Hello! I'm your CarbonSense climate assistant. I can help with transport, electricity, diet, fuel, goals, forecasts, recommendations, and more.",
            "Try asking about a specific area — like 'how can I reduce my transport emissions?' or 'what are my goals?'",
        ],
    },
}


def find_matching_topics(message: str) -> list[str]:
    """Return a list of topic keys that match the user's message."""
    matches = []
    for topic, config in TIPS.items():
        if any(kw in message for kw in config["keywords"]):
            matches.append(topic)
    return matches


def build_response(message: str, context: dict[str, Any]) -> str:
    """Build a conversational response from context and matched topics."""
    topics = find_matching_topics(message)

    # Personal stats
    parts: list[str] = []
    activity_count = context.get("activityEntries", 0)
    run_count = context.get("runCount", 0)
    accepted = context.get("acceptedRecommendations", 0)
    completed = context.get("completedRecommendations", 0)
    goal_kg = context.get("activeGoalKg")
    streak = context.get("streak", 0)
    top = context.get("topContributor")
    latest_kg = context.get("latestPredictionKg")

    if latest_kg:
        parts.append(f"Your latest AI estimate is {latest_kg} kg CO₂e for the month.")
    if top:
        parts.append(f"Your dominant modeled contributor is **{top['label']}** (+{top['shapValue']} kg in your latest result) — that's usually the best place to start.")
    if activity_count or run_count:
        parts.append(f"Your workspace has {run_count} recorded estimate{'s' if run_count != 1 else ''}, {activity_count} activity {'entries' if activity_count != 1 else 'entry'}, and {accepted} accepted action{'s' if accepted != 1 else ''}.")
    if completed:
        parts.append(f"You've completed {completed} action{'s' if completed != 1 else ''}.")
    if goal_kg:
        parts.append(f"Your active goal is {goal_kg} kg CO₂e.")
    if streak:
        parts.append(f"You have a {streak}-day engagement streak.")

    # Topic-specific guidance
    if topics:
        for topic in topics[:2]:  # max 2 topics
            config = TIPS[topic]
            parts.append(f"\n**{config['title']}:**")
            # rotate suggestions based on hash of message for variety
            suggestion_idx = hash(message) % len(config["suggestions"])
            parts.append(config["suggestions"][suggestion_idx])
            if config.get("suggestion2"):
                parts.append(config["suggestion2"])
    else:
        # Fallback: broad guidance
        parts.append("I can help with transport, electricity, diet, fuel, goals, forecasts, recommendations, organization management, and privacy. What would you like to know?")
        parts.append("Try asking something like 'how can I reduce my transport emissions?' or 'what are my current goals?'")

    return "\n\n".join(parts)


@router.post("/chat")
async def chat(
    payload: AssistantRequest,
    user: Annotated[dict[str, Any], Depends(get_current_user)],
    db: Annotated[AsyncIOMotorDatabase, Depends(get_database)],
) -> dict[str, Any]:
    # Gather user context
    user_id = str(user["_id"])
    activity = await db.activity_ledger.find({"user_id": user_id}).to_list(500)
    goals = await db.carbon_goals.find({"user_id": user_id, "status": "active"}).to_list(1)
    recommendations = await db.user_recommendations.find({"user_id": user_id}).to_list(50)
    runs = await db.footprint_runs.find({"user_id": user_id}).to_list(100)
    reminders = await db.reminders.find({"user_id": user_id, "status": "pending"}).to_list(50)

    accepted = [row for row in recommendations if row.get("status") == "accepted"]
    completed = [row for row in recommendations if row.get("status") == "completed"]
    verified = [row for row in completed if row.get("verification_status") == "verified"]

    # The user's dominant modeled contributor (SHAP) from the newest run makes
    # even the rule-based fallback personalized rather than canned.
    top_contributor = None
    latest_run = next((row for row in runs if row.get("run_type") == "prediction"), None)
    factors = (latest_run or {}).get("dominant_factors") or []
    if factors:
        top = max(factors, key=lambda f: abs(float(f.get("shapValue", 0) or 0)))
        if float(top.get("shapValue", 0) or 0) > 0:
            top_contributor = {"label": top.get("label", "a lifestyle area"), "shapValue": float(top.get("shapValue", 0) or 0)}

    context = {
        "activityEntries": len(activity),
        "runCount": len(runs),
        "acceptedRecommendations": len(accepted),
        "completedRecommendations": len(completed),
        "verifiedRecommendations": len(verified),
        "activeGoalKg": goals[0]["target_kg"] if goals else None,
        "streak": min(12, len(runs) + len(completed)),
        "pendingReminders": len(reminders),
        "topContributor": top_contributor,
        "latestPredictionKg": latest_run.get("predicted_kg") if latest_run else None,
    }

    answer = await gemini_reply(payload.message, context)
    engine = "gemini"
    if answer is None:
        answer = build_response(payload.message.lower(), context)
        engine = "rules"

    # Determine suggested action
    topics = find_matching_topics(payload.message.lower())
    suggested_action = None
    if topics:
        config = TIPS[topics[0]]
        suggested_action = config.get("recommendation_key")

    return {
        "answer": answer,
        "engine": engine,
        "scope": "your authenticated activity ledger, goals, recommendations, and organization state",
        "suggestedAction": suggested_action,
        "context": context,
    }
