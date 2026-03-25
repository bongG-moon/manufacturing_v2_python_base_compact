# Issue-Focused 10 Case Retest Report

| Case ID | 제목 | 기대 결과 | 실제 Tool | 판정 | 응답 요약 |
| --- | --- | --- | --- | --- | --- |
| R01 | 집계 후 없는 MODE 컬럼 요청 | 마지막 질문에서 MODE 컬럼이 현재 결과 테이블에 없다는 안내가 나와야 함 | analyze_current_data | PASS | 요청하신 컬럼(조건) `MODE`은 현재 결과 테이블에 없습니다. 현재 사용할 수 있는 주요 컬럼은 `공정군, target` 입니다. |
| R02 | 집계 후 없는 라인 컬럼 요청 | 마지막 질문에서 라인 컬럼이 현재 결과 테이블에 없다는 안내가 나와야 함 | analyze_current_data | PASS | 요청하신 컬럼(조건) `라인`은 현재 결과 테이블에 없습니다. 현재 사용할 수 있는 주요 컬럼은 `공정군, target` 입니다. |
| R03 | 현재 데이터에 없는 임의 컬럼 요청 | 담당자 컬럼이 없다는 안내가 나와야 함 | analyze_current_data | PASS | 요청하신 컬럼(조건) `담당자`은 현재 결과 테이블에 없습니다. 현재 사용할 수 있는 주요 컬럼은 `날짜, 공정, 공정군, MODE, DEN, TECH, LEAD, MCP_NO, 라인, production, 단위` 입니다. |
| R04 | 생산 데이터 공정군 그룹화 성공 | 공정군 기준 groupby가 정상 수행되어야 함 | analyze_current_data | PASS | 현재 데이터를 공정군별로 그룹화한 결과, 총 8개의 공정군으로 집계되었습니다. 생산량이 가장 높은 공정군은 ASSY_PREP(42.4K)이며, 이어서 MOLD(27.5K), DIE_ATTACH(25.5K) 순으로 나타났습니다. 현재 결과는 생산량이 많은 순서대로 정렬되어 있으며, 상세 내역은 아래 테이블에서 확인하실 수 있습니다. |
| R05 | 생산 데이터 라인 그룹화 성공 | 라인 기준 groupby가 정상 수행되어야 함 | analyze_current_data | PASS | 현재 조회된 데이터를 라인별로 그룹화하여 생산량 합계를 산출했습니다. 분석 결과, ASSY-L1 라인이 28.9K로 가장 높은 생산량을 기록했으며 MOLD-L1(18.9K), DA-L1(18.2K) 순으로 집계되었습니다. 총 16개 라인의 데이터가 생산량 내림차순으로 정렬되어 있으며, 상세 내역은 아래 테이블에서 확인하실 수 있습니다. |
| R06 | 복합 그룹화와 그룹별 상위 N 성공 | 복합 groupby와 상위 N 분석이 정상 수행되어야 함 | analyze_current_data | PASS | 현재 조회된 18건의 데이터를 MODE, DEN, TECH 기준으로 그룹화하여 생산량 상위 3개 항목씩 정리했습니다.  CIS/16Gb/FO 그룹에서는 wafer_bake 공정이 2629K로 가장 높은 실적을 보였으며, DDR5_5600/32Gb/WB 그룹은 epoxy_dispense 공정이 3432K로 상위를 차지하고 있습니다. 각 그룹 내에서 생산량이 높은 순서대로 정렬되어 있으며, 상세한 공정별 실적은 아래 테이블을 통해 확인하실 수 있습니다. |
| R07 | 불량 집계 후 없는 MODE 요청 | 마지막 질문에서 MODE 컬럼이 현재 결과 테이블에 없다는 안내가 나와야 함 | analyze_current_data | FAIL | 현재 데이터를 MODE별로 그룹화하여 검사수량, 불량수량, 불량률을 집계한 결과입니다.  검사수량 기준으로는 DDR5_5600이 96.7K로 가장 많으며, 불량률은 CIS가 1.8%로 가장 높게 나타났습니다. LPDDR5X_8533과 UFS3.1은 각각 1.4%의 상대적으로 낮은 불량률을 기록하고 있습니다. 상세한 MODE별 현황은 아래 표를 통해 확인하실 수 있습니다. |
| R08 | WIP 집계 후 없는 MODE 요청 | 마지막 질문에서 MODE 컬럼이 현재 결과 테이블에 없다는 안내가 나와야 함 | analyze_current_data | PASS | 요청하신 컬럼(조건) `MODE`은 현재 결과 테이블에 없습니다. 현재 사용할 수 있는 주요 컬럼은 `공정군, 재공수량, avg_wait_minutes` 입니다. |
| R09 | 설비 집계 후 없는 라인 요청 | 마지막 질문에서 라인 컬럼이 현재 결과 테이블에 없다는 안내가 나와야 함 | analyze_current_data | PASS | 요청하신 컬럼(조건) `라인`은 현재 결과 테이블에 없습니다. 현재 사용할 수 있는 주요 컬럼은 `공정군, planned_hours, actual_hours, 가동률` 입니다. |
| R10 | 주제 전환 시 파라미터 승계 | 날짜와 제품 조건이 승계된 상태로 불량 조회가 수행되어야 함 | get_defect_rate | PASS | 현재 조회된 15건의 LPDDR5X_8533 생산 데이터의 평균 불량률은 1.41%입니다.  공정별로는 flip_place 공정의 불량률이 2.4%(105건)로 가장 높으며, 주요 불량 유형은 bump_short로 확인됩니다. 불량 수량이 가장 많은 공정은 reflow(110건)로 warpage가 주요 원인이며, plasma_clean(92건) 공정에서는 bake_fail이 주로 발생했습니다.  상세 테이블을 통해 공정별 불량 수량과 주요 불량 유형을 한눈에 확인하실 수 있습니다. |

