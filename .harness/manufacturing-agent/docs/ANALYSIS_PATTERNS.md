# Analysis Patterns

## 공통 패턴
- filter
- groupby
- aggregate
- sort
- top N
- derived metric

## 제조 지표 패턴

### 달성율
- 기본 해석: `sum(production) / sum(target) * 100`

### 불량률
- 기본 해석: `defect_rate` 우선
- 없으면 `불량수량 / inspection_qty * 100`

### 수율
- 기본 해석: `sum(pass_qty) / sum(tested_qty) * 100`

### 대표 사유 / 최빈 case
- 기본 해석: reason 컬럼의 최빈값

## 다중 데이터셋 분석 원칙
- 먼저 필요한 데이터셋을 정확히 선택
- grain이 맞지 않으면 무조건 merge하지 않음
- 필요한 경우만 pre-aggregation 후 비교
- merge는 전략 중 하나이지 기본 전제가 아님
