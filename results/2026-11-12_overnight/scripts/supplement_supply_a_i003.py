"""I-003 pure-discovery no-skills trace: original verifier only, no resolving."""
import argparse,fcntl,hashlib,json,sys,time
from pathlib import Path
R=Path(__file__).resolve().parent;W=R.parents[1]
sys.path.insert(0,str(R))
from run_breadth_i003 import FixedStudy

def main():
 folder=R/'launch-03/runs/shock-analysis-supply/repeat-1/no-skills';events=[json.loads(x) for x in (folder/'events.jsonl').read_text().splitlines()]
 calls=[x for x in events if x.get('type')=='tool_call.in_progress']
 assert any(x.get('tool_name')=='tool_search' for x in calls)
 assert not any(x.get('tool_name')=='skills_read' or (x.get('tool_name')=='read' and Path((x.get('parameters') or {}).get('file_path','')).name=='SKILL.md') for x in calls)
 assert not (folder/'ORIGINAL_SCORE.json').exists() and not (folder/'grading-only').exists()
 original_hash=hashlib.sha256((folder/'NIGHT_RECORD.json').read_bytes()).hexdigest()
 args=argparse.Namespace(workspace=str(W),out=str(folder.parent),task='shock-analysis-supply',target_skill='xlsx',expected_parent_md_sha='9bdc1fee81f3be9cb34ac49f8890c094a3855d3d0236783d10e0ea6df1515e01',keys_file='/Users/mac/Desktop/obsidian files/Profy related keys.md',allow_paid=True,native_file_runtime=True,hard_timeout_sec=1600,native_package_versions=None,expected_input_hashes=None)
 with (R/'PROFY_SERIAL.lock').open('a') as lock:
  fcntl.flock(lock,fcntl.LOCK_EX);study=FixedStudy(args);began=time.time();score=None;error=None
  try:score=study.grade('shock-analysis-supply',folder)
  except Exception as e:error=type(e).__name__+': '+str(e)
 assert hashlib.sha256((folder/'NIGHT_RECORD.json').read_bytes()).hexdigest()==original_hash
 overlay={'instruction':'I-003 C','task':'shock-analysis-supply','repeat':1,'condition':'no-skills','original_record':str(folder/'NIGHT_RECORD.json'),'original_record_sha256':original_hash,'score':score,'error':error,'supplemental_grading_only':True,'new_solver_calls':0,'environment_limited':True,'elapsed_sec':time.time()-began,'completed_epoch':time.time(),'cost_usd':'unknown','allowed_discovery_no_skill_reads_verified':True}
 with (folder/'SCORE_OVERLAY_I003.json').open('x') as f:json.dump(overlay,f,indent=2)
 with (R/'PROGRESS.md').open('a') as f:f.write('\nI003 supplementary original grading for supply/no-skills: '+json.dumps(overlay,ensure_ascii=False)+'\n')
 print('SUPPLEMENTAL_GRADE_FINISHED',json.dumps(overlay),flush=True)
if __name__=='__main__':main()
