# 메인 화면 확장 기능 상세 분석

이 문서는 현재 `Compact Manufacturing Chat Service` 메인 화면에 추가된 확장 기능을 Python 초보자도 따라갈 수 있게 자세히 설명하는 문서입니다.

설명 대상 기능:

- `Available Datasets`
- `Domain Registry`
- `Recommended Sub Agents`
- `Engineer detail mode`

이 문서의 목표는 단순히 "무슨 기능인가"를 설명하는 데서 끝나지 않고, 아래 4가지를 한 번에 이해하도록 돕는 것입니다.

1. 화면에서 무엇이 보이는가
2. 어떤 파일이 이 기능을 구현하는가
3. 내부에서 어떤 데이터 구조와 함수가 연결되는가
4. 기능을 바꾸려면 어디부터 읽어야 하는가

---

## 1. 먼저 큰 그림

현재 메인 화면은 단순 채팅창이 아닙니다. 실제로는 아래 순서로 여러 보조 패널과 상태 관리 기능이 같이 동작합니다.

```text
app.py
  -> Streamlit 페이지 시작
  -> 세션 상태 초기화
  -> 현재 context 표시
  -> Engineer detail mode 토글 표시
  -> Available Datasets 패널 표시
  -> Domain Registry 패널 표시
  -> Recommended Sub Agents 패널 표시
  -> 이전 대화 렌더링
  -> 사용자 입력 수신
  -> core/agent.py::run_agent() 호출
  -> 결과/소스 테이블/분석 코드 렌더링
```

즉, 화면은 크게 2개 역할을 같이 수행합니다.

- 질문을 입력받는 채팅 인터페이스
- 시스템 내부 상태와 확장 지점을 설명해 주는 운영용 대시보드

초보자 입장에서 중요한 포인트는 이것입니다.

- `app.py`는 화면 순서를 정하는 파일입니다.
- `ui_renderer.py`는 화면 안의 각 패널을 실제로 그리는 파일입니다.
- `core/*.py`는 패널에 들어갈 데이터와 실제 동작 로직을 만드는 파일입니다.

---

## 2. 메인 화면을 만드는 파일 구조

메인 화면을 이해할 때는 아래 파일 순서로 읽으면 가장 쉽습니다.

### 2-1. 화면 진입점

- `app.py`

여기서 하는 일:

- Streamlit 페이지 제목과 레이아웃 설정
- 세션 상태 초기화
- 상단 레이아웃 구성
- 각 패널 렌더링 함수 호출
- 채팅 입력 처리
- `run_agent()` 실행

핵심 함수:

- `main()`
- `_run_chat_turn()`
- `_render_saved_chat_history()`

### 2-2. 화면 컴포넌트 모음

- `ui_renderer.py`

여기서 하는 일:

- context 배너 표시
- `Available Datasets` 패널 렌더링
- `Domain Registry` 패널 렌더링
- `Recommended Sub Agents` 패널 렌더링
- tool result 표, 소스 테이블, 분석 요약 렌더링

핵심 함수:

- `init_session_state()`
- `render_context()`
- `render_available_datasets()`
- `render_domain_registry()`
- `render_sub_agent_blueprint()`
- `render_tool_results()`

### 2-3. 화면 뒤의 실제 데이터 공급자

- `core/dataset_contracts.py`
- `core/domain_registry.py`
- `core/sub_agents.py`
- `core/agent.py`
- `core/data_tools.py`
- `core/parameter_resolver.py`

이 파일들은 화면에 직접 그림을 그리지는 않지만, 화면에 표시할 내용을 준비합니다.

---

## 3. 앱이 켜질 때 실제로 무슨 일이 일어나는가

메인 화면은 `app.py::main()`에서 시작됩니다.

대략 이런 구조입니다.

```python
def main() -> None:
    init_session_state()

    st.title("Compact Manufacturing Chat")
    st.caption(...)

    col_left, col_right = st.columns([5, 2])
    with col_left:
        render_context()
    with col_right:
        st.session_state.detail_mode = st.toggle("Engineer detail mode", ...)

    render_available_datasets()
    render_domain_registry()
    render_sub_agent_blueprint()
    _render_saved_chat_history()

    user_input = st.chat_input(...)
```

