---
name: xlsx
description: "Create, edit, analyze, and recalculate spreadsheets (.xlsx, .xlsm, .csv, .tsv). Use for formulas, two-condition lookups, financial calculations, data analysis, charts, and edits that must preserve existing workbook formatting."
license: Proprietary. LICENSE.txt has complete terms
---

# Spreadsheet work

## Contract
- Deliver dynamic Excel formulas for derived values, not Python-computed constants. Python may independently check results.
- Preserve existing sheets, formulas, styles, dimensions, and other workbook features unless changes are requested. Existing template conventions override all defaults below. Do not add comments, helper sheets, macros, or other customizations when prohibited.
- Recalculate formulas and deliver no Excel errors (#REF!, #DIV/0!, #VALUE!, #N/A, #NAME?, #NUM!, #NULL!). Do not save a `data_only=True` workbook: that destroys formulas.
- Follow the active execution adapter and file-delivery rules. Attached skill files are resources, not necessarily registered skill IDs. Run task code only inside the supplied environment; do not change adapter files.

## One workflow
1. **Inspect once, narrowly.** Read sheet names, relevant source/target rectangles, actual headers, and representative target number formats/styles. Use explicit `iter_rows(min_row=..., max_row=..., min_col=..., max_col=...)` bounds. Styled empty cells can inflate `max_column` to 16384; never dump or scan the entire worksheet on that basis. Print only needed values, not every styled blank.
2. **Map formulas.** Match actual series keys and year headers, not assumed positions. If instructions name a blank header row but the workbook has populated year headers nearby, use the populated row and briefly disclose the discrepancy. Confirm source units and target number formats before selecting percentage scale.
3. **Write only intended targets.** Use openpyxl for ordinary workbook edits, pandas for analysis/flat CSV/TSV data. Keep calculations as formulas, anchor fill references correctly, and preserve existing formulas. For exact-package preservation use the ZIP procedure below rather than a full workbook round-trip.
4. **Recalculate once** using the appropriate environment route below. For strict templates recalculate a scratch copy, not the deliverable.
5. **Validate in one pass.** Confirm every requested target has a formula and a numeric cached result; scan relevant populated ranges for errors, check representative source matches and independent aggregate arithmetic, and check that non-target cells/styles and sheet names remain unchanged. Fix genuine errors and recalculate only if needed. Report completion and requested results concisely; do not create an extra report.

## Formula patterns and units
- Two-condition retrieval: `=INDEX(Data!$H$21:$M$40,MATCH($D12,Data!$B$21:$B$40,0),MATCH(H$9,Data!$H$4:$M$4,0))`. Coordinates are illustrative: derive ranges from the actual workbook. Both MATCH calls use exact matching; do not assume country order matches source order.
- A ratio in an existing `0.0%` cell remains a fraction. A value labeled "percent" in an existing `0.0` cell uses ratio times 100. Preserve the format rather than changing it to fit your formula.
- GDP-weighted percentage: `=SUMPRODUCT(country_percent_range,gdp_range)/SUM(gdp_range)`. Ranges must contain the same countries in the same order. Independently this equals total net exports divided by total GDP, scaled consistently.
- Summary functions: MIN, MAX, MEDIAN, AVERAGE, PERCENTILE.INC (legacy PERCENTILE is also inclusive). Use a different percentile convention only when requested.
- Check missing keys, source duplicates, zero denominators, row offsets, and currency/scale compatibility where relevant. Do not conceal invalid source data with blanket IFERROR.

## Recalculation routes
**Normal environment:** use the attached script, `python <skill_dir>/recalc.py <file.xlsx> 120`. It recalculates and returns `status`, `total_errors`, `total_formulas`, and optional `error_summary` with counts/locations. Resolve errors rather than treating an unsuccessful JSON result as completion.

**Prepared Profy Linux/PRoot environment from the observed DEV run:** skip the known-broken macro setup and `/usr/bin/libreoffice` wrapper. The script reported `LibreOffice macro not configured properly`; the wrapper looked for nonexistent `/usr/bin/oosplash`. The working macro-free route is:
```bash
mkdir -p work/calculated
/usr/lib/libreoffice/program/soffice -env:UserInstallation=file:///tmp/xlsx_calc_profile --headless --convert-to xlsx --outdir work/calculated work/recalc.xlsx
```
Use distinct input/output paths, an isolated profile, and the task adapter's required command wrapper. A javaldx warning alone did not prevent conversion. Read the output with openpyxl `data_only=True` to verify numeric caches and errors. This direct conversion is authorized for this environment; do not repeat the failed wrapper/macro probes or install dependencies. Do not assume this environment-specific failure applies elsewhere.

## Exact-template ZIP preservation
When formatting/package fidelity is strict, retain an untouched original ZIP. Resolve the target worksheet part through workbook relationships, then modify only target `<c>` elements: preserve attributes/style IDs, remove stale value/type content, and write `<f>` formula text without `=`. Preserve all unrelated package entries. Recalculate a scratch copy. Transfer only the recalculated target `<v>` caches (and appropriate result types if nonnumeric) back into the formula-bearing original package; never replace it with LibreOffice's rewritten package. This retains original formulas, styles, source sheets, and workbook components. In the final validation compare untouched ZIP entries byte-for-byte and the target sheet structure with edited cell contents excluded. Do not add VBA or new workbook components.

## Defaults for new financial models only
Use referenced assumption cells rather than embedded business assumptions. Fonts: inputs blue, formulas black, intra-workbook links green, external links red; key inputs yellow fill. Years ungrouped, currency units in headers, percentages `0.0%`, multiples `0.0x`, negatives in parentheses, zeros as dashes. Document new hardcoded source data with source/date/reference/URL when allowed. These are not instructions to restyle an existing template.

## Data tools
Use pandas `read_excel(..., sheet_name=..., usecols=...)` for analysis, explicit dtypes for identifiers, and parse dates only where appropriate. Do not use `DataFrame.to_excel` to rebuild a formatted existing workbook. Use openpyxl `load_workbook` with formulas retained for edits; `keep_vba=True` is needed when preserving an existing .xlsm, never for adding macros. Keep scripts and printed output minimal.
