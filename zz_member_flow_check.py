import json, time, requests, pymongo
base = "http://127.0.0.1:8015/api/v1"
admin = requests.Session()
admin_resp = admin.post(base + "/auth/login", json={"email":"testuser@carbonsense.dev","password":"TestPass12345"}, timeout=30)
print("ADMIN_LOGIN", admin_resp.status_code)
print(admin_resp.text[:400])
admin_data = admin_resp.json()
org_id = admin_data["user"]["organizationId"]
print("ORG_ID", org_id)
email = f"memberflow_{int(time.time())}@carbonsense.dev"
member = requests.Session()
register = member.post(base + "/auth/register", json={"name":"Member Flow Demo","email":email,"password":"MemberFlowDemo123","country":"US","organizationId":org_id}, timeout=30)
print("REGISTER", register.status_code)
print(register.text[:500])
reg = register.json()
member_id = reg["user"]["id"]
print("MEMBER_ID", member_id)
payload = {
    "age": 31,
    "sex": "female",
    "body_type": "normal",
    "diet": "omnivore",
    "how_often_shower": "daily",
    "heating_energy_source": "electricity",
    "energy_efficiency": "Yes",
    "transport": "private",
    "vehicle_type": "petrol",
    "vehicle_monthly_distance_km": 300,
    "frequency_of_traveling_by_air": "rarely",
    "region": "mixed",
    "monthly_grocery_bill": 200,
    "how_many_new_clothes_monthly": 2,
    "waste_bag_size": "medium",
    "waste_bag_weekly_count": 3,
    "how_long_tv_pc_daily_hour": 4,
    "how_long_internet_daily_hour": 4,
    "social_activity": "sometimes",
    "recycling": ["paper", "plastic"],
    "cooking_with": ["stove", "oven"],
    "currency": "USD",
}
pred = member.post(base + "/model/predict", json=payload, timeout=60)
print("PREDICT", pred.status_code)
print(pred.text[:1200])
assign = admin.post(base + "/recommendations/assign", json={"user_id": member_id, "recommendation_key": "transit_two_trips"}, timeout=30)
print("ASSIGN", assign.status_code)
print(assign.text[:400])
mine = member.get(base + "/recommendations/mine", timeout=30)
print("MINE", mine.status_code)
print(mine.text[:1200])
import os
uri = os.environ["MONGODB_URI"]  # read from .env - never hardcode credentials
mongo = pymongo.MongoClient(uri, serverSelectionTimeoutMS=20000, tls=True, tlsAllowInvalidCertificates=True)
db = mongo["carbonsense_fastapi"]
user = db.users.find_one({"email": email})
print("DB_USER", user["_id"], user.get("organization_id"))
runs = list(db.footprint_runs.find({"user_id": str(user["_id"]) }).sort("created_at", -1).limit(5))
print("DB_RUNS", json.dumps(runs, default=str))
recs = list(db.user_recommendations.find({"user_id": str(user["_id"]) }).sort("created_at", -1).limit(10))
print("DB_RECS", json.dumps(recs, default=str))
