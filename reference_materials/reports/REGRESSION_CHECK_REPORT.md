# Regression Check Report

## 기본 조회
### 질문: 오늘 생산량 보여줘
- tool: get_production_data
- row_count: 90
- summary: 총 90건, 총 생산량 188.2K
- extracted_params: {'date': '20260324', 'process_name': None, 'product_name': None, 'line_name': None, 'group_by': None, 'metrics': [], 'mode': None, 'den': None, 'tech': None, 'lead': None, 'mcp_no': None}
- applied_params: {'date': '20260324'}
- response_preview: 2026년 3월 24일 기준 총 생산량은 188.2K이며, 총 90건의 세부 데이터가 조회되었습니다. 주요 품목으로는 DDR5_5600(3019K), DDR5_6400(2913K), PMIC(2673K) 등이 포함되어 있습니다. 현재 결과는 ASSY-L1 라인의 incoming_sort 공정을 중심으로 구성되어 있으며, 상세 생산 내역은 아래 테이블을 통해 확인하실 수 있습니다.

## 공정군 도메인 추출
### 질문: 오늘 WIRE_BOND 공정 불량 보여줘
- tool: get_defect_rate
- row_count: 9
- summary: 총 9건, 평균 불량률 1.33%
- extracted_params: {'date': '20260324', 'process_name': ['first_bond', 'second_bond', 'stitch_bond', 'pull_test'], 'product_name': None, 'line_name': None, 'group_by': None, 'metrics': [], 'mode': None, 'den': None, 'tech': None, 'lead': None, 'mcp_no': None}
- applied_params: {'date': '20260324', 'process_name': ['first_bond', 'second_bond', 'stitch_bond', 'pull_test']}
- response_preview: 금일(2026-03-24) WIRE_BOND 공정군에서 발생한 불량 데이터는 총 9건이며, 평균 불량률은 1.33%입니다.  세부적으로는 first_bond 공정의 DDR5_6400 및 UFS3.1 모델에서 1.7%의 가장 높은 불량률을 보였으며, 주요 원인은 wire_sweep과 nsop로 확인됩니다. stitch_bond 공정의 경우 DDR5 모델들에서 1.1% 수준의 상대적으로 낮은 불량률을 기록하고 있습니다. 전체적으로 wire_sweep, nsop, heel_crack 등이 주요 불량 유

## 후속 그룹 분석
### 질문: 오늘 생산량 보여줘
- tool: get_production_data
- row_count: 90
- summary: 총 90건, 총 생산량 188.2K
- extracted_params: {'date': '20260324', 'process_name': None, 'product_name': None, 'line_name': None, 'group_by': None, 'metrics': [], 'mode': None, 'den': None, 'tech': None, 'lead': None, 'mcp_no': None}
- applied_params: {'date': '20260324'}
- response_preview: 2026년 3월 24일 기준 총 생산량은 188.2K이며, 총 90건의 세부 데이터가 조회되었습니다. 주요 품목으로는 DDR5_5600(3019K), DDR5_6400(2913K), PMIC(2673K) 등이 포함되어 있습니다. 현재 결과는 ASSY-L1 라인의 incoming_sort 공정을 중심으로 구성되어 있으며, 상세 생산 내역은 아래 테이블을 통해 확인하실 수 있습니다.

