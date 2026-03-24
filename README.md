# Compact Manufacturing Chat Service

제조 데이터 조회와 `current_data` 기반 pandas 후속 분석에 집중한 경량 서비스입니다.

포함 기능:
- 생산 / 목표 / 불량 / 설비 / WIP 조회
- 도메인 지식 기반 질문 조건 추출
- `current_data` 기반 pandas 후속 분석
- 파라미터 승계
- 추출 조건, 분석 계획, 생성된 pandas 코드 표시

실행:

```bash
pip install -r requirements.txt
streamlit run app.py
```

환경 변수:

```bash
copy .env.example .env
```
