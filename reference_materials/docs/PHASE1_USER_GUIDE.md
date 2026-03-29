# Phase 1 User Guide

이 문서는 현재 `Compact Manufacturing Chat Service`의 Phase 1 상태를 확인하기 위한 상세 가이드입니다.

## 1. 이번 Phase 1에서 반영된 내용

### 1-1. 데이터셋 계약 기반 조회

각 데이터셋은 이제 아래 기준으로 관리됩니다.

- 어떤 파라미터가 필수인지
- 어떤 파라미터가 선택인지
- `date`가 필수인지, 선택인지

현재 코드 기준 주요 예시는 아래와 같습니다.

- `production`, `target`, `defect`, `equipment`, `wip`, `yield`, `hold`, `scrap`: `date` 필수
- `recipe`, `lot_trace`: `date` 선택

관련 코드:

- `core/dataset_contracts.py`
- `core/agent.py`

### 1-2. 조회 / 후속분석 판별 개선

이제 질문이 들어오면 시스템은 다음을 함께 봅니다.

- 현재 결과 테이블이 존재하는지
- 질문 안에 데이터셋 키워드가 있는지
- 질문이 새 조회를 의미하는지
- 질문이 현재 결과에 대한 정렬/비교/그룹화인지

관련 코드:

- `core/intent_router.py`
- `core/agent.py`

### 1-3. 도메인 등록 파일 지원

이제 일반 사용자도 Python 코드를 수정하지 않고 Markdown 파일만 추가해서 도메인 용어를 확장할 수 있습니다.

등록 위치:

- `reference_materials/domain_registry/`

관련 코드:

- `core/domain_registry.py`
- `core/data_tools.py`
- `core/parameter_resolver.py`
- `core/analysis_llm.py`

### 1-4. 분석 근거 테이블 표시 / 다운로드

이제 화면에서 아래를 함께 확인할 수 있습니다.

- 최종 결과 테이블
- 분석에 사용된 원본 테이블
- 다중 데이터셋 분석 시 결합된 분석 기준 테이블

각 테이블은 CSV로 다운로드할 수 있습니다.

관련 코드:

- `ui_renderer.py`
- `app.py`

## 2. 실행 방법

```bash
pip install -r requirements.txt
copy .env.example .env
streamlit run app.py
```

`LLM_API_KEY`는 `.env`에 설정되어 있어야 합니다.

## 3. 화면에서 확인할 항목

앱을 실행하면 상단에서 아래 패널을 확인할 수 있습니다.

### 3-1. `Available Datasets`

여기에서 현재 조회 가능한 데이터셋과 필수 조건을 볼 수 있습니다.

확인 포인트:

- 어떤 데이터셋이 있는지
- 어떤 데이터셋이 `date`를 필수로 요구하는지

### 3-2. `Domain Registry`

여기에서 현재 로딩된 domain 파일과 키워드, 공정군 정보를 확인할 수 있습니다.

확인 포인트:

- 어떤 Markdown 파일이 로딩되었는지
- dataset keywords가 어떻게 등록되어 있는지
- process group이 어떻게 매핑되어 있는지
- 충돌 경고가 있는지

### 3-3. `Engineer detail mode`

켜면 아래 정보가 더 많이 보입니다.

- generated pandas code
- 결과 expander 기본 펼침
- latency

운영 사용자 기준으로는 평소 `OFF` 상태를 권장합니다.

## 4. 질문 예시

### 4-1. 새 데이터 조회

- `오늘 생산 보여줘`
- `20260324 목표 조회`
- `어제 수율 데이터 보여줘`
- `오늘 홀드 lot 보여줘`

### 4-2. 현재 결과 후속 분석

먼저 `오늘 생산 보여줘`를 실행한 뒤 아래처럼 물어봅니다.

- `현재 결과를 공정별 상위 3개로 정렬해줘`
- `MODE별로 비교해줘`
- `라인별로 요약해줘`

### 4-3. 모호한 질문

현재 결과가 있는 상태에서 아래처럼 물으면 시스템이 재질문할 수 있습니다.

- `목표 비교`
- `수율 정리`

이 경우 시스템은 아래처럼 다시 확인합니다.

- 새 조회: `오늘 목표 데이터 조회`
- 후속 분석: `현재 결과를 공정별 상위 3개로 정렬`

이 동작은 의도 오판을 줄이기 위한 Phase 1 보호장치입니다.

## 5. Domain Registry 사용 방법

### 5-1. 파일 추가 위치

새 Markdown 파일을 아래 폴더에 추가합니다.

- `reference_materials/domain_registry/`

### 5-2. 기본 형식

아래 4개 섹션 중 필요한 것만 써도 됩니다.

- `## Dataset Keywords`
- `## Process Groups`
- `## Value Groups`
- `## Notes`

### 5-3. 예시

```markdown
# Custom Domain

## Dataset Keywords
| dataset_key | label | keywords | description |
|---|---|---|---|
| production | 생산 | 생산, 생산량, 일일 생산 | 생산 실적 조회 |

## Process Groups
| group | synonyms | values |
|---|---|---|
| DIE_ATTACH | die attach, da, 다이 어태치 | epoxy_dispense, die_place, post_cure |

## Value Groups
| field | canonical | synonyms | values |
|---|---|---|---|
| tech | WB | wb, wire bond | WB |
```

### 5-4. 작성 팁

- 한 줄에 한 개념만 넣기
- 키워드는 쉼표로 구분하기
- 실제 현장에서 쓰는 표현만 추가하기
- 너무 비슷한 단어를 여러 데이터셋에 동시에 넣지 않기

### 5-5. 등록 후 확인

앱을 새로고침한 뒤 `Domain Registry` 패널에서 확인합니다.

- `Loaded files`
- `Dataset keywords`
- `Process groups`
- `Registry warnings`

## 6. 다운로드 확인 방법

결과 영역에서 아래 다운로드 버튼을 확인할 수 있습니다.

- `Download result CSV`
- `Download <source table> CSV`
- `Download Analysis Base Table CSV`

추천 확인 순서:

1. 새 데이터 조회 실행
2. 다중 데이터셋 분석 실행
3. 원본 테이블과 결합 테이블이 보이는지 확인
4. CSV 다운로드가 정상 동작하는지 확인

## 7. 테스트 방법

아래 명령으로 현재 구현 검증이 가능합니다.

```bash
pytest -q
```

현재 테스트는 아래를 포함합니다.

- dataset contract
- domain registry 로딩
- intent router
- safe code executor
- sub-agent registry

## 8. 현재 한계

Phase 1은 의도적으로 가볍게 구현되어 있습니다.

아직 하지 않은 것:

- LangGraph 전환
- 실제 병렬 tool 실행
- domain 충돌 자동 해결
- ZIP 묶음 다운로드
- low confidence 재질문 이후 버튼형 선택 UI

즉, 지금은 운영 복잡도를 낮추면서 안정성을 올리는 단계입니다.

## 9. 추천 확인 순서

처음 확인할 때는 아래 순서를 권장합니다.

1. `streamlit run app.py`
2. `Available Datasets` 패널 확인
3. `Domain Registry` 패널 확인
4. `오늘 생산 보여줘`
5. `현재 결과를 공정별 상위 3개로 정렬해줘`
6. `목표 비교` 입력 후 재질문 동작 확인
7. `reference_materials/domain_registry/sample_custom_domain.md` 내용 확인
8. CSV 다운로드 확인
