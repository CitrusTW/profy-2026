"""Export only assistant metadata and generated reports, never received source or skills."""
import argparse,hashlib,json
from pathlib import Path

def checkpoint(root):
 root=Path(root);rows=[]
 for p in sorted(root.glob('round-*/ROUND.json')):
  d=json.loads(p.read_text());e=p.parent/'evolution';skill=e/'candidate_SKILL.md'
  out={'round':d['round'],'status':d['status'],'baseline_tokens':d['baseline_tokens'],'evolution':d['evolution'],'candidate_sha256':hashlib.sha256(skill.read_bytes()).hexdigest() if skill.exists() else None,'model_reports':{}}
  for phase in ['development','confirmation']:
   if phase in d:out[phase]=d[phase]
   report=p.parent/phase/'output/report.json'
   if report.exists():out['model_reports'][phase]=json.loads(report.read_text())
  rows.append(out)
 data={'rounds':rows,'model':'gpt-6.1-sol','evolution_provider':'OpenRouter owner key','solver_provider':'Profy owner key','paper_changed':False}
 b=root/'BASELINE.json'
 if b.exists():data['baseline']=json.loads(b.read_text())
 (root/'GIT_CHECKPOINT.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
 return data
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--root',required=True);a=p.parse_args();d=checkpoint(a.root);print(json.dumps({'rounds':len(d['rounds'])}))
