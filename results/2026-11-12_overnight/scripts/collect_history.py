import csv,hashlib,json
from pathlib import Path
R=Path(__file__).resolve().parent;W=R.parents[1];B=W/'01_任务结果'
def load(p):return json.loads(p.read_text())
rows=[];sources={}
def retain(p):sources[str(p.relative_to(W))]=hashlib.sha256(p.read_bytes()).hexdigest();return load(p)
def add(task,status,rr):
 assert len(rr)==3
 rows.append({'task':task,'status_en':status,'checks':[str(x['score']['passed'])+'/'+str(x['score']['tests']) for x in rr],'tokens':[(x.get('tokens') or {}).get('total_tokens') for x in rr],'strict':[x['score'].get('strict') for x in rr]})
labels=['no-skills','with-skills','with-CogniLife-skills']
p=B/'2026-11-10_skillsbench_evolution/run-04-up-to30/full-compatible-two/FULL_TWO_RESULTS.json';j=retain(p)
for t in ['threejs-to-obj','threejs-structure-parser']:add(t,'Development/selection',[next(x for x in j['rows'] if x['task']==t and x['label']==l) for l in labels])
p=B/'2026-11-11_skillsbench_full_library/network-family/frozen-evaluation';add('energy-market-pricing','Prior new-task test',[retain(p/l/'result.json') for l in labels])
p=B/'2026-11-11_skillsbench_cloud_serial/mesh-evolution/frozen-three-arm/RESULTS.json';j=retain(p);add('3d-scan-calc','Development/selection',[j[k] for k in ['no_skills','with_skills','evolved_development']])
p=B/'2026-11-11_skillsbench_cloud_serial/xlsx-family/native-proot-v2';rr=[retain(p/'development'/l/'result.json') for l in labels[:2]];rr.append(retain(p/'evolution/round-11/development/with-CogniLife-skills/result.json'));add('weighted-gdp-calc','Development/selection',rr)
p=B/'2026-11-11_skillsbench_cloud_serial/xlsx-family/heldout-native-v2/protein-expression-analysis/network-retry-1';add('protein-expression-analysis','Prior test; later selection',[retain(p/l/'result.json') for l in labels])
p=B/'2026-11-10_skillsbench_evolution/run-01/RESULTS.json';j=retain(p)
print('first pilot validation keys',list(j['validation']))
first={'source':'01_任务结果/2026-11-10_skillsbench_evolution/run-01/RESULTS.json','validation':j['validation'],'evolution':j['evolution']}
with (R/'history_results.json').open('x') as f:json.dump({'six_tasks':rows,'first_pilot':first,'source_sha256':sources},f,indent=2,ensure_ascii=False)
with (R/'history_six_tasks.csv').open('x',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows([{k:json.dumps(v) if isinstance(v,list) else v for k,v in r.items()} for r in rows])
print([(r['task'],r['checks']) for r in rows])