초보자가 여기서 꼭 봐야 할 포인트:

- `init_session_state()`가 먼저 실행됩니다.
- `detail_mode`는 일반 변수 아니라 `st.session_state.detail_mode`에 저장됩니다.
- 세 개의 확장 패널은 모두 `ui_renderer.py` 함수로 분리되어 있습니다.
- 입력창은 제일 아래에 있고, 그 전까지는 화면 설명용 정보 패널이 먼저 그려집니다.

세션 상태에 저장되는 주요 값:

- `messages`: 지금까지의 채팅 기록
- `current_data`: 방금 조회하거나 분석한 현재 테이블
- `context`: 날짜, 공정, 제품 등 다음 질문으로 이어질 문맥
- `detail_mode`: 상세 표시 여부

이 구조 덕분에 사용자는 채팅만 하고 있어도, 내부적으로는 "현재 결과", "이전 필터", "상세 보기 상태"가 계속 유지됩니다.

---

## 4. `Available Datasets` 상세 분석

### 4-1. 화면에서 보이는 기능

이 패널은 사용자가 "지금 어떤 데이터셋을 조회할 수 있는지" 빠르게 확인하게 해 줍니다.

표시 내용:

- 데이터셋 이름
- 데이터셋 설명
- 필수 파라미터

예를 들어 사용자는 이런 질문을 하기 전에 이 패널을 보고 감을 잡을 수 있습니다.

- 생산은 날짜가 필요하구나
- recipe는 날짜가 선택 사항이구나
- lot trace도 조회 가능하구나

### 4-2. 구현 파일

- `app.py`
- `ui_renderer.py`
- `core/dataset_contracts.py`
- `core/agent.py`
- `tests/test_dataset_contracts.py`

### 4-3. 화면 렌더링 함수

실제 렌더링은 `ui_renderer.py::render_available_datasets()`가 담당합니다.

핵심 구조:

```python
with st.expander("Available Datasets", expanded=False):
    for contract in list_dataset_contracts():
        required = ", ".join(contract.required_params) if contract.required_params else "none"
        st.markdown(f"- **{contract.label}**: {contract.description} | required: `{required}`")
```

이 코드를 보면 초보자도 흐름을 읽을 수 있습니다.

1. 패널 하나를 연다
2. 등록된 데이터셋 계약 목록을 가져온다
3. 각 데이터셋의 이름, 설명, 필수 조건을 한 줄씩 출력한다

### 4-4. 실제 데이터 원본은 어디인가

화면에 나오는 데이터셋 목록의 원본은 `core/dataset_contracts.py`의 `DATASET_CONTRACTS`입니다.

여기에는 각 데이터셋별로 아래 정보가 들어 있습니다.

- `key`
- `label`
- `description`
- `required_params`
- `optional_params`
- `date_policy`
- `default_group_by`

즉, 이 파일은 단순 상수가 아니라 "이 데이터셋은 어떤 계약을 갖는가"를 정의하는 표준 문서 역할을 합니다.

### 4-5. 관련 기능과 연결점

이 패널은 화면 설명용으로만 끝나지 않습니다. 실제 동작에도 연결됩니다.

관련 연결:

- `list_dataset_contracts()`
  - 패널에서 목록을 보여줄 때 사용
- `format_missing_params_message()`
  - 사용자가 필수 조건 없이 질문했을 때 안내 메시지 생성
- `format_available_datasets_message()`
  - 어떤 데이터셋인지 판단이 안 될 때 사용 가능한 목록 안내
- `core/agent.py::_run_retrieval()`
  - 실제 조회 전 필수 조건을 검사

즉, `Available Datasets`는 "보기용 목록"이면서 동시에 "조회 규칙의 실제 기준표"이기도 합니다.

### 4-6. 동작 프로세스

```text
사용자 질문
  -> core/agent.py 에서 어떤 dataset이 필요한지 판단
  -> core/dataset_contracts.py 에서 필수 파라미터 확인
  -> 부족하면 안내 메시지 반환
  -> 충분하면 core/data_tools.py 의 실제 조회 함수 실행
```

### 4-7. 수정하려면 어디를 봐야 하나

