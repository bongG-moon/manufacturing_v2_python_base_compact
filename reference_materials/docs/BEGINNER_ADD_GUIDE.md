# 초보자용 추가 가이드

이 문서는 새 데이터를 붙이거나 도메인 지식을 늘릴 때 어디를 수정해야 하는지 아주 짧게 설명합니다.

## 1. 새 데이터셋 추가 방법

새 데이터셋은 보통 아래 2곳만 보면 됩니다.

### 먼저 할 일

1. `core/data_tools.py`에 조회 함수 추가
2. `core/domain_knowledge.py`의 `DATASET_METADATA`에 등록

### 예시 순서

1. `core/data_tools.py`에 `get_alarm_data()` 같은 함수를 만듭니다.
2. 함수가 `list[dict]` 형태의 행 데이터를 반환하게 만듭니다.
3. `core/data_tools.py`의 `DATASET_TOOL_FUNCTIONS`에 `"alarm": get_alarm_data`를 추가합니다.
4. `core/domain_knowledge.py`의 `DATASET_METADATA`에 아래처럼 추가합니다.

```python
"alarm": {
    "label": "알람",
    "keywords": ["알람", "alarm", "경보"],
}
```

### 왜 이렇게 나눠두었나요?

- `domain_knowledge.py`는 질문에서 어떤 데이터셋을 찾을지 결정하는 기준 사전입니다.
- `data_tools.py`는 실제 데이터를 만들어 주는 조회기입니다.
- 그래서 새 데이터셋을 추가할 때도 역할이 섞이지 않아 초보자도 따라가기 쉽습니다.

## 2. 도메인 지식 추가 방법

도메인 지식은 대부분 `core/domain_knowledge.py`에서 관리합니다.

### 주로 수정하는 항목

- `PROCESS_SPECS`
  - 공정명, 공정군, 설명
- `PROCESS_GROUP_SYNONYMS`
  - 공정군 별칭
- `PRODUCTS`
  - 제품명
- `PRODUCT_TECH_FAMILY`
  - 제품과 기술 계열 연결
- `MODE_GROUPS`, `DEN_GROUPS`, `TECH_GROUPS`
  - 질문에서 자주 쓰는 분류값
- `DATASET_METADATA`
  - 데이터셋 이름, 화면 라벨, 키워드

### 예시

새 공정 `FINAL_TEST`를 넣고 싶다면:

1. `PROCESS_SPECS`에 공정 정보 추가
2. 필요하면 `PROCESS_GROUP_SYNONYMS`에 별칭 추가
3. 이 공정을 쓰는 데이터 생성 함수가 있으면 `data_tools.py`에서 후보 값에 반영

## 3. 가장 중요한 원칙

- 도메인 용어는 먼저 `domain_knowledge.py`에 넣습니다.
- 실제 조회 로직은 `data_tools.py`에 넣습니다.
- 질문 해석 기준과 실제 데이터 값이 다르면 나중에 오류가 생기기 쉽습니다.

## 4. 수정 후 빠른 확인 방법

### 문법 확인

```bash
python -m py_compile app.py ui_renderer.py core\agent.py core\domain_knowledge.py core\data_tools.py
```

### 질문 확인

- `오늘 생산량 보여줘`
- `오늘 수율 보여줘`
- `오늘 생산과 목표를 같이 조회해줘`
- `오늘 TEST 공정 WIP 보여줘`

위 질문이 동작하면 새 데이터셋이나 새 도메인 용어가 기본 흐름에 잘 연결된 것입니다.
