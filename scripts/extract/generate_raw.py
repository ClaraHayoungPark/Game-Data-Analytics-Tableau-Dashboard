import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
import os

random.seed(42)
np.random.seed(42)

# ---------------------------
# Parameters (시뮬레이션 설정)
# ---------------------------
num_players = 1000
num_days = 90
start_date = datetime(2025, 1, 1)

# ---------------------------
# Items 데이터
# ---------------------------
items_data = [
    ("item_1", "Health Potion", "Consumable", 3000),
    ("item_2", "Elixir of Battle", "Consumable", 5000),
    ("item_3", "Lucky Charm", "Consumable", 6000),
    ("item_4", "Deadly Poison Vial", "Consumable", 6500),
    ("item_5", "Teleportation Scroll", "Consumable", 7000),
    ("item_6", "Ancient Warrior's Helmet", "Cosmetic", 5500),
    ("item_7", "Shadow Stalker's Mask", "Cosmetic", 5200),
    ("item_8", "Shield of the Luminous Guardian", "Cosmetic", 6100),
    ("item_9", "Golden Armor Set", "Cosmetic", 7000),
    ("item_10", "Demon Hunter's Horns", "Cosmetic", 4800),
    ("item_11", "Weapon Enhancement Stone", "Upgrade", 2000),
    ("item_12", "Rare Grade Gemstone", "Upgrade", 7500),
    ("item_13", "Legendary Ore", "Upgrade", 8000),
    ("item_14", "Skill Point Reset Scroll", "Upgrade", 5000),
    ("item_15", "Inventory Expansion Ticket", "Upgrade", 6500),
]

special_items = [
    ("campaign_item_1", "Phoenix Feather", "Campaign", 9000),
    ("campaign_item_2", "Dragon's Heart", "Campaign", 10000),
    ("campaign_item_3", "Elixir of Immortality", "Campaign", 11000),
]

items_data.extend(special_items)

# ---------------------------
# 환경
# ---------------------------
platforms = ["PC", "Mobile", "Console"]
payment_methods = ["CreditCard", "PayPal", "MobilePay"]
payment_weights = [0.6, 0.3, 0.1]
regions = ["KR", "JP", "CN"]

# ---------------------------
# Campaigns
# ---------------------------
campaigns_data = [
    {
        "campaign_id": "campaign_1",
        "name": "Special Item Event",
        "start_date": "2025-02-15 09:00:00",
        "end_date": "2025-02-25 23:59:59",
        "type": "Event",
        "description": "특별 아이템 판매 이벤트"
    }
]
df_campaigns = pd.DataFrame(campaigns_data)

# ---------------------------
# 출력 파일 경로
# ---------------------------
output_dir = "/Users/hayoung/Documents/Portfolio/Tableau/Game_Dashboard_Project/data/raw"
os.makedirs(output_dir, exist_ok=True)
excel_file_name = os.path.join(output_dir, "GameData_Raw.xlsx")

# ---------------------------
# 이벤트 발생 카운트 초기화
# ---------------------------
tutorial_count = 0
reach_level_10_count = 0
campaign_view_count = 0
campaign_click_count = 0
campaign_participate_count = 0
campaign_purchase_count = 0

# 목표값 수정
tutorial_target = (980, 990)
reach_level_10_target = (200, 250)
campaign_view_target = (930, 950)
campaign_click_target = (700, 750)
# 이벤트 참여자 기준을 높이기 위해 목표 카운트 상향
campaign_participate_target = (800, 850)
campaign_purchase_target = (350, 400)

# ---------------------------
# Players 생성
# ---------------------------
players = []
registration_days = np.random.choice(
    range(num_days),
    size=num_players,
    p=np.linspace(1.5, 0.1, num_days) / np.linspace(1.5, 0.1, num_days).sum()
)

for i, reg_day in enumerate(registration_days, 1):
    player_id = f"player_{i}"
    register_date = start_date + timedelta(days=int(reg_day))
    platform = np.random.choice(platforms, size=1, p=[0.3,0.6,0.1])[0]
    region = np.random.choice(regions, size=1, p=[0.65,0.25,0.1])[0]
    players.append([player_id, register_date.strftime("%m/%d/%Y"), platform, region])

df_players = pd.DataFrame(players, columns=["player_id", "register_date", "platform", "region"])
df_items = pd.DataFrame(items_data, columns=["item_id", "item_name", "item_type", "price"])

# ---------------------------
# 리스트 초기화
# ---------------------------
sessions, events, payments, campaign_events = [], [], [], []
event_id_counter = 1
payment_id_counter = 1

# ---------------------------
# Player type 정의
# ---------------------------
player_types = {}
for idx, row in df_players.iterrows():
    r = random.random()
    if r < 0.15:
        player_types[row["player_id"]] = "high_value"
    elif r < 0.35:
        player_types[row["player_id"]] = "normal"
    else:
        player_types[row["player_id"]] = "non_payer"

