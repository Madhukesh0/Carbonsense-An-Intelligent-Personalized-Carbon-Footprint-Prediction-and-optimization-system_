import json
import sys
from typing import Any

import pymongo
import requests

base = 'http://127.0.0.1:8015/api/v1'
import os
uri = os.environ["MONGODB_URI"]  # read from .env - never hardcode credentials
member_email = 'asha_org_member_2@carbonsense.dev'
member_password = 'AshaMember123!'
org_id = 'edf615ca-273b-4e37-b133-3a846520783f'


def print_step(label: str, value: Any) -> None:
    print(f'[{label}] {value}')


try:
    s = requests.Session()
    reg = s.post(
        base + '/auth/register',
        json={
            'email': member_email,
            'password': member_password,
            'name': 'Asha Rao',
            'country': 'IN',
            'region': 'mixed',
            'organization_id': org_id,
        },
        timeout=30,
    )
    print_step('REGISTER_STATUS', reg.status_code)
    print_step('REGISTER_BODY', reg.text[:500])
    if reg.status_code not in (200, 201):
        raise SystemExit(1)

    member_login = requests.Session()
    ml = member_login.post(
        base + '/auth/login',
        json={'email': member_email, 'password': member_password},
        timeout=30,
    )
    print_step('MEMBER_LOGIN_STATUS', ml.status_code)
    print_step('MEMBER_LOGIN_BODY', ml.text[:400])
    if ml.status_code != 200:
        raise SystemExit(1)

    member_user = ml.json()['user']
    member_id = member_user['id']
    print_step('MEMBER_ID', member_id)

    payload = {
        'age': 31,
        'sex': 'female',
        'body_type': 'normal',
        'diet': 'omnivore',
        'how_often_shower': 'daily',
        'heating_energy_source': 'electricity',
        'energy_efficiency': 'Yes',
        'transport': 'private',
        'vehicle_type': 'petrol',
        'vehicle_monthly_distance_km': 350,
        'frequency_of_traveling_by_air': 'rarely',
        'region': 'mixed',
        'monthly_grocery_bill': 220,
        'how_many_new_clothes_monthly': 3,
        'waste_bag_size': 'medium',
        'waste_bag_weekly_count': 4,
        'how_long_tv_pc_daily_hour': 5,
        'how_long_internet_daily_hour': 6,
        'social_activity': 'sometimes',
        'recycling': ['paper', 'plastic'],
        'cooking_with': ['stove', 'oven'],
        'currency': 'USD',
    }

    pred = member_login.post(base + '/model/predict', json=payload, timeout=60)
    print_step('PREDICT_STATUS', pred.status_code)
    print_step('PREDICT_BODY', pred.text[:1500])
    if pred.status_code != 200:
        raise SystemExit(1)

    admin = requests.Session()
    adm = admin.post(
        base + '/auth/login',
        json={'email': 'testuser@carbonsense.dev', 'password': 'TestPass12345'},
        timeout=30,
    )
    print_step('ADMIN_LOGIN_STATUS', adm.status_code)
    print_step('ADMIN_LOGIN_BODY', adm.text[:400])
    if adm.status_code != 200:
        raise SystemExit(1)

    assign = admin.post(
        base + '/recommendations/assign',
        json={'user_id': member_id, 'recommendation_key': 'cleaner_energy'},
        timeout=30,
    )
    print_step('ASSIGN_STATUS', assign.status_code)
    print_step('ASSIGN_BODY', assign.text[:500])
    if assign.status_code != 200:
        raise SystemExit(1)

    mine = member_login.get(base + '/recommendations/mine', timeout=30)
    print_step('MINE_STATUS', mine.status_code)
    print_step('MINE_BODY', mine.text[:1000])
    if mine.status_code != 200:
        raise SystemExit(1)

    client = pymongo.MongoClient(uri, serverSelectionTimeoutMS=20000, tls=True, tlsAllowInvalidCertificates=True)
    db = client['carbonsense_fastapi']
    user_doc = db.users.find_one({'email': member_email}, {'_id': 1, 'email': 1, 'organization_id': 1, 'role': 1, 'name': 1})
    print_step('USER_DOC', json.dumps(user_doc, default=str))

    run_doc = db.footprint_runs.find_one({'user_id': str(user_doc['_id'])}, sort=[('created_at', -1)])
    if run_doc:
        run_summary = {k: run_doc[k] for k in ['user_id', 'organization_id', 'run_type', 'predicted_kg', 'dominant_factors', 'created_at']}
        print_step('RUN_DOC', json.dumps(run_summary, default=str))
    else:
        print_step('RUN_DOC', 'NOT_FOUND')

    rec_docs = list(db.user_recommendations.find({'user_id': str(user_doc['_id'])}).sort('created_at', -1).limit(10))
    print_step('REC_DOCS', json.dumps(rec_docs, default=str))

except Exception as exc:
    print(f'FLOW_ERROR: {type(exc).__name__}: {exc}', file=sys.stderr)
    raise
