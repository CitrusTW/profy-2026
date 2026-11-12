---
name: xlsx
description: "Create, edit, analyze, and recalculate spreadsheets (.xlsx, .xlsm, .csv, .tsv), including two-condition lookups, financial formulas, charts, and edits preserving existing formatting."
license: Proprietary. LICENSE.txt has complete terms
---

# Spreadsheet work

## Contract
Use Excel formulas for derived values; Python may independently check them. Preserve existing sheets, formulas, styles, dimensions, and features. Template conventions override defaults. Respect prohibitions on comments, helpers, sheets, VBA, and other customizations. Never save a workbook loaded with `data_only=True`. Deliver recalculated results without Excel errors.

Follow the active execution adapter: supplied skill files are resources, not necessarily registered IDs. Use only the supplied environment and permitted dependencies. In native-owned Profy, use the receipt's mapped paths or task-relative paths; historical PRoot failures do not describe this runtime. Do not inspect restricted material or modify adapters.

## Lean execution
After required setup/resource reading, aim for two task-shell calls when the layout is known: (1) bounded inspection/assertions, formula writing, scratch recalculation; (2) cache transfer and complete validation. Split only when inspection reveals an unresolved layout difference. No separate discovery call is needed merely to print known coordinates.

Inspect only relevant rectangles and representative formats. Always bound `iter_rows`: styled blanks inflated `max_column` to 16384 in DEV. Do not dump every populated row or repeat target styles across columns; print only discrepancies, compact headers, and final validation results. Check exact/unique keys, actual year headers, compatible units, country alignment, and valid denominators before writing. If the specified year row is blank, use the nearby populated header and briefly disclose the discrepancy in the final reply.

### Verified GCC template
Use this mapping only after checking sheet names, keys, headers, and target labels in the current workbook; never substitute remembered numeric answers:
- Sheets `Task`, `Data`. Task years are H9:L9 (2019–2023); row 10 is blank. Source years are Data!H4:M4 (2018–2023), series keys B21:B40, values H21:M40.
- Lookup targets H12:L17, H19:L24, H26:L31: exports, imports, GDP. Match each row's column D key; source country order differs.
- Example H12: `=INDEX(Data!$H$21:$M$40,MATCH($D12,Data!$B$21:$B$40,0),MATCH(H$9,Data!$H$4:$M$4,0))`. Fill with anchored references and exact matches.
- H35: `=(H12-H19)/H26*100`; fill six countries and five years. Existing `0.0` format requires percentage-point values, not fractions. For `0.0%` formats use fractions instead; never restyle to fit arithmetic.
- Rows 42–47: MIN, MAX, MEDIAN, AVERAGE, PERCENTILE(range,0.25), PERCENTILE(range,0.75), over country rows 35:40. Inclusive percentiles unless requested otherwise.
- H50: `=SUMPRODUCT(H35:H40,H26:H31)/SUM(H26:H31)`; fill through L50. Independently check against total net exports / total GDP × 100.
- Exactly 155 new formulas for this layout. Do not alter other cells. Do not hide invalid inputs with blanket IFERROR.

## Recalculate once
Prepared native-owned Profy DEV successfully used this macro-free command directly, with distinct input/output paths:
```bash
mkdir -p work/calculated
/usr/lib/libreoffice/program/soffice -env:UserInstallation=file:///tmp/xlsx_calc_profile --headless --convert-to xlsx --outdir work/calculated work/recalc.xlsx
```
Run inside the required adapter wrapper. A javaldx warning alone did not prevent conversion. Verify output existence and calculated cells; exit status alone is insufficient. Do not repeat successful recalculation for tiny numeric differences.

Outside that prepared environment use the attached `python <skill_dir>/recalc.py <file.xlsx> 120`; inspect JSON `status`, `total_errors`, and `error_summary`. Error JSON is not success.

## Exact-template edits
For strict preservation keep an untouched original ZIP. Resolve the sheet part via `xl/workbook.xml` name → relationship ID → `xl/_rels/workbook.xml.rels` target. Relative targets resolve against `xl/`; absolute targets lose the leading slash. Resolve each workbook's part independently if needed.

Use XML nodes, not regex: DEV regex swallowed adjacent self-closing cells. Materialize ZIP entries before writing the same path; otherwise reads can fail with `BadZipFile: Truncated file header`.
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
1. Map addresses to formula text without `=`. Retain cell attributes/style IDs; remove old children and stale `t`, then set `E.SubElement(cell,TAG+'f').text`. Assert targets exist; insert genuinely absent cells in correct row/column order. Save the formula-bearing deliverable and copy it to `work/recalc.xlsx`.
2. Recalculate only the scratch copy. Parse its results, assert numeric finite target caches, then patch only deliverable target `<v>` nodes using deep copies. Remove old caches first; for nonnumeric results transfer the result type too. Never replace the deliverable with LibreOffice's rewritten package. Retain shared formulas outside targets.

Validate once after cache transfer: exact target formulas, numeric caches, source matches, country arithmetic, summaries, and independent weighted aggregate. Use `math.isclose(actual,expected,rel_tol=1e-12,abs_tol=1e-12)`, not exact float equality. Scan relevant populated rectangles for errors. Compare unrelated ZIP entries byte-for-byte and target-sheet XML structure with edited cell children excluded; this covers non-target values, formulas, formatting, and dimensions without a second full-cell comparison. Finish concisely; no unsolicited report.

## Other work
For ordinary edits use openpyxl with formulas retained; `keep_vba=True` only preserves existing XLSM macros. Use pandas for analysis/CSV/TSV with bounded `usecols`, identifier dtypes, and date parsing; never rebuild a formatted template with `DataFrame.to_excel`. For new financial models only: inputs blue, formulas black, sheet links green, external links red; label units, reference assumption cells, use ungrouped years, `0.0%` percentages, `0.0x` multiples, parentheses for negatives and dashes for zeros. Document new hardcoded sources when allowed. These defaults never justify restyling existing templates.
