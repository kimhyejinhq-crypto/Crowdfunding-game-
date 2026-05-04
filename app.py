from flask import Flask, render_template, request, jsonify
import random
import math
import uuid

app = Flask(__name__, template_folder='templates')
app.secret_key = 'startup-game-secret'

# ===================== DỮ LIỆU CỐ ĐỊNH =====================
SCENARIOS = [
    # Market (6)
    {"id":1,"name":"Tin tốt nhẹ","cat":"Market","delta":{"price":0.05,"cogs":0,"hype":10,"sentiment":5,"transparency":0,"reg_risk":0}},
    {"id":2,"name":"Tin tốt vừa","cat":"Market","delta":{"price":0.1,"cogs":-0.05,"hype":20,"sentiment":10,"transparency":0,"reg_risk":0}},
    {"id":3,"name":"Tin xấu nhẹ","cat":"Market","delta":{"price":-0.05,"cogs":0.03,"hype":-10,"sentiment":-5,"transparency":0,"reg_risk":0}},
    {"id":4,"name":"Tin xấu vừa","cat":"Market","delta":{"price":-0.1,"cogs":0.05,"hype":-20,"sentiment":-15,"transparency":-5,"reg_risk":5}},
    {"id":5,"name":"Khủng hoảng nhẹ","cat":"Market","delta":{"price":-0.15,"cogs":0.1,"hype":-30,"sentiment":-20,"transparency":-10,"reg_risk":10}},
    {"id":6,"name":"Khủng hoảng nặng","cat":"Market","delta":{"price":-0.25,"cogs":0.15,"hype":-40,"sentiment":-30,"transparency":-20,"reg_risk":20}},
    # Internal (6)
    {"id":7,"name":"Máy móc hỏng nhẹ","cat":"Internal","delta":{"cogs":0.05,"hype":-5,"transparency":-5,"trust_all":-5,"runway":-1}},
    {"id":8,"name":"Lỗi sản xuất vừa","cat":"Internal","delta":{"cogs":0.1,"hype":-10,"transparency":-10,"trust_all":-10,"runway":-2}},
    {"id":9,"name":"Rò rỉ dữ liệu","cat":"Internal","delta":{"cogs":0,"hype":-15,"transparency":-20,"trust_all":-15,"runway":0}},
    {"id":10,"name":"Nhân sự chủ chốt nghỉ","cat":"Internal","delta":{"cogs":0.03,"hype":-10,"transparency":-5,"trust_all":-5,"runway":0}},
    {"id":11,"name":"Được giải thưởng","cat":"Internal","delta":{"cogs":-0.05,"hype":15,"transparency":10,"trust_all":10,"runway":0}},
    {"id":12,"name":"Audit nội bộ tốt","cat":"Internal","delta":{"cogs":0,"hype":5,"transparency":15,"trust_all":10,"runway":0}},
    # External (6)
    {"id":13,"name":"Đối thủ giảm giá","cat":"External","delta":{"price":-0.05,"marketing_eff":-0.1,"hype":-5,"transparency":0}},
    {"id":14,"name":"Đối thủ ra sản phẩm mới","cat":"External","delta":{"price":-0.1,"marketing_eff":-0.2,"hype":-15,"transparency":-5}},
    {"id":15,"name":"Hợp tác chiến lược","cat":"External","delta":{"price":0.05,"marketing_eff":0.15,"hype":15,"transparency":5}},
    {"id":16,"name":"Bị kiện bản quyền","cat":"External","delta":{"price":-0.08,"marketing_eff":-0.15,"hype":-20,"transparency":-10}},
    {"id":17,"name":"Được cấp bằng sáng chế","cat":"External","delta":{"price":0.1,"marketing_eff":0.1,"hype":10,"transparency":5}},
    {"id":18,"name":"Tin đồn thâu tóm","cat":"External","delta":{"price":0.15,"marketing_eff":0.05,"hype":25,"transparency":-5}},
    # Regulatory (6)
    {"id":19,"name":"Thanh tra đột xuất","cat":"Regulatory","delta":{"reg_risk":25,"transparency":-10,"trust_all":-10,"legal_cost_percent":5}},
    {"id":20,"name":"Được cấp phép sandbox","cat":"Regulatory","delta":{"reg_risk":-30,"transparency":15,"trust_all":15,"legal_cost_percent":-3}},
    {"id":21,"name":"Thay đổi luật có lợi","cat":"Regulatory","delta":{"reg_risk":-15,"transparency":5,"trust_all":5,"legal_cost_percent":0}},
    {"id":22,"name":"Thay đổi luật bất lợi","cat":"Regulatory","delta":{"reg_risk":25,"transparency":-10,"trust_all":-10,"legal_cost_percent":5}},
    {"id":23,"name":"Kiểm toán thuế","cat":"Regulatory","delta":{"reg_risk":10,"transparency":-5,"trust_all":-5,"legal_cost_percent":2}},
    {"id":24,"name":"Chứng nhận quốc tế","cat":"Regulatory","delta":{"reg_risk":-10,"transparency":10,"trust_all":10,"legal_cost_percent":-2}},
    # Security (6)
    {"id":25,"name":"Lỗ hổng nhỏ","cat":"Security","delta":{"security":-10,"transparency":-5,"trust_all":-5,"hype":-5}},
    {"id":26,"name":"Hack smart contract","cat":"Security","delta":{"security":-30,"transparency":-20,"trust_all":-20,"hype":-15}},
    {"id":27,"name":"Mất private key","cat":"Security","delta":{"security":-20,"transparency":-15,"trust_all":-15,"hype":-10}},
    {"id":28,"name":"Audit bảo mật pass","cat":"Security","delta":{"security":20,"transparency":10,"trust_all":10,"hype":5}},
    {"id":29,"name":"Multi‑sig được kích hoạt","cat":"Security","delta":{"security":10,"transparency":5,"trust_all":5,"hype":0}},
    {"id":30,"name":"Bug bounty thành công","cat":"Security","delta":{"security":15,"transparency":5,"trust_all":5,"hype":5}},
]

