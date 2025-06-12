import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import matplotlib.font_manager as fm
import matplotlib.gridspec as gridspec
import matplotlib.ticker as ticker

# 한글 폰트 설정 (Windows 환경 기준)
font_path = "C:/Windows/Fonts/malgun.ttf"  # 맑은 고딕 폰트 경로
font_name = fm.FontProperties(fname=font_path).get_name()
plt.rc('font', family=font_name)

# 데이터 로드
rent_data = pd.read_csv("서울특별시_전월세가_2024.csv", encoding="euc-kr")
sale_data = pd.read_csv("서울시 부동산 실거래가 정보.csv", encoding="euc-kr")

# 중복 컬럼 추출
common_columns = ["자치구코드", "자치구명", "법정동코드", "법정동명", "계약일"]

# 전월세 데이터에서 필요한 컬럼 선택
rent_data = rent_data[common_columns + ["보증금(만원)", "임대료(만원)", "전월세구분", "임대면적"]]

# 매매 데이터에서 필요한 컬럼 선택
sale_data = sale_data[common_columns + ["물건금액(만원)", "건물면적(㎡)"]]

# 데이터 병합 (outer join)
merged_data = pd.merge(rent_data, sale_data, on=common_columns, how="outer")

# 결과 저장
merged_data.to_csv("통합된_부동산_데이터.csv", index=False)
print("데이터 통합 완료!")

# 데이터 로드
data = pd.read_csv("통합된_부동산_데이터.csv", encoding="utf-8-sig")

# '전월세구분' 컬럼이 '매매'인 경우 처리 (결측값 채우기)
data["전월세구분"] = data["전월세구분"].fillna("매매")

# 면적과 금액 데이터 준비
data["면적(㎡)"] = data["임대면적"].combine_first(data["건물면적(㎡)"])  # 임대면적과 건물면적 결합
data["금액(만원)"] = data["보증금(만원)"].combine_first(data["물건금액(만원)"])  # 보증금과 매매금액 결합

# 결측값 제거
data = data.dropna(subset=["면적(㎡)", "금액(만원)", "전월세구분"])

# 면적 그룹화 (10가지 그룹)
area_bins = [0, 10, 49, 59, 75, 85, 135, float('inf')]  # 마지막 구간은 무한대로 설정
area_labels = [
    "0~10㎡",
    "10~49㎡ (소형)",
    "49~59㎡ (소형)",
    "59~75㎡ (소형)",
    "75~85㎡ (중형)",
    "85~135㎡ (중형)",
    "135㎡ 초과 (대형)"
]
data["면적_그룹"] = pd.cut(data["면적(㎡)"], bins=area_bins, labels=area_labels, include_lowest=True)

# 금액 그룹화 (천만 원 단위로 10단계)
_, price_bins = pd.qcut(data["금액(만원)"], q=10, retbins=True)
price_labels = [f"{int(price_bins[i] // 1000)}-{int(price_bins[i+1] // 1000)}천만원" for i in range(len(price_bins)-1)]
data["금액_그룹"] = pd.cut(data["금액(만원)"], bins=price_bins, labels=price_labels, include_lowest=True)

# 그룹별 전세/월세/매매 건수 계산
grouped_by_area = data.groupby(["면적_그룹", "전월세구분"]).size().unstack(fill_value=0)
grouped_by_price = data.groupby(["금액_그룹", "전월세구분"]).size().unstack(fill_value=0)

# 퍼센트 비율 추가 (전체 대비 비율)
grouped_by_area_percentage = grouped_by_area.div(grouped_by_area.sum(axis=1), axis=0) * 100
grouped_by_price_percentage = grouped_by_price.div(grouped_by_price.sum(axis=1), axis=0) * 100

# 자치구별 전세/월세/매매 건수 계산
grouped_by_district = data.groupby(["자치구명", "전월세구분"]).size().unstack(fill_value=0)

# 퍼센트 비율 추가 (전체 대비 비율)
grouped_by_district_percentage = grouped_by_district.div(grouped_by_district.sum(axis=1), axis=0) * 100

# 1. 막대 그래프를 하나의 창에 묶음
plt.figure(figsize=(16, 12))  # 가로 500px에 맞춰 크기 조정
gs_bar = gridspec.GridSpec(3, 1, height_ratios=[1, 1, 1])  # 3행 1열의 그리드 생성

