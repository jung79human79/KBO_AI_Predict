import pickle
import numpy as np
import pandas as pd
from database.db import get_db_connection
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split

def train_prediction_model():
    conn = get_db_connection()
    team_stats = pd.read_sql_query("SELECT * FROM 팀별능력", conn)
    df_h2h = pd.read_sql_query("SELECT * FROM 상대전적", conn)
    df_results = pd.read_sql_query("SELECT * FROM 경기결과", conn)
    conn.close()
    
    h2h_dict = {}
    df_h2h = df_h2h.rename(columns={'Unnamed: 0': 'Team_A'})
    team_col = 'Team_A'
    for idx, row in df_h2h.iterrows():
        t1 = str(row[team_col]).strip()
        for t2 in df_h2h.columns[1:]:
            t2_clean = str(t2).strip()
            if t1 == t2_clean: continue
            record = str(row[t2])
            if '승' in record and '패' in record:
                w = int(record.split('승')[0])
                l = int(record.split('승')[1].split('패')[0])
                win_rate = w / (w + l) if (w + l) > 0 else 0.5
                h2h_dict[(t1, t2_clean)] = win_rate
    # 4. 피처 결합 및 노이즈 행 예외 필터링 (성공 코드 로직 이식)
    features_list = []
    labels = []

    for idx, row in df_results.iterrows():
        if pd.isna(row['경기_결과(팀A승리=1)']): 
            continue
            
        try:
            result_val = row['경기_결과(팀A승리=1)']
        except ValueError:
            continue
            
        if result_val not in [0, 1]: 
            continue
            
        tA = str(row['팀_A(원정/좌)']).strip()
        tB = str(row['팀_B(홈/우)']).strip()
        
        if '팀_' in tA or '팀_' in tB:
            continue
        
        stats_A = team_stats[team_stats['Team'] == tA]
        stats_B = team_stats[team_stats['Team'] == tB]
        
        if len(stats_A) == 0 or len(stats_B) == 0: 
            continue
        
        sA = stats_A.iloc[0]
        sB = stats_B.iloc[0]
        h2h_prob = h2h_dict.get((tA, tB), 0.5)
        
        features = [
            float(sA['Team_AVG'] - sB['Team_AVG']),
            float(sA['Team_OBP'] - sB['Team_OBP']),
            float(sA['Team_SLG'] - sB['Team_SLG']),
            float(sA['Team_ERA'] - sB['Team_ERA']),
            float(sA['Team_K_BB'] - sB['Team_K_BB']),
            float(sA['HR'] - sB['HR']),
            float((sA['Team_SLG'] - sA['Team_AVG']) - (sB['Team_SLG'] - sB['Team_AVG'])), 
            float(h2h_prob),
            float(h2h_prob * (sA['Team_AVG'] - sB['Team_AVG'])),
            0.0  # 학습 시 팀A는 무조건 원정이므로 0 고정
        ]
        features_list.append(features)
        labels.append(result_val)
    X = np.array(features_list)
    y = np.array(labels)
    print(f"📊 웹 서버 초기화 - 최종 학습에 사용된 총 경기 수: {len(X)}건")
    
    # 모델 분할 및 XGBoost 학습 (과적합 방지 파라미터 튜닝)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    # 검증 완료된 최적의 XGBoost 하이퍼파라미터 세팅
    model = XGBClassifier(
        n_estimators=60,
        max_depth=6,
        learning_rate=0.02,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
        eval_metric='logloss'
    )
    model.fit(X_train, y_train)
    
    pickle.dump(model, open("ml/model.pkl","wb"))
    pickle.dump(team_stats, open("ml/team_stats.pkl","wb"))
    pickle.dump(h2h_dict, open("ml/h2h_dict.pkl","wb"))

    print("모델 저장 완료")
if __name__ == "__main__":
    train_prediction_model()