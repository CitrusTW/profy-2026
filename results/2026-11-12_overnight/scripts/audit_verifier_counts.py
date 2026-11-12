"""Keep original receipt and parse final pytest summary, never alter either."""
import hashlib,json,re
from pathlib import Path
R=Path(__file__).resolve().parent

def main():
 folders=[p.parent for p in (R/'launch-03/runs').glob('*/repeat-*/*/NIGHT_RECORD.json')]
 folders += [p.parent for p in (R/'historical_inputs').glob('*/*/result.json')]
 for folder in folders:
  target=folder/'PYTEST_COUNTS_AUDIT.json'
  if target.exists():continue
  logs=list((folder/'grading-only/output').glob('original_verifier_stdout.log'))
  if not logs:continue
  log=logs[0];raw=log.read_bytes();text=re.sub(r'\x1b\[[0-9;]*m','',raw.decode(errors='replace'))
  summaries=[]
  for line in text.splitlines():
   if not line.startswith('='):continue
   counts={k:int(v) for v,k in re.findall(r'(\d+) (passed|failed|skipped|error)(?=[, =])',line)}
   if counts:summaries.append((line,counts))
  if not summaries:continue
  receipt=folder/'ORIGINAL_SCORE.json'
  if receipt.exists():original=json.loads(receipt.read_text())
  elif (folder/'result.json').exists():original=json.loads((folder/'result.json').read_text()).get('score') or {}
  else:continue
  line,counts=summaries[-1];observed={k:counts.get(k,0) for k in ['passed','failed','skipped','error']}
  old={k:original.get(k) for k in ['tests','passed','failed','skipped']}
  mismatch=any(old.get(k) is not None and old[k]!=observed[k] for k in ['passed','failed','skipped'])
  result={'receipt_counts':old,'pytest_terminal_counts':observed,'pytest_terminal_total':sum(observed.values()),'counts_disagree':mismatch,'terminal_summary':line,'stdout_sha256':hashlib.sha256(raw).hexdigest(),'original_reward_unchanged':original.get('original_reward'),'no_rerun':True,'interpretation':'Raw receipt and raw pytest terminal counts are distinct. This sidecar does not rewrite the verifier or its reward.'}
  with target.open('x') as f:json.dump(result,f,indent=2)
  if mismatch:print('COUNT_DISAGREEMENT',folder.relative_to(R),json.dumps(old),json.dumps(observed),flush=True)
if __name__=='__main__':main()