# 첫 번째 그래프: 면적 그룹별 전세/월세/매매 건수 막대 그래프
ax1 = plt.subplot(gs_bar[0])
grouped_by_area.plot(kind="bar", stacked=True, colormap="viridis", ax=ax1)
ax1.set_title("면적 그룹별 전세/월세/매매 건수", fontsize=14)
ax1.set_xlabel("면적 그룹", fontsize=12)
ax1.set_ylabel("건수", fontsize=12)
ax1.tick_params(axis='x', rotation=45, labelsize=10)
plt.xticks(ha="right")  # 눈금 레이블 정렬 수정
ax1.legend(title="전월세구분", loc="upper right", fontsize=10)
ax1.yaxis.set_major_formatter(ticker.StrMethodFormatter('{x:,.0f}'))  # y축 큰 숫자 ',' 표시

# 두 번째 그래프: 금액 그룹별 전세/월세/매매 건수 막대 그래프
ax2 = plt.subplot(gs_bar[1])
grouped_by_price.plot(kind="bar", stacked=True, colormap="plasma", ax=ax2)
ax2.set_title("금액 그룹별 전세/월세/매매 건수", fontsize=14)
ax2.set_xlabel("금액 그룹 (천만 원)", fontsize=12)
ax2.set_ylabel("건수", fontsize=12)
ax2.tick_params(axis='x', rotation=45, labelsize=10)
plt.xticks(ha="right")  # 눈금 레이블 정렬 수정
ax2.legend(title="전월세구분", loc="upper right", fontsize=10)
ax2.yaxis.set_major_formatter(ticker.StrMethodFormatter('{x:,.0f}'))  # y축 큰 숫자 ',' 표시

# 세 번째 그래프: 자치구별 전세/월세/매매 건수 막대 그래프
ax3 = plt.subplot(gs_bar[2])
grouped_by_district.plot(kind="bar", stacked=True, colormap="tab20", ax=ax3)
ax3.set_title("자치구별 전세/월세/매매 건수", fontsize=14)
ax3.set_xlabel("자치구명", fontsize=12)
ax3.set_ylabel("건수", fontsize=12)
ax3.tick_params(axis='x', rotation=45, labelsize=10)
plt.xticks(ha="right")  # 눈금 레이블 정렬 수정
ax3.legend(title="전월세구분", loc="upper right", fontsize=10)
ax3.yaxis.set_major_formatter(ticker.StrMethodFormatter('{x:,.0f}'))  # y축 큰 숫자 ',' 표시

# 레이아웃 조정 및 표시
plt.tight_layout()
plt.show()

# 2. 히트맵을 하나의 창에 묶음
plt.figure(figsize=(16, 12))  # 가로 500px에 맞춰 크기 조정
gs_heatmap = gridspec.GridSpec(3, 1, height_ratios=[1, 1, 1])  # 3행 1열의 그리드 생성

# 첫 번째 히트맵: 면적 그룹별 전세/월세/매매 비율 히트맵
ax4 = plt.subplot(gs_heatmap[0])
sns.heatmap(grouped_by_area_percentage, annot=True, fmt=".1f", cmap="coolwarm", cbar_kws={'label': 'Percentage (%)'}, ax=ax4)
ax4.set_title("면적 그룹별 전세/월세/매매 비율 히트맵", fontsize=14)
ax4.set_xlabel("전월세구분", fontsize=12)
ax4.set_ylabel("면적 그룹", fontsize=12)

# 두 번째 히트맵: 금액 그룹별 전세/월세/매매 비율 히트맵
ax5 = plt.subplot(gs_heatmap[1])
sns.heatmap(grouped_by_price_percentage, annot=True, fmt=".1f", cmap="coolwarm", cbar_kws={'label': 'Percentage (%)'}, ax=ax5)
ax5.set_title("금액 그룹별 전세/월세/매매 비율 히트맵", fontsize=14)
ax5.set_xlabel("전월세구분", fontsize=12)
ax5.set_ylabel("금액 그룹 (천만 원)", fontsize=12)

# 세 번째 히트맵: 자치구별 전세/월세/매매 비율 히트맵
ax6 = plt.subplot(gs_heatmap[2])
sns.heatmap(grouped_by_district_percentage, annot=True, fmt=".1f", cmap="coolwarm", cbar_kws={'label': 'Percentage (%)'}, ax=ax6)
ax6.set_title("자치구별 전세/월세/매매 비율 히트맵", fontsize=14)
ax6.set_xlabel("전월세구분", fontsize=12)
ax6.set_ylabel("자치구명", fontsize=12)

# 레이아웃 조정 및 표시
plt.tight_layout()
plt.show()