상황별 수정 위치:

- 화면 문구를 바꾸고 싶다
  - `ui_renderer.py::render_available_datasets()`
- 데이터셋 설명이나 필수 파라미터를 바꾸고 싶다
  - `core/dataset_contracts.py`
- 실제 조회 가능한 데이터셋 자체를 추가하고 싶다
  - `core/dataset_contracts.py`
  - `core/data_tools.py`
  - 필요하면 `core/domain_registry.py`

### 4-8. 초보자가 자주 헷갈리는 점

- 이 패널에 데이터셋이 보인다고 해서 자동으로 조회 함수가 완성된 것은 아닙니다.
- 실제 조회는 `core/data_tools.py`에 함수가 등록되어 있어야 합니다.
- 즉, `계약 정의`와 `실제 구현`은 분리되어 있습니다.

---

## 5. `Domain Registry` 상세 분석

### 5-1. 화면에서 보이는 기능

이 패널은 "Python 코드를 고치지 않고도 도메인 용어를 확장할 수 있다"는 점을 보여주는 기능입니다.

화면에서 볼 수 있는 것:

- 도메인 파일 작성 방법 안내
- 예시 Markdown 형식
- 로드된 파일 목록
- 충돌 경고
- dataset keywords 테이블
- process groups 테이블

이 패널은 사용자 설명용이면서, 동시에 운영자가 "내가 추가한 용어가 잘 읽혔는지" 확인하는 검증 도구이기도 합니다.

### 5-2. 구현 파일

- `ui_renderer.py`
- `core/domain_registry.py`
- `core/parameter_resolver.py`
- `core/data_tools.py`
- `reference_materials/domain_registry/README.md`
- `reference_materials/domain_registry/sample_custom_domain.md`
- `tests/test_domain_registry.py`

### 5-3. 왜 이 기능이 중요한가

제조 현장에서는 같은 뜻을 여러 표현으로 말합니다.

예:

- `die attach`
- `DA`
- `다이 어태치`

또 데이터셋도 현장마다 다르게 부릅니다.

예:

- `생산`
- `output qty`
- `일일 생산`

이런 표현 차이를 매번 Python 코드에 직접 하드코딩하면 유지보수가 어려워집니다. 그래서 이 프로젝트는 Markdown 파일을 읽어 도메인 사전을 확장하는 방식을 택했습니다.

### 5-4. 핵심 구조

`core/domain_registry.py`에는 세 가지 핵심 데이터 구조가 있습니다.

- `DatasetKeywordEntry`
  - 어떤 데이터셋을 어떤 키워드로 찾을지
- `DomainGroup`
  - 공정 그룹, 값 그룹의 대표값과 동의어 묶음
- `DomainRegistry`
  - 전체 registry 결과물

이 registry 안에는 보통 아래 정보가 들어갑니다.

- `dataset_keywords`
- `process_groups`
- `value_groups`
- `notes`
- `loaded_files`
- `warnings`

### 5-5. 로딩 과정

도메인 registry는 `load_domain_registry()`에서 만들어집니다.

동작 순서:

1. 기본 내장 사전(`DEFAULT_*`)을 먼저 만든다
2. `reference_materials/domain_registry/*.md` 파일을 읽는다
3. 파일마다 `Dataset Keywords`, `Process Groups`, `Value Groups` 섹션을 파싱한다
4. 기존 사전에 merge 한다
5. 키워드 충돌이 있는지 검사한다
6. 최종 summary를 화면과 다른 모듈에서 사용한다

즉, "기본 사전 + 사용자 추가 파일" 구조입니다.

### 5-6. 화면 패널은 어떤 함수를 쓰는가

`ui_renderer.py::render_domain_registry()`는 내부적으로 `get_domain_registry_summary()`를 호출합니다.

흐름:

```text
render_domain_registry()
  -> get_domain_registry_summary()
     -> load_domain_registry()
        -> 기본 사전 준비
        -> markdown 파일 읽기
        -> 충돌 검사
  -> summary를 표와 경고 메시지로 표시
```

### 5-7. 이 기능이 실제 에이전트 동작에 어떻게 연결되는가

