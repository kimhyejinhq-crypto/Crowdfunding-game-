from flask import Flask, render_template, request, jsonify
import random
import math
import uuid

app = Flask(__name__)
app.secret_key = 'startup-game-secret'

# ===================== DỮ LIỆU MẪU (tối giản để test) =====================
SCENARIOS = [
    {"id":1,"name":"Tin tốt nhẹ","cat":"Market","delta":{"price":0.05,"hype":10,"transparency":5}},
    {"id":2,"name":"Tin xấu nhẹ","cat":"Market","delta":{"price":-0.05,"hype":-10,"transparency":-5}},
]

ACTIVE_CARDS_FULL = [
    {"id":"A1","name":"Marketing Blitz","cost":2,"type":"red","desc":"Tăng Hype","effect":{"hype":25,"transparency":-5}},
    {"id":"D1","name":"Cost Cutting","cost":1,"type":"green","desc":"Giảm COGS","effect":{"cogs_percent":-3,"transparency":5}},
]

REACTION_CARDS = [
    {"id":"R1","name":"Emergency PR","trigger":"on_scenario_market_bad","desc":"Giảm 50% delta xấu","cost_percent":3,"effect":{"halve_negative_delta":1}},
]

# Hàm tạo bot giả
def init_bots(seed=42):
    random.seed(seed)
    bots = []
    for i in range(1, 51):  # chỉ 50 bot để nhẹ
        bot_type = random.choice(["FOMO","Value Hunter"])
        wealth = random.randint(10000, 200000)
        bots.append({"id":i,"type":bot_type,"wealth":wealth,"weights":{"hype":0.5,"transparency":0.5}})
    return bots

BOTS = init_bots()

# ===================== HÀM TÍNH TOÁN =====================
def clamp(x, lo, hi): return max(lo, min(hi, x))

def calculate_metrics(proj):
    return {"runway":10, "funding_progress":proj.get('funding_progress',0)}

def attractiveness(project, bot, metrics):
    return random.uniform(0,100)

def final_score(proj, phases_used, metrics):
    return proj.get('funding_progress',0) * 100

# ===================== QUẢN LÝ PHÒNG =====================
rooms = {}

@app.route('/')
def index():
    return render_template('host.html')

@app.route('/play/<room_id>/<int:player_index>')
def play_page(room_id, player_index):
    if room_id not in rooms:
        return "Phòng không tồn tại", 404
    room = rooms[room_id]
    if player_index < 0 or player_index >= room['num_players']:
        return "Chỉ số người chơi không hợp lệ", 400
    if room['players'][player_index] is not None:
        return "Slot này đã có người chơi", 400
    return render_template('play.html', room_id=room_id, player_index=player_index, max_players=room['num_players'])

@app.route('/api/create_room', methods=['POST'])
def create_room():
    data = request.json
    num_players = data.get('num_players', 4)
    room_id = str(uuid.uuid4())[:8]
    base_url = request.host_url.rstrip('/')
    join_links = [f"{base_url}/play/{room_id}/{i}" for i in range(num_players)]
    rooms[room_id] = {
        'num_players': num_players,
        'players': [None] * num_players,
        'phase': 0,
        'max_phase': 0,
        'status': 'waiting',
        'bot_alloc': None,
        'logs': [],
        'player_ready': [False] * num_players,
        'pending_cards': {},
        'mulligan_used': [False] * num_players,
        'game_ended': False,
        'player_triggers': [{} for _ in range(num_players)]
    }
    return jsonify({'room_id': room_id, 'join_links': join_links})

@app.route('/api/submit_project', methods=['POST'])
def submit_project():
    data = request.json
    room_id = data['room_id']
    player_index = data['player_index']
    project_data = data['project']
    if room_id not in rooms:
        return jsonify({'error': 'Room not found'}), 404
    room = rooms[room_id]
    if room['players'][player_index] is not None:
        return jsonify({'error': 'Slot taken'}), 400
    project_data['funding_progress'] = 0
    project_data['current_phase'] = 0
    room['players'][player_index] = project_data
    room['player_ready'][player_index] = True
    if all(p is not None for p in room['players']):
        room['status'] = 'choosing_deck'
        room['player_ready'] = [False] * room['num_players']
    return jsonify({'ok': True})