### 질문: mode, den, tech별로 그룹화해주고 그룹별로 상위 3개씩만 보여줘
- tool: analyze_current_data
- row_count: 18
- summary: 현재 데이터 분석 결과: 18행
- extracted_params: {'date': '20260324', 'process_name': None, 'product_name': None, 'line_name': None, 'group_by': 'MODE, DEN, TECH', 'metrics': [], 'mode': None, 'den': None, 'tech': None, 'lead': None, 'mcp_no': None, 'date_inherited': True}
- applied_params: {'date': '20260324', 'group_by': 'MODE, DEN, TECH'}
- analysis_plan: {'intent': 'Group by MODE, DEN, TECH and show top 3 production records per group', 'operations': ['groupby', 'sort_values', 'head'], 'output_columns': ['MODE', 'DEN', 'TECH', 'production', '날짜', '공정', '공정군', 'LEAD', 'MCP_NO', '라인', '단위'], 'group_by_columns': ['MODE', 'DEN', 'TECH'], 'partition_by_columns': ['MODE', 'DEN', 'TECH'], 'filters': [], 'sort_by': 'production', 'sort_order': 'desc', 'metric_column': 'production', 'warnings': [], 'code': "result = df.sort_values(['MODE', 'DEN', 'TECH', 'production'], ascending=[True, True, True, False]).groupby(['MODE', 'DEN', 'TECH']).head(3)", 'source': 'llm_primary', 'top_n_per_group': 3}
```python
result = df.sort_values(['MODE', 'DEN', 'TECH', 'production'], ascending=[True, True, True, False]).groupby(['MODE', 'DEN', 'TECH']).head(3)
```
- response_preview: 현재 조회된 18건의 데이터를 MODE, DEN, TECH 기준으로 그룹화하여 생산량 상위 3개 항목씩 정리했습니다.  CIS/16Gb/FO 그룹에서는 wafer_bake 공정이 2629K로 가장 높은 실적을 보였으며, DDR5_5600/32Gb/WB 그룹은 epoxy_dispense 공정이 3432K로 상위를 차지하고 있습니다. 각 그룹 내에서 생산량이 높은 순서대로 정렬되어 있으며, 상세한 공정별 실적은 아래 테이블을 통해 확인하실 수 있습니다.

## 필터 후 재분석
### 질문: 오늘 생산량 보여줘
- tool: get_production_data
- row_count: 90
- summary: 총 90건, 총 생산량 188.2K
- extracted_params: {'date': '20260324', 'process_name': None, 'product_name': None, 'line_name': None, 'group_by': None, 'metrics': [], 'mode': None, 'den': None, 'tech': None, 'lead': None, 'mcp_no': None}
- applied_params: {'date': '20260324'}
- response_preview: 2026년 3월 24일 기준 총 생산량은 188.2K이며, 총 90건의 세부 데이터가 조회되었습니다. 주요 품목으로는 DDR5_5600(3019K), DDR5_6400(2913K), PMIC(2673K) 등이 포함되어 있습니다. 현재 결과는 ASSY-L1 라인의 incoming_sort 공정을 중심으로 구성되어 있으며, 상세 생산 내역은 아래 테이블을 통해 확인하실 수 있습니다.

### 질문: LPDDR5X_8533만 보여줘
- tool: analyze_current_data
- row_count: 15
- summary: 현재 데이터 분석 결과: 15행
- extracted_params: {'date': '20260324', 'process_name': None, 'product_name': None, 'line_name': None, 'group_by': None, 'metrics': [], 'mode': ['LPDDR5X_8533'], 'den': None, 'tech': None, 'lead': None, 'mcp_no': None}
- applied_params: {'date': '20260324', 'mode': ['LPDDR5X_8533']}
- analysis_plan: {'intent': 'filter by MODE LPDDR5X_8533', 'operations': ['filter'], 'output_columns': ['날짜', '공정', '공정군', 'MODE', 'DEN', 'TECH', 'LEAD', 'MCP_NO', '라인', 'production', '단위'], 'group_by_columns': [], 'partition_by_columns': [], 'filters': [{'column': 'MODE', 'operator': '==', 'value': 'LPDDR5X_8533'}], 'sort_by': 'None', 'sort_order': 'None', 'metric_column': 'None', 'warnings': [], 'code': "result = df[df['MODE'] == 'LPDDR5X_8533']", 'source': 'llm_primary'}
```python
result = df[df['MODE'] == 'LPDDR5X_8533']
```
- response_preview: 현재 데이터에서 품목(MODE)이 LPDDR5X_8533인 내역은 총 15건이 확인됩니다. 2026년 3월 24일 기준 wafer_bake 공정에서 2768K, incoming_sort 공정에서 2060K 등의 생산량을 기록하였습니다. ASSY-L1, FC-L1 등 각 라인별 공정군에 따른 상세 생산 수치는 아래 테이블에서 확인하실 수 있습니다.

