import parser
import preprocessing

import re
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

df["hour"] = df["ts"].dt.tz_convert("Asia/Seoul").dt.hour
df[["ts", "hour"]].head()

df["hour"].value_counts().sort_index()

(
    df.groupby(["hour", "action"])
      .size()
      .unstack(fill_value=0)
)


# 시간대별 Action 별 이용자 수
plt.figure(figsize=(20, 6))

for i in df["action"].unique():
    plt.subplot(1,2,1,)
    subset = df[df["action"] == i]
    counts = subset["hour"].value_counts().sort_index()
    plt.plot(counts.index, counts.values, label=i)
    plt.legend()

plt.subplot(1,2,2)
sns.heatmap(
    df.pivot_table(index="action", columns="hour", aggfunc="size", fill_value=0),
    cmap="YlGnBu",
    fmt="d"
)
plt.show()


df["user_key"] = df["ip"].astype(str) + " | " + df["ua"].astype(str)
df["gap_min"] = (
    df.groupby("user_key")["ts"]
      .diff()
      .dt.total_seconds()
      .div(60)
)

df["new_session"] = df["gap_min"].isna() | (df["gap_min"] > 30)
df["session_id"] = df.groupby("user_key")["new_session"].cumsum()
df["session_key"] = df["user_key"] + " | s=" + df["session_id"].astype(str)

stamp_sessions = df[df["action"] == "Stamp"]["session_key"].unique()
df_stamp = df[df["session_key"].isin(stamp_sessions)].copy()

df_stamp = df_stamp.sort_values(["session_key", "ts"])

# Stamp 바로 이전 행동 찾기
prev_actions = []

for sk, g in df_stamp.groupby("session_key"):
    acts = g["action"].tolist()
    for i in range(1, len(acts)):
        if acts[i] == "Stamp":
            prev_actions.append(acts[i-1])

pd.Series(prev_actions).value_counts()


stamp_sessions = set(
    df[df["action"] == "Stamp"]["session_key"]
)

df["stamp_user"] = df["session_key"].apply(
    lambda x: 1 if x in stamp_sessions else 0
)
df["stamp_user"].value_counts()

def create_session_summary(df):
    # 1. 집계 함수 정의
    aggregations = {
        'stamp_user': 'max',              
        'action': ['count', 'nunique'], 
        'ts': lambda x: (x.max() - x.min()).total_seconds() 
    }
    
    # 2. 기본 집계 수행 (세션 키 기준)
    session_summary = df.groupby('session_key').agg(aggregations)
    
    # 3. 컬럼 이름 평탄화 (MultiIndex 정리)
    session_summary.columns = [
        'stamp_user', 
        'action_count', 
        'unique_actions', 
        'session_time'
    ]

    # Booth 뷰 카운트
    session_summary['booth_views'] = df[df['action'] == 'Booth'].groupby('session_key').size()
    
    # Notice 뷰 카운트
    session_summary['notice_views'] = df[df['action'] == 'Notice'].groupby('session_key').size()
    
    # Auth 시도 카운트
    session_summary['auth_count'] = df[df['action'] == 'Auth'].groupby('session_key').size()
    
    # 5. NaN 값(행동이 0번인 경우)을 0으로 채우기
    session_summary = session_summary.fillna(0)
    
    # 6. 정수형 변환이 필요한 컬럼 처리
    cols_to_int = ['stamp_user', 'action_count', 'unique_actions', 'booth_views', 'notice_views', 'auth_count']
    session_summary[cols_to_int] = session_summary[cols_to_int].astype(int)
    
    return session_summary

session_summary = create_session_summary(df)
session_summary.groupby("stamp_user")[
    [
        "action_count",
        "unique_actions",
        "booth_views",
        "notice_views",
        "auth_count",
        "session_time"
    ]
].mean()

sns.barplot(x=df["stamp_user"], y=df["time"])
plt.show()

# 스템프 기능 사용자의 긴 체류시간 원인 확인
df = df.sort_values(["session_key", "ts"])

df["delta_sec"] = (
    df.groupby("session_key")["ts"]
      .diff()
      .dt.total_seconds()
)

action_time = (
    df.groupby(["stamp_user", "action"])["delta_sec"]
      .mean()
      .reset_index()
)

df["long_wait"] = df["delta_sec"] > 120
session_wait = (
    df.groupby(["session_key", "stamp_user"])["long_wait"]
      .mean()
      .reset_index(name="long_wait_ratio")
)
session_wait.groupby("stamp_user")["long_wait_ratio"].mean()

repeat_rate = (
    df.groupby("session_key")["action"]
      .apply(lambda x: x.value_counts().iloc[0] / len(x))
      .reset_index(name="repeat_ratio")
)

repeat_rate["stamp_user"] = repeat_rate["session_key"].isin(
    df[df["action"] == "Stamp"]["session_key"]
)

repeat_rate.groupby("stamp_user")["repeat_ratio"].mean()


