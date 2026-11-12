"""Assemble an explicit assistant-only allowlist for the connected GitHub writer."""
import json,re
from pathlib import Path
from checkpoint_network import checkpoint
h=Path(__file__).parent
r=h.parents[2]/'01_任务结果/2026-11-11_skillsbench_full_library'
checkpoint(r/'network-family')
entries=[]
for name in ['README.md','network_family.py','checkpoint_network.py','prepare_git_checkpoint.py','PAID_STOP_SUPERSEDED_20261111.json','full_library_preflight.py']:
 p=h/name;entries.append({'path':'experiments/skillsbench_evolution_20261110/'+name,'mode':'100644','type':'blob','content':p.read_text()})
for name in ['API_AUTHORIZATION.json','SCOPE.json','PLAN.md','OFFLINE_STATUS.md','network-family/GIT_CHECKPOINT.json','network-family/REPORT.md']:
 p=r/name;entries.append({'path':'results/2026-11-11_skillsbench_full_library/'+name,'mode':'100644','type':'blob','content':p.read_text()})
f=r/'network-family/frozen-evaluation/RESULTS.json'
if f.exists():entries.append({'path':'results/2026-11-11_skillsbench_full_library/network-family/frozen-evaluation/RESULTS.json','mode':'100644','type':'blob','content':f.read_text()})
for label in ['no-skills','with-skills','with-CogniLife-skills']:
 f=r/'network-family/frozen-evaluation'/label/'output/report.json'
 if f.exists():entries.append({'path':'results/2026-11-11_skillsbench_full_library/network-family/frozen-evaluation/'+label+'/model_report.json','mode':'100644','type':'blob','content':f.read_text()})
f=r/'full-grading-preflight/SUMMARY.json'
if f.exists():entries.append({'path':'results/2026-11-11_skillsbench_full_library/full-grading-preflight/SUMMARY.json','mode':'100644','type':'blob','content':f.read_text()})
assert not re.search(r'\bsk-(?:pro|or)-[A-Za-z0-9._-]{20,}',json.dumps(entries))
# Stop file already removed in resume commit.
p=Path('/private/tmp/cgl-network-git-entries.json');p.write_text(json.dumps(entries,ensure_ascii=False));print(len(p.read_text()))
