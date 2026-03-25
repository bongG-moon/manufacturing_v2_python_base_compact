# 100 Case Quality Review

이 문서는 실패는 아니지만 품질이 어색하거나 추가 보정이 필요한 케이스를 정리한 문서입니다.

## 자연어 답변의 단위 표현 어색함
- Case 001: 오늘 생산량 보여줘
  - Tool: get_production_data
  - Pandas Logic: -
  - Answer Preview: 2026년 3월 24일 기준, 총 90건의 생산 데이터가 조회되었으며 전체 생산량은 188.2K입니다. 현재 데이터는 ASSY-L1 라인의 incoming_sort 공정을 중심으로 DDR5, LPDDR5X, UFS3.1 등 다양한 모드의 생산 실적을 포함하고 있습니다. 주요 항목으로 DDR5_5600 제품이 3019K, DDR5_6400 제품이 2913K 생산된 것을 확인할 수 있습니다. 상
- Case 002: 상위 5개만 보여줘
  - Tool: analyze_current_data
  - Pandas Logic: result = df.sort_values(by='production', ascending=False).head(5)
  - Answer Preview: 오늘 생산 데이터 중 생산량이 가장 높은 상위 5개 항목을 추출한 결과입니다. DDR5_5600 모델의 epoxy_dispense 공정이 3432K로 가장 높은 실적을 기록했으며, 그 뒤를 이어 UFS3.1 모델의 die_place(3123K)와 epoxy_dispense(3096K) 공정이 순위에 올랐습니다. 상위 5개 항목은 주로 DDR5와 UFS3.1 제품군으로 구성되어 있으며, 상세한
- Case 016: 오늘 생산량 보여줘
  - Tool: get_production_data
  - Pandas Logic: -
  - Answer Preview: 2026년 3월 24일 기준, 총 90건의 생산 데이터가 조회되었으며 전체 생산량은 188.2K입니다. 현재 데이터는 ASSY-L1 라인의 incoming_sort 공정을 중심으로 DDR5, LPDDR5X, UFS3.1 등 다양한 모드의 생산 실적을 포함하고 있습니다. 주요 항목으로 DDR5_5600 제품이 3019K, DDR5_6400 제품이 2913K 생산된 것을 확인할 수 있습니다. 상
- Case 017: LPDDR5X_8533만 보여줘
  - Tool: analyze_current_data
  - Pandas Logic: result = df[df['MODE'] == 'LPDDR5X_8533']
  - Answer Preview: 요청하신 LPDDR5X_8533 모드에 해당하는 데이터만 필터링하여 총 15건의 결과를 구성했습니다. incoming_sort, wafer_bake, reflow 등 주요 공정별 생산 실적이 포함되어 있으며, ASSY-L1부터 FC-L1까지 다양한 라인의 정보를 확인할 수 있습니다. 각 공정별 생산량은 1252K에서 2768K 사이로 집계되었으며, 상세 내역은 아래 테이블을 참고해 주시기 바
- Case 021: 오늘 생산량 보여줘
  - Tool: get_production_data
  - Pandas Logic: -
  - Answer Preview: 2026년 3월 24일 기준, 총 90건의 생산 데이터가 조회되었으며 전체 생산량은 188.2K입니다. 현재 데이터는 ASSY-L1 라인의 incoming_sort 공정을 중심으로 DDR5, LPDDR5X, UFS3.1 등 다양한 모드의 생산 실적을 포함하고 있습니다. 주요 항목으로 DDR5_5600 제품이 3019K, DDR5_6400 제품이 2913K 생산된 것을 확인할 수 있습니다. 상
- Case 022: mode, den, tech별로 그룹화해주고 그룹별로 상위 3개씩만 보여줘
  - Tool: analyze_current_data
  - Pandas Logic: result = df.sort_values(by='production', ascending=False).groupby(['MODE', 'DEN', 'TECH']).head(3)
  - Answer Preview: 현재 조회된 18건의 데이터를 바탕으로 MODE, DEN, TECH별 생산량 상위 3개 항목을 정리했습니다. DDR5_5600(32Gb, WB) 그룹에서는 epoxy_dispense 공정의 3432K 실적이 가장 높게 나타났으며, UFS3.1(128Gb, MCP) 그룹은 die_place 공정의 3123K를 포함한 상위 항목들이 추출되었습니다. 각 그룹 내에서 생산량이 높은 순서대로 최대 3
- Case 026: 오늘 목표 보여줘
  - Tool: get_target_data
  - Pandas Logic: -
  - Answer Preview: 2026년 3월 24일 기준, 총 90건의 생산 목표 데이터가 조회되었습니다. 전체 목표량은 261.0K이며, DDR5_6400 및 LPDDR5X_8533 등 다양한 제품군이 포함되어 있습니다. 현재 데이터는 ASSY-L1 라인의 incoming_sort 공정을 중심으로 각 항목당 3600K 수준의 목표가 설정된 상태입니다.
