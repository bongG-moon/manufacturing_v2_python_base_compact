# Harness Script Quickstart

이 문서는 제조 에이전트 하네스를 실제 구현 리포지터리에서 사용할 때,
어떤 스크립트를 언제 실행해야 하는지 빠르게 확인하기 위한 문서입니다.

대상 스크립트:

- [setup_harness_subtree.ps1](C:\Users\qkekt\Desktop\Harness\tools\setup_harness_subtree.ps1)
- [pull_harness.ps1](C:\Users\qkekt\Desktop\Harness\tools\pull_harness.ps1)
- [push_harness.ps1](C:\Users\qkekt\Desktop\Harness\tools\push_harness.ps1)

## 1. 기본 개념

기준 하네스 저장소:

- [Harness](C:\Users\qkekt\Desktop\Harness)

실제 구현 리포지터리 안에서 하네스가 들어가는 위치:

- `.harness/manufacturing-agent/`

작업 흐름은 항상 아래 순서입니다.

1. Harness에서 기준 하네스를 관리
2. 실제 구현 리포지터리로 가져오기
3. 코드 작업
4. 하네스 문서가 바뀌면 다시 Harness로 반영

## 2. 어떤 스크립트를 언제 쓰는가

### `setup_harness_subtree.ps1`

사용 시점:

- 실제 리포지터리에서 하네스를 **처음 연결할 때**
- 기존 복사본 `.harness`를 subtree 방식으로 정리하고 싶을 때

실행:

```powershell
powershell -ExecutionPolicy Bypass -File C:\Users\qkekt\Desktop\Harness\tools\setup_harness_subtree.ps1 -RepoPath C:\path\to\repo
```

이 스크립트가 하는 일:

- `harness` remote를 추가합니다.
- Harness의 배포 branch를 fetch 합니다.
- `.harness/manufacturing-agent/`를 subtree 방식으로 연결합니다.

### `pull_harness.ps1`

사용 시점:

- 실제 작업을 시작하기 직전
- 하네스 문서를 최신 상태로 맞추고 싶을 때

실행:

```powershell
powershell -ExecutionPolicy Bypass -File C:\Users\qkekt\Desktop\Harness\tools\pull_harness.ps1 -RepoPath C:\path\to\repo
```

이 스크립트가 하는 일:

- Harness의 최신 `dist/manufacturing-agent` 내용을
- 현재 리포지터리의 `.harness/manufacturing-agent/`에 반영합니다.

### `push_harness.ps1`

사용 시점:

- 실제 작업 중 `.harness/manufacturing-agent/` 문서를 수정했을 때
- 수정한 하네스를 다시 Harness 리포지터리로 보내야 할 때

실행:

```powershell
powershell -ExecutionPolicy Bypass -File C:\Users\qkekt\Desktop\Harness\tools\push_harness.ps1 -RepoPath C:\path\to\repo
```

이 스크립트가 하는 일:

- 현재 리포지터리의 `.harness/manufacturing-agent/` 변경분만 분리합니다.
- Harness 리포지터리의 `inbox/...` branch로 push 합니다.

## 3. 가장 권장하는 작업 순서

### Codex App/Desktop에서 작업할 때

1. 하네스 최신화

```powershell
powershell -ExecutionPolicy Bypass -File C:\Users\qkekt\Desktop\Harness\tools\pull_harness.ps1 -RepoPath C:\path\to\repo
```

2. 아래 두 파일을 먼저 읽습니다.

- `AGENTS.md`
- `.harness/manufacturing-agent/AGENTS.md`

3. 코드 작업을 진행합니다.
4. 하네스 문서도 바뀌었다면 `push_harness.ps1`로 되돌립니다.

```powershell
powershell -ExecutionPolicy Bypass -File C:\Users\qkekt\Desktop\Harness\tools\push_harness.ps1 -RepoPath C:\path\to\repo
```

### Codex Web에서 작업할 때

Codex Web은 보통 현재 리포지터리만 기준으로 작업합니다.
그래서 아래처럼 쓰는 것이 가장 현실적입니다.

1. `.harness/manufacturing-agent/`가 이미 들어 있는 리포지터리에서 작업합니다.
2. Web에서 먼저 아래 파일을 읽게 합니다.

- `AGENTS.md`
- `.harness/manufacturing-agent/AGENTS.md`

3. 코드와 `.harness/` 문서를 같이 수정합니다.
4. 작업이 끝나면 Desktop/App 환경에서 `push_harness.ps1`를 실행해 Harness에 반영합니다.

즉 역할은 이렇게 나누면 됩니다.

- Web: 실제 코드 작업
- Desktop/App: 하네스 배포와 회수

## 4. 자주 쓰는 실제 예시

### 예시 1. compact 리포지터리에서 작업 시작

```powershell
powershell -ExecutionPolicy Bypass -File C:\Users\qkekt\Desktop\Harness\tools\pull_harness.ps1 -RepoPath C:\Users\qkekt\Desktop\compact_manufacturing_service
```

### 예시 2. 제조 에이전트 리포지터리에 처음 연결

```powershell
powershell -ExecutionPolicy Bypass -File C:\Users\qkekt\Desktop\Harness\tools\setup_harness_subtree.ps1 -RepoPath C:\Users\qkekt\Desktop\제조_에이전트_python기반
```

### 예시 3. 작업 후 하네스 변경 반영

```powershell
powershell -ExecutionPolicy Bypass -File C:\Users\qkekt\Desktop\Harness\tools\push_harness.ps1 -RepoPath C:\Users\qkekt\Desktop\compact_manufacturing_service
```

## 5. Codex에 바로 시킬 때 쓸 문장

### App/Desktop용

```text
작업 시작 전에 pull_harness.ps1로 하네스를 최신으로 맞춰줘.
그 다음 AGENTS.md와 .harness/manufacturing-agent/AGENTS.md를 먼저 읽고 작업해줘.
하네스 문서가 바뀌면 .harness 안 문서도 같이 수정해줘.
```

### Web용

```text
이 리포지터리의 AGENTS.md와 .harness/manufacturing-agent/AGENTS.md를 먼저 읽고, 하네스 기준 문서에 맞춰 작업해줘.
작업 중 하네스 구조가 바뀌면 .harness 안 문서도 같이 수정해줘.
작업이 끝나면 Harness에 다시 반영해야 할 변경점을 별도 목록으로 정리해줘.
```

## 6. 문제가 생기면 먼저 볼 것

1. `.harness/manufacturing-agent/`가 현재 리포 안에 있는가
2. `harness` remote가 등록되어 있는가
3. Harness 리포지터리에 `dist/manufacturing-agent` branch가 있는가
4. 실제 변경이 `.harness/` 안에 들어 있는가

## 7. 한 줄 요약

- 처음 연결: `setup_harness_subtree.ps1`
- 작업 전 최신화: `pull_harness.ps1`
- 작업 후 반영: `push_harness.ps1`
