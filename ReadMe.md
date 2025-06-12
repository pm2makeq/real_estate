## 📁 파일 설명

### 📊 데이터 파일

- **`estate_org.csv`**  
  서울시 부동산 실거래가 데이터 (거래일, 가격, 면적, 층수 등 포함)

- **`school_org.csv`**  
  서울시 소재 학교 정보 데이터 (학교명, 유형, 위치 좌표 등 포함)

- **`subway_org.csv`**  
  서울시 지하철 역 정보 데이터 (역명, 호선, 위치 좌표 등 포함)

---

### 📥 출력 파일

- **`merged_with_school.csv`**  
  부동산 데이터와 가장 가까운 학교/지하철 역까지의 거리 정보가 추가된 통합 데이터
  
---

### 📘 노트북 파일

- **`0_data_comb.ipynb`**  
  위 세 개의 데이터를 기반으로 통합 데이터셋(`merged_with_school.csv`) 생성

- **`1_Predicting the Real Estate Price.ipynb`**  
  통합된 데이터를 사용해 서울시 부동산 가격 예측 모델 학습 및 평가