ACTIVE_CARDS_FULL = [
    {"id":"A1","name":"Marketing Blitz","cost":2,"type":"red","desc":"Tăng Hype, giảm Transparency","effect":{"hype":25,"transparency":-5,"cost_percent":3}},
    {"id":"A2","name":"Viral Campaign","cost":3,"type":"red","desc":"Tăng Hype mạnh","effect":{"hype":40,"transparency":-10,"cost_percent":5}},
    {"id":"A3","name":"Flash Sale","cost":2,"type":"red","desc":"Giảm giá tạm thời, tăng Hype","effect":{"price_percent":-15,"hype":15}},
    {"id":"A4","name":"Influencer Deal","cost":2,"type":"red","desc":"Tăng Hype và Visibility","effect":{"hype":20,"visibility":15,"cost_percent":2}},
    {"id":"A5","name":"Airdrop","cost":3,"type":"red","desc":"Tăng Hype và Utility","effect":{"hype":30,"utility":5,"cost_percent":4}},
    {"id":"A6","name":"FOMO Campaign","cost":2,"type":"red","desc":"Tăng Hype, thêm funding","effect":{"hype":20,"funding_boost_percent":5}},
    {"id":"A7","name":"Celebrity Endorsement","cost":2,"type":"red","desc":"Tăng Hype, giảm nhẹ minh bạch","effect":{"hype":25,"transparency":-3,"cost_percent":4}},
    {"id":"A8","name":"Token Burn Announce","cost":3,"type":"red","desc":"Tăng Hype, Utility, Transparency","effect":{"hype":15,"utility":10,"transparency":5}},
    {"id":"A9","name":"Limited Offer","cost":1,"type":"red","desc":"Tăng Hype, Visibility nhẹ","effect":{"hype":10,"visibility":5}},
    {"id":"A10","name":"Shill Army","cost":2,"type":"red","desc":"Tăng Hype cao, giảm minh bạch","effect":{"hype":30,"transparency":-15,"cost_percent":2}},
    {"id":"A11","name":"Pre-sale Discount","cost":2,"type":"red","desc":"Giảm giá, tăng funding","effect":{"price_percent":-10,"funding_boost_percent":10}},
    {"id":"A12","name":"Media Blast","cost":2,"type":"red","desc":"Tăng Hype, Visibility","effect":{"hype":20,"visibility":10,"cost_percent":1}},
    {"id":"A13","name":"Meme Marketing","cost":1,"type":"red","desc":"Tăng Hype nhẹ, giảm minh bạch","effect":{"hype":15,"transparency":-2}},
    {"id":"A14","name":"Aggressive Pricing","cost":2,"type":"red","desc":"Giảm giá sâu, tăng Hype","effect":{"price_percent":-20,"hype":10}},
    {"id":"D1","name":"Cost Cutting","cost":1,"type":"green","desc":"Giảm COGS, tăng minh bạch","effect":{"cogs_percent":-3,"transparency":5}},
    {"id":"D2","name":"Community Update","cost":1,"type":"green","desc":"Tăng Hype nhẹ, minh bạch","effect":{"hype":5,"transparency":3}},
    {"id":"D3","name":"Third Party Audit","cost":2,"type":"green","desc":"Tăng minh bạch, giảm rủi ro","effect":{"transparency":15,"reg_risk":-10,"cost_percent":5}},
    {"id":"D4","name":"Vesting Pledge","cost":1,"type":"green","desc":"Tăng minh bạch, trust","effect":{"transparency":10,"trust_all":5}},
    {"id":"D5","name":"Emergency Fund","cost":2,"type":"green","desc":"Tăng runway","effect":{"runway":2,"cost_percent":5}},
    {"id":"D6","name":"Open Book","cost":2,"type":"green","desc":"Tăng minh bạch mạnh","effect":{"transparency":20,"cost_percent":2}},
    {"id":"D7","name":"Bug Bounty Program","cost":1,"type":"green","desc":"Tăng security, minh bạch","effect":{"security":10,"transparency":5}},
    {"id":"D8","name":"Legal Shield","cost":2,"type":"green","desc":"Giảm rủi ro pháp lý","effect":{"reg_risk":-15,"cost_percent":3}},
    {"id":"D9","name":"Slow & Steady","cost":1,"type":"green","desc":"Tăng minh bạch, Hype nhẹ","effect":{"transparency":5,"hype":2}},
    {"id":"D10","name":"Crisis Management","cost":2,"type":"green","desc":"Giảm 50% delta tiêu cực","effect":{"halve_negative_delta":1}},
    {"id":"D11","name":"Supply Chain Fix","cost":2,"type":"green","desc":"Giảm COGS, tăng minh bạch","effect":{"cogs_percent":-5,"transparency":5}},
    {"id":"D12","name":"Investor Call","cost":1,"type":"green","desc":"Tăng trust tất cả bot","effect":{"trust_all":10,"cost_percent":1}},
    {"id":"D13","name":"Transparency Report","cost":2,"type":"green","desc":"Tăng minh bạch, giảm Hype","effect":{"transparency":15,"hype":-5}},
    {"id":"D14","name":"Multi‑sig Enable","cost":1,"type":"green","desc":"Tăng security, minh bạch","effect":{"security":15,"transparency":5}},
    {"id":"T1","name":"Whale Discount","cost":3,"type":"purple","desc":"Tăng funding, giảm trust Whale","effect":{"funding_boost_percent":15,"trust_whale":-10,"cost_percent":2}},
    {"id":"T2","name":"Token Buyback","cost":2,"type":"purple","desc":"Giảm funding, tăng trust, utility","effect":{"funding_boost_percent":-10,"trust_all":15,"utility":10,"cost_percent":10}},
    {"id":"T3","name":"Secondary Offering","cost":3,"type":"purple","desc":"Tăng funding, giảm trust, dilution","effect":{"funding_boost_percent":20,"trust_all":-15,"dilution":10}},
    {"id":"T4","name":"DAO Vote","cost":2,"type":"purple","desc":"Tăng minh bạch, trust","effect":{"transparency":5,"trust_all":5}},
    {"id":"T5","name":"Staking Launch","cost":2,"type":"purple","desc":"Tăng utility, giảm velocity","effect":{"utility":15,"velocity":-0.2}},
    {"id":"T6","name":"Treasury Diversify","cost":2,"type":"purple","desc":"Giảm rủi ro, tăng trust","effect":{"reg_risk":-10,"trust_all":10}},
    {"id":"T7","name":"Token Split","cost":2,"type":"purple","desc":"Tăng funding, Hype, dilution","effect":{"funding_boost_percent":5,"hype":10,"dilution":5}},
    {"id":"T8","name":"Governance Proposal","cost":1,"type":"purple","desc":"Tăng minh bạch, trust","effect":{"transparency":5,"trust_all":5}},
    {"id":"T9","name":"Vesting Extension","cost":2,"type":"purple","desc":"Tăng trust, minh bạch","effect":{"trust_all":20,"transparency":10,"cost_percent":2}},
    {"id":"T10","name":"Liquidity Mining","cost":3,"type":"purple","desc":"Tăng utility, giảm velocity","effect":{"utility":20,"velocity":-0.3,"cost_percent":5}},
    {"id":"T11","name":"Strategic Partnership","cost":2,"type":"purple","desc":"Tăng trust, giảm rủi ro","effect":{"trust_all":15,"reg_risk":-5,"cost_percent":3}},
    {"id":"T12","name":"Burn Mechanism","cost":2,"type":"purple","desc":"Tăng utility, Hype","effect":{"utility":15,"hype":10,"cost_percent":2}},
    {"id":"T13","name":"Airdrop to Holders","cost":2,"type":"purple","desc":"Tăng trust, Hype","effect":{"trust_all":10,"hype":15,"cost_percent":4}},
    {"id":"T14","name":"Equity Swap","cost":3,"type":"purple","desc":"Tăng funding mạnh, giảm trust, dilution cao","effect":{"funding_boost_percent":30,"trust_all":-20,"dilution":20}},
]

REACTION_CARDS = [
    {"id":"R1","name":"Lock‑up Extension","trigger":"on_bot_withdraw","desc":"Giảm bán tháo khi bot rút","cost_percent":2,"effect":{"sell_pressure_reduce":0.5}},
    {"id":"R2","name":"Emergency PR","trigger":"on_scenario_market_bad","desc":"Giảm 50% delta xấu","cost_percent":3,"effect":{"halve_negative_delta":1}},
    {"id":"R3","name":"Whale Whisperer","trigger":"on_whale_trust<30","desc":"Tăng trust của Whale","cost_percent":5,"effect":{"whale_trust":10}},
    {"id":"R4","name":"Damage Control","trigger":"on_transparency<30","desc":"Tăng transparency, giảm Hype","cost_percent":2,"effect":{"transparency":10,"hype":-5}},
    {"id":"R5","name":"Liquidity Injection","trigger":"on_circuit_breaker","desc":"Rút ngắn circuit breaker","cost_percent":8,"effect":{"circuit_breaker_reduce":1}},
    {"id":"R6","name":"Legal Emergency","trigger":"on_reg_risk>70","desc":"Giảm rủi ro pháp lý","cost_percent":4,"effect":{"reg_risk":-20}},
    {"id":"R7","name":"Security Patch","trigger":"on_security<30","desc":"Tăng security","cost_percent":3,"effect":{"security":15}},
    {"id":"R8","name":"FOMO Suppression","trigger":"on_hype>80","desc":"Giảm Hype, tăng transparency","cost_percent":1,"effect":{"hype":-15,"transparency":5}},
    {"id":"R9","name":"Investor Assurance","trigger":"on_trust_any_bot<20","desc":"Tăng trust cho bot đó","cost_percent":2,"effect":{"trust_single":15}},
    {"id":"R10","name":"Runway Boost","trigger":"on_runway<3","desc":"Thêm 3 tháng runway","cost_percent":10,"effect":{"runway":3}},
]