이 부분이 가장 중요합니다. `Domain Registry`는 단순 문서 패널이 아니라 실제 질문 해석 품질에 영향을 줍니다.

연결 지점 1:

- `core/parameter_resolver.py::resolve_required_params()`
- 내부에서 `build_domain_knowledge_prompt()` 호출

의미:

- LLM에게 파라미터를 추출시킬 때
- dataset 키워드, 공정 그룹, value group 정보를 프롬프트에 같이 넣음
- 따라서 질문에 현장 용어가 들어와도 더 잘 해석하게 됨

연결 지점 2:

- `core/data_tools.py::get_dataset_registry()`
- 내부에서 `get_dataset_keyword_map()` 호출

의미:

- 사용자의 질문에서 어떤 데이터셋을 꺼낼지 정할 때
- registry의 키워드 목록을 실제로 사용함

즉, 이 기능은 아래 두 단계에 모두 영향을 줍니다.

- 질문 해석
- 데이터셋 선택

### 5-8. 실제 예시 시나리오

예를 들어 `reference_materials/domain_registry/sample_custom_domain.md`에 아래가 들어 있다고 가정하겠습니다.

```markdown
| dataset_key | label | keywords |
| production | 생산 | output qty, 생산 실적, 일일 생산 |
```

그러면 이런 질문이 가능해집니다.

- `오늘 output qty 보여줘`

내부 흐름:

```text
사용자 질문
  -> core/data_tools.py::pick_retrieval_tools()
  -> domain registry에서 production 키워드 목록 확인
  -> "output qty"가 production에 매칭
  -> production 데이터셋 선택
  -> 실제 조회 실행
```

### 5-9. 충돌 경고는 왜 필요한가

예를 들어 같은 키워드가 두 데이터셋에 동시에 들어가 있으면 어떤 데이터셋을 선택해야 할지 모호해집니다.

그래서 `_detect_conflicts()`가 아래 같은 문제를 경고합니다.

- dataset keyword conflict
- process synonym conflict
- value group synonym conflict

이 경고는 앱을 망가뜨리기 위한 것이 아니라, "질문 해석이 애매해질 수 있으니 정리하자"는 운영 신호입니다.

### 5-10. 수정하려면 어디를 봐야 하나

상황별 수정 위치:

- 새 용어 파일만 추가하고 싶다
  - `reference_materials/domain_registry/`
- Markdown 파싱 규칙을 바꾸고 싶다
  - `core/domain_registry.py`
- 화면 표시 형식을 바꾸고 싶다
  - `ui_renderer.py::render_domain_registry()`
- 질문 해석 프롬프트에 registry 반영 방식을 바꾸고 싶다
  - `core/parameter_resolver.py`

### 5-11. 초보자가 자주 헷갈리는 점

- `Domain Registry`는 데이터를 새로 만드는 기능이 아닙니다.
- 이 기능은 "질문을 이해하는 vocabulary layer"에 가깝습니다.
- 실제 데이터 행(row)은 여전히 `core/data_tools.py`의 mock 조회 함수가 만듭니다.

---

## 6. `Recommended Sub Agents` 상세 분석

### 6-1. 화면에서 보이는 기능

이 패널은 현재 서비스의 확장 방향을 보여주는 설계 블루프린트입니다.

패널 내용:

- 현재 서비스 강점
- 현재 리스크
- 추천 구현 순서
- 추천 서브 에이전트 카드 목록

중요한 해석:

- 이 패널은 "이미 실제로 여러 에이전트가 돌아간다"는 뜻이 아닙니다.
- 현재는 "앞으로 어떤 서브 에이전트로 분리하면 좋은지"를 정리한 제품 설계 정보입니다.

### 6-2. 구현 파일

- `ui_renderer.py`
- `core/sub_agents.py`
- `reference_materials/docs/SUB_AGENT_BLUEPRINT.md`
- `tests/test_sub_agents.py`

### 6-3. 핵심 데이터 구조

`core/sub_agents.py`에는 `SubAgentSpec`라는 dataclass가 있습니다.

이 구조가 서브 에이전트 1개의 설계 카드를 표현합니다.

필드:

