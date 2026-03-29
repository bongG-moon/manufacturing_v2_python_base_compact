# Domain Registry

Add Markdown files in this folder to extend manufacturing domain knowledge without editing Python code.

## Supported sections

- `## Dataset Keywords`
- `## Process Groups`
- `## Value Groups`
- `## Notes`

## Table formats

### Dataset Keywords

| dataset_key | label | keywords | description |
|---|---|---|---|
| production | 생산 | 생산, 생산량, output | 생산 실적 조회 |

### Process Groups

| group | synonyms | values |
|---|---|---|
| DIE_ATTACH | die attach, da, 다이 어태치 | epoxy_dispense, die_place, post_cure |

### Value Groups

| field | canonical | synonyms | values |
|---|---|---|---|
| mode | DDR5_6400 | ddr5 6400, ddr5_6400 | DDR5_6400 |
| tech | WB | wb, wire bond | WB |

## Tips

- Separate multiple keywords with commas.
- Keep one concept per row.
- Add new files instead of editing Python modules.
- Use the app's `Domain Registry` panel to confirm loaded files and warnings.
