# Codex Workflow

이 문서는 **Codex App/Desktop** 과 **Codex Web** 에서 제조 하네스를 어떻게 사용하는지 정리한 문서입니다.

## 1. 가장 권장하는 방식

### Codex App/Desktop
- Harness 리포지터리와 실제 구현 리포지터리를 동시에 다루기 좋습니다.
- subtree pull / push 또는 보조 sync script 실행이 가능합니다.

### Codex Web
- 현재 작업 리포지터리 기준으로 움직이는 경우가 많습니다.
- 그래서 `.harness/manufacturing-agent/`를 읽고 작업하는 방식이 더 현실적입니다.
- 하네스 배포/회수는 `git remote + subtree` 기준으로 생각해야 합니다.

## 2. Codex App/Desktop용 시작 프롬프트

```text
작업 시작 전에 아래 순서로 진행해줘.

1. 현재 리포지터리에 하네스가 최신이 아니면 Harness의 setup_harness_subtree.ps1 또는 pull_harness.ps1 을 사용해서 .harness/manufacturing-agent 를 최신으로 맞춰줘.
2. AGENTS.md 와 .harness/manufacturing-agent/AGENTS.md 읽기
3. 하네스 기준 문서에 맞춰 작업 범위를 정리
4. 실제 코드 수정
5. 코드 변경 때문에 하네스 내용도 바뀌어야 하면 .harness 안 문서도 같이 수정
```

## 3. Codex App/Desktop용 종료 프롬프트

```text
작업이 끝났으면 아래 순서로 진행해줘.

1. 실제 리포의 .harness/manufacturing-agent 변경사항 확인
2. 하네스 변경이 있으면 Harness의 push_harness.ps1 을 사용해서 Harness inbox branch 로 반영해줘
3. 실제 리포와 Harness 리포에 남겨야 할 변경사항을 각각 정리
4. 가능하면 현재 리포는 바로 커밋
```

## 4. Codex Web용 시작 프롬프트

Codex Web에서는 보통 현재 리포 기준으로 이렇게 시키는 게 좋습니다.

```text
이 리포지터리의 AGENTS.md 와 .harness/manufacturing-agent/AGENTS.md 를 먼저 읽고, 하네스 기준 문서에 맞춰 작업해줘.
하네스 구조와 실제 코드가 어긋나면 .harness 안 문서도 같이 수정해줘.
작업이 끝나면 하네스에 다시 반영해야 할 변경점을 별도 목록으로 정리하고, 필요하면 push_harness.ps1 사용 지침까지 제안해줘.
```

## 5. Codex Web 종료 후 처리

Web 작업이 끝나면 나중에 App/Desktop 또는 동일 리포에서 git remote 접근 가능한 환경에서 아래처럼 반영하면 됩니다.

```bash
powershell -ExecutionPolicy Bypass -File C:\Users\qkekt\Desktop\Harness\tools\push_harness.ps1 -RepoPath C:\path\to\repo
```

## 6. 제일 실용적인 운영 규칙

- App/Desktop: Harness canonical 관리 + subtree 배포/회수 담당
- Web: 실제 구현 리포에서 `.harness` 기준으로 빠른 작업 담당
- 최종 기준은 항상 Harness 리포지터리 `services/manufacturing-agent/`

## 7. 아주 짧은 운영 문장

작업 전에:
- `setup/pull 스크립트 실행 -> AGENTS 읽기 -> 코드 작업`

작업 후:
- `하네스 변경 있으면 push 스크립트 실행 -> Harness 반영`
