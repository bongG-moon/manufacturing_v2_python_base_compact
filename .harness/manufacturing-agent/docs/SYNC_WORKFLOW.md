# Sync Workflow

## 권장 방식
이 하네스는 `git subtree`보다 **copy/sync script 방식**을 기본 권장합니다.

이유:
- 하네스 리포지터리 한 곳에서 여러 서비스 폴더를 관리하기 쉬움
- 초보자도 이해하기 쉬움
- 특정 서비스 폴더만 실제 리포지터리로 가져오고 다시 반영하기 쉬움

## pull
Harness -> 실제 구현 리포지터리

```bash
python tools/sync_harness.py pull --service manufacturing-agent --repo-path C:\path\to\real_repo
```

## push
실제 구현 리포지터리 -> Harness

```bash
python tools/sync_harness.py push --service manufacturing-agent --repo-path C:\path\to\real_repo
```

## 기본 import 경로
실제 구현 리포지터리 안에서 하네스는 아래 경로로 복사됩니다.

```text
.harness/manufacturing-agent/
```

## 운영 규칙
- 하네스 기준 문서가 바뀌면 먼저 Harness 리포지터리를 업데이트
- 실제 리포지터리에서 수정한 하네스 내용도 push로 되돌려 반영
- 드리프트 방지는 `validate_harness.py`로 점검
