# current_data 설명

`current_data`는 이 프로젝트에서 가장 중요한 개념입니다.

## current_data가 무엇인가

`current_data`는 “방금 사용자에게 보여준 결과 테이블”입니다.

즉:
- 원본 조회 결과일 수도 있고
- 후속 pandas 분석 결과일 수도 있습니다

다음 질문이 들어오면, 시스템은 이 `current_data`를 기준으로 다시 분석할 수 있습니다.

## 왜 필요한가

이 값이 있어야 사용자가 이렇게 이어서 말할 수 있습니다.

- 오늘 생산량 보여줘
- 상위 5개만 보여줘
- MODE별로 그룹화해줘

두 번째와 세 번째 질문은 새 조회가 아니라, 바로 직전 결과 테이블을 변형하는 요청입니다. 이때 기준이 되는 값이 `current_data`입니다.

## 흐름 예시

1. `오늘 생산량 보여줘`
   - 원본 조회 실행
   - 결과 테이블이 `current_data`로 저장됨

2. `MODE별로 상위 3개만 보여줘`
   - 새 조회를 하지 않음
   - `current_data`를 pandas로 변형
   - 변형된 결과가 다시 `current_data`로 저장됨

3. `DDR5만 보여줘`
   - 방금 변형된 결과를 다시 필터링

## 코드에서 어디서 쓰이나

- [app.py](/C:/Users/qkekt/Desktop/compact_manufacturing_service/app.py)
  - 세션에 `current_data`를 저장하고 다음 질문에 넘깁니다

- [core/agent.py](/C:/Users/qkekt/Desktop/compact_manufacturing_service/core/agent.py)
  - `current_data`가 있는지 확인하고
  - 조회가 아니라 후속 분석으로 처리할지 결정합니다

- [core/data_analysis_engine.py](/C:/Users/qkekt/Desktop/compact_manufacturing_service/core/data_analysis_engine.py)
  - `current_data["data"]`를 DataFrame으로 바꿔 pandas 분석을 수행합니다

## 초보자 관점에서 꼭 기억할 점

- `current_data`는 “직전 결과 테이블”입니다
- 후속 질문은 보통 이 데이터를 기준으로 처리됩니다
- 따라서 후속 분석이 이상하면
  - `current_data`가 제대로 저장됐는지
  - 후속 질문이 조회로 잘못 라우팅되지 않았는지
  먼저 보면 됩니다
