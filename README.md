# Compact Manufacturing Chat Service

제조 데이터 조회와 `current_data` 기반 pandas 후속 분석에 집중한 경량 서비스입니다.

## 실행

```bash
pip install -r requirements.txt
copy .env.example .env
streamlit run app.py
```

## 루트에 남겨둔 실행 파일

- `app.py`: Streamlit 진입점
- `ui_renderer.py`: 화면 렌더링
- `core/`: 조회, 파라미터 추출, pandas 분석 로직
- `.env.example`
- `requirements.txt`

## 참고 자료 위치

- `reference_materials/docs/`
  - 구조 설명 문서
  - 기능 요약
  - 테스트 질문 모음
- `reference_materials/reports/`
  - 100건 테스트 결과
  - 회귀 점검 보고서
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
- `ui_renderer.py`: 결과 표, 필터 정보, 분석 요약 표시
- `core/agent.py`: 새 조회와 후속 분석 라우팅
- `core/parameter_resolver.py`: 질문 조건 추출과 para 승계
- `core/data_tools.py`: 생산 / 목표 / 불량 / 설비 / WIP 조회
- `core/data_analysis_engine.py`: LLM 기반 pandas 코드 생성과 실행
- `core/number_format.py`: 수량 컬럼 단위 표시
