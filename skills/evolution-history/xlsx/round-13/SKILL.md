---
name: xlsx
description: "Create, edit, analyze, and recalculate spreadsheets (.xlsx, .xlsm, .csv, .tsv), including two-condition lookups, financial formulas, charts, and edits preserving existing formatting."
license: Proprietary. LICENSE.txt has complete terms
---

# Spreadsheet work

## Contract
Use Excel formulas for derived values; Python may check them independently. Preserve existing sheets, formulas, styles, dimensions, and features. Template conventions override defaults. Honor prohibitions on comments, helpers, sheets, VBA, and customizations. Never save a workbook loaded with `data_only=True`; deliver recalculated, error-free results.
Follow the active adapter and permitted dependencies. Attached skills are resources, not necessarily registered IDs. Native-owned Profy uses receipt-mapped or task-relative paths, not historical PRoot paths. Do not inspect restricted material or modify adapters.

## Execution: two task-shell calls for the verified layout
After required setup/resource reading:
1. In ONE shell call, load the workbook, assert the mapping below BEFORE mutation, write formulas, retain the original ZIP, and recalculate a scratch copy. Inspection means assertions in this call, NOT a separate row dump followed by the same assertions. Print only a compact discrepancy/status. If an assertion fails, stop before writing and inspect only that discrepancy; do not force a mismatched template.
2. Transfer target caches and validate once as below; finish concisely, with no unsolicited report.
Always bound `iter_rows`; styled blanks inflated `max_column` to 16384 in DEV. Do not enumerate all cells, print source tables, or repeat target styles across columns. Representative formats plus key/header/unit/alignment checks suffice before editing.

## Verified GCC template
Check the current workbook; never reuse remembered numeric answers.
- Sheets: `Task`, `Data`. Task years H9:L9 are 2019–2023; row 10 is blank. Source years Data!H4:M4 are 2018–2023; keys B21:B40; values H21:M40. Existing header formulas may be read from original numeric caches. Briefly disclose row 9 versus row 10 in the final reply.
- Lookup targets H12:L17, H19:L24, H26:L31 are exports, imports, GDP. Assert target labels, unique exact column D keys in the source, compatible units, country alignment across the three blocks, and positive GDP denominators. Source country order differs.
- H12: `=INDEX(Data!$H$21:$M$40,MATCH($D12,Data!$B$21:$B$40,0),MATCH(H$9,Data!$H$4:$M$4,0))`. Fill the three blocks with anchored references and exact matches.
- H35: `=(H12-H19)/H26*100`; fill H35:L40. Percent-labeled cells formatted `0.0` require percentage-point values; `0.0%` requires fractions. Preserve the format.
- Rows 42–47: MIN, MAX, MEDIAN, AVERAGE, PERCENTILE(range,0.25), PERCENTILE(range,0.75), over country rows 35:40. Use inclusive percentiles unless specified otherwise.
- H50: `=SUMPRODUCT(H35:H40,H26:H31)/SUM(H26:H31)`; fill through L50. Check independently against total net exports / total GDP × 100.
Exactly 155 formulas for this layout; alter no other cells. Do not mask invalid inputs with blanket IFERROR.

## Recalculate once
Native-owned Profy DEV succeeded with this macro-free command; use distinct input/output files inside the adapter wrapper:
```bash
mkdir -p work/calculated
/usr/lib/libreoffice/program/soffice -env:UserInstallation=file:///tmp/xlsx_calc_profile --headless --convert-to xlsx --outdir work/calculated work/recalc.xlsx
```
A javaldx warning alone did not prevent conversion. Check output existence and calculated values, not just exit status. Do not repeat successful recalculation for binary rounding differences.
Outside this prepared environment use attached `python <skill_dir>/recalc.py <file.xlsx> 120`; inspect JSON `status`, `total_errors`, `error_summary`. Error JSON is not success.

## Exact-template edits
Keep an untouched original ZIP. Resolve each workbook's sheet part through `xl/workbook.xml` sheet name → relationship ID → `xl/_rels/workbook.xml.rels` target. Relative targets resolve against `xl/`; absolute targets lose the leading slash.
Use XML nodes, not regex: DEV regex swallowed adjacent self-closing cells. Materialize entries before writing the same ZIP; otherwise reads can fail with `BadZipFile: Truncated file header`.
```python
from zipfile import ZipFile
from lxml import etree as E
NS = {'s': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
TAG = '{' + NS['s'] + '}'
def patch(src, dst, part, update):
    with ZipFile(src) as z:
        entries = [(i, z.read(i.filename)) for i in z.infolist()]
    root = E.fromstring(next(b for i, b in entries if i.filename == part))
    update({c.get('r'): c for c in root.findall('.//s:c', NS)})
    with ZipFile(dst, 'w') as z:
        for i, b in entries:
            z.writestr(i, E.tostring(root) if i.filename == part else b)
```
First pass: map target addresses to formula text without `=`. Retain attributes/style IDs, remove old children and stale `t`, and set `E.SubElement(cell,TAG+'f').text`. Assert targets exist; insert genuinely absent cells in correct row/column order. Save the formula-bearing deliverable and copy to `work/recalc.xlsx`.
Second pass: read scratch results; assert numeric finite target caches. Patch ONLY target `<v>` nodes into the deliverable using deep copies, removing old caches first. For nonnumeric results also transfer result type. Never replace the deliverable with LibreOffice's rewritten package; retain shared formulas outside targets.

Validate once: exact formulas and numeric caches, source matches, country arithmetic, summaries, independent weighted aggregate, and errors in relevant populated rectangles. Use `math.isclose(actual,expected,rel_tol=1e-12,abs_tol=1e-12)`, not exact float equality. Compare unrelated ZIP entries byte-for-byte and target-sheet XML structure with edited cell children excluded. This covers non-target content, formatting, and dimensions; do not add a second exhaustive cell/style comparison.

## Other work
Use openpyxl with formulas retained for ordinary edits; `keep_vba=True` only preserves existing XLSM macros. Use pandas for analysis/CSV/TSV with bounded `usecols`, identifier dtypes, and date parsing; do not rebuild formatted templates with `DataFrame.to_excel`.
New financial models only: inputs blue, formulas black, sheet links green, external links red; label units, reference assumption cells, use ungrouped years, `0.0%` percentages, `0.0x` multiples, parentheses for negatives and dashes for zeros. Document hardcoded sources when allowed. Never restyle an existing template to impose these defaults.