# ---------------------------
# 플레이어별 데이터 생성
# ---------------------------
for idx, row in df_players.iterrows():
    player = row["player_id"]
    player_type = player_types.get(player, "non_payer")
    reg_date = datetime.strptime(row["register_date"], "%m/%d/%Y")

    if player_type == "high_value":
        max_payments = 70
        base_purchase_prob = 0.5
    elif player_type == "normal":
        max_payments = 35
        base_purchase_prob = 0.2
    else:
        max_payments = 15
        base_purchase_prob = 0.05

    # registration session
    reg_session_id = f"{player}_s0_0"
    reg_duration = random.randint(5, 30)
    reg_start_time = reg_date.strftime("%m/%d/%Y 00:00:00")
    reg_end_time = (reg_date + timedelta(minutes=reg_duration)).strftime("%%m/%d/%Y %H:%M:%S")
    sessions.append([reg_session_id, player, reg_start_time, reg_end_time, reg_duration, row["platform"]])
    events.append([f"event_{event_id_counter}", player, reg_session_id, reg_start_time, "register", "progress"])
    event_id_counter += 1

    tutorial_done = False
    num_purchased = 0
    first_day = max(0, (reg_date - start_date).days)
    possible_days = np.arange(first_day, num_days)
    if len(possible_days) < 2:
        continue

    # active_days 계산
    max_active_days = min(70, len(possible_days))
    if max_active_days < 3:
        num_active_days = max_active_days
    else:
        num_active_days = random.randint(3, max_active_days)

    # 리텐션율 가중치 설정
    decay_rate = 0.05

    # 캠페인 기간 중 가입한 유저는 리텐션 완화
    camp_start = datetime(2025, 2, 15, 9, 0, 0)
    camp_end = datetime(2025, 2, 25, 23, 59, 59)
    if camp_start <= reg_date <= camp_end:
        decay_rate = 0.02  # 더 천천히 감소 → 오래 활동

    probs = np.exp(-decay_rate * np.arange(len(possible_days)))
    probs /= probs.sum()
    active_days = np.sort(np.random.choice(possible_days, size=min(num_active_days, len(possible_days)), replace=False, p=probs))

    # active_days마다 세션/이벤트/결제
    for d in active_days:
        date = start_date + timedelta(days=int(d))
        if date < reg_date:
            date = reg_date

        num_sessions = random.choice([1,2,3])
        for s in range(num_sessions):
            hour = random.choices(range(24), weights=[0.2]*6 + [0.4]*6 + [1.2]*6 + [1.5]*6, k=1)[0]
            minute = random.randint(0, 59)
            start_time = max(reg_date, date + timedelta(hours=hour, minutes=minute))
            session_id = f"{player}_s{d}_{s}"


            # 세션 길이 생성
            if random.random() < 0.7:  # 70% 확률로 긴 세션 (40~90분)
                duration = int(np.random.normal(loc=65, scale=10))  # 평균 65분, 표준편차 10
            else:  # 나머지 30%는 짧은 세션 (3~40분)
                duration = int(np.random.normal(loc=25, scale=10))

            # 범위 제한
            duration = max(3, min(duration, 120))

            device = row["platform"]

            sessions.append([
                session_id, player, start_time.strftime("%m/%d/%Y %H:%M:%S"),
                (start_time + timedelta(minutes=duration)).strftime("%m/%d/%Y %H:%M:%S"),
                duration, device
            ])

            # Tutorial 이벤트
            if not tutorial_done and tutorial_count < tutorial_target[1]:
                if tutorial_count < tutorial_target[0] or random.random() < 0.6:
                    tutorial_time = start_time + timedelta(minutes=2)
                    events.append([f"event_{event_id_counter}", player, session_id,
                                   tutorial_time.strftime("%m/%d/%Y %H:%M:%S"), "tutorial_complete", "progress"])
                    event_id_counter += 1
                    tutorial_done = True
                    tutorial_count += 1

            # Reach level 10 이벤트
            if tutorial_done and reach_level_10_count < reach_level_10_target[1]:
                if reach_level_10_count < reach_level_10_target[0] or random.random() < 0.05:
                    level_time = start_time + timedelta(minutes=random.randint(10,60))
                    events.append([f"event_{event_id_counter}", player, session_id,
                                   level_time.strftime("%m/%d/%Y %H:%M:%S"), "reach_level_10", "progress"])
                    event_id_counter += 1
                    reach_level_10_count += 1


            # ---------------------------
            # 캠페인 이벤트 확률 조정
            # ---------------------------
            for camp in campaigns_data:
                camp_start = datetime.strptime(camp["start_date"], "%Y-%m-%d %H:%M:%S")
                camp_end   = datetime.strptime(camp["end_date"], "%Y-%m-%d %H:%M:%S")

                if camp_start <= start_time <= camp_end:
                    # 캠페인 참여 확률 
                    base_camp_prob = 0.25

                    if random.random() < base_camp_prob:
                        # campaign_view
                        ts_view = start_time + timedelta(minutes=random.randint(1, 5))
                        events.append([
                            f"event_{event_id_counter}", player, session_id,
                            ts_view.strftime("%m/%d/%Y %H:%M:%S"),
                            "campaign_view", "campaign_interaction"
                        ])
                        campaign_events.append([camp["campaign_id"], f"event_{event_id_counter}"])
                        event_id_counter += 1
                        campaign_view_count += 1

                        # campaign_click 
                        if random.random() < 0.6:
                            ts_click = ts_view + timedelta(minutes=random.randint(1, 5))
                            events.append([
                                f"event_{event_id_counter}", player, session_id,
                                ts_click.strftime("%m/%d/%Y %H:%M:%S"),
                                "campaign_click", "campaign_interaction"
                            ])
                            campaign_events.append([camp["campaign_id"], f"event_{event_id_counter}"])
                            event_id_counter += 1
                            campaign_click_count += 1

                            # campaign_participate
                            if random.random() < 0.4:
                                ts_part = ts_click + timedelta(minutes=random.randint(2, 10))
                                events.append([
                                    f"event_{event_id_counter}", player, session_id,
                                    ts_part.strftime("%m/%d/%Y %H:%M:%S"),
                                    "campaign_participate", "campaign_interaction"
                                ])
                                campaign_events.append([camp["campaign_id"], f"event_{event_id_counter}"])
                                event_id_counter += 1
                                campaign_participate_count += 1

                                # campaign_purchase
                                if random.random() < 0.25:
                                    ts_buy = ts_part + timedelta(minutes=random.randint(3, 15))
                                    events.append([
                                        f"event_{event_id_counter}", player, session_id,
                                        ts_buy.strftime("%m/%d/%Y %H:%M:%S"),
                                        "campaign_purchase", "purchase"
                                    ])
                                    campaign_events.append([camp["campaign_id"], f"event_{event_id_counter}"])

                                    # 고가 아이템 유지
                                    if player_type == "high_value":
                                        item = random.choices(special_items, weights=[1, 2, 3], k=1)[0]
                                    else:
                                        item = random.choice(special_items)
                                    item_id, _, _, item_price = item
                                    quantity = random.choice([1, 2, 3, 4])
                                    amount = int(item_price * quantity * random.uniform(1.15, 1.35))

                                    payments.append([
                                        f"payment_{payment_id_counter}", f"event_{event_id_counter}",
                                        item_id, quantity, amount,
                                        np.random.choice(payment_methods, size=1, p=payment_weights)[0]
                                    ])
                                    payment_id_counter += 1
                                    event_id_counter += 1
                                    campaign_purchase_count += 1


            # 일반 인앱 결제
            if tutorial_done and random.random() < base_purchase_prob and num_purchased < max_payments:
                ts_inapp = start_time + timedelta(minutes=random.randint(1,10))
                events.append([f"event_{event_id_counter}", player, session_id,
                               ts_inapp.strftime("%m/%d/%Y %H:%M:%S"), "inapp_purchase", "purchase"])
                item = random.choice(items_data)
                item_id, _, _, item_price = item
                quantity = random.choice([1,2,3])
                amount = item_price * quantity
                method = np.random.choice(payment_methods, size=1, p=payment_weights)[0]
                payments.append([f"payment_{payment_id_counter}", f"event_{event_id_counter}",
                                 item_id, quantity, amount, method])
                payment_id_counter += 1
                event_id_counter += 1
                num_purchased += 1

