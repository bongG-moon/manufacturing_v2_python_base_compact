# 100 Case Summary

- 총 케이스 수: 100
- 성공: 84
- 애매: 13
- 개선필요: 3

## 도구별 분포
- analyze_current_data: 77
- get_production_data: 7
- get_defect_rate: 5
- get_wip_status: 5
- get_target_data: 3
- get_equipment_status: 3

## 시나리오별 분포
- 생산 기본 흐름: 5
- 생산 공정군 필터: 5
- 생산 제품 필터: 5
- 생산 조건 후 재필터: 5
- 생산 복합 그룹: 5
- 목표 기본 흐름: 5
- 목표 공정군 필터: 5
- 목표 제품 필터: 5
- 불량 기본 흐름: 5
- 불량 공정군 필터: 5
- 불량 제품 필터: 5
- 불량 주제 전환: 5
- 설비 기본 흐름: 5
- 설비 공정군 필터: 5
- 설비 주제 전환: 5
- WIP 기본 흐름: 5
- WIP 공정군 필터: 5
- WIP 상태성 후속: 5
- WIP 제품 필터: 5
- 혼합 전환 종합: 5

## 애매 케이스
- Case 001: 오늘 생산량 보여줘
  - Tool: get_production_data
  - Summary: 총 90건, 총 생산량 188.2K
- Case 002: 상위 5개만 보여줘
  - Tool: analyze_current_data
  - Summary: 현재 데이터 분석 결과: 5행
- Case 016: 오늘 생산량 보여줘
  - Tool: get_production_data
  - Summary: 총 90건, 총 생산량 188.2K
- Case 017: LPDDR5X_8533만 보여줘
  - Tool: analyze_current_data
  - Summary: 현재 데이터 분석 결과: 15행
- Case 021: 오늘 생산량 보여줘
  - Tool: get_production_data
  - Summary: 총 90건, 총 생산량 188.2K
- Case 022: mode, den, tech별로 그룹화해주고 그룹별로 상위 3개씩만 보여줘
  - Tool: analyze_current_data
  - Summary: 현재 데이터 분석 결과: 18행
- Case 026: 오늘 목표 보여줘
  - Tool: get_target_data
  - Summary: 총 90건, 총 목표량 261.0K
- Case 034: 라인별로 그룹화해줘
  - Tool: analyze_current_data
  - Summary: 현재 데이터 분석 결과: 1행
- Case 040: 라인별로 그룹화해줘
  - Tool: analyze_current_data
  - Summary: 현재 데이터 분석 결과: 5행
- Case 064: 라인별로 그룹화해줘
  - Tool: analyze_current_data
  - Summary: 현재 데이터 분석 결과: 7행
- Case 080: 라인별로 그룹화해줘
  - Tool: analyze_current_data
  - Summary: 현재 데이터 분석 결과: 8행
- Case 096: 오늘 생산량 보여줘
  - Tool: get_production_data
  - Summary: 총 90건, 총 생산량 188.2K
- Case 097: LPDDR5X_8533만 보여줘
  - Tool: analyze_current_data
  - Summary: 현재 데이터 분석 결과: 15행

## 개선필요 케이스
- Case 010: MODE별로 그룹화해줘
  - Tool: analyze_current_data
  - Summary: 
  - Answer: 분석 코드 실행 실패: 'MODE'
- Case 029: MODE별로 그룹화해줘
  - Tool: analyze_current_data
  - Summary: 
  - Answer: 분석 코드 실행 실패: 'MODE'
- Case 035: MODE별로 그룹화해줘
  - Tool: analyze_current_data
  - Summary: 
  - Answer: 분석 코드 실행 실패: 'MODE'