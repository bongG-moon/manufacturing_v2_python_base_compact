# Domain Model

## 핵심 도메인 축
- 공정군(Process Family)
- 제품 / MODE
- 라인
- 생산 / 목표 / 불량 / 설비 / WIP / 수율 / 홀드 / 스크랩 / 레시피 / LOT 이력

## 공정군 예시
- ASSY_PREP
- DIE_ATTACH
- WIRE_BOND
- FLIP_CHIP
- MOLD
- SINGULATION
- TEST
- PACK_OUT

## 제품 / MODE 예시
- DDR5_6400
- DDR5_5600
- LPDDR5X_8533
- UFS3.1
- PMIC
- CIS

## 핵심 해석 원칙
- 질문에서 공정군이 나오면 공정 축 우선 해석
- 제품/모드 관련 표현은 MODE / DEN / TECH / LEAD / MCP_NO와 연결
- 후속 질문은 현재 테이블의 컬럼과 샘플 row를 기준으로 해석