## 상세 결과

### R01 - 집계 후 없는 MODE 컬럼 요청
- 질문 흐름: 오늘 목표 보여줘 -> 공정군별로 그룹화해줘 -> MODE별로 그룹화해줘
- 기대 결과: 마지막 질문에서 MODE 컬럼이 현재 결과 테이블에 없다는 안내가 나와야 함
- 실제 Tool: analyze_current_data
- 판정: PASS
- Summary: -
- Error: 요청하신 컬럼(조건) `MODE`은 현재 결과 테이블에 없습니다. 현재 사용할 수 있는 주요 컬럼은 `공정군, target` 입니다.
- Data Rows: 0
- Pandas Code: `-`
- Final Response: 요청하신 컬럼(조건) `MODE`은 현재 결과 테이블에 없습니다. 현재 사용할 수 있는 주요 컬럼은 `공정군, target` 입니다.

### R02 - 집계 후 없는 라인 컬럼 요청
- 질문 흐름: 오늘 목표 보여줘 -> 공정군별로 그룹화해줘 -> 라인별로 정리해줘
- 기대 결과: 마지막 질문에서 라인 컬럼이 현재 결과 테이블에 없다는 안내가 나와야 함
- 실제 Tool: analyze_current_data
- 판정: PASS
- Summary: -
- Error: 요청하신 컬럼(조건) `라인`은 현재 결과 테이블에 없습니다. 현재 사용할 수 있는 주요 컬럼은 `공정군, target` 입니다.
- Data Rows: 0
- Pandas Code: `-`
- Final Response: 요청하신 컬럼(조건) `라인`은 현재 결과 테이블에 없습니다. 현재 사용할 수 있는 주요 컬럼은 `공정군, target` 입니다.

