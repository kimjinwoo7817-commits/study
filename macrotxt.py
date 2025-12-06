import pandas as pd
import pandas_datareader.data as web
import yfinance as yf
import datetime

# 날짜 설정 (최근 5년 데이터)
end_date = datetime.datetime.today()
start_date = end_date - datetime.timedelta(days=365*5)

print("데이터 수집 중입니다... 잠시만 기다려주세요.")

# ---------------------------------------------------------
# 1. FRED (Federal Reserve Economic Data) - 경제 근본 지표
# ---------------------------------------------------------
# 시리즈 ID 매핑
fred_indicators = {
    'CPIAUCSL': 'CPI (소비자물가지수)',
    'PCEPI': 'PCE (개인소비지출)',
    'UNRATE': 'Unemployment Rate (실업률)',
    'DGS10': '10-Year Treasury (미국채 10년물)',
    'DGS2': '2-Year Treasury (미국채 2년물)',
    'T10Y2Y': 'Yield Spread (10Y-2Y 장단기 금리차)',
    'M2SL': 'M2 Money Supply (통화량)',
    'FEDFUNDS': 'Fed Funds Rate (기준금리)'
}

# 데이터 가져오기 (소스: fred)
try:
    df_macro = web.DataReader(list(fred_indicators.keys()), 'fred', start_date, end_date)
    df_macro.rename(columns=fred_indicators, inplace=True)
except Exception as e:
    print(f"FRED 데이터 수집 중 오류 발생: {e}")
    df_macro = pd.DataFrame()

# ---------------------------------------------------------
# 2. Yahoo Finance - 시장 반응 지표 (금, 환율, VIX)
# ---------------------------------------------------------
tickers = {
    'GC=F': 'Gold (금 선물)',
    'SI=F': 'Silver (은 선물)',  # 사용자 관심 자산 반영
    'DX-Y.NYB': 'Dollar Index (달러 인덱스)',
    'KRW=X': 'USD/KRW (원달러 환율)',
    '^VIX': 'VIX (공포지수)',
    '^GSPC': 'S&P 500'
}

df_market = yf.download(list(tickers.keys()), start=start_date, end=end_date, progress=False)['Close']
df_market.rename(columns=tickers, inplace=True)

# ---------------------------------------------------------
# 3. 데이터 병합 및 전처리
# ---------------------------------------------------------
# FRED(월/일 단위 혼재)와 Yahoo(일 단위) 병합
# 'ffill' (Forward Fill)을 사용하여 주말/공휴일 결측치 보정
df_total = pd.concat([df_macro, df_market], axis=1).ffill().dropna()

# 결과 출력 (최근 5행)
print("\n[최근 수집된 매크로 및 시장 데이터]")
print(df_total.tail())

# (선택) 상관관계 분석 출력
print("\n[주요 지표 간 상관관계 - 금 vs 달러 vs 금리]")
correlation = df_total[['Gold (금 선물)', 'Dollar Index (달러 인덱스)', '10-Year Treasury (미국채 10년물)']].corr()
print(correlation)
