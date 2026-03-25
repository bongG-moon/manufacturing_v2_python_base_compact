# 기능 요약

## 포함 기능

- 생산 / 목표 / 불량 / 설비 / WIP 조회
- 수율 / 홀드 / 스크랩 / 레시피 조건 / LOT 이력 조회
- 도메인 지식 기반 질문 조건 추출
- `current_data` 기반 pandas 후속 분석
- 첫 조회 이후 para 승계
- 추출된 필터 조건 확인
- 분석 과정 요약 표시
- 생성된 pandas 코드 표시
- 간단한 채팅 UI
- registry 기반 multi-tool 조회

## 제외 기능

- 프로세스 분석 워크플로
- UI 버튼 기반 후속 분석
- 복잡한 운영 리포트 화면

## 핵심 데이터셋

- 생산: `production`
- 목표: `target`
- 불량: `defect_rate`, `불량수량`
- 설비: `가동률`, `비가동사유`
- WIP: `재공수량`, `상태`
- 수율: `tested_qty`, `pass_qty`, `yield_rate`
- 홀드: `hold_qty`, `hold_reason`, `hold_owner`, `hold_hours`
- 스크랩: `scrap_qty`, `scrap_rate`, `loss_cost_usd`
- 레시피: `recipe_id`, `temp_c`, `pressure_kpa`, `process_time_sec`
- LOT 이력: `lot_id`, `route_step`, `current_status`, `elapsed_hours`

## 핵심 파일

- `app.py`: 채팅 UI
- `core/agent.py`: 조회 / 후속 분석 라우팅
- `core/parameter_resolver.py`: 질문 조건 추출
- `core/domain_knowledge.py`: 제조 도메인 사전
- `core/data_tools.py`: 예시 제조 데이터 생성과 registry
- `core/data_analysis_engine.py`: pandas 계획 / 코드 생성
- `core/safe_code_executor.py`: 안전 실행기