- Case 096: 오늘 생산량 보여줘
  - Tool: get_production_data
  - Pandas Logic: -
  - Answer Preview: 2026년 3월 24일 기준, 총 90건의 생산 데이터가 조회되었으며 전체 생산량은 188.2K입니다. 현재 데이터는 ASSY-L1 라인의 incoming_sort 공정을 중심으로 DDR5, LPDDR5X, UFS3.1 등 다양한 모드의 생산 실적을 포함하고 있습니다. 주요 항목으로 DDR5_5600 제품이 3019K, DDR5_6400 제품이 2913K 생산된 것을 확인할 수 있습니다. 상
- Case 097: LPDDR5X_8533만 보여줘
  - Tool: analyze_current_data
  - Pandas Logic: result = df[df['MODE'] == 'LPDDR5X_8533']
  - Answer Preview: 요청하신 LPDDR5X_8533 모드에 해당하는 데이터만 필터링하여 총 15건의 결과를 구성했습니다. incoming_sort, wafer_bake, reflow 등 주요 공정별 생산 실적이 포함되어 있으며, ASSY-L1부터 FC-L1까지 다양한 라인의 정보를 확인할 수 있습니다. 각 공정별 생산량은 1252K에서 2768K 사이로 집계되었으며, 상세 내역은 아래 테이블을 참고해 주시기 바

## 질문 의도와 다른 그룹 기준
- Case 034: 라인별로 그룹화해줘
  - Tool: analyze_current_data
  - Pandas Logic: result = df.groupby('공정', as_index=False)['target'].sum()
  - Answer Preview: 요청하신 대로 데이터를 그룹화하여 정리해 드립니다. 현재 분석 결과, **final_test** 공정을 기준으로 **target** 합계는 **13.0K**로 집계되었습니다. 현재 데이터 내에서는 해당 공정이 유일하여 단일 항목으로 표시되며, 이를 기준으로 합산이 완료된 결과입니다.
- Case 040: 라인별로 그룹화해줘
  - Tool: analyze_current_data
  - Pandas Logic: result = df.groupby('공정군', as_index=False)['target'].mean()
  - Answer Preview: 현재 결과 테이블은 **공정군**별로 그룹화하여 목표 수량의 평균을 산출한 결과로, 총 5개의 항목이 조회되었습니다. 

분석 결과, ASSY_PREP과 DIE_ATTACH가 10.8K로 가장 높은 목표치를 기록하고 있으며, MOLD와 WIRE_BOND가 7.8K로 그 뒤를 잇고 있습니다. PACK_OUT 공정군은 5.2K로 집계되었으며, 현재 테이블을 통해 각 공정군별로 정렬된 상세 수치를
- Case 064: 라인별로 그룹화해줘
  - Tool: analyze_current_data
  - Pandas Logic: result = df.groupby('공정군', as_index=False).mean(numeric_only=True)
  - Answer Preview: 요청하신 대로 데이터를 그룹화하여 공정군별 가동 현황을 정리했습니다.

분석 결과 MOLD 공정군이 95.4%로 가장 높은 가동률을 기록했으며, PACK_OUT(95.2%)과 FLIP_CHIP(89.3%) 공정이 그 뒤를 이어 높은 효율을 보였습니다. 반면 DIE_ATTACH 공정군은 73.0%로 현재 집계된 공정 중 가장 낮은 가동률을 나타내고 있습니다.

총 7개 공정군에 대한 계획 대비
- Case 080: 라인별로 그룹화해줘
  - Tool: analyze_current_data
  - Pandas Logic: result = df.groupby('공정군', as_index=False).agg({'재공수량': 'sum', 'avg_wait_minutes': 'mean'}).sort_values('재공수량', ascending=False)
  - Answer Preview: 현재 데이터를 그룹화하여 재공수량 합계와 평균 대기 시간을 집계한 결과입니다.

**DIE_ATTACH** 공정군이 4,925 EA로 가장 많은 재공수량을 보유하고 있으며, 이어서 **PACK_OUT**(4,652 EA)과 **MOLD**(2,589 EA) 순으로 집계되었습니다. 특히 PACK_OUT 공정군은 평균 대기 시간이 383분으로 다른 그룹에 비해 상대적으로 길게 나타나고 있는 점이

## 해석 가이드
- `성공`: 질문 의도, tool 선택, 후속 분석 흐름이 대체로 자연스러운 케이스
- `애매`: 실패는 아니지만 그룹 기준이나 단위 표현이 질문 의도와 완전히 맞지 않을 가능성이 있는 케이스
- `개선필요`: 라우팅 실패, 실행 실패, 또는 응답이 명확히 부정확한 케이스