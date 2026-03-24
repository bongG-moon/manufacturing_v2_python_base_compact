# Compact Manufacturing Chat Service

제조 데이터 조회와 `current_data` 기반 pandas 후속 분석에 집중한 경량 서비스입니다.

## 포함 기능

- 생산 / 목표 / 불량 / 설비 / WIP 조회
- 도메인 지식 기반 질문 조건 추출
- `current_data` 기반 pandas 후속 분석
- 파라미터 승계
- 추출 조건, 분석 계획, 생성된 pandas 코드 표시

## 실행 방법

```bash
pip install -r requirements.txt
copy .env.example .env
streamlit run app.py
```

## 초보자용 읽기 순서

1. [BEGINNER_STRUCTURE_GUIDE.md](/C:/Users/qkekt/Desktop/compact_manufacturing_service/BEGINNER_STRUCTURE_GUIDE.md)
2. [CURRENT_DATA_GUIDE.md](/C:/Users/qkekt/Desktop/compact_manufacturing_service/CURRENT_DATA_GUIDE.md)
3. [COLUMN_NAMING_GUIDE.md](/C:/Users/qkekt/Desktop/compact_manufacturing_service/COLUMN_NAMING_GUIDE.md)
4. [app.py](/C:/Users/qkekt/Desktop/compact_manufacturing_service/app.py)
5. [core/agent.py](/C:/Users/qkekt/Desktop/compact_manufacturing_service/core/agent.py)

## 주요 파일

- [app.py](/C:/Users/qkekt/Desktop/compact_manufacturing_service/app.py): Streamlit 채팅 UI
- [core/agent.py](/C:/Users/qkekt/Desktop/compact_manufacturing_service/core/agent.py): 조회 / 후속 분석 라우팅
- [core/parameter_resolver.py](/C:/Users/qkekt/Desktop/compact_manufacturing_service/core/parameter_resolver.py): 질문 조건 추출
- [core/data_tools.py](/C:/Users/qkekt/Desktop/compact_manufacturing_service/core/data_tools.py): 예시 제조 데이터 조회
- [core/data_analysis_engine.py](/C:/Users/qkekt/Desktop/compact_manufacturing_service/core/data_analysis_engine.py): pandas 분석 계획과 코드 생성
- [core/number_format.py](/C:/Users/qkekt/Desktop/compact_manufacturing_service/core/number_format.py): 수량 컬럼 표시 단위 포맷
