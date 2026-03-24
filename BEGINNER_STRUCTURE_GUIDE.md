# 초보자용 구조 안내

이 프로젝트는 Python 초보자도 수정 시작점을 잡기 쉽게 `UI -> 라우팅 -> 조회/분석` 흐름으로 나뉘어 있습니다.

## 가장 먼저 이해할 흐름

1. 사용자가 [app.py](/C:/Users/qkekt/Desktop/compact_manufacturing_service/app.py) 에서 질문을 입력합니다.
2. 질문은 [core/agent.py](/C:/Users/qkekt/Desktop/compact_manufacturing_service/core/agent.py) 의 `run_agent()`로 들어갑니다.
3. `run_agent()`는 질문이 아래 둘 중 무엇인지 판단합니다.
   - 새 원본 데이터 조회
   - 이미 조회한 `current_data`를 기준으로 한 후속 분석
4. 새 조회면 [core/data_tools.py](/C:/Users/qkekt/Desktop/compact_manufacturing_service/core/data_tools.py) 를 호출합니다.
5. 후속 분석이면 [core/data_analysis_engine.py](/C:/Users/qkekt/Desktop/compact_manufacturing_service/core/data_analysis_engine.py) 를 호출합니다.
6. 결과는 다시 [app.py](/C:/Users/qkekt/Desktop/compact_manufacturing_service/app.py) 로 돌아와 표와 텍스트로 표시됩니다.

## 파일별 역할

- [app.py](/C:/Users/qkekt/Desktop/compact_manufacturing_service/app.py)
  - 화면 표시 담당
  - 채팅 입력, 컨텍스트 표시, 표 렌더링 담당

- [core/agent.py](/C:/Users/qkekt/Desktop/compact_manufacturing_service/core/agent.py)
  - 전체 흐름 제어 담당
  - “조회냐 후속 분석이냐”를 결정
  - 최종 응답 텍스트 생성

- [core/parameter_resolver.py](/C:/Users/qkekt/Desktop/compact_manufacturing_service/core/parameter_resolver.py)
  - 질문에서 날짜, 공정, 제품, MODE 같은 조건 추출

- [core/domain_knowledge.py](/C:/Users/qkekt/Desktop/compact_manufacturing_service/core/domain_knowledge.py)
  - 제조 도메인 사전
  - 공정군, MODE, DEN, TECH 같은 지식 보관

- [core/data_tools.py](/C:/Users/qkekt/Desktop/compact_manufacturing_service/core/data_tools.py)
  - 생산 / 목표 / 불량 / 설비 / WIP 조회 데이터 생성 및 반환

- [core/data_analysis_engine.py](/C:/Users/qkekt/Desktop/compact_manufacturing_service/core/data_analysis_engine.py)
  - 후속 질문을 pandas 코드로 바꾸고 실행

- [core/safe_code_executor.py](/C:/Users/qkekt/Desktop/compact_manufacturing_service/core/safe_code_executor.py)
  - 생성된 pandas 코드를 안전하게 실행

- [core/number_format.py](/C:/Users/qkekt/Desktop/compact_manufacturing_service/core/number_format.py)
  - 수량 컬럼을 K/M 단위로 보기 좋게 포맷

## 수정 시작 추천 순서

- 화면 문구를 바꾸고 싶다
  - [app.py](/C:/Users/qkekt/Desktop/compact_manufacturing_service/app.py)

- 어떤 데이터를 조회할지 바꾸고 싶다
  - [core/data_tools.py](/C:/Users/qkekt/Desktop/compact_manufacturing_service/core/data_tools.py)

- 질문에서 조건을 더 잘 뽑고 싶다
  - [core/parameter_resolver.py](/C:/Users/qkekt/Desktop/compact_manufacturing_service/core/parameter_resolver.py)

- 후속 pandas 분석을 더 잘하게 만들고 싶다
  - [core/data_analysis_engine.py](/C:/Users/qkekt/Desktop/compact_manufacturing_service/core/data_analysis_engine.py)

- 제조 도메인 용어를 넓히고 싶다
  - [core/domain_knowledge.py](/C:/Users/qkekt/Desktop/compact_manufacturing_service/core/domain_knowledge.py)
