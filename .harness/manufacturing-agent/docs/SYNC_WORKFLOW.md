# Sync Workflow

## 기본 원칙
Codex Web / 클라우드 환경까지 고려하면, 제조 하네스 동기화의 기본 표준은 **Git remote + subtree 방식**입니다.

이유:
- 현재 작업 리포지터리 하나만 체크아웃된 환경에서도 동작합니다.
- 로컬 `C:\...` 경로에 의존하지 않습니다.
- `.harness/manufacturing-agent/`를 실제 리포 안에서 일반 파일처럼 버전 관리할 수 있습니다.
- 변경 내용을 다시 Harness 리포지터리로 되돌리기 쉽습니다.

## 권장 구조

### Harness 리포지터리
- canonical source:
  - `services/manufacturing-agent/`
- 배포용 branch:
  - `dist/manufacturing-agent`

### 실제 구현 리포지터리
- import 위치:
  - `.harness/manufacturing-agent/`

## 왜 subtree인가

### subtree 장점
- 실제 리포 안에 하네스 파일이 일반 파일처럼 들어옵니다.
- Codex Web에서도 현재 리포 기준으로 바로 읽고 수정할 수 있습니다.
- Git 기록과 함께 pull / push가 가능합니다.

### submodule이 덜 적합한 이유
- 초보자에게 더 어렵습니다.
- nested repo 개념을 이해해야 합니다.
- Web 환경에서 추가 인증/체크아웃 이슈가 생길 수 있습니다.

### 로컬 copy script가 덜 적합한 이유
- Desktop에서는 편하지만 Web에서는 로컬 경로가 없습니다.
- Git 이력 연결이 약합니다.

## 1. Harness 쪽 배포 branch 갱신

Harness 리포지터리에서 canonical 폴더를 배포 branch로 export 합니다.

```bash
git subtree split --prefix=services/manufacturing-agent -b dist/manufacturing-agent
git push origin dist/manufacturing-agent --force
```

설명:
- `services/manufacturing-agent/` 폴더 내용만 분리해서
- 실제 리포지터리가 가져갈 branch를 만듭니다.

## 2. 실제 리포지터리에서 pull

최초 1회:

```bash
git remote add harness https://github.com/bongG-moon/Harness.git
git fetch harness
git subtree add --prefix=.harness/manufacturing-agent harness dist/manufacturing-agent --squash
```

이후 업데이트:

```bash
git fetch harness
git subtree pull --prefix=.harness/manufacturing-agent harness dist/manufacturing-agent --squash
```

더 쉬운 방식:

```powershell
powershell -ExecutionPolicy Bypass -File C:\Users\qkekt\Desktop\Harness\tools\setup_harness_subtree.ps1 -RepoPath C:\path\to\repo
powershell -ExecutionPolicy Bypass -File C:\Users\qkekt\Desktop\Harness\tools\pull_harness.ps1 -RepoPath C:\path\to\repo
```

## 3. 실제 리포지터리에서 작업

작업 전:
- 루트 `AGENTS.md` 읽기
- `.harness/manufacturing-agent/AGENTS.md` 읽기
- `.harness/manufacturing-agent/docs/` 기준 문서 확인

작업 중:
- 코드 변경
- 하네스 규칙이 바뀌면 `.harness/manufacturing-agent/` 안 문서도 같이 수정

## 4. 실제 리포지터리에서 Harness로 되돌리기

실제 리포지터리에서 하네스 문서를 수정했다면, 그 변경을 별도 branch로 push 합니다.

```bash
git subtree split --prefix=.harness/manufacturing-agent -b harness-manufacturing-agent-update
git push harness harness-manufacturing-agent-update:refs/heads/inbox/manufacturing-agent-from-<repo-name>
```

예:

```bash
git push harness harness-manufacturing-agent-update:refs/heads/inbox/manufacturing-agent-from-compact
```

더 쉬운 방식:

```powershell
powershell -ExecutionPolicy Bypass -File C:\Users\qkekt\Desktop\Harness\tools\push_harness.ps1 -RepoPath C:\path\to\repo
```

## 5. Harness 리포지터리에서 되받기

Harness 리포지터리에서 inbox branch를 canonical 폴더로 다시 반영합니다.

```bash
git fetch origin
git subtree pull --prefix=services/manufacturing-agent origin inbox/manufacturing-agent-from-compact --squash
git subtree split --prefix=services/manufacturing-agent -b dist/manufacturing-agent
git push origin dist/manufacturing-agent --force
```

## 6. Desktop 보조 방식

Desktop에서는 보조적으로 아래 스크립트를 쓸 수 있습니다.

```bash
python tools/sync_harness.py pull --service manufacturing-agent --repo-path C:\path\to\repo
python tools/sync_harness.py push --service manufacturing-agent --repo-path C:\path\to\repo
```

하지만 이 방식은 **로컬 경로 기반 편의 기능**으로만 보고,
표준 운영 흐름은 subtree 방식으로 유지하는 것을 권장합니다.

## 7. 운영 규칙

- source of truth는 항상 Harness 리포지터리 `main`의 `services/manufacturing-agent/`
- 실제 리포지터리는 `.harness/manufacturing-agent/`를 소비하고 필요 시 수정 가능
- 수정이 생기면 inbox branch -> Harness canonical 폴더 -> dist branch 재생성 순서로 반영