### 질문: 공정군별로 그룹화해줘
- tool: analyze_current_data
- row_count: 6
- summary: 현재 데이터 분석 결과: 6행
- extracted_params: {'date': '20260324', 'process_name': None, 'product_name': None, 'line_name': None, 'group_by': '공정군', 'metrics': [], 'mode': ['LPDDR5X_8533'], 'den': None, 'tech': None, 'lead': None, 'mcp_no': None}
- applied_params: {'date': '20260324', 'mode': ['LPDDR5X_8533'], 'group_by': '공정군'}
- analysis_plan: {'intent': '공정군별 생산량 합계 집계', 'operations': ['groupby', 'sum'], 'output_columns': ['공정군', 'production'], 'group_by_columns': ['공정군'], 'partition_by_columns': [], 'filters': [], 'sort_by': 'None', 'sort_order': 'None', 'metric_column': 'production', 'warnings': [], 'code': "result = df.groupby('공정군', as_index=False)['production'].sum()", 'source': 'llm_primary'}
```python
result = df.groupby('공정군', as_index=False)['production'].sum()
```
- response_preview: 현재 필터링된 LPDDR5X_8533 품목의 데이터를 공정군별로 그룹화하여 생산량 합계를 산출했습니다. 분석 결과, ASSY_PREP 공정군이 6669로 가장 높은 생산량을 기록했으며 FLIP_CHIP(5190), MOLD(5041) 순으로 집계되었습니다. SINGULATION(3874)과 PACK_OUT(3728)을 포함한 총 5개 공정군의 상세 수치는 아래 테이블을 통해 확인하실 수 있습니다.

## 주제 전환과 para 승계
### 질문: 오늘 LPDDR5X_8533 생산량 보여줘
- tool: get_production_data
- row_count: 15
- summary: 총 15건, 총 생산량 27.9K
- extracted_params: {'date': '20260324', 'process_name': None, 'product_name': None, 'line_name': None, 'group_by': None, 'metrics': [], 'mode': ['LPDDR5X_8533'], 'den': None, 'tech': None, 'lead': None, 'mcp_no': None}
- applied_params: {'date': '20260324', 'mode': ['LPDDR5X_8533']}
- response_preview: 2026년 3월 24일 기준, LPDDR5X_8533 모델의 총 생산량은 27.9K이며 총 15건의 데이터가 조회되었습니다. 주요 공정으로는 incoming_sort, wafer_bake, flip_place 등이 포함되어 있으며, ASSY-L1 및 FC-L1 등 다양한 라인에서 생산이 이루어졌습니다. 공정별로는 wafer_bake 공정에서 2,768K로 높은 생산량을 보였으며, 상세 내역은 제공된 테이블을 통해 확인하실 수 있습니다.

### 질문: 불량 보여줘
- tool: get_defect_rate
- row_count: 15
- summary: 총 15건, 평균 불량률 1.41%
- extracted_params: {'date': '20260324', 'process_name': None, 'product_name': None, 'line_name': None, 'group_by': None, 'metrics': [], 'mode': ['LPDDR5X_8533'], 'den': None, 'tech': None, 'lead': None, 'mcp_no': None}
- applied_params: {'date': '20260324', 'mode': ['LPDDR5X_8533']}
- response_preview: 현재 조회된 LPDDR5X_8533 모델의 15건 데이터 기준, 평균 불량률은 1.41%로 집계되었습니다. 공정별로는 flip_place 공정의 불량률이 2.4%로 가장 높으며, plasma_clean(2.0%)과 reflow(1.5%) 공정이 그 뒤를 잇고 있습니다. 불량 수량 면에서는 reflow 공정에서 110건으로 가장 많은 불량이 발생했으며, 주요 불량 유형으로는 bump_short, warpage, bake_fail 등이 확인됩니다. 상세한 공정별 불량 현황은 제공된 테이블을 통해 확인

