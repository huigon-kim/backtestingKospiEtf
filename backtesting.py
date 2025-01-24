import pandas as pd

from google.colab import files
uploaded = files.upload()  # 파일 업로드
file_path = list(uploaded.keys())[0]  # 업로드된 파일 이름 저장

# 데이터 로드
data = pd.read_csv(file_path, encoding='utf-8')

# 데이터 전처리
data.columns = ['date', 'close', 'open', 'high', 'low', 'volume', 'change_percent']  # 컬럼 이름 정리
data['date'] = pd.to_datetime(data['date'].str.replace(r'\s+', '', regex=True))  # 날짜 정리
for col in ['close', 'open', 'high', 'low']:
    data[col] = data[col].str.replace(',', '').astype(float)  # 숫자 변환
data = data.sort_values(by='date')  # 날짜 기준 정렬

# 5일 이동평균선 계산
data['ma_5'] = data['close'].rolling(window=5).mean()

# 전일 종가 열 추가
data['prev_close'] = data['close'].shift(1)

# 매수 조건: 시가가 전일 종가 대비 상승 & 시가 < 5일 이평선 & 종가 > 5일 이평선
data['buy_signal'] = (data['open'] > data['prev_close']) & (data['open'] < data['ma_5']) & (data['close'] > data['ma_5'])

# 백테스팅 변수 초기화
position = False  # 현재 포지션 여부
entry_price = 0  # 매수가격
cumulative_return = 1  # 누적 수익률
daily_returns = []  # 매일의 수익률 기록

data = data.sort_values(by='date', ascending=True).reset_index(drop=True)

# 백테스팅 실행
for i in range(len(data)):
    if data.loc[i, 'buy_signal'] and not position:  # 매수 조건
        position = True
        entry_price = data.loc[i, 'close']  # 종가에 매수
    elif position:  # 포지션을 보유한 상태
        if data.loc[i, 'close'] < data.loc[i, 'ma_5']:  # 종가가 5일 이평선 아래로 내려오면 매도
            daily_return = (data.loc[i, 'close'] - entry_price) / entry_price
            cumulative_return *= (1 + daily_return)
            daily_returns.append(daily_return)
            position = False  # 포지션 종료
            entry_price = 0  # 매수가격 초기화

# 누적 수익률 계산
data['daily_return'] = 0  # 기본값 0으로 초기화
for j, ret in enumerate(daily_returns):
    data.loc[data.index[j], 'daily_return'] = ret
data['cumulative_return'] = (1 + data['daily_return']).cumprod()

# 결과 출력
print(data[['date', 'open', 'high', 'close', 'ma_5', 'buy_signal', 'daily_return', 'cumulative_return']])

# 백테스팅 최종 결과
final_cumulative_return = cumulative_return
print(f"최종 누적 수익률: {final_cumulative_return:.2f}")
