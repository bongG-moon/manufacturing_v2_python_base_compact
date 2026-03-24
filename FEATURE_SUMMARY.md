# 기능 요약

## 포함 기능

- 생산 / 목표 / 불량 / 설비 / WIP 조회
- 도메인 지식 기반 질문 조건 추출
- `current_data` 기반 pandas 후속 분석
- 첫 조회 이후 파라미터 승계
- 추출된 필터 조건 확인
- 분석 과정 요약 표시
- 생성된 pandas 코드 표시
- 간단한 채팅 UI

## 제외 기능

- 프로세스 분석 워크플로
- UI 버튼 기반 후속 분석
- 복잡한 운영 리포트 화면

## 핵심 파일

- `app.py`: 채팅 UI
- `core/agent.py`: 조회/후속 분석 라우팅
- `core/parameter_resolver.py`: 질문 조건 추출
- `core/domain_knowledge.py`: 제조 도메인 사전
- `core/data_tools.py`: 예시 제조 데이터 생성 및 조회
- `core/data_analysis_engine.py`: pandas 계획/코드 생성
- `core/safe_code_executor.py`: 안전 실행기