## 다른 데이터 주제 연결
### 질문: 오늘 TEST 공정 WIP 보여줘
- tool: get_wip_status
- row_count: 12
- summary: 총 12건, 총 WIP 15.1K EA, 대기/홀드 2건
- extracted_params: {'date': '20260324', 'process_name': ['pre_test', 'final_test', 'burn_in', 'scan_test'], 'product_name': None, 'line_name': None, 'group_by': None, 'metrics': [], 'mode': None, 'den': None, 'tech': None, 'lead': None, 'mcp_no': None}
- applied_params: {'date': '20260324', 'process_name': ['pre_test', 'final_test', 'burn_in', 'scan_test']}
- response_preview: 오늘 TEST 공정의 재공(WIP) 데이터는 총 12건이며, 전체 수량은 15.1K EA로 집계되었습니다. 주요 항목으로는 TEST-L1 라인의 DDR5_5600(2,104 EA)과 DDR5_6400(1,619 EA) 등이 확인됩니다. 현재 대기 및 홀드 상태는 총 2건이며, PMIC 제품의 경우 평균 대기 시간이 215분으로 나타나고 있습니다. 요청하신 공정군 내 상세 현황을 확인해 보시기 바랍니다.

### 질문: 설비 상태도 보여줘
- tool: get_equipment_status
- row_count: 1
- summary: 총 1건, 평균 가동률 65.1%
- extracted_params: {'date': '20260324', 'process_name': ['pre_test', 'final_test', 'burn_in', 'scan_test'], 'product_name': None, 'line_name': None, 'group_by': None, 'metrics': [], 'mode': None, 'den': None, 'tech': None, 'lead': None, 'mcp_no': None}
- applied_params: {'date': '20260324', 'process_name': ['pre_test', 'final_test', 'burn_in', 'scan_test']}
- response_preview: 현재 TEST 공정의 설비 상태는 TST-04(Final Test Handler) 1건이 확인됩니다. 해당 설비는 TEST-L1 라인에서 운용 중이며, 계획된 24시간 중 15.6시간을 가동하여 65.1%의 가동률을 기록했습니다. 주요 비가동 사유는 'contact fail'로 파악되었으니 업무에 참고하시기 바랍니다.

## 정렬 분석
### 질문: 오늘 불량 보여줘
- tool: get_defect_rate
- row_count: 90
- summary: 총 90건, 평균 불량률 1.51%
- extracted_params: {'date': '20260324', 'process_name': None, 'product_name': None, 'line_name': None, 'group_by': None, 'metrics': [], 'mode': None, 'den': None, 'tech': None, 'lead': None, 'mcp_no': None}
- applied_params: {'date': '20260324'}
- response_preview: 오늘(20260324) 발생한 불량 데이터는 총 90건이며, 평균 불량률은 1.51%로 집계되었습니다. 주요 항목 중 UFS3.1(128Gb)의 불량률이 2.1%로 가장 높게 나타났으며, LPDDR5X_8533은 0.4%로 비교적 낮은 수치를 기록했습니다. 주요 불량 유형으로는 bake_fail과 particle이 확인되었으며, 특히 bake_fail이 여러 모드에서 빈번하게 발생하고 있습니다. 전체 90건에 대한 상세 불량 수량과 공정별 현황은 아래 표를 참고해 주시기 바랍니다.

