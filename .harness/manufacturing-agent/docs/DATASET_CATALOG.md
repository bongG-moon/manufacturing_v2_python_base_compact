# Dataset Catalog

## 기본 데이터셋

### production
- 목적: 실제 생산 수량 조회
- 핵심 컬럼: 날짜, 공정군, MODE, 라인, production

### target
- 목적: 목표 수량 조회
- 핵심 컬럼: 날짜, 공정군, MODE, 라인, target

### defect
- 목적: 검사/불량/불량률 조회
- 핵심 컬럼: 날짜, 공정군, MODE, 라인, inspection_qty, 불량수량, defect_rate, 주요불량유형

## 확장 데이터셋

### equipment
- planned_hours, actual_hours, 가동률

### wip
- 재공수량, avg_wait_minutes, 상태

### yield
- tested_qty, pass_qty, yield_rate

### hold
- lot_id, hold_qty, hold_reason, hold_hours

### scrap
- scrap_qty, scrap_rate, loss_cost_usd

### recipe
- recipe_id, temp_c, pressure_kpa, process_time_sec

### lot_trace
- lot_id, route_step, current_status, elapsed_hours
