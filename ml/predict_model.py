import pickle
import numpy as np
import pandas as pd
from database.db import get_db_connection
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# ================================
# 저장된 AI 모델 불러오기
# ================================

with open("ml/model.pkl", "rb") as f:
    model = pickle.load(f)

with open("ml/team_stats.pkl", "rb") as f:
    team_stats = pickle.load(f)

with open("ml/h2h_dict.pkl", "rb") as f:
    h2h_dict = pickle.load(f)


# ================================
# 승부 예측 함수
# ================================

def predict_matchup(team_A, team_B, team_A_is_home=False):
    """
    team_A : 첫 번째 팀
    team_B : 두 번째 팀

    team_A_is_home=False
        False → team_A = 원정
        True  → team_A = 홈
    """

    stats_A = team_stats[team_stats["Team"] == team_A]
    stats_B = team_stats[team_stats["Team"] == team_B]

    if len(stats_A) == 0:
        raise ValueError(f"{team_A} 팀 데이터를 찾을 수 없습니다.")

    if len(stats_B) == 0:
        raise ValueError(f"{team_B} 팀 데이터를 찾을 수 없습니다.")

    sA = stats_A.iloc[0]
    sB = stats_B.iloc[0]

    h2h_prob = h2h_dict.get((team_A, team_B), 0.5)

    is_home = 1 if team_A_is_home else 0

    features = np.array([[
        float(sA["Team_AVG"] - sB["Team_AVG"]),
        float(sA["Team_OBP"] - sB["Team_OBP"]),
        float(sA["Team_SLG"] - sB["Team_SLG"]),
        float(sA["Team_ERA"] - sB["Team_ERA"]),
        float(sA["Team_K_BB"] - sB["Team_K_BB"]),
        float(sA["HR"] - sB["HR"]),
        float(
            (sA["Team_SLG"] - sA["Team_AVG"])
            -
            (sB["Team_SLG"] - sB["Team_AVG"])
        ),
        float(h2h_prob),
        float(
            h2h_prob *
            (sA["Team_AVG"] - sB["Team_AVG"])
        ),
        float(is_home)
    ]])

    prob = model.predict_proba(features)[0]

    away_prob = round(prob[1] * 100, 1)
    home_prob = round(prob[0] * 100, 1)

    winner = team_A if away_prob > home_prob else team_B

    confidence = max(away_prob, home_prob)

    if confidence >= 80:
        confidence_level = "매우 높음"

    elif confidence >= 70:
        confidence_level = "높음"

    elif confidence >= 60:
        confidence_level = "보통"

    else:
        confidence_level = "낮음"

    return {

        "winner": winner,

        "away_prob": away_prob,

        "home_prob": home_prob,

        "confidence": confidence,

        "confidence_level": confidence_level,

        "statA": sA,

        "statB": sB,

        "h2h": round(h2h_prob * 100, 1)

    }

def predict_matchup_2(team_A, team_B, team_A_is_home=False):

    stats_A = team_stats[team_stats["Team"] == team_A]
    stats_B = team_stats[team_stats["Team"] == team_B]

    if len(stats_A) == 0:
        raise ValueError(f"{team_A} 팀 데이터를 찾을 수 없습니다.")

    if len(stats_B) == 0:
        raise ValueError(f"{team_B} 팀 데이터를 찾을 수 없습니다.")

    sA = stats_A.iloc[0]
    sB = stats_B.iloc[0]

    h2h_prob = h2h_dict.get((team_A, team_B), 0.5)

    is_home = 1 if team_A_is_home else 0

    features = np.array([[

        float(sA["Team_AVG"] - sB["Team_AVG"]),
        float(sA["Team_OBP"] - sB["Team_OBP"]),
        float(sA["Team_SLG"] - sB["Team_SLG"]),
        float(sA["Team_ERA"] - sB["Team_ERA"]),
        float(sA["Team_K_BB"] - sB["Team_K_BB"]),
        float(sA["HR"] - sB["HR"]),

        float(
            (sA["Team_SLG"] - sA["Team_AVG"])
            -
            (sB["Team_SLG"] - sB["Team_AVG"])
        ),

        float(h2h_prob),

        float(
            h2h_prob *
            (sA["Team_AVG"] - sB["Team_AVG"])
        ),

        float(is_home)

    ]])

    prob = model.predict_proba(features)[0]

    prob_A = round(prob[1] * 100, 1)
    prob_B = round(prob[0] * 100, 1)

    winner = team_A if prob_A > prob_B else team_B
    
    confidence = abs(prob_A - prob_B)

    if confidence >= 40:
        confidence_text = "★★★★★ 매우 높은 신뢰도의 예측입니다."
    elif confidence >= 30:
        confidence_text = "★★★★☆ 높은 신뢰도의 예측입니다."
    elif confidence >= 20:
        confidence_text = "★★★☆☆ 보통 수준의 예측입니다."
    elif confidence >= 10:
        confidence_text = "★★☆☆☆ 신뢰도가 다소 낮습니다."
    else:
        confidence_text = "★☆☆☆☆ 두 팀의 전력이 비슷합니다."

    return {

        "team_A": team_A,
        "team_B": team_B,

        "prob_A": prob_A,
        "prob_B": prob_B,

        "winner": winner,

        "winner_prob": max(prob_A, prob_B),

        "confidence": confidence,

        "confidence_text": confidence_text,

        "statA": sA,
        "statB": sB,

        "h2h": round(h2h_prob * 100, 1),

        "loc_A": "홈" if is_home else "원정",
        "loc_B": "원정" if is_home else "홈"
    }