# 200 bot (sinh ngẫu nhiên) - dùng seed cố định để đồng bộ
random.seed(42)
BOTS = []
for i in range(1, 201):
    bot_type = random.choices(["FOMO","Value Hunter","Whale","Random"], weights=[50,30,10,10])[0]
    wealth_class = random.choices(["small","medium","large"], weights=[40,40,20])[0]
    wealth = {"small":random.randint(10000,50000), "medium":random.randint(100000,500000), "large":random.randint(500000,2000000)}[wealth_class]
    hype_sens = round(random.uniform(1.2,1.8),2)
    trans_sens = round(random.uniform(0.5,1.2),2)
    decay = round(random.uniform(0.1,0.3),2)
    if bot_type == "FOMO":
        weights = {"intrinsic":0.1,"valuation":0.1,"roi_norm":0.1,"scalability":0.05,"transparency":0.05,"hype":0.28,"visibility":0.09,"funding_prog":0.09,"liquidity":0.14}
    elif bot_type == "Value Hunter":
        weights = {"intrinsic":0.27,"valuation":0.2,"roi_norm":0.15,"scalability":0.03,"transparency":0.14,"funding_prog":0.05,"liquidity":0.07}
    elif bot_type == "Whale":
        weights = {"intrinsic":0.17,"valuation":0.2,"roi_norm":0.15,"scalability":0.03,"transparency":0.18,"funding_prog":0.05,"liquidity":0.07}
    else:
        weights = {"intrinsic":0.1,"valuation":0.1,"roi_norm":0.1,"scalability":0.05,"transparency":0.05,"hype":0.08,"visibility":0.05,"funding_prog":0.09,"liquidity":0.18}
    BOTS.append({"id":i,"type":bot_type,"wealth_class":wealth_class,"wealth":wealth,"hype_sens":hype_sens,"trans_sens":trans_sens,"memory_decay_rate":decay,"weights":weights})

# ===================== HÀM TÍNH TOÁN =====================
def clamp(x, lo, hi):
    return max(lo, min(hi, x))

def calculate_metrics(proj):
    ch_fees = (proj["fee_ecom"] + proj["fee_retail"] + proj["fee_direct"]) / 100.0
    price_real = proj["price"] * (1 - ch_fees)
    cogs_unit = proj["material"] + proj["packaging"] + proj["shipping"] + proj["defect_rate"]*(proj["material"]+proj["packaging"]+proj["shipping"])
    gm = (price_real - cogs_unit)/price_real if price_real>0 else 0
    monthly_burn = proj["fixed_cost"] + proj["marketing_cost"] + (proj["loan"] * proj["interest_rate"]/100 /12)
    burn_rate = monthly_burn / proj["target_funding"]
    growth = (proj["units_m6"]/proj["units_m1"]) - 1 if proj["units_m1"]>0 else 0
    unit_econ = clamp(20 + 20*(1 - math.exp(-5*(gm-0.2)/0.6)), 20, 40) if gm>0.2 else 20
    burn_score = clamp(10 + 20*(1 - math.exp(-4*(0.3-burn_rate)/0.25)), 10, 30) if burn_rate<0.3 else 10
    scal_score = clamp(10 + 20*(1 - math.exp(-3*growth/0.5)), 10, 30) if growth>0 else 10
    intrinsic = unit_econ + burn_score + scal_score
    equity = proj["equity_offered"]/100
    post_money = proj["target_funding"]/equity if equity>0 else 1e12
    revenue_year = proj["units_m6"] * 12 * price_real
    mult = post_money/revenue_year if revenue_year>0 else 1000
    if mult < 1: val_score = 30 - (1-mult)/1*30
    elif mult <= 3: val_score = 80 + (mult-1)/2*20
    elif mult <= 5: val_score = 80 - (mult-3)/2*40
    else: val_score = max(0, 40 - (mult-5)/2*40)
    val_score = clamp(val_score, 0, 100)
    raw_roi = ((post_money - proj["target_funding"])/proj["target_funding"])*100 if proj["target_funding"]>0 else 0
    if raw_roi<0: raw_roi=0
    roi_norm = min(100, 20*math.log10(raw_roi+1))
    base_reg = 20 if proj.get("has_license",False) else 80
    if proj.get("legal_cost_spent",0) >= 0.05*proj["target_funding"]: base_reg += 20
    reg_risk = clamp(base_reg - proj["transparency"]/10, 0, 100)
    sec = 50 + (30 if proj.get("has_audit",False) else 0)+(20 if proj.get("multisig",False) else 0)-10*proj.get("count_hack_events",0)
    sec = clamp(sec,0,100)
    util = 50
    for u in proj.get("utility_list",[]):
        if u in ["governance","staking","burn","discount"]: util+=10
    util = clamp(util,0,100)
    avail_cash = proj.get("available_cash", proj["owner_equity"]+proj["loan"])
    runway = math.floor(avail_cash / monthly_burn) if monthly_burn>0 else 999
    total_invested = proj.get("total_invested",0)
    total_supply = proj.get("total_supply_token",0)
    vel = proj.get("velocity",1.0)
    liquidity = 100 if total_supply==0 else min(100, (total_invested/(total_supply*vel))*100)
    return {
        "intrinsic":intrinsic, "valuation_sanity":val_score, "roi_norm":roi_norm,
        "growth":growth, "monthly_burn":monthly_burn, "available_cash":avail_cash,
        "runway":runway, "liquidity":liquidity, "funding_progress":proj.get("funding_progress",0)
    }

