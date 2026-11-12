"""Engineering assistance through the existing OpenRouter key; never evolves skills or sees gold."""
import argparse,json,sys,urllib.request
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'skillsbench_evolution_20261110'))
from run import ProfyTransport,load_own_transport,save,sha
from native_evolution import require_paid
if __name__=='__main__':
 p=argparse.ArgumentParser()
 for n in ['workspace','keys-file','environment-input','out']:p.add_argument('--'+n,required=True)
 p.add_argument('--allow-paid',action='store_true');a=p.parse_args();require_paid(a.allow_paid)
 out=Path(a.out);out.mkdir(exist_ok=False);transport=ProfyTransport(load_own_transport(Path(a.workspace)),a.keys_file)
 metadata=json.loads(Path(a.environment_input).read_text());own_code={n:(HERE/n).read_text() for n in ['remote_native.py','remote_tools.py','remote_setup.py','study.py']}
 prompt='''Engineering only, not CogniLife Evolution. We need the smallest safe extension of our working Profy Linux file-task runner to these nine existing SkillsBench tasks. Original questions, skills, inputs and scoring rules must not be redesigned. No questions, verifier, gold or answers are included here. Use only supplied official Dockerfiles and public input-file manifests as source facts. Return JSON with task_specs (task, workdir, literal original COPY mappings, apt packages, pip requirements, input-generation needs) and minimal code_changes. Do not invent files or generate substitute input data. If Docker RUN creates required inputs, identify the original setup command and flag that copying alone is insufficient; do not rewrite its generator. Respect platform permissions/package restrictions; no obfuscation or bypass. No local images, builds or large caches. Everything serial. Our PRoot adapter caused a LibreOffice wrapper/macro compatibility problem; the cloud has already proven kernel mount namespace support. Recommend the minimal common environment fix so original and evolved skills are compared fairly, with solver uid dropped back to1000 after fixed mounts, while original scoring runs as root in its separate private namespace. Do not suggest more experiments, scoring changes, human review, new benchmarks, paid services or purchases. Do not edit any SKILL.md or replace the received Evolution method. Existing pinned xlsx skill is frozen and all future tasks are unseen. Avoid copying third-party program source into our private code archive. JSON only.'''
 body={'model':'openai/gpt-6.1-sol','max_tokens':8000,'response_format':{'type':'json_object'},'messages':[{'role':'system','content':prompt},{'role':'user','content':json.dumps({'public_environment_metadata':metadata,'our_existing_adapter_code':own_code},ensure_ascii=False)}]}
 save(out/'request.json',body)
 req=urllib.request.Request('https://openrouter.ai/api/v1/chat/completions',data=json.dumps(body).encode(),headers={'Authorization':'Bearer '+transport.evolution_key(),'Content-Type':'application/json','X-Title':'SkillsBench environment engineering, not Evolution'},method='POST')
 with urllib.request.urlopen(req,timeout=240) as r:response=json.load(r)
 save(out/'response.json',transport.scrub(response));plan=json.loads(response['choices'][0]['message']['content']);save(out/'PLAN.json',plan)
 save(out/'PROVENANCE.json',{'purpose':'Engineering only, not skill Evolution or benchmark solving','model':'openai/gpt-6.1-sol','benchmark_questions_verifier_gold_or_answers_included':False,'request_sha256':sha(json.dumps(body,ensure_ascii=False,sort_keys=True).encode()),'usage':response.get('usage'),'no_original_Dockerfile_code_to_copy_to_private_repo':True})
 print(json.dumps({'plan_file':str(out/'PLAN.json'),'usage':response.get('usage')}))
