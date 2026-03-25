# Compact Manufacturing Chat Service

제조 데이터 조회와 `current_data` 기반 pandas 후속 분석에 집중한 경량 서비스입니다.

## 실행

```bash
pip install -r requirements.txt
copy .env.example .env
streamlit run app.py
```

## 현재 포함된 조회 데이터셋

- 생산
- 목표
- 불량
- 설비
- WIP
- 수율
- 홀드
- 스크랩
- 레시피 조건
- LOT 이력

## 루트에 남겨둔 실행 파일

- `app.py`
- `ui_renderer.py`
- `core/`
- `.env.example`
- `requirements.txt`

## 참고 자료 위치

- `reference_materials/docs/`
  - 구조 설명
  - 기능 요약
  - 테스트 질문 모음
- `reference_materials/reports/`
  - 테스트 결과와 회귀 보고서
- `reference_materials/scripts/`
  - 테스트/리포트 생성용 보조 스크립트

## 초보자용 읽기 순서

1. `reference_materials/docs/BEGINNER_STRUCTURE_GUIDE.md`
2. `reference_materials/docs/CURRENT_DATA_GUIDE.md`
3. `reference_materials/docs/COLUMN_NAMING_GUIDE.md`
4. `app.py`
5. `core/agent.py`

## 핵심 파일

- `app.py`: Streamlit 채팅 UI
- `ui_renderer.py`: 결과 표와 분석 요약 렌더링
- `core/agent.py`: 새 조회와 후속 분석 라우팅
- `core/parameter_resolver.py`: 질문 조건 추출과 para 승계
- `core/domain_knowledge.py`: 제조 도메인 사전
- `core/data_tools.py`: 조회 데이터셋 생성과 registry
- `core/data_analysis_engine.py`: LLM 기반 pandas 코드 생성과 실행
- `core/number_format.py`: 수량 컬럼 단위 표시
