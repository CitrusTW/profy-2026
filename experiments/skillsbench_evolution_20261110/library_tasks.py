"""Public task filesystem transport and original Docker scoring, no learning prompt."""
import argparse,hashlib,json,shutil,subprocess,tarfile,uuid
from pathlib import Path
from run import Study,save,sha

class LibraryStudy(Study):
    def __init__(self,args):
        self.task=args.task
        bench=Path(args.workspace)/'04_项目数据与代码/skillsbench/tasks'/self.task
        names=sorted(p.parent.name for p in (bench/'environment/skills').glob('*/SKILL.md'))
        if not names:raise ValueError('No public skill in task; record identical conditions explicitly')
        args.dev_task=self.task;args.skill_name=names[0]
        if self.task=='threejs-to-obj':args.skill_name='threejs'
        super().__init__(args);self.names=names

    def input_file(self,task):
        raise RuntimeError('Local Docker preparation is retired: cloud-only execution is required. Use an explicitly verified cloud subclass.')
        # Historical implementation below is retained for provenance, never executed.
        root=self.out/'public-snapshot';archive=self.out/'public_environment.tar.gz'
        if archive.exists():return archive,'public_environment.tar.gz'
        root.mkdir(exist_ok=True);image='cognilife-sb-full-'+task
        name='cgl-snapshot-'+uuid.uuid4().hex[:12]
        subprocess.run(['docker','create','--name',name,image],check=True,capture_output=True)
        try:
            for path in ['root','app','workspace','data','workspaces']:
                dest=root/'fs'/path;dest.parent.mkdir(parents=True,exist_ok=True)
                p=subprocess.run(['docker','cp',name+':/'+path,str(dest)],capture_output=True)
                if p.returncode and dest.exists():shutil.rmtree(dest)
        finally:subprocess.run(['docker','rm',name],check=True,capture_output=True)
        # Source data stays local; cache/tool installations and bundled skill copies are not solver inputs.
        excluded={'skills','.claude','.agents','.cache','.npm','.cargo','.rustup','.venv','node_modules','__pycache__','oracle','verifier','ground_truth'}
        with tarfile.open(archive,'w:gz') as tar:
            for p in sorted(root.rglob('*')):
                if p.is_file() and not p.is_symlink() and not any(x in excluded for x in p.relative_to(root).parts):tar.add(p,p.relative_to(root).as_posix(),recursive=False)
            tar.add(self.bench/task/'environment/Dockerfile','PUBLIC_DOCKERFILE.txt')
        if archive.stat().st_size>150_000_000:raise ValueError('Public input archive exceeds bounded transport size; no model called')
        return archive,'public_environment.tar.gz'

    def instructions(self,task,no_skills):
        names=['bench_skills/'+n+'/SKILL.md' for n in self.names]
        setup=('No benchmark skills supplied. Do not discover, activate or import any other expert/user/builtin skills. ' if no_skills else
            'Unzip benchmark_skills.zip. Read all supplied skills in full: '+', '.join(names)+'. Print SBP_ACTIVE_SKILL_SHA256:<computed SHA256> for '+self.skill_name+' at bench_skills/'+self.skill_name+'/SKILL.md. ')
        common='''
Execution adapter (same across groups): Unzip task_input.zip, then extract public_environment.tar.gz. fs/root, fs/app, fs/workspace, fs/data and fs/workspaces represent the original absolute directories. Interpret original task paths through these mappings; start in fs/root unless the original public Dockerfile specifies another working directory. PUBLIC_DOCKERFILE.txt lists the original public dependencies; install needed equivalents with ordinary tools. The source archive is immutable, but task files may be edited when the original task requests edits. Do not access oracle, verifier, reference answers, Memory or other sessions. Use public network resources only when the original task needs them. At most 48 tool calls and 24 model turns.
After solving, package only the originally requested deliverables, preserving their exact bytes and logical filesystem location. For example fs/root/result.json becomes output/fs/root/result.json inside deliverables.zip. Include manifest.json at ZIP root with input_sha256 equal to the SHA256 of public_environment.tar.gz and files mapping each archived output path to its exact SHA256. Do not include original inputs, dependencies or skill files unless the original task explicitly requests the input file be edited. Never package /verifier, /oracle, /logs, /etc or /usr. Print [OUTPUT] deliverables.zip and SBP_NATIVE_ZIP_SHA256:<computed SHA256 of deliverables.zip>.
'''
        return setup,common

    def grade(self,task,folder):
        raise RuntimeError('Local Docker grading is retired: use an explicitly verified cloud grader.')
        # Historical implementation below is retained for provenance, never executed.
        scoring=folder/'scoring_only';scoring.mkdir(exist_ok=True)
        outputs=folder/'output/fs';outputs.mkdir(parents=True,exist_ok=True)
        if any(p.name not in ['root','app','workspace','data','workspaces','tmp','output'] for p in outputs.iterdir()):raise ValueError('Output filesystem root not allowed')
        staging=Path('/private/tmp/cgl-full-preflight-staging')/task/'verifier'
        source=self.bench/task/'verifier'
        shutil.copytree(source,staging,dirs_exist_ok=True)
        command=['docker','run','--rm','--cpus','2','--memory','8g',
            '--mount',f'type=bind,source={staging},target=/verifier,readonly',
            '--mount',f'type=bind,source={scoring},target=/logs/verifier',
            '--mount',f'type=bind,source={outputs},target=/model_outputs,readonly',
            'cognilife-sb-full-'+task,'bash','-lc','cp -a /model_outputs/. / && bash /verifier/test.sh']
        with (scoring/'docker.log').open('w') as log:p=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT,timeout=1800)
        reward=scoring/'reward.txt'
        if not reward.exists():raise RuntimeError('Original scorer did not return a reward; preserve run as infrastructure error')
        value=float(reward.read_text().strip());strict=int(value==1.0)
        tests=passed=failed=skipped=0
        if (scoring/'ctrf.json').exists():
            summary=json.loads((scoring/'ctrf.json').read_text())['results']['summary'];tests=summary['tests'];passed=summary['passed'];failed=summary.get('failed',0);skipped=summary.get('skipped',0)
        result={'strict':strict,'original_reward':value,'tests':tests,'passed':passed,'failed':failed,'skipped':skipped,'original_returncode':p.returncode,'test_counts_available':bool(tests),'verifier_unmodified':True,'source_hashes':{p.relative_to(source).as_posix():sha(p.read_bytes()) for p in source.rglob('*') if p.is_file()}}
        save(scoring/'receipt.json',result);return result

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--workspace',required=True);p.add_argument('--out',required=True);p.add_argument('--task',required=True);p.add_argument('--label',choices=['no-skills','with-skills'],required=True);p.add_argument('--keys-file',required=True);p.add_argument('--allow-paid',action='store_true');args=p.parse_args()
    study=LibraryStudy(args);study.input_file(args.task)
    ready=Path(args.workspace)/'01_任务结果/2026-11-11_skillsbench_full_library/full-grading-preflight'/args.task/'STATUS.json'
    if not ready.exists() or float(json.loads(ready.read_text()).get('original_reward') or -1)!=1.0:raise ValueError('Original grading environment must pass before a paid solve')
    study.solve(args.label,args.task,no_skills=args.label=='no-skills')