### R03 - 현재 데이터에 없는 임의 컬럼 요청
- 질문 흐름: 오늘 생산량 보여줘 -> 담당자별로 정리해줘
- 기대 결과: 담당자 컬럼이 없다는 안내가 나와야 함
- 실제 Tool: analyze_current_data
- 판정: PASS
- Summary: -
- Error: 요청하신 컬럼(조건) `담당자`은 현재 결과 테이블에 없습니다. 현재 사용할 수 있는 주요 컬럼은 `날짜, 공정, 공정군, MODE, DEN, TECH, LEAD, MCP_NO, 라인, production, 단위` 입니다.
- Data Rows: 0
- Pandas Code: `-`
- Final Response: 요청하신 컬럼(조건) `담당자`은 현재 결과 테이블에 없습니다. 현재 사용할 수 있는 주요 컬럼은 `날짜, 공정, 공정군, MODE, DEN, TECH, LEAD, MCP_NO, 라인, production, 단위` 입니다.

### R04 - 생산 데이터 공정군 그룹화 성공
- 질문 흐름: 오늘 생산량 보여줘 -> 공정군별로 그룹화해줘
- 기대 결과: 공정군 기준 groupby가 정상 수행되어야 함
- 실제 Tool: analyze_current_data
- 판정: PASS
- Summary: 현재 데이터 분석 결과: 8행
- Error: -
- Data Rows: 8
- Pandas Code: `result = df.groupby('공정군', as_index=False)['production'].sum().sort_values('production', ascending=False)`
- Final Response: 현재 데이터를 공정군별로 그룹화한 결과, 총 8개의 공정군으로 집계되었습니다. 생산량이 가장 높은 공정군은 ASSY_PREP(42.4K)이며, 이어서 MOLD(27.5K), DIE_ATTACH(25.5K) 순으로 나타났습니다. 현재 결과는 생산량이 많은 순서대로 정렬되어 있으며, 상세 내역은 아래 테이블에서 확인하실 수 있습니다.

### R05 - 생산 데이터 라인 그룹화 성공
- 질문 흐름: 오늘 생산량 보여줘 -> 라인별로 그룹화해줘
- 기대 결과: 라인 기준 groupby가 정상 수행되어야 함
- 실제 Tool: analyze_current_data
- 판정: PASS
- Summary: 현재 데이터 분석 결과: 16행
- Error: -
- Data Rows: 16
- Pandas Code: `result = df.groupby('라인', as_index=False)['production'].sum().sort_values('production', ascending=False)`
- Final Response: 현재 조회된 데이터를 라인별로 그룹화하여 생산량 합계를 산출했습니다. 분석 결과, ASSY-L1 라인이 28.9K로 가장 높은 생산량을 기록했으며 MOLD-L1(18.9K), DA-L1(18.2K) 순으로 집계되었습니다. 총 16개 라인의 데이터가 생산량 내림차순으로 정렬되어 있으며, 상세 내역은 아래 테이블에서 확인하실 수 있습니다.

### R06 - 복합 그룹화와 그룹별 상위 N 성공
- 질문 흐름: 오늘 생산량 보여줘 -> mode, den, tech별로 그룹화해주고 그룹별로 상위 3개씩만 보여줘
- 기대 결과: 복합 groupby와 상위 N 분석이 정상 수행되어야 함
- 실제 Tool: analyze_current_data
- 판정: PASS
- Summary: 현재 데이터 분석 결과: 18행
- Error: -
- Data Rows: 18
- Pandas Code: `result = df.sort_values(['MODE', 'DEN', 'TECH', 'production'], ascending=[True, True, True, False]).groupby(['MODE', 'DEN', 'TECH']).head(3)`
- Final Response: 현재 조회된 18건의 데이터를 MODE, DEN, TECH 기준으로 그룹화하여 생산량 상위 3개 항목씩 정리했습니다.

CIS/16Gb/FO 그룹에서는 wafer_bake 공정이 2629K로 가장 높은 실적을 보였으며, DDR5_5600/32Gb/WB 그룹은 epoxy_dispense 공정이 3432K로 상위를 차지하고 있습니다. 각 그룹 내에서 생산량이 높은 순서대로 정렬되어 있으며, 상세한 공정별 실적은 아래 테이블을 통해 확인하실 수 있습니다.

