import os
import json
from flask import Flask, request, jsonify
import logging
import requests
from datetime import datetime

app = Flask(__name__)

LOG_DIR = '/var/log/alerts'
LOG_FILE = os.path.join(LOG_DIR, 'alerts.log')
os.makedirs(LOG_DIR, exist_ok=True)

logging.basicConfig(
    filename=LOG_FILE, 
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s'
)

GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN')
GITHUB_REPO = os.environ.get('GITHUB_REPO')
DISCORD_WEBHOOK_URL = os.environ.get('DISCORD_WEBHOOK_URL')

@app.route('/', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'service': 'incident-webhook'})

@app.route('/alert', methods=['POST'])
def alert():
    payload = request.get_json()
    logging.info('Received alert: %s', json.dumps(payload))
    
    # GitHub integration for critical alerts
    if GITHUB_TOKEN and GITHUB_REPO:
        try:
            alerts = payload.get('alerts', [])
            for a in alerts:
                labels = a.get('labels', {})
                severity = labels.get('severity', 'none')
                if severity == 'critical':
                    title = f"[{severity}] {labels.get('alertname', 'Alert')} on {labels.get('instance', '')}"
                    body = '```json\n' + json.dumps(a, indent=2) + '\n```'
                    create_github_issue(title, body)
        except Exception as e:
            logging.exception('Error creating GitHub issue: %s', e)
    
    # Discord webhook
    if DISCORD_WEBHOOK_URL:
        try:
            send_to_discord(payload)
        except Exception as e:
            logging.exception('Error sending to Discord: %s', e)
    
    return jsonify({'status': 'ok'})

def create_github_issue(title, body):
    url = f'https://api.github.com/repos/{GITHUB_REPO}/issues'
    headers = {
        'Authorization': f'token {GITHUB_TOKEN}',
        'Accept': 'application/vnd.github.v3+json'
    }
    data = {'title': title, 'body': body}
    r = requests.post(url, headers=headers, json=data, timeout=10)
    if r.status_code in (200, 201):
        logging.info('Created GitHub issue: %s', r.json().get('html_url'))
    else:
        logging.error('Failed to create GitHub issue: %s %s', r.status_code, r.text)

def send_to_discord(payload):
    """Send alerts to Discord with rich embed format"""
    alerts = payload.get('alerts', [])
    if not alerts:
        return
    
    # Group alerts by status
    status = payload.get('status', 'unknown')
    
    embeds = []
    for a in alerts:
        labels = a.get('labels', {})
        annotations = a.get('annotations', {})
        alert_status = a.get('status', 'unknown')
        
        # Determine color based on severity and status
        severity = labels.get('severity', 'info')
        if alert_status == 'resolved':
            color = 3066993  # Green
        elif severity == 'critical':
            color = 15158332  # Red
        elif severity == 'warning':
            color = 16776960  # Yellow/Orange
        else:
            color = 3447003  # Blue (info)
        
        # Build embed
        embed = {
            'title': f"🚨 {labels.get('alertname', 'Alert')}",
            'color': color,
            'fields': [
                {
                    'name': '🔴 Severity',
                    'value': severity.upper(),
                    'inline': True
                },
                {
                    'name': '📍 Status',
                    'value': alert_status.upper(),
                    'inline': True
                },
                {
                    'name': '🖥️ Instance',
                    'value': labels.get('instance', 'N/A'),
                    'inline': True
                }
            ],
            'timestamp': a.get('startsAt', datetime.utcnow().isoformat())
        }
        
        # Add summary if available
        if annotations.get('summary'):
            embed['description'] = f"**Summary:** {annotations.get('summary')}"
        
        # Add description as field
        if annotations.get('description'):
            embed['fields'].append({
                'name': '📝 Description',
                'value': annotations.get('description')[:1024],  # Discord limit
                'inline': False
            })
        
        # Add additional labels if they exist
        if labels.get('vlan'):
            embed['fields'].append({
                'name': '🌐 VLAN',
                'value': labels.get('vlan'),
                'inline': True
            })
        
        if labels.get('location'):
            embed['fields'].append({
                'name': '📍 Location',
                'value': labels.get('location'),
                'inline': True
            })
        
        if labels.get('name'):  # For container alerts
            embed['fields'].append({
                'name': '🐳 Container',
                'value': labels.get('name'),
                'inline': True
            })
        
        embeds.append(embed)
    
    # Send to Discord (max 10 embeds per message)
    for i in range(0, len(embeds), 10):
        batch = embeds[i:i+10]
        data = {
            'username': 'Prometheus Alert',
            'embeds': batch
        }
        
        headers = {'Content-Type': 'application/json'}
        r = requests.post(DISCORD_WEBHOOK_URL, headers=headers, json=data, timeout=10)
        
        if r.status_code in (200, 204):
            logging.info(f'Sent {len(batch)} alerts to Discord webhook')
        else:
            logging.error(f'Failed to send to Discord: {r.status_code} {r.text}')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
