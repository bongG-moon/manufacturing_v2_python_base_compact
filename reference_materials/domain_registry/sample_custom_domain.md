# Sample Custom Domain

This file shows how non-developers can add extra domain language in plain text and tables.

## Dataset Keywords

| dataset_key | label | keywords | description |
|---|---|---|---|
| production | 생산 | output qty, 생산 실적, 일일 생산 | 생산 실적 조회 확장 키워드 |
| equipment | 설비 | 장비 상태, line utilization | 설비 조회 확장 키워드 |

## Process Groups

| group | synonyms | values |
|---|---|---|
| DIE_ATTACH | die attach, da line, 다이 접착 | epoxy_dispense, die_place, post_cure |
| TEST | final test, electrical test, 전기 검사 | final_test, burn_in |

## Value Groups

| field | canonical | synonyms | values |
|---|---|---|---|
| mode | LPDDR5X_8533 | lp5x, lpddr5x 8533 | LPDDR5X_8533 |
| tech | FC | flip chip, fc pkg | FC |

## Notes

Use daily fab language first. Add only terms that operators actually use.