### R07 - 불량 집계 후 없는 MODE 요청
- 질문 흐름: 오늘 불량 보여줘 -> 주요 불량 유형별로 그룹화해줘 -> MODE별로 그룹화해줘
- 기대 결과: 마지막 질문에서 MODE 컬럼이 현재 결과 테이블에 없다는 안내가 나와야 함
- 실제 Tool: analyze_current_data
- 판정: FAIL
- Summary: 현재 데이터 분석 결과: 6행
- Error: -
- Data Rows: 6
- Pandas Code: `result = df.groupby('MODE', as_index=False).agg({'inspection_qty': 'sum', '불량수량': 'sum'})
result['defect_rate'] = (result['불량수량'] / result['inspection_qty'] * 100).round(2)
result = result.sort_values('inspection_qty', ascending=False)`
- Final Response: 현재 데이터를 MODE별로 그룹화하여 검사수량, 불량수량, 불량률을 집계한 결과입니다.

검사수량 기준으로는 DDR5_5600이 96.7K로 가장 많으며, 불량률은 CIS가 1.8%로 가장 높게 나타났습니다. LPDDR5X_8533과 UFS3.1은 각각 1.4%의 상대적으로 낮은 불량률을 기록하고 있습니다. 상세한 MODE별 현황은 아래 표를 통해 확인하실 수 있습니다.

### R08 - WIP 집계 후 없는 MODE 요청
- 질문 흐름: 오늘 WIP 보여줘 -> 공정군별로 그룹화해줘 -> MODE별로 그룹화해줘
- 기대 결과: 마지막 질문에서 MODE 컬럼이 현재 결과 테이블에 없다는 안내가 나와야 함
- 실제 Tool: analyze_current_data
- 판정: PASS
- Summary: -
- Error: 요청하신 컬럼(조건) `MODE`은 현재 결과 테이블에 없습니다. 현재 사용할 수 있는 주요 컬럼은 `공정군, 재공수량, avg_wait_minutes` 입니다.
- Data Rows: 0
- Pandas Code: `-`
- Final Response: 요청하신 컬럼(조건) `MODE`은 현재 결과 테이블에 없습니다. 현재 사용할 수 있는 주요 컬럼은 `공정군, 재공수량, avg_wait_minutes` 입니다.

### R09 - 설비 집계 후 없는 라인 요청
- 질문 흐름: 오늘 설비 가동률 보여줘 -> 공정군별로 그룹화해줘 -> 라인별로 정리해줘
- 기대 결과: 마지막 질문에서 라인 컬럼이 현재 결과 테이블에 없다는 안내가 나와야 함
- 실제 Tool: analyze_current_data
- 판정: PASS
- Summary: -
- Error: 요청하신 컬럼(조건) `라인`은 현재 결과 테이블에 없습니다. 현재 사용할 수 있는 주요 컬럼은 `공정군, planned_hours, actual_hours, 가동률` 입니다.
- Data Rows: 0
- Pandas Code: `-`
- Final Response: 요청하신 컬럼(조건) `라인`은 현재 결과 테이블에 없습니다. 현재 사용할 수 있는 주요 컬럼은 `공정군, planned_hours, actual_hours, 가동률` 입니다.

### R10 - 주제 전환 시 파라미터 승계
- 질문 흐름: 오늘 LPDDR5X_8533 생산량 보여줘 -> 불량 보여줘
- 기대 결과: 날짜와 제품 조건이 승계된 상태로 불량 조회가 수행되어야 함
- 실제 Tool: get_defect_rate
- 판정: PASS
- Summary: 총 15건, 평균 불량률 1.41%
- Error: -
- Data Rows: 15
- Pandas Code: `-`
- Final Response: 현재 조회된 15건의 LPDDR5X_8533 생산 데이터의 평균 불량률은 1.41%입니다.

공정별로는 flip_place 공정의 불량률이 2.4%(105건)로 가장 높으며, 주요 불량 유형은 bump_short로 확인됩니다. 불량 수량이 가장 많은 공정은 reflow(110건)로 warpage가 주요 원인이며, plasma_clean(92건) 공정에서는 bake_fail이 주로 발생했습니다.

상세 테이블을 통해 공정별 불량 수량과 주요 불량 유형을 한눈에 확인하실 수 있습니다.