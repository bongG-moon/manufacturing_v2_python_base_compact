# 시작하기

이 문서는 처음 이 프로젝트를 여는 사람이 가장 먼저 읽는 문서입니다.

## 이 서비스가 하는 일

이 서비스는 제조 데이터를 채팅으로 조회하고, 바로 직전 결과를 다시 pandas로 분석할 수 있는 경량 앱입니다.

사용자는 보통 이렇게 씁니다.

1. `오늘 생산량 보여줘`
2. `상위 5개만 보여줘`
3. `공정군별로 그룹화해줘`

즉 첫 질문은 조회, 그다음 질문은 후속 분석입니다.

## 실행 방법

```bash
pip install -r requirements.txt
copy .env.example .env
streamlit run app.py
```

## 지금 들어 있는 데이터셋

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

## 가장 먼저 봐야 할 파일

- `app.py`
  - 채팅 화면 시작점
- `core/agent.py`
  - 질문이 새 조회인지 후속 분석인지 결정
- `core/data_tools.py`
  - 조회 데이터 생성
- `core/domain_knowledge.py`
  - 제조 용어 사전

## 초보자용 읽기 순서

1. `START_HERE.md`
2. `QUESTION_GUIDE.md`
3. `DOMAIN_GUIDE.md`
4. `BEGINNER_ADD_GUIDE.md`
5. `TEST_QUESTIONS.md`

## 정말 중요한 개념 2개

### 1. 새 조회

예:

- `오늘 생산량 보여줘`
- `오늘 TEST 공정 불량 보여줘`

이런 질문은 원본 데이터를 새로 가져옵니다.

### 2. 후속 분석

예:

- `상위 5개만 보여줘`
- `공정군별로 그룹화해줘`
- `목표 대비 달성율 계산해줘`

이런 질문은 방금 본 결과를 다시 가공합니다.

## 막히면 어디부터 볼까

- 실행이 안 되면: `README.md`, `.env`, `requirements.txt`
- 질문 조건이 이상하면: `core/parameter_resolver.py`
- 조회 데이터가 이상하면: `core/data_tools.py`
- 후속 pandas 분석이 이상하면: `core/data_analysis_engine.py`, `core/analysis_llm.py`