- `key`
- `name`
- `priority`
- `mission`
- `why_now`
- `primary_inputs`
- `outputs`
- `owned_modules`
- `sample_prompts`

초보자 관점에서 dataclass를 이렇게 이해하면 됩니다.

- 여러 관련 값을 한 묶음으로 저장하는 "설계서용 박스"

### 6-4. 화면은 어떻게 그려지는가

흐름:

```text
render_sub_agent_blueprint()
  -> get_system_analysis_snapshot()
  -> build_sub_agent_cards()
     -> get_recommended_sub_agents()
        -> SubAgentSpec 목록 생성
  -> Streamlit markdown으로 카드 렌더링
```

`get_system_analysis_snapshot()`는 서비스 전체 진단 요약을 주고,
`get_recommended_sub_agents()`는 실제 추천 에이전트 목록을 줍니다.

### 6-5. 왜 메인 화면에 이 기능이 있는가

이 프로젝트는 compact 버전이지만, 앞으로 기능을 늘릴 때 어떤 방향으로 분리할지 미리 보여주기 위해 이 패널이 들어가 있습니다.

특히 현재 코드의 약점을 문서가 아닌 "실행 UI 안"에서도 볼 수 있게 한 점이 중요합니다.

예:

- intent routing은 heuristic 의존
- multi-dataset join은 grain 검증이 약함
- regression guard가 아직 약함

즉, 이 패널은 단순 소개가 아니라 "현재 구조의 기술 부채와 다음 작업 후보"를 한눈에 보여주는 운영 메모 역할도 합니다.

### 6-6. 각 서브 에이전트는 무엇을 의미하는가

현재 추천 목록:

1. `Intent & Context Guard Agent`
2. `Semantic Join Planner Agent`
3. `Yield & Defect RCA Agent`
4. `WIP & Dispatch Optimization Agent`
5. `Quality Regression Guard Agent`

이 이름들을 실제 현재 코드와 연결해서 보면 이해가 쉽습니다.

- `Intent & Context Guard Agent`
  - 현재 `core/intent_router.py`, `core/agent.py`, `core/parameter_resolver.py`가 같이 맡는 역할
- `Semantic Join Planner Agent`
  - 현재 `core/agent.py::_build_analysis_base_table()`가 단순 join으로 처리하는 부분을 더 안전하게 만들 후보
- `Yield & Defect RCA Agent`
  - 현재는 표를 보여주고 정렬/그룹화 정도만 하지만, 앞으로 원인 분석까지 확장할 후보
- `WIP & Dispatch Optimization Agent`
  - 현재 WIP/hold/equipment/target 데이터를 운영 의사결정으로 연결하는 후보
- `Quality Regression Guard Agent`
  - 현재 `tests/`와 `safe_code_executor` 중심의 검증을 더 강화하는 후보

### 6-7. 수정하려면 어디를 봐야 하나

상황별 수정 위치:

- 카드 문구를 바꾸고 싶다
  - `core/sub_agents.py`
- 화면 표현 순서를 바꾸고 싶다
  - `ui_renderer.py::render_sub_agent_blueprint()`
- 장기 설계 문서를 같이 바꾸고 싶다
  - `reference_materials/docs/SUB_AGENT_BLUEPRINT.md`

### 6-8. 초보자가 자주 헷갈리는 점

- 여기 적힌 에이전트들은 현재 `run_agent()` 안에서 실제 병렬 실행되지 않습니다.
- 지금은 "추천 설계안"이지, "실행 중인 멀티 에이전트 시스템"은 아닙니다.

이 구분을 이해하면 현재 구현 범위를 정확히 볼 수 있습니다.

---

## 7. `Engineer detail mode` 상세 분석

### 7-1. 화면에서 보이는 기능

이 기능은 메인 화면 오른쪽 상단 토글입니다.

켜면:

- 결과 expander가 기본 펼침 상태가 됨
- 분석 결과에 generated pandas code가 표시됨
- latency가 표시됨
- 에러 발생 시 상세 에러 문구가 보임

끄면:

- 일반 사용자에게 필요한 핵심 결과만 보이고
- 내부 분석 코드나 디버깅 정보는 숨겨집니다

### 7-2. 구현 파일

