# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.13.7
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# +
# 패키지 불러오기

# api 요청
import requests
import json
# 데이터 자료형 및 분석도구
import pandas as pd
import numpy as np
# 시각화 패키지
import matplotlib as mlp
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
from matplotlib import patheffects

# %matplotlib inline
sns.set()
# 스케일링
from sklearn.preprocessing import MinMaxScaler
# 시간
import time
from datetime import datetime
# 진행 사항 확인
from tqdm import tqdm

# PUBG 분석 도구
from chicken_dinner.pubgapi import PUBG
from chicken_dinner.constants import COLORS
from chicken_dinner.constants import map_dimensions
from chicken_dinner.models import tournaments

# +
# api key 설정 및 데이터 요청
api_key = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJqdGkiOiI2ZGNjNzNhMC0yMDk5LTAxMzctYjNjMi0wMmI4NjZkNzliOGIiLCJpc3MiOiJnYW1lbG9ja2VyIiwiaWF0IjoxNTUxNjk2NzA2LCJwdWIiOiJibHVlaG9sZSIsInRpdGxlIjoicHViZyIsImFwcCI6InB1YmctYmVzdC1wbGF5In0.Oz7GmLsWF7038XIO4vKd5sivhLreOnizxTNcARAEFQs'

headers = {'accept': 'application/vnd.api+json',
           'Authorization': f'Bearer {api_key}'}
'''
accountId로 필터 ( 아이디를 알면 ['data']['id'] 를 사용해 accountId 확인가능 ) -> 게임 아이디를 바꿀수있으니 이를 방지할때 accountId사용 
url = "https://api.pubg.com/shards/steam/players/account.573238034f5b4d368c993c5f4d36a2f1" 
r = requests.get(url, headers=headers)
Hwet = r.json()
Hwet['data']['id'] 로 accountId 확인가능
'''

# 아이디로 필터
id = 'Hwet_J'
url = f"https://api.pubg.com/shards/steam/players?filter[playerNames]={id}"
r = requests.get(url, headers=headers)
Hwet = r.json()

# match_list 저장
match_list = [Hwet['data'][0]['relationships']['matches']['data'][count]['id'] for count in range(len(Hwet['data'][0]['relationships']['matches']['data']))]
# print(match_list)

# -

print(match_list)
print(len(match_list))


# +
# apply lambda를 위한 함수 (시리즈 변환)
def ParticipantsMerge(row):
    participants = pd.Series(row['attributes']['stats'])
    participants['id'] = row['id']
    return participants

mat_id = match_list[0]
url = f'https://api.pubg.com/shards/steam/matches/{mat_id}'
r = requests.get(url, headers=headers)
data = r.json()
print(data['data'])
print()
# print(data['data']['attributes']['matchType'])  # competitive
# print(data['data']['attributes']['createdAt'])  # 2022-03-24T14:24:21Z
print()
included = pd.DataFrame(data['included'])
rosters = included[included['type'] == 'roster']
rosters = rosters.apply(lambda row: [row['attributes']['stats']['rank'],
                                     row['attributes']['stats']['teamId'],
                                     row['attributes']['won'],
                                     pd.DataFrame(row['relationships']['participants']['data']),
                                     row['id']], axis=1)
rosters = pd.DataFrame(list(rosters), columns=['rank', 'teamId', 'won', 'participants', 'id'])
# print(rosters)
# print(data['data']['relationships']['rosters'])

# match_dict = {match['attributes']['createdAt']: mat_id for match in data['data'] if 'competitive' in match['matchType']}
participants = included[included['type'] == 'participant']
participants = participants.apply(lambda row: ParticipantsMerge(row), axis=1)
participants = participants.reset_index(drop=True)
print(participants['playerId'])
participants = participants.drop(['killPoints', 'killPointsDelta', 'lastKillPoints', 'lastWinPoints',
                                  'mostDamage', 'rankPoints', 'winPoints', 'winPointsDelta'],
                                  axis=1, errors='ignore')

# -



# <p>print(data['data']['attributes'])</p>
# {'shardId': 'steam', 'tags': None, 'mapName': 'Tiger_Main', 'seasonState': 'progress', 'duration': 1655, 'gameMode': 'squad', 'titleId': 'bluehole-pubg', 'matchType': 'competitive', 'createdAt': '2022-03-24T14:24:21Z', 'stats': None, 'isCustomMatch': False}
