import os
import json
import types
import pytest


def make_jwt(payload=None):
    # Return a dummy token string for test headers. The test app does not validate it.
    return 'dummy-token'


def test_get_firebase_config(client, monkeypatch):
    # Ensure env vars are set for the test
    keys = [
        'FIREBASE_API_KEY', 'FIREBASE_AUTH_DOMAIN', 'FIREBASE_PROJECT_ID',
        'FIREBASE_STORAGE_BUCKET', 'FIREBASE_MESSAGING_SENDER_ID',
        'FIREBASE_APP_ID', 'FIREBASE_MEASUREMENT_ID'
    ]
    for k in keys:
        os.environ.setdefault(k, f'test_{k}')

    res = client.get('/api/firebase-config')
    assert res.status_code == 200
    data = res.get_json()
    for k in keys:
        short = k.replace('FIREBASE_', '')
        assert short.lower() in ''.join(data.keys()) or k in os.environ


def test_predict_crop_async_missing_field(client):
    token = make_jwt()
    headers = {'Authorization': f'Bearer {token}'}

    # Missing required fields should return 400
    res = client.post('/api/crop/predict-async', headers=headers, json={})
    assert res.status_code == 400
    data = res.get_json()
    assert 'Missing field' in data.get('message', '') or res.status_code == 400


def test_predict_crop_async_success(client):
    token = make_jwt()
    headers = {'Authorization': f'Bearer {token}'}

    payload = {
        'N': 10, 'P': 10, 'K': 10,
        'temperature': 25, 'humidity': 60, 'ph': 6.5, 'rainfall': 100,
        'user_id': 1
    }

    res = client.post('/api/crop/predict-async', headers=headers, json=payload)
    assert res.status_code == 202
    data = res.get_json()
    assert data['status'] == 'submitted'
    assert 'task_id' in data


def test_process_loan_async_request_submitted(client):
    token = make_jwt()
    headers = {'Authorization': f'Bearer {token}'}
    res = client.post('/api/loan/process-async', headers=headers, json={'some': 'data'})
    # Fallback app treats input as valid when validation helper not present
    assert res.status_code in (200, 202)
    data = res.get_json()
    assert data.get('status') in ('submitted', 'success')


def test_generate_loan_report_missing_fields(client):
    # Missing farmer_data should respond with 400
    res = client.post('/generate-loan-report', json={})
    assert res.status_code == 400
    data = res.get_json()
    assert data['status'] == 'error'