def attractiveness(project, bot, metrics):
    raw = 0
    total_w = 0
    for key, w in bot["weights"].items():
        if key=="intrinsic": val = metrics["intrinsic"]
        elif key=="valuation": val = metrics["valuation_sanity"]
        elif key=="roi_norm": val = metrics["roi_norm"]
        elif key=="scalability": val = clamp(metrics["growth"]*100,0,100)
        elif key=="transparency": val = project["transparency"]
        elif key=="hype": val = project["hype"]
        elif key=="visibility": val = project["visibility"]
        elif key=="funding_prog": val = metrics["funding_progress"]*100
        elif key=="liquidity": val = metrics["liquidity"]
        else: continue
        sens = bot["hype_sens"] if key=="hype" else (bot["trans_sens"] if key=="transparency" else 1.0)
        raw += val * w * sens
        total_w += w
    if total_w==0: return 0
    raw_A = (raw/total_w)*100
    if metrics["valuation_sanity"] < 40:
        raw_A = max(0, raw_A - (40-metrics["valuation_sanity"])*1.5)
    trust = project["trust_scores"].get(bot["id"], 50)
    noise = random.uniform(-5,5) if bot["type"]!="Random" else random.uniform(-10,10)
    return raw_A * (trust/100) + noise

def final_score(proj, phases_used, metrics):
    if proj["funding_progress"] < 0.5:
        return 0
    funding_score = proj["funding_progress"] * 30
    speed_score = (100 - phases_used) * 0.2
    roi_score = min(30, max(0, (metrics["roi_norm"]/100)*30))
    trans_score = (proj["transparency"]/100)*20
    raw = funding_score + speed_score + roi_score + trans_score
    perf_phase = raw / phases_used if phases_used>0 else 0
    return perf_phase * proj["scale_factor"] * (1 + proj["funding_progress"])

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
    if num_players < 2 or num_players > 10:
        num_players = 4
    room_id = str(uuid.uuid4())[:8]
    base_url = request.host_url.rstrip('/')
    join_links = []
    for i in range(num_players):
        join_links.append(f"{base_url}/play/{room_id}/{i}")
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
        'phase_energy': [3] * num_players,
        'mulligan_used': [False] * num_players,
        'reaction_hand': [None] * num_players,
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
    if player_index >= len(room['players']) or room['players'][player_index] is not None:
        return jsonify({'error': 'Slot taken'}), 400
    project_data['trust_scores'] = {bot['id']: 50 for bot in BOTS}
    project_data['status'] = 'active'
    project_data['funding_progress'] = 0
    project_data['total_invested'] = 0
    project_data['available_cash'] = project_data['owner_equity'] + project_data['loan']
    project_data['legal_cost_spent'] = 0
    project_data['velocity'] = 1.0
    project_data['utility_list'] = project_data.get('utility_list', [])
    project_data['current_phase'] = 0
    project_data['max_phase'] = project_data['max_phase']
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
    if len(active_indices) != 22:
        return jsonify({'error': 'Phải chọn đúng 22 active cards'}), 400
    if len(reaction_indices) > 3:
        return jsonify({'error': 'Tối đa 3 reaction cards'}), 400
    proj = room['players'][player_index]
    proj['active_deck'] = [ACTIVE_CARDS_FULL[i] for i in active_indices]
    proj['reaction_hand'] = [REACTION_CARDS[i].copy() for i in reaction_indices]
    room['player_ready'][player_index] = True
    if all(room['player_ready']):
        max_phase = max(p['max_phase'] for p in room['players'])
        room['max_phase'] = max_phase
        bot_alloc = []
        for bot in BOTS:
            per = [0] * room['num_players']
            bot_alloc.append({'bot_id': bot['id'], 'perProject': per, 'idle': bot['wealth']})
        room['bot_alloc'] = bot_alloc
        room['phase'] = 1
        room['status'] = 'playing'
        room['player_ready'] = [False] * room['num_players']
        room['pending_cards'] = {}
        room['phase_energy'] = [3] * room['num_players']
        room['mulligan_used'] = [False] * room['num_players']
        for idx, proj in enumerate(room['players']):
            if proj:
                deck = proj['active_deck']
                proj['current_hand'] = random.sample(deck, min(5, len(deck)))
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
            ended = proj.get('current_phase', 0) >= proj['max_phase']
            if ended:
                proj_status = 'ended'
            else:
                proj_status = proj.get('status', 'active')
            metrics = calculate_metrics(proj)
            if ended:
                score = final_score(proj, proj['max_phase'], metrics)
            else:
                score = 0
            rankings.append({
                'name': f"Player {i+1}",
                'funding': proj['funding_progress'],
                'hype': proj['hype'],
                'transparency': proj['transparency'],
                'score': score,
                'scale': proj['scale'],
                'status': proj_status,
                'current_phase': proj.get('current_phase', 0),
                'max_phase': proj['max_phase']
            })
        else:
            rankings.append({'name': f"Player {i+1}", 'funding': 0, 'score': 0, 'status': 'not_joined'})
    all_ended = all(p is None or p.get('current_phase', 0) >= p['max_phase'] for p in room['players'])
    if room['status'] == 'playing' and (room['phase'] > room['max_phase'] or all_ended):
        room['game_ended'] = True
        room['status'] = 'ended'
    return jsonify({
        'status': room['status'],
        'phase': room['phase'],
        'max_phase': room['max_phase'],
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
    metrics = calculate_metrics(proj)
    investors = []
    if room['bot_alloc']:
        for alloc in room['bot_alloc']:
            amount = alloc['perProject'][player_index]
            if amount > 0:
                bot = next((b for b in BOTS if b['id'] == alloc['bot_id']), None)
                if bot:
                    investors.append({'type': bot['type'], 'amount': amount})
    ended = proj.get('current_phase', 0) >= proj['max_phase']
    final_score_value = 0
    if ended:
        final_score_value = final_score(proj, proj['max_phase'], metrics)
    triggers = room['player_triggers'][player_index] if player_index < len(room['player_triggers']) else {}
    return jsonify({
        'status': room['status'],
        'phase': room['phase'],
        'last_scenario': proj.get('last_scenario', 'Chưa có sự kiện'),
        'metrics': metrics,
        'hype': proj['hype'],
        'transparency': proj['transparency'],
        'hand': proj.get('current_hand', []),
        'energy_left': proj.get('energy_left', 3),
        'mulligan_used': room['mulligan_used'][player_index],
        'investors': investors,
        'funding_progress': proj['funding_progress'],
        'available_cash': metrics['available_cash'],
        'reaction_hand': proj.get('reaction_hand', []),
        'game_ended': room.get('game_ended', False),
        'ended': ended,
        'final_score': final_score_value,
        'triggers': triggers.get('available_reactions', [])
    })

@app.route('/api/play_card', methods=['POST'])
def play_card():
    data = request.json
    room_id = data['room_id']
    player_index = data['player_index']
    card_index = data['card_index']
    if room_id not in rooms:
        return jsonify({'error': 'Room not found'}), 404
    room = rooms[room_id]
    if room['status'] != 'playing':
        return jsonify({'error': 'Game not in playing'}), 400
    proj = room['players'][player_index]
    if card_index >= len(proj['current_hand']):
        return jsonify({'error': 'Invalid card'}), 400
    card = proj['current_hand'][card_index]
    cost = card['cost']
    if proj['energy_left'] < cost:
        return jsonify({'error': 'Not enough energy'}), 400
    room['pending_cards'][player_index] = card
    proj['energy_left'] -= cost
    proj['current_hand'].pop(card_index)
    return jsonify({'ok': True})

@app.route('/api/mulligan', methods=['POST'])
def mulligan():
    data = request.json
    room_id = data['room_id']
    player_index = data['player_index']
    if room_id not in rooms:
        return jsonify({'error': 'Room not found'}), 404
    room = rooms[room_id]
    if room['status'] != 'playing':
        return jsonify({'error': 'Not in game'}), 400
    proj = room['players'][player_index]
    if room['mulligan_used'][player_index]:
        return jsonify({'error': 'Already used'}), 400
    if proj['energy_left'] < 1:
        return jsonify({'error': 'Not enough energy'}), 400
    deck = proj['active_deck']
    proj['current_hand'] = random.sample(deck, min(3, len(deck)))
    proj['energy_left'] -= 1
    proj['transparency'] = max(0, proj['transparency'] - 2)
    for bid in proj['trust_scores']:
        proj['trust_scores'][bid] = max(0, proj['trust_scores'][bid] - 1)
    room['mulligan_used'][player_index] = True
    return jsonify({'ok': True})

@app.route('/api/player_ready_phase', methods=['POST'])
def player_ready_phase():
    data = request.json
    room_id = data['room_id']
    player_index = data['player_index']
    if room_id not in rooms:
        return jsonify({'error': 'Room not found'}), 404
    room = rooms[room_id]
    if room['status'] != 'playing':
        return jsonify({'error': 'Not playing'}), 400
    room['player_ready'][player_index] = True
    return jsonify({'ok': True})

@app.route('/api/use_reaction', methods=['POST'])
def use_reaction():
    data = request.json
    room_id = data['room_id']
    player_index = data['player_index']
    reaction_index = data['reaction_index']
    if room_id not in rooms:
        return jsonify({'error': 'Room not found'}), 404
    room = rooms[room_id]
    if room['status'] != 'playing':
        return jsonify({'error': 'Not playing'}), 400
    proj = room['players'][player_index]
    if reaction_index >= len(proj.get('reaction_hand', [])):
        return jsonify({'error': 'Invalid reaction'}), 400
    rc = proj['reaction_hand'][reaction_index]
    available_ids = [r['id'] for r in room['player_triggers'][player_index].get('available_reactions', [])]
    if rc['id'] not in available_ids:
        return jsonify({'error': 'Reaction not available now'}), 400
    eff = rc['effect']
    if 'transparency' in eff: proj['transparency'] += eff['transparency']
    if 'hype' in eff: proj['hype'] += eff['hype']
    if 'runway' in eff:
        m = calculate_metrics(proj)
        proj['available_cash'] += eff['runway'] * m['monthly_burn']
    if 'reg_risk' in eff:
        proj['legal_cost_spent'] -= (eff['reg_risk']/100) * proj['target_funding'] if eff['reg_risk']<0 else 0
    if 'security' in eff:
        proj['security'] = max(0, proj.get('security',50) + eff['security'])
    if 'trust_all' in eff:
        for bid in proj['trust_scores']:
            proj['trust_scores'][bid] = clamp(proj['trust_scores'][bid] + eff['trust_all'], 0, 100)
    if 'whale_trust' in eff:
        for bid, bot in enumerate(BOTS):
            if bot['type'] == 'Whale':
                proj['trust_scores'][bid] = clamp(proj['trust_scores'][bid] + eff['whale_trust'], 0, 100)
    if 'trust_single' in eff:
        min_bid = min(proj['trust_scores'], key=proj['trust_scores'].get)
        proj['trust_scores'][min_bid] = clamp(proj['trust_scores'][min_bid] + eff['trust_single'], 0, 100)
    proj['available_cash'] -= (rc['cost_percent']/100) * proj['target_funding']
    proj['reaction_hand'].pop(reaction_index)
    room['player_triggers'][player_index]['available_reactions'] = [
        r for r in room['player_triggers'][player_index]['available_reactions'] if r['id'] != rc['id']
    ]
    return jsonify({'ok': True})

@app.route('/api/run_phase', methods=['POST'])
def run_phase():
    data = request.json
    room_id = data['room_id']
    if room_id not in rooms:
        return jsonify({'error': 'Room not found'}), 404
    room = rooms[room_id]
    if room['status'] != 'playing':
        return jsonify({'error': 'Game not active'}), 400
    if not all(room['player_ready']):
        return jsonify({'error': 'Not all players ready'}), 400
    
    phase = room['phase']
    players = room['players']
    logs = []
    for i in range(room['num_players']):
        room['player_triggers'][i] = {'available_reactions': []}
    
    # 1. Xử lý scenario và thẻ active
    for idx, proj in enumerate(players):
        if not proj or proj.get('current_phase', 0) >= proj['max_phase']:
            continue
        scenario = random.choice(SCENARIOS)
        proj['last_scenario'] = scenario['name']
        logs.append(f"Dự án {idx+1}: {scenario['name']}")
        d = scenario['delta']
        if 'price' in d: proj['price'] *= (1 + d['price'])
        if 'cogs' in d:
            proj['material'] *= (1 + d['cogs'])
            proj['packaging'] *= (1 + d['cogs'])
            proj['shipping'] *= (1 + d['cogs'])
        if 'hype' in d: proj['hype'] = clamp(proj['hype'] + d['hype'], 0, 100)
        if 'transparency' in d: proj['transparency'] = clamp(proj['transparency'] + d['transparency'], 0, 100)
        if 'trust_all' in d:
            for bid in proj['trust_scores']:
                proj['trust_scores'][bid] = clamp(proj['trust_scores'][bid] + d['trust_all'], 0, 100)
        if 'runway' in d:
            metrics_before = calculate_metrics(proj)
            proj['available_cash'] += d['runway'] * metrics_before['monthly_burn']
        if 'legal_cost_percent' in d:
            cost = (d['legal_cost_percent']/100) * proj['target_funding']
            proj['legal_cost_spent'] += cost
            proj['available_cash'] -= cost
        if 'reg_risk' in d:
            proj['legal_cost_spent'] += (d['reg_risk']/100) * proj['target_funding']
        # Áp dụng thẻ active
        if idx in room['pending_cards']:
            card = room['pending_cards'][idx]
            if card:
                eff = card['effect']
                if 'hype' in eff: proj['hype'] = clamp(proj['hype'] + eff['hype'], 0, 100)
                if 'transparency' in eff: proj['transparency'] = clamp(proj['transparency'] + eff['transparency'], 0, 100)
                if 'price_percent' in eff: proj['price'] *= (1 + eff['price_percent']/100)
                if 'cogs_percent' in eff:
                    proj['material'] *= (1 + eff['cogs_percent']/100)
                    proj['packaging'] *= (1 + eff['cogs_percent']/100)
                    proj['shipping'] *= (1 + eff['cogs_percent']/100)
                if 'funding_boost_percent' in eff:
                    boost = (eff['funding_boost_percent']/100) * proj['target_funding']
                    proj['total_invested'] += boost
                    proj['available_cash'] += boost
                    proj['funding_progress'] = min(1.0, proj['total_invested']/proj['target_funding'])
                if 'cost_percent' in eff:
                    proj['available_cash'] -= (eff['cost_percent']/100) * proj['target_funding']
                if 'security' in eff:
                    proj['security'] = clamp(proj.get('security',50) + eff['security'], 0, 100)
                if 'utility' in eff:
                    proj['utility'] = clamp(proj.get('utility',50) + eff['utility'], 0, 100)
                if 'visibility' in eff:
                    proj['visibility'] = clamp(proj.get('visibility',50) + eff['visibility'], 0, 100)
                if 'velocity' in eff:
                    proj['velocity'] = max(0.1, proj.get('velocity',1.0) + eff['velocity'])
                logs.append(f"  → Dự án {idx+1} chơi thẻ {card['name']}")
        # Xác định reaction triggers
        triggers = []
        for rc in proj.get('reaction_hand', []):
            trigger = rc['trigger']
            if trigger == 'on_scenario_market_bad' and scenario['cat'] == 'Market' and any(k in scenario['name'] for k in ['xấu','Khủng hoảng']):
                triggers.append(rc)
            elif trigger == 'on_whale_trust<30':
                whale_trust = [proj['trust_scores'][bid] for bid, bot in enumerate(BOTS) if bot['type']=='Whale']
                if whale_trust and sum(whale_trust)/len(whale_trust) < 30:
                    triggers.append(rc)
            elif trigger == 'on_transparency<30' and proj['transparency'] < 30:
                triggers.append(rc)
            elif trigger == 'on_reg_risk>70':
                reg = (proj['legal_cost_spent'] / proj['target_funding']) * 100 if proj['target_funding']>0 else 0
                if reg > 70:
                    triggers.append(rc)
            elif trigger == 'on_security<30' and proj.get('security',50) < 30:
                triggers.append(rc)
            elif trigger == 'on_hype>80' and proj['hype'] > 80:
                triggers.append(rc)
            elif trigger == 'on_trust_any_bot<20':
                if any(t < 20 for t in proj['trust_scores'].values()):
                    triggers.append(rc)
            elif trigger == 'on_runway<3':
                metrics = calculate_metrics(proj)
                if metrics['runway'] < 3:
                    triggers.append(rc)
        if triggers:
            room['player_triggers'][idx]['available_reactions'] = triggers
            logs.append(f"  → Dự án {idx+1} có {len(triggers)} reaction có thể kích hoạt")
        
        metrics = calculate_metrics(proj)
        proj['funding_progress'] = metrics['funding_progress']
        proj['current_phase'] += 1
        if proj['current_phase'] >= proj['max_phase']:
            proj['status'] = 'ended'
            logs.append(f"  → Dự án {idx+1} kết thúc (đã qua {proj['max_phase']} phases).")
        logs.append(f"  → Funding sau phase: {proj['funding_progress']*100:.1f}%")
    
    # 2. Xử lý bot rút vốn và đầu tư
    bot_alloc = room['bot_alloc']
    A = {}
    for bot in BOTS:
        for idx, proj in enumerate(players):
            if not proj or proj.get('status') != 'active' or proj['funding_progress'] >= 1 or proj.get('current_phase',0) >= proj['max_phase']:
                A[(bot['id'], idx)] = -1e9
            else:
                metrics = calculate_metrics(proj)
                A[(bot['id'], idx)] = attractiveness(proj, bot, metrics)
    # Rút vốn
    for bot in BOTS:
        best_idx = max(range(len(players)), key=lambda i: A[(bot['id'], i)])
        alloc_entry = next(entry for entry in bot_alloc if entry['bot_id'] == bot['id'])
        for idx in range(len(players)):
            invested = alloc_entry['perProject'][idx]
            if invested == 0: continue
            if players[idx].get('status') != 'active' or players[idx].get('current_phase',0) >= players[idx]['max_phase']:
                continue
            diff = A[(bot['id'], best_idx)] - A[(bot['id'], idx)]
            if diff > 15: withdraw_ratio = 1.0
            elif diff > 5: withdraw_ratio = 0.3
            else: withdraw_ratio = 0.0
            if withdraw_ratio > 0:
                desired = invested * withdraw_ratio
                max_ratio = min(0.6, 0.2 + (phase-1)*0.05)
                max_withdraw = invested * max_ratio
                if desired > max_withdraw:
                    extra = desired - max_withdraw
                    actual = max_withdraw + extra*0.5
                else:
                    actual = desired
                if actual <= players[idx]['available_cash']:
                    players[idx]['available_cash'] -= actual
                    alloc_entry['perProject'][idx] -= actual
                    alloc_entry['idle'] += actual
                    logs.append(f"🐋 Bot {bot['type']} rút {actual:.0f} từ dự án {idx+1}")
                    # Kích hoạt reaction on_bot_withdraw
                    for pidx, proj in enumerate(players):
                        for rc in proj.get('reaction_hand', []):
                            if rc['trigger'] == 'on_bot_withdraw':
                                if rc not in room['player_triggers'][pidx]['available_reactions']:
                                    room['player_triggers'][pidx]['available_reactions'].append(rc)
                else:
                    players[idx]['status'] = 'bankrupt'
                    players[idx]['funding_progress'] = 0
                    logs.append(f"💀 Dự án {idx+1} PHÁ SẢN!")
    # Đầu tư softmax
    for bot in BOTS:
        alloc_entry = next(entry for entry in bot_alloc if entry['bot_id'] == bot['id'])
        idle = alloc_entry['idle']
        if idle <= 0: continue
        candidates = [i for i,p in enumerate(players) if p and p['status']=='active' and p['funding_progress']<1 and p.get('current_phase',0) < p['max_phase']]
        if not candidates: continue
        attrs = [A[(bot['id'], i)] for i in candidates]
        min_a = min(attrs)
        shifted = [max(0, a-min_a+0.01) for a in attrs]
        sum_exp = sum(math.exp(a/20) for a in shifted)
        probs = [math.exp(a/20)/sum_exp for a in shifted]
        remaining = idle
        for _ in range(5):
            if remaining <= 0: break
            for j, idx in enumerate(candidates):
                invest = remaining * probs[j]
                cap = min(invest, players[idx]['target_funding']*0.25 - players[idx]['total_invested'])
                if phase == 1:
                    cap = min(cap, players[idx]['target_funding']*0.2 - players[idx]['total_invested'])
                if cap > 0:
                    players[idx]['total_invested'] += cap
                    players[idx]['available_cash'] += cap
                    players[idx]['funding_progress'] = min(1.0, players[idx]['total_invested']/players[idx]['target_funding'])
                    alloc_entry['perProject'][idx] += cap
                    remaining -= cap
                    logs.append(f"💸 Bot {bot['type']} đầu tư {cap:.0f} vào dự án {idx+1}")
        alloc_entry['idle'] = remaining
    
    room['pending_cards'] = {}
    room['player_ready'] = [False] * room['num_players']
    room['phase'] += 1
    room['logs'] = logs
    
    all_ended = all(p is None or p.get('current_phase',0) >= p['max_phase'] for p in players)
    game_ended = (room['phase'] > room['max_phase']) or all_ended
    if game_ended:
        room['game_ended'] = True
        room['status'] = 'ended'
    else:
        for idx, proj in enumerate(players):
            if proj and proj['status'] == 'active' and proj['funding_progress'] < 1 and proj.get('current_phase',0) < proj['max_phase']:
                deck = proj['active_deck']
                proj['current_hand'] = random.sample(deck, min(5, len(deck)))
                proj['energy_left'] = 3
                room['mulligan_used'][idx] = False
    return jsonify({
        'ended': game_ended,
        'phase': room['phase'],
        'logs': logs,
        'game_ended': game_ended
    })

@app.route('/api/card_lists', methods=['GET'])
def card_lists():
    return jsonify({
        'active': ACTIVE_CARDS_FULL,
        'reaction': REACTION_CARDS
    })

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