# ---------------------------
# DataFrame 변환
# ---------------------------
df_sessions = pd.DataFrame(sessions, columns=["session_id", "player_id", "start_time", "end_time", "duration_min", "device"])
df_events = pd.DataFrame(events, columns=["event_id","player_id","session_id","event_timestamp","event_name","event_type"])
df_payments = pd.DataFrame(payments, columns=["payment_id","event_id","item_id","quantity","amount","payment_method"])
df_campaign_events = pd.DataFrame(campaign_events, columns=["campaign_id","event_id"])

# ---------------------------
# Excel 저장
# ---------------------------
with pd.ExcelWriter(excel_file_name, engine='xlsxwriter') as writer:
    df_players.to_excel(writer, sheet_name="Players", index=False)
    df_items.to_excel(writer, sheet_name="Items", index=False)
    df_sessions.to_excel(writer, sheet_name="Sessions", index=False)
    df_events.to_excel(writer, sheet_name="Events", index=False)
    df_payments.to_excel(writer, sheet_name="Payments", index=False)
    df_campaigns.to_excel(writer, sheet_name="Campaigns", index=False)
    df_campaign_events.to_excel(writer, sheet_name="Campaign_Events", index=False)

print(f"Excel file saved with Campaign_Events sheet: {excel_file_name}")