"""Small three-condition skill-refinement pilot. Written for this study.

External expert/benchmark files remain external. Never commits or uploads gold.
New research implementation inspired by paper section 3.4, not native Profy evolution.
"""
from __future__ import annotations
import argparse
import ast
import base64
import collections
import concurrent.futures
import datetime as dt
import gzip
import hashlib
import io
import json
import mimetypes
import os
import re
import shutil
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

MODEL = 'gpt-6.1-sol'
WRITER = 'openai/gpt-4.1-mini'
DEV = 'pdf-excel-diff'
TEST = 'invoice-fraud-detection'
SKILL = 'skills/expense-record-reconciliation/SKILL.md'
SKILL_HEADER = '---\nname: expense-record-reconciliation\ndescription: Reconcile source records and preserve evidence.\n---\n'
MAX_WRITER_REQUESTS = 2
CONDITIONS = ['no-skills', 'with-skills', 'with-skills-cognilife-method']
INPUTS = {DEV:['employees_backup.pdf','employees_current.xlsx'],
          TEST:['invoices.pdf','vendors.xlsx','purchase_orders.csv']}
OUTPUTS = {DEV:'diff_report.json',TEST:'fraud_report.json'}

def sha(data):
    return hashlib.sha256(data).hexdigest()

def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2))

def decode_file(texts):
    text = '\n'.join(texts)
    hashes = re.findall(r'PILOT_SHA256:\s*([0-9a-f]{64})', text)
    sizes = re.findall(r'PILOT_BYTES:\s*(\d+)', text)
    parts = {}
    total = None
    for match in re.finditer(r'PILOT_PART_(\d+)_OF_(\d+):\s*([A-Za-z0-9+/=]+)', text):
        index, count = int(match[1]), int(match[2])
        if not 1 <= index <= count <= 256:
            raise ValueError('Invalid output part count')
        if index in parts and parts[index] != match[3]:
            raise ValueError('Conflicting output part')
        parts[index] = match[3]
        total = count
    if not hashes or not sizes or not total or len(parts) != total:
        return None
    encoded = ''.join(parts[i] for i in range(1,total+1))
    compressed = base64.b64decode(encoded, validate=True)
    with gzip.GzipFile(fileobj=io.BytesIO(compressed)) as stream:
        raw = stream.read(2_000_001)
    if len(raw) > 2_000_000 or len(raw) != int(sizes[-1]) or sha(raw) != hashes[-1]:
        raise ValueError('Output transport hash/size mismatch')
    json.loads(raw)
    return raw

def strings(value):
    if isinstance(value,str):
        yield value
    elif isinstance(value,dict):
        for v in value.values():
            yield from strings(v)
    elif isinstance(value,list):
        for v in value:
            yield from strings(v)

def exported_file(events):
    # A read of prior experience may contain an older file-export packet.
    # Only bash export results from this attempt carry the current file bytes.
    texts = []
    final_text = []
    for event in events:
        if event.get('type') == 'tool_call.result' and event.get('tool_name') == 'bash':
            texts.extend(strings(event.get('result')))
        if event.get('type') == 'output.text.delta':
            final_text.append(event.get('delta') or event.get('content') or '')
    raw = decode_file(texts)
    stated = re.findall(r'SHA256[^a-f0-9]{0,12}([a-f0-9]{64})', ''.join(final_text), re.I)
    if raw is not None and stated and sha(raw) != stated[-1].lower():
        raise ValueError('Export differs from final stated output hash')
    return raw

def tool_calls(events):
    found = {}
    for event in events:
        if event.get('type') not in ['tool_call.created','tool_call.in_progress']:
            continue
        key = event.get('tool_call_id')
        if key and event.get('tool_name'):
            found.setdefault(key,event['tool_name'])
    return list(found.values())

def proposal_gate(before, after, old_text, new_text):
    quality = before['tests'] > 0 and after['tests'] == before['tests'] and after['passed'] >= before['passed']
    efficiency = len(new_text.encode()) < len(old_text.encode())
    return {'accepted':quality and efficiency, 'quality_nondegrading':quality,
            'skill_footprint_improved':efficiency, 'before_utf8_bytes':len(old_text.encode()),
            'after_utf8_bytes':len(new_text.encode()),
            'efficiency_scope':'skill document UTF-8 footprint; not a guarantee of runtime or billed-token improvement'}

def public_writer_evidence(score, experience, max_bytes):
    """Allowlisted public task plus numeric metrics; never expert text or tool outputs."""
    return {'public_development_task':experience['public_task'],
            'development_metrics':{k:score[k] for k in ['tests','passed','failed','strict']},
            'execution_metrics':{'completed':bool(experience['run_completed']),
                                 'elapsed_sec':experience['elapsed_sec'],
                                 'tool_call_count':len(experience['tools'])},
            'max_body_utf8_bytes':max_bytes}

def shared_experience(public_task, result):
    # Raw read results can contain private skills and old file-export packets.
    return {'task':DEV,'public_task':public_task,'run_completed':result['completed'],
            'error':result['error'],'elapsed_sec':result['elapsed_sec'],
            'tools':result['tool_names'],'output_received':result['output_received']}

def candidate_document(body, old_text):
    if not isinstance(body,str) or not body.strip():
        raise ValueError('Candidate body must be nonempty Markdown')
    content = SKILL_HEADER + body
    if len(content.encode()) >= len(old_text.encode()):
        raise ValueError(f'Candidate is {len(content.encode())} UTF-8 bytes; must be below {len(old_text.encode())}. Rewrite more concisely; do not truncate steps.')
    if re.search(r'EMP\d{3,}|PO-\d{3,}|Vendor\s+\d+|/verifier|ground_truth|expected_output',content,re.I):
        raise ValueError('Candidate contains task-specific IDs or grading references')
    return content

def skill_read_evidence(events, expected_text):
    matches = []
    observed_hashes = []
    for event in events:
        if event.get('type') != 'tool_call.result' or event.get('is_error'):
            continue
        result = event.get('result') or {}
        if event.get('tool_name') == 'read' and isinstance(result,dict):
            path = result.get('file_path','')
            content = '\n'.join(strings(result.get('content')))
            if path.endswith('/expert/'+SKILL) and expected_text.strip() in content:
                matches.append(event.get('tool_call_id'))
        if event.get('tool_name') == 'bash':
            observed_hashes.extend(re.findall(r'PILOT_ACTIVE_SKILL_SHA256:\s*([a-f0-9]{64})','\n'.join(strings(result))))
    expected_hash = sha(expected_text.encode())
    return {'expected_sha256':expected_hash,'native_read_call_ids':matches,
            'native_read_matches_expected':bool(matches),
            'bash_hash_matches_expected':expected_hash in observed_hashes,
            'verified':bool(matches) and expected_hash in observed_hashes}