### 질문: 불량률 높은 순으로 정렬해줘
- tool: analyze_current_data
- row_count: 90
- summary: 현재 데이터 분석 결과: 90행
- extracted_params: {'date': '20260324', 'process_name': None, 'product_name': None, 'line_name': None, 'group_by': None, 'metrics': [], 'mode': None, 'den': None, 'tech': None, 'lead': None, 'mcp_no': None}
- applied_params: {'date': '20260324'}
- analysis_plan: {'intent': 'Sort the dataframe by defect rate in descending order to identify high-defect items.', 'operations': ['sort_values'], 'output_columns': ['날짜', '공정', '공정군', 'MODE', 'DEN', 'TECH', 'LEAD', 'MCP_NO', 'inspection_qty', '불량수량', 'defect_rate', '주요불량유형'], 'group_by_columns': [], 'partition_by_columns': [], 'filters': [], 'sort_by': 'defect_rate', 'sort_order': 'desc', 'metric_column': 'defect_rate', 'warnings': [], 'code': "result = df.sort_values(by='defect_rate', ascending=False)", 'source': 'llm_primary'}
```python
result = df.sort_values(by='defect_rate', ascending=False)
```
- response_preview: 오늘 발생한 90건의 데이터를 불량률이 높은 순서대로 정렬했습니다. DDR5_5600(tray_pack), DDR5_6400(epoxy_dispense), CIS(underfill_cure) 공정의 불량률이 2.7%로 가장 높게 나타났습니다. 그 뒤를 이어 UFS3.1과 CIS의 특정 공정들이 2.6%의 불량률을 기록하고 있습니다. 상세한 공정별 불량 현황과 주요 불량 유형은 아래 표에서 확인하실 수 있습니다.

## 상위 N 분석
### 질문: 오늘 WIP 보여줘
- tool: get_wip_status
- row_count: 90
- summary: 총 90건, 총 WIP 116.7K EA, 대기/홀드 19건
- extracted_params: {'date': '20260324', 'process_name': None, 'product_name': None, 'line_name': None, 'group_by': None, 'metrics': [], 'mode': None, 'den': None, 'tech': None, 'lead': None, 'mcp_no': None}
- applied_params: {'date': '20260324'}
- response_preview: 오늘(2026-03-24) 기준 총 WIP는 116.7K EA이며, 전체 90건의 데이터가 집계되었습니다. 현재 대기 또는 홀드 상태인 항목은 19건이며, ASSY-L1 라인의 incoming_sort 공정에서 다양한 제품군이 처리 중입니다. 미리보기 데이터상으로는 UFS3.1 제품의 재공수량이 2,107 EA로 가장 많고, 평균 대기 시간은 220분으로 확인됩니다.

### 질문: 재공수량 상위 10개만 보여줘
- tool: analyze_current_data
- row_count: 10
- summary: 현재 데이터 분석 결과: 10행
- extracted_params: {'date': '20260324', 'process_name': None, 'product_name': None, 'line_name': None, 'group_by': None, 'metrics': [], 'mode': None, 'den': None, 'tech': None, 'lead': None, 'mcp_no': None}
- applied_params: {'date': '20260324'}
- analysis_plan: {'intent': 'top_n_analysis', 'operations': ['sort_values', 'head'], 'output_columns': ['날짜', '공정', '공정군', 'MODE', 'DEN', 'TECH', '라인', '재공수량', 'avg_wait_minutes', '상태'], 'group_by_columns': [], 'partition_by_columns': [], 'filters': [], 'sort_by': '재공수량', 'sort_order': 'desc', 'metric_column': '재공수량', 'warnings': [], 'code': "result = df.sort_values(by='재공수량', ascending=False).head(10)", 'source': 'llm_primary', 'top_n': 10}
```python
result = df.sort_values(by='재공수량', ascending=False).head(10)
```
- response_preview: 오늘(2026-03-24) 재공수량이 가장 많은 상위 10개 항목을 추출한 결과입니다.  MOLD-L2 라인의 marking 공정이 2,589 EA로 가장 높은 재공을 기록하고 있으며, 이어서 epoxy_dispense(2,563 EA)와 saw_cut(2,543 EA) 공정 순으로 재공이 많습니다. 상위권에는 MOLD, DIE_ATTACH, SINGULATION 등 다양한 공정군이 포함되어 있으며, 현재 상태는 대기(WAIT), 가동(RUNNING), 홀드(HOLD) 등으로 다양하게 확인됩니다.