- `app.py`
- `ui_renderer.py`

### 7-3. 핵심 상태 저장 방식

이 기능은 `st.session_state.detail_mode`라는 boolean 값으로 관리됩니다.

토글 코드:

```python
st.session_state.detail_mode = st.toggle(
    "Engineer detail mode",
    value=bool(st.session_state.get("detail_mode", False)),
    help="Show analysis code and open result panels by default.",
)
```

중요 포인트:

- 단순 지역 변수가 아니라 session state에 저장됨
- 따라서 같은 세션 안에서는 다음 렌더링에도 상태가 유지됨

### 7-4. 이 값이 실제로 어디에 쓰이는가

연결 지점 1:

- `app.py`

토글이 켜져 있으면 assistant 메시지 아래에 아래 정보가 추가됩니다.

- `error_detail`
- `latency_seconds`

연결 지점 2:

- `ui_renderer.py::render_tool_results()`

내부에서:

```python
expanded = bool(st.session_state.get("detail_mode", False))
```

즉, 결과 expander를 기본으로 열지 닫을지 결정합니다.

연결 지점 3:

- `render_tool_results()` 안에서
- `tool_name == "analyze_current_data"` 이고
- `expanded`가 `True`일 때
- generated pandas code를 보여줍니다

즉, 이 모드는 "분석 엔진 자체를 바꾸는 기능"이 아니라 "분석 결과를 얼마나 자세히 보여줄지"를 제어하는 UI 모드입니다.

### 7-5. 동작 프로세스

```text
사용자가 Engineer detail mode ON
  -> st.session_state.detail_mode = True 저장
  -> 이후 렌더링에서 expanded=True 사용
  -> 결과 패널 자동 펼침
  -> 분석 결과면 generated_code 표시
  -> app.py 에서 latency / error detail 표시
```

### 7-6. 관련 기능

이 토글과 특히 잘 연결되는 기능:

- follow-up pandas analysis
- source table 보기
- analysis base table 보기
- CSV 다운로드

왜냐하면 복잡한 분석일수록 아래를 같이 보고 싶어지기 때문입니다.

- 원본 테이블이 무엇이었는지
- join된 테이블이 무엇이었는지
- 어떤 pandas 코드가 생성되었는지

### 7-7. 수정하려면 어디를 봐야 하나

상황별 수정 위치:

- 토글 위치나 도움말을 바꾸고 싶다
  - `app.py`
- 어떤 정보를 상세 모드에서 더 보여줄지 바꾸고 싶다
  - `app.py`
  - `ui_renderer.py::render_tool_results()`
- generated code를 항상 보이게 하고 싶다
  - `ui_renderer.py`

### 7-8. 초보자가 자주 헷갈리는 점

- detail mode를 켠다고 분석 정확도가 올라가지는 않습니다.
- detail mode는 디버그/설명용 표시를 늘리는 기능입니다.

---

## 8. 이 네 기능은 서로 어떻게 연결되는가

처음 보면 각 패널이 따로 놀아 보일 수 있지만, 실제로는 하나의 흐름으로 연결됩니다.

### 예시 시나리오

사용자 질문:

- `오늘 output qty 보여줘`

내부 흐름:

```text
1. Domain Registry
   -> "output qty"를 production 키워드로 인식할 수 있게 도와줌

2. Available Datasets
   -> production은 date가 필요하다는 규칙을 dataset contract가 정의

3. core/agent.py
   -> 질문에서 production retrieval을 선택
   -> 날짜가 있으면 조회 진행

4. core/data_tools.py
   -> production mock data 생성

5. ui_renderer.py
   -> 결과 표 렌더링

6. Engineer detail mode가 ON 이면
   -> 결과 패널 자동 펼침
   -> 후속 분석 시 generated code까지 표시

7. Recommended Sub Agents
   -> 이 서비스가 앞으로 어떤 방향으로 발전할지 설계 힌트를 제공
```

즉, 네 기능의 역할은 다음처럼 구분하면 이해하기 쉽습니다.

- `Available Datasets`
  - 무엇을 조회할 수 있는가
- `Domain Registry`
  - 질문 용어를 어떻게 이해할 것인가