class Pilot:
    def __init__(self, args):
        self.root, self.out = Path(args.workspace).resolve(), Path(args.out).resolve()
        self.bench = self.root/'04_项目数据与代码/skillsbench/tasks'
        self.expert = self.root/'04_项目数据与代码/experts/01-财务报销管家'
        self.dev_inputs = Path(args.dev_inputs).resolve()
        self.lock = threading.Lock()
        self.reservations = 0
        secret = Path(args.keys_file).read_text()
        self.key = next(k for k in re.findall(r'\bsk-[A-Za-z0-9._-]+', secret) if k.startswith('sk-pro-'))
        self.router_key = next(k for k in re.findall(r'\bsk-[A-Za-z0-9._-]+', secret) if k.startswith('sk-or-'))
        self.expert_id = re.search(r'expert identifier\s*:\s*([A-Za-z0-9_-]+)', secret, re.I)[1]
        self.out.mkdir(parents=True, exist_ok=True)

    def scrub(self, value):
        if isinstance(value,str):
            value = value.replace(self.key,'[REDACTED]').replace(self.router_key,'[REDACTED]')
            return re.sub(r'https://[^\s<>"\']+\?[^\s<>"\']+', '[SIGNED_URL_REDACTED]', value)
        if isinstance(value,list):
            return [self.scrub(v) for v in value]
        if isinstance(value,dict):
            return {k:self.scrub(v) for k,v in value.items()}
        return value

    def api(self, path, body, end_user):
        req = urllib.request.Request('https://api.profy.cn'+path, data=json.dumps(body).encode(),
            headers={'Authorization':'Bearer '+self.key, 'Content-Type':'application/json',
                     'X-Profy-End-User-Id':end_user}, method='POST')
        with urllib.request.urlopen(req, timeout=60) as response:
            obj = json.load(response)
        if obj.get('code',0) != 0:
            raise RuntimeError('Profy request rejected: '+str(obj.get('code')))
        return obj.get('data',obj)

    def upload(self, path, end_user):
        raw = path.read_bytes()
        mime = mimetypes.guess_type(path.name)[0] or 'application/octet-stream'
        ticket = self.api('/v1/files/upload-url', {'filename':path.name,'content_type':mime,'size':len(raw)},end_user)
        if urllib.parse.urlsplit(ticket['upload_url']).scheme != 'https':
            raise ValueError('Non-HTTPS storage destination')
        req = urllib.request.Request(ticket['upload_url'],data=raw,headers={'Content-Type':mime},method='PUT')
        with urllib.request.urlopen(req, timeout=90) as response:
            assert response.status < 300
        result = self.api('/v1/files',{'file_key':ticket['file_key'],'filename':path.name,'content_type':mime},end_user)
        return {'filename':path.name,'file_id':result['id'],'sha256':sha(raw),'bytes':len(raw)}

    def package(self, folder, candidate=None):
        target = folder/'expert.zip'
        with zipfile.ZipFile(target,'w',compression=zipfile.ZIP_DEFLATED) as archive:
            for source in sorted(self.expert.rglob('*')):
                if not source.is_file() or source.name.startswith('.'):
                    continue
                rel = source.relative_to(self.expert).as_posix()
                assert '..' not in Path(rel).parts
                raw = candidate.encode() if rel == SKILL and candidate is not None else source.read_bytes()
                archive.writestr('expert/'+rel,raw)
        return target

    def solve(self, label, task, candidate=None, experience=None, use_expert=True):
        folder = self.out/label
        folder.mkdir(exist_ok=True)
        if (folder/'started.json').exists():
            raise RuntimeError('Attempt already reserved; do not launch twice: '+label)
        with self.lock:
            self.reservations += 1
            assert self.reservations <= 5, 'At most five Profy model invocations'
        save(folder/'started.json',{'label':label,'task':task,'model':MODEL,'utc':dt.datetime.now(dt.timezone.utc).isoformat()})
        end_user = 'cgl-three-arm-'+self.out.name+'-'+label
        src = self.dev_inputs if task == DEV else self.bench/task/'environment'
        files = [src/name for name in INPUTS[task]]
        if use_expert:
            files.append(self.package(folder,candidate))
        if experience is not None:
            exp = folder/'development_experience.json'
            save(exp,experience)
            files.append(exp)
        receipts = [self.upload(p,end_user) for p in files]
        save(folder/'uploads.json',receipts)
        sid = self.api('/v1/sessions',{'agent':self.expert_id,'title':'Three-arm '+label},end_user)['id']
        save(folder/'session.json',{'id':sid})
        instruction = (self.bench/task/'task.md').read_text().split('---',2)[2].strip()
        setup = ('Unzip expert.zip into the current session directory. Read expert/IDENTITY.md, SOUL.md, AGENTS.md, USER.md and MEMORY.md, and the relevant expert/skills instructions. '
                 'Before solving, use the read tool to read expert/skills/expense-record-reconciliation/SKILL.md in full. Then use bash to compute SHA256 of that exact file and print PILOT_ACTIVE_SKILL_SHA256:<computed 64 hex>. Do not retype or guess its hash. Apply that procedure while obeying the current original task contract. '
                 'Follow the original task output contract over default expert formats. '
                 if use_expert else 'No project expert package is supplied. Use the original task and ordinary file/code tools. Do not discover or activate any project/expert skills. ')
        notes = '''\nExecution instructions common to all conditions:
Use only this session's attached files and supplied development experience, if present. No web, product Memory, external expert skills, other sessions, delegation or persistent expert modifications. read/bash are allowed. Paths /root/ in the original task mean the current session directory. Preserve original inputs. Do not ask for missing facts; return the best supported output. You may write analysis code from the public task, but do not search for benchmark tests, gold or oracle. Use at most 32 tool calls.
Write the original requested JSON output file. Return its exact bytes through bash output: compute SHA256, gzip.compress the bytes and base64 encode. Print PILOT_SHA256:<64 hex> and PILOT_BYTES:<original byte count>. Split base64 into at most 4096 characters per part, printing one part per bash result as PILOT_PART_1_OF_N:<base64>, and so on. Do not retype or summarize these bytes. Final text only states the output file and hash.
'''
        body = {'agent':{'id':self.expert_id,'model':MODEL,'tools':[]},'rules':[],
                'environment':{'type':'profy_hosted','skills':[]},'expert_partner':[],
                'input':instruction+'\n'+setup+notes,'stream':True,'session_id':sid,
                'attachment_file_ids':[r['file_id'] for r in receipts]}
        save(folder/'request.json',body)
        stopped = threading.Event()
        def interrupt(reason):
            if stopped.is_set():
                return
            stopped.set()
            try:
                save(folder/'interrupt.json',self.scrub(self.api('/v1/sessions/'+sid+'/interrupt',{},end_user)))
            except Exception as exc:
                save(folder/'interrupt_error.json',{'error_type':type(exc).__name__})
        timer = threading.Timer(900,lambda:interrupt('time_limit'))
        timer.daemon = True
        timer.start()
        start = time.monotonic()
        counts = collections.Counter()
        observed_tools = {}
        text, usage, tool_names = [], [], []
        completed, error = False, None
        print('START',label,task,flush=True)
        try:
            req = urllib.request.Request('https://api.profy.cn/v1/agents/run',data=json.dumps(body).encode(),
                headers={'Authorization':'Bearer '+self.key,'Content-Type':'application/json',
                         'X-Profy-End-User-Id':end_user,'Accept':'text/event-stream'},method='POST')
            with urllib.request.urlopen(req,timeout=120) as response, (folder/'events.jsonl').open('w') as log:
                for raw in response:
                    if stopped.is_set():
                        break
                    line = raw.decode().strip()
                    if line.startswith('data:') and line[5:].strip() == '[DONE]':
                        break
                    if not line.startswith('data:'):
                        continue
                    event = json.loads(line[5:])
                    kind = event.get('type','unknown')
                    counts[kind] += 1
                    log.write(json.dumps(self.scrub(event),ensure_ascii=False)+'\n')
                    log.flush()
                    if kind in ['tool_call.result','run.completed','output.text.delta']:
                        text.extend(strings(event))
                    if kind == 'usage.token':
                        usage.append(self.scrub(event))
                    if kind in ['tool_call.created','tool_call.in_progress'] and event.get('tool_call_id') and event.get('tool_name'):
                        call_id = event['tool_call_id']
                        if call_id not in observed_tools:
                            observed_tools[call_id] = event['tool_name']
                            tool_names.append(event['tool_name'])
                            print('TOOL',label,tool_names[-1],flush=True)
                    if len(observed_tools) > 32 or counts['run.in_progress'] > 16:
                        error = 'call_or_turn_budget'
                        interrupt(error)
                    if kind in ['run.failed','request_user_input']:
                        error = kind
                        interrupt(error)
                    if kind == 'run.completed':
                        completed = True
        except Exception as exc:
            error = type(exc).__name__
            interrupt(error)
        finally:
            timer.cancel()
        logged_events = [json.loads(line) for line in (folder/'events.jsonl').read_text().splitlines()] if (folder/'events.jsonl').exists() else []
        try:
            output = exported_file(logged_events)
        except ValueError as exc:
            output = None
            error = 'output_transport_'+type(exc).__name__
        if output is not None:
            (folder/OUTPUTS[task]).write_bytes(output)
        result = {'label':label,'task':task,'completed':completed,'error':error,
                  'elapsed_sec':round(time.monotonic()-start,3),'output_received':output is not None,
                  'output_sha256':sha(output) if output else None,'events':dict(counts),'tool_names':tool_names,
                  'platform_skill_tool_observed':any('skill' in n.lower() for n in tool_names),
                  'money_usd':None,'money_note':'No auditable Profy currency bill obtained; do not treat missing as zero'}
        if use_expert:
            result['active_skill_evidence'] = skill_read_evidence(logged_events,candidate if candidate is not None else (self.expert/SKILL).read_text())
        save(folder/'usage.json',usage)
        save(folder/'run_summary.json',result)
        result['score'] = self.grade(folder,task)
        save(folder/'result.json',result)
        print('DONE',label,json.dumps({'elapsed_sec':result['elapsed_sec'],'score':result['score']}),flush=True)
        return result

    def grade(self, folder, task):
        if not (folder/OUTPUTS[task]).exists():
            return {'tests':0,'passed':0,'failed':0,'strict':0,'status':'missing_output'}
        source = self.bench/task/'verifier'
        stage = folder/'scoring_only'
        stage.mkdir(exist_ok=True)
        for file in source.glob('*.json'):
            shutil.copy2(file,stage/file.name)
        code = source/'test_outputs.py'
        tree = ast.parse(code.read_text())
        paths = {'/root/'+OUTPUTS[task]:str(folder/OUTPUTS[task]),
                 '/verifier/expected_output.json':str(stage/'expected_output.json')}
        original_asserts = sum(isinstance(n,ast.Assert) for n in ast.walk(tree))
        class BindPaths(ast.NodeTransformer):
            def visit_Constant(self,node):
                return ast.copy_location(ast.Constant(paths[node.value]),node) if isinstance(node.value,str) and node.value in paths else node
        tree = BindPaths().visit(tree)
        assert original_asserts == sum(isinstance(n,ast.Assert) for n in ast.walk(tree))
        (stage/'test_outputs.py').write_text(ast.unparse(tree)+'\n')
        bootstrap = "import sys;sys.path.extend(['/private/tmp/cognilife-e2e-env/lib/python3.12/site-packages','/private/tmp/cgl-expert-preflight-deps']);import pytest;raise SystemExit(pytest.main(sys.argv[1:]))"
        run = subprocess.run([sys.executable,'-c',bootstrap,str(stage/'test_outputs.py'),'-q','-p','no:cacheprovider',
                              '--junitxml='+str(stage/'junit.xml')],capture_output=True,text=True,timeout=120)
        (stage/'pytest.log').write_text(run.stdout+run.stderr)
        cases = ET.parse(stage/'junit.xml').findall('.//testcase')
        failed = sum(c.find('failure') is not None or c.find('error') is not None for c in cases)
        result = {'tests':len(cases),'passed':len(cases)-failed,'failed':failed,'strict':int(run.returncode==0),
                  'status':'scored','original_scorer_sha256':sha(code.read_bytes()),'path_binding_only':True}
        save(stage/'receipt.json',result)
        return result

    def propose(self, before, old_text, experience):
        prompt = '''Propose a compact reusable workflow for reconciling records across a document and a current table, informed only by this PUBLIC development task and numeric execution results. This is a new research prototype, not native product evolution. Return only JSON {"body": "Markdown workflow without YAML header", "rationale": "brief"}. Aim for 500-700 ASCII bytes in body, always stay below max_body_utf8_bytes. Use 4-6 short steps, no headings or examples. Keep source evidence, distinguish missing from zero, use stable IDs and explicit normalization, do not modify originals, and obey each current task's output contract. Do not memorize people, row IDs, exact answers, amounts, filenames, benchmark checks or output values. Do not change identity, Soul or permissions. You receive no private expert content, raw tool results, answers or hidden tests. A separate real development execution decides acceptance; your own estimates do not prove improvement.\n'''
        header = SKILL_HEADER
        evidence = public_writer_evidence(before['score'],experience,len(old_text.encode())-len(header.encode())-1)
        messages = [{'role':'user','content':prompt+json.dumps(evidence,ensure_ascii=False)}]
        for attempt in range(1,MAX_WRITER_REQUESTS+1):
            request = {'model':WRITER,'temperature':0,'max_tokens':1200,'messages':list(messages),
                       'response_format':{'type':'json_object'}}
            suffix = '' if attempt == 1 else '_'+str(attempt)
            save(self.out/('writer_request'+suffix+'.json'),request)
            req = urllib.request.Request('https://openrouter.ai/api/v1/chat/completions',data=json.dumps(request).encode(),
                  headers={'Authorization':'Bearer '+self.router_key,'Content-Type':'application/json'},method='POST')
            with urllib.request.urlopen(req,timeout=120) as response:
                result = json.load(response)
            save(self.out/('writer_response'+suffix+'.json'),self.scrub(result))
            reply = result['choices'][0]['message']['content']
            try:
                content = candidate_document(json.loads(reply)['body'],old_text)
            except (ValueError,KeyError,TypeError) as exc:
                save(self.out/('candidate_rejection_'+str(attempt)+'.json'),{'reason':str(exc)})
                if attempt == MAX_WRITER_REQUESTS:
                    raise ValueError('No valid candidate after bounded development revision') from exc
                messages.extend([{'role':'assistant','content':reply},
                                 {'role':'user','content':str(exc)+' Return revised JSON with body and rationale. Use only the same public development evidence. No test-task feedback is available.'}])
                continue
            (self.out/'candidate_SKILL.md').write_text(content)
            return content

    def run(self):
        assert not (self.out/'protocol.json').exists(), 'Already launched; no implicit retries'
        for task,names in INPUTS.items():
            root = self.dev_inputs if task == DEV else self.bench/task/'environment'
            assert all((root/n).exists() for n in names)
        old = (self.expert/SKILL).read_text()
        protocol = {'protocol_version':2,'model':MODEL,'updater_model':WRITER,'development_task':DEV,'heldout_task':TEST,
                    'driver_sha256':sha(Path(__file__).read_bytes()),
                    'conditions':CONDITIONS,'max_profy_invocations':5,'max_writer_invocations':MAX_WRITER_REQUESTS,
                    'invalid_update_policy':'stop before held-out testing; never substitute original skill for third arm',
                    'attempt_timeout_sec':900,'retries':0,'test_concurrency':2,
                    'active_skill_verification':'native full read of exact skill content plus bash file SHA256; mandatory for development adoption and third-arm validity',
                    'common_experience_scope':'public development task plus numeric/status/tool-name metrics only; no raw skill or tool output text',
                    'method':'new procedural skill-refinement prototype; actual dev validation + nondegradation and footprint gate',
                    'not_native_product_evolution':True,'cross_expert_attribution_tested':False,
                    'openrouter_data_scope':'public task text + numeric metrics only; no private expert content, tool result text or answers',
                    'original_skill_sha256':sha(old.encode()),'expert_files':{str(p.relative_to(self.expert)):sha(p.read_bytes()) for p in sorted(self.expert.rglob('*')) if p.is_file() and not p.name.startswith('.')},
                    'inputs':{task:{n:sha(((self.dev_inputs if task==DEV else self.bench/task/'environment')/n).read_bytes()) for n in names} for task,names in INPUTS.items()}}
        save(self.out/'protocol.json',protocol)
        before = self.solve('dev_before',DEV)
        experience = shared_experience((self.bench/DEV/'task.md').read_text().split('---',2)[2],before)
        save(self.out/'development_experience.json',experience)
        accepted, candidate, after = False, None, None
        try:
            if before['score']['tests'] == 0:
                raise ValueError('Cannot validate a candidate without a scorable development baseline')
            candidate = self.propose(before,old,experience)
            after = self.solve('dev_candidate',DEV,candidate)
            gate = proposal_gate(before['score'],after['score'],old,candidate)
            gate['initial_skill_read_verified'] = before.get('active_skill_evidence',{}).get('verified',False)
            gate['updated_skill_read_verified'] = after.get('active_skill_evidence',{}).get('verified',False)
            gate['accepted'] = gate['accepted'] and gate['initial_skill_read_verified'] and gate['updated_skill_read_verified']
            accepted = gate['accepted']
        except Exception as exc:
            gate = {'accepted':False,'error_type':type(exc).__name__,'reason':str(exc),
                    'action':'stop before held-out testing'}
        save(self.out/'gate.json',gate)
        if not accepted:
            save(self.out/'summary.json',{'protocol':protocol,'gate':gate,'development_before':before,
                 'development_candidate':after,'test_results':[],
                 'profy_model_invocations_reserved':self.reservations,
                 'status':'stopped_before_heldout_test',
                 'scope':'No valid third-arm update; no three-arm effectiveness comparison executed.'})
            print('PILOT_STOPPED: no adopted update; held-out test not launched',flush=True)
            return
        used = candidate
        save(self.out/'frozen_test_configuration.json',{'candidate_accepted':accepted,'active_skill_sha256':sha(used.encode()),
              'original_skill_sha256':sha(old.encode()),'experience_sha256':sha((self.out/'development_experience.json').read_bytes()),
              'test_answers_or_scores_used_for_update':False})
        def one(condition):
            return self.solve(condition,TEST,used if condition==CONDITIONS[2] else None,
                              experience=experience,use_expert=condition!=CONDITIONS[0])
        results = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
            futures = {pool.submit(one,c):c for c in CONDITIONS}
            for future in concurrent.futures.as_completed(futures):
                try:
                    results.append(future.result())
                except Exception as exc:
                    results.append({'label':futures[future],'error_type':type(exc).__name__,'score':{'strict':0,'status':'failed_attempt'}})
        summary = {'protocol':protocol,'gate':gate,'development_before':before,'development_candidate':after,
                   'test_results':sorted(results,key=lambda r:CONDITIONS.index(r['label'])),
                   'profy_model_invocations_reserved':self.reservations,
                   'scope':'One development task and one held-out task. No significance or broad generalization claim. No cross-expert attribution or native Memory/evolution claim.'}
        save(self.out/'summary.json',summary)
        print('PILOT_FINISHED',json.dumps({'gate':gate,'scores':[{k:r.get(k) for k in ['label','score','elapsed_sec']} for r in summary['test_results']]}),flush=True)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--workspace',required=True)
    parser.add_argument('--out',required=True)
    parser.add_argument('--dev-inputs',required=True)
    parser.add_argument('--keys-file',required=True)
    parser.add_argument('--run',action='store_true')
    args = parser.parse_args()
    if not args.run:
        print('Dry configuration: add --run to authorize model invocations. No credentials read.')
    else:
        Pilot(args).run()