@app.route('/api/submit_deck', methods=['POST'])
def submit_deck():
    data = request.json
    room_id = data['room_id']
    player_index = data['player_index']
    active_indices = data['active_indices']
    reaction_indices = data['reaction_indices']
    if room_id not in rooms:
        return jsonify({'error': 'Room not found'}), 404
    room = rooms[room_id]
    proj = room['players'][player_index]
    proj['active_deck'] = [ACTIVE_CARDS_FULL[i] for i in active_indices]
    proj['reaction_hand'] = [REACTION_CARDS[i] for i in reaction_indices]
    room['player_ready'][player_index] = True
    if all(room['player_ready']):
        max_phase = max(p['max_phase'] for p in room['players'])
        room['max_phase'] = max_phase
        room['phase'] = 1
        room['status'] = 'playing'
        room['player_ready'] = [False] * room['num_players']
        for idx, proj in enumerate(room['players']):
            if proj:
                proj['current_hand'] = random.sample(proj['active_deck'], min(5, len(proj['active_deck'])))
                proj['energy_left'] = 3
    return jsonify({'ok': True})

@app.route('/api/host_state', methods=['GET'])
def host_state():
    room_id = request.args.get('room_id')
    if room_id not in rooms:
        return jsonify({'error': 'Room not found'}), 404
    room = rooms[room_id]
    rankings = []
    for i, proj in enumerate(room['players']):
        if proj:
            rankings.append({
                'name': f"Player {i+1}",
                'funding': proj.get('funding_progress',0),
                'hype': 50,
                'transparency': 50,
                'score': 0,
                'scale': 'M',
                'status': 'active',
            })
        else:
            rankings.append({'name': f"Player {i+1}", 'funding': 0, 'score': 0, 'status': 'not_joined'})
    return jsonify({
        'status': room['status'],
        'phase': room['phase'],
        'players_joined': sum(1 for p in room['players'] if p is not None),
        'max_players': room['num_players'],
        'logs': room.get('logs', []),
        'rankings': rankings,
        'all_ready': all(room['player_ready']) if room['status']=='playing' else False,
        'game_ended': room.get('game_ended', False)
    })

@app.route('/api/player_state', methods=['GET'])
def player_state():
    room_id = request.args.get('room_id')
    player_index = int(request.args.get('player_index', -1))
    if room_id not in rooms:
        return jsonify({'error': 'Room not found'}), 404
    room = rooms[room_id]
    if player_index < 0 or player_index >= len(room['players']) or room['players'][player_index] is None:
        return jsonify({'error': 'Player not found'}), 404
    proj = room['players'][player_index]
    return jsonify({
        'status': room['status'],
        'phase': room['phase'],
        'metrics': {'runway':10},
        'hype': 50,
        'transparency': 50,
        'hand': proj.get('current_hand', []),
        'energy_left': proj.get('energy_left', 3),
        'funding_progress': proj.get('funding_progress',0),
        'game_ended': room.get('game_ended', False),
        'triggers': []
    })

@app.route('/api/play_card', methods=['POST'])
def play_card():
    return jsonify({'ok': True})

@app.route('/api/mulligan', methods=['POST'])
def mulligan():
    return jsonify({'ok': True})

@app.route('/api/player_ready_phase', methods=['POST'])
def player_ready_phase():
    data = request.json
    room_id = data['room_id']
    player_index = data['player_index']
    if room_id not in rooms:
        return jsonify({'error': 'Room not found'}), 404
    room = rooms[room_id]
    room['player_ready'][player_index] = True
    return jsonify({'ok': True})

@app.route('/api/use_reaction', methods=['POST'])
def use_reaction():
    return jsonify({'ok': True})

@app.route('/api/run_phase', methods=['POST'])
def run_phase():
    data = request.json
    room_id = data['room_id']
    if room_id not in rooms:
        return jsonify({'error': 'Room not found'}), 404
    room = rooms[room_id]
    room['player_ready'] = [False] * room['num_players']
    room['phase'] += 1
    return jsonify({'ended': room['phase'] > room['max_phase'], 'phase': room['phase']})

@app.route('/api/card_lists', methods=['GET'])
def card_lists():
    return jsonify({'active': ACTIVE_CARDS_FULL, 'reaction': REACTION_CARDS})

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
