# kakaomap.py

# 크롤링 작업을 위한 라이브러리 임포트
from bs4 import BeautifulSoup as bs
from selenium import webdriver
import requests
import pandas as pd
import json
import time   # 코드 진행 지연을 위한 time 임포트
from selenium.webdriver.common.by import By   # 2022년 7월 이후 selenium 업데이트로 인한 xpath 추적 임포트
from selenium.webdriver.common.keys import Keys

##### 카카오 주소를 좌표(위도, 경도)로 변환 api
## 개인 api key를 할당 받아 적용
api_key = '054a38bc8bc9ee2f8fadaaad44e27f97'
def addr_to_lat_lon(addr):
    url = f'https://dapi.kakao.com/v2/local/search/address.json?query={addr}'
    headers = {"Authorization": "KakaoAK " + api_key}
    result = json.loads(str(requests.get(url, headers=headers).text))

    match_first = result['documents'][0]['address']
    return float(match_first['x']), float(match_first['y'])

##### 카카오맵 minimap으로 생성
## No module named 'folium' 라는 에러가 뜬다면
## anaconda cmd 창에서 "pip install folium" 으로 설치
import folium
from folium.plugins import MiniMap

def make_map(df, region):
    # 해당 지역 시/도청 좌표 Search
    yp = addr_to_lat_lon(region)[0]
    xp = addr_to_lat_lon(region)[1]
    
    # 지도 생성하기
    m = folium.Map(location=[xp, yp],   # 뽑은 좌표
                   zoom_start=12)
    # 미니맵 추가하기
    minimap = MiniMap() 
    m.add_child(minimap)
    # 마커 추가하기
    for i in range(len(df.index)):
        folium.Marker(location=[df['위도'].iloc[i],df['경도'].iloc[i]],
                  popup=df['점수'].iloc[i],
                  tooltip=[df['식당명'].iloc[i], "\n점수", df['점수'].iloc[i]]
                  ).add_to(m)
    return m

### xpath로 크롤링한 값을 각 list에 입력하는 func
def parsing_data(n_list, s_list, a_list, px_list, py_list):
    source = driver.page_source
    parsed_source = bs(source, 'html.parser')

    names_div_list = parsed_source.find_all("li",class_ = 'PlaceItem clickArea')        # 가게명
    names_span_list = parsed_source.find_all('span', class_ = 'screen_out')
    span_names = names_span_list[1:31:2]
    for i in range(len(span_names)):
        names = span_names[i].text
        n_list.append(names)

    div_scores = parsed_source.find_all('em', class_ = "num") 
    del div_scores[-1]
    for i in range(len(div_scores)):
        scores = div_scores[i].text
        s_list.append(scores)

    div_address = parsed_source.find_all('div', class_ = "addr")                        # 주소
    for i in range(len(div_address)):
        address = div_address[i].text.replace('\n','').split('(지번)')[0]
        try:
            px_list.append(addr_to_lat_lon(address)[0])
            py_list.append(addr_to_lat_lon(address)[1])
        except:
            print(f"{i+1}번 가게 주소 데이터 error")
        a_list.append(address)
    time.sleep(2)