- `Recommended Sub Agents`
  - 앞으로 어떤 구조로 확장할 것인가
- `Engineer detail mode`
  - 내부 과정을 얼마나 자세히 보여줄 것인가

---

## 9. 초보자를 위한 읽기 순서

이 기능들을 코드와 함께 이해하고 싶다면 아래 순서가 가장 쉽습니다.

1. `app.py`
2. `ui_renderer.py`
3. `core/dataset_contracts.py`
4. `core/domain_registry.py`
5. `core/sub_agents.py`
6. `core/agent.py`
7. `core/data_tools.py`
8. `core/parameter_resolver.py`

읽을 때 체크할 질문:

- 이 함수는 화면을 그리는가, 데이터를 만드는가, 아니면 둘을 연결하는가
- 이 값은 화면 표시용인가, 실제 로직 제어용인가
- 이 기능은 설명 패널인가, 실제 동작에도 참여하는가

특히 구분이 중요합니다.

- `Recommended Sub Agents`는 현재 설명/설계 패널 비중이 큼
- `Domain Registry`는 실제 로직에 직접 참여함
- `Engineer detail mode`는 실제 로직보다 렌더링 동작에 참여함

---

## 10. 수정 작업별 빠른 가이드

### 10-1. 메인 화면에 새 패널을 추가하고 싶다

읽을 파일:

- `app.py`
- `ui_renderer.py`

방법:

1. `ui_renderer.py`에 `render_xxx()` 함수 추가
2. `app.py::main()`에서 호출 위치 지정

### 10-2. Available Datasets 목록을 바꾸고 싶다

읽을 파일:

- `core/dataset_contracts.py`
- `ui_renderer.py`
- `core/data_tools.py`

### 10-3. 사용자 용어를 더 많이 인식하게 하고 싶다

읽을 파일:

- `reference_materials/domain_registry/`
- `core/domain_registry.py`
- `core/parameter_resolver.py`
- `core/data_tools.py`

### 10-4. 상세 모드에서 더 많은 디버그 정보를 보고 싶다

읽을 파일:

- `app.py`
- `ui_renderer.py`
- 필요하면 `core/data_analysis_engine.py`

### 10-5. 추천 서브 에이전트 카드를 바꾸고 싶다

읽을 파일:

- `core/sub_agents.py`
- `reference_materials/docs/SUB_AGENT_BLUEPRINT.md`

---

## 11. 관련 테스트

이 기능들과 직접 연결된 테스트 파일도 같이 보면 이해가 빨라집니다.

- `tests/test_dataset_contracts.py`
  - dataset contract 규칙 확인
- `tests/test_domain_registry.py`
  - domain registry 로딩과 summary 확인
- `tests/test_intent_router.py`
  - 조회 vs 후속분석 라우팅 확인
- `tests/test_sub_agents.py`
  - 추천 서브 에이전트 목록 구조 확인

초보자에게 테스트는 "정답 예시"처럼 도움이 됩니다.

- 어떤 입력이 들어오면
- 어떤 출력이 나와야 하는지

를 문장보다 더 명확하게 보여주기 때문입니다.

---

## 12. 핵심 정리

이 메인 화면은 더 이상 단순 채팅창이 아닙니다. 현재 구조에서는 아래 네 층이 함께 붙어 있습니다.

1. 질문을 입력받는 채팅 UI
2. 조회 가능한 데이터셋 규칙 안내
3. 도메인 용어 확장과 검증
4. 제품 확장 방향과 디버그 가시성 제공

초보자 기준으로 가장 중요한 이해 포인트는 이것입니다.

- `app.py`는 화면의 순서를 잡는다
- `ui_renderer.py`는 화면 부품을 그린다
- `core/dataset_contracts.py`는 조회 계약을 정의한다
- `core/domain_registry.py`는 질문 용어 사전을 확장한다
- `core/sub_agents.py`는 미래 확장 설계를 정리한다
- `detail_mode`는 내부 정보를 얼마나 자세히 보여줄지 결정한다

이 구조를 이해하면 메인 화면에 새로운 기능이 보일 때도 "이건 UI인가, 계약인가, 사전인가, 설계 문서인가"를 구분하면서 읽을 수 있습니다.
