# Manufacturing Agent V3 Plan

## 목표
제조 에이전트 구현의 완성도를 높이기 위해, 하네스를 기준으로 실제 리포지터리의 구조/도메인/평가 체계를 점진적으로 정렬한다.

## 범위
- `manufacturing_v2_python_base`
- `manufacturing_v2_python_base_compact`
- Harness `services/manufacturing-agent`

## 핵심 원칙
1. 하네스가 기준 문서다
2. 실제 리포지터리는 하네스를 불러와 사용한다
3. 코드 구조가 바뀌면 하네스 문서도 같이 업데이트한다
4. 평가 세트와 분석 패턴을 기준점으로 삼는다

## Phase 1. 구조 정렬
- 하네스 기준 문서 pull
- 실제 리포지터리 루트에 `AGENTS.md` 연결
- `.harness/manufacturing-agent` 기준 확인

완료 기준:
- 각 실제 리포지터리에서 하네스 문서 진입점이 존재
- 개발자가 루트에서 바로 하네스 문서를 찾을 수 있음

## Phase 2. 도메인 / 데이터셋 정렬
- 공정군, MODE, 데이터셋 정의를 하네스 기준 문서와 비교
- 차이가 있으면 하네스 또는 구현 코드 중 기준을 먼저 결정
- production / target / defect / equipment / wip / yield / hold / scrap / recipe / lot_trace 의미 정렬

완료 기준:
- 핵심 데이터셋 의미가 하네스 문서와 코드에서 모순되지 않음

## Phase 3. 질문 / 분석 패턴 정렬
- 단일 조회
- 다중 데이터셋 조회
- 후속 질문
- 파생 지표 질문
- 없는 컬럼 요청

완료 기준:
- 질문 유형별 expected flow가 문서화됨
- 실제 구현이 그 흐름과 크게 어긋나지 않음

## Phase 4. 평가 체계 정렬
- 최소 평가 세트 정의
- 리그레션 질문 세트 정의
- 결과 grounding 기준 정리
- 데이터셋 선택 오류 / 파생 컬럼 오류 / follow-up 오류를 별도 체크

완료 기준:
- 평가 문서와 실제 테스트 질문 세트가 연결됨

## Phase 5. 운영 자동화
- `sync_harness.py`로 pull / push 사용
- `validate_harness.py`로 문서 누락 점검
- 필요 시 실제 리포지터리용 validate 스크립트 추가

완료 기준:
- 하네스 구조를 기준으로 운영 가능
- 초보자도 문서와 스크립트만 보고 흐름을 따라갈 수 있음

## 즉시 다음 액션
1. 실제 리포지터리 두 곳에 루트 `AGENTS.md` 추가
2. `.harness/manufacturing-agent` 연결 확인
3. 이후 기능 개발 시 하네스 문서부터 갱신하는 습관 정착
