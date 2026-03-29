# AGENTS.md

이 리포지터리는 제조 에이전트의 compact 구현 저장소입니다.

먼저 읽을 파일:

- [하네스 AGENTS](C:\Users\qkekt\Desktop\compact_manufacturing_service\.harness\manufacturing-agent\AGENTS.md)
- [하네스 README](C:\Users\qkekt\Desktop\compact_manufacturing_service\.harness\manufacturing-agent\README.md)
- [스크립트 빠른 안내](C:\Users\qkekt\Desktop\compact_manufacturing_service\.harness\manufacturing-agent\docs\HARNESS_SCRIPT_QUICKSTART.md)

이 리포지터리의 역할:

- compact 버전의 실제 기능을 구현합니다.
- 초보자도 읽기 쉬운 구조와 최소 기능 구성을 유지합니다.
- 하네스 기준 구조를 참고해 구현 방향을 맞춥니다.

작업 시작 전:

```powershell
powershell -ExecutionPolicy Bypass -File C:\Users\qkekt\Desktop\Harness\tools\pull_harness.ps1 -RepoPath C:\Users\qkekt\Desktop\compact_manufacturing_service
```

작업 중 원칙:

1. 먼저 `.harness/manufacturing-agent/` 문서를 읽습니다.
2. compact 코드 변경을 진행합니다.
3. 구조 규칙이나 작업 방식이 바뀌면 `.harness/` 문서도 같이 수정합니다.

작업이 끝난 뒤 하네스 문서도 바뀌었다면:

```powershell
powershell -ExecutionPolicy Bypass -File C:\Users\qkekt\Desktop\Harness\tools\push_harness.ps1 -RepoPath C:\Users\qkekt\Desktop\compact_manufacturing_service
```

중요한 주의:

- compact 버전도 도메인 지식과 질문/분석 규칙은 하네스 기준 문서를 따릅니다.
- 구현을 단순하게 유지하더라도, 하네스 기준과 어긋나는 변경은 문서에 같이 반영해야 합니다.
