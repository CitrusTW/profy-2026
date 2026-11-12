"""After solving only: freeze/export actual files, execute the original verifier, clean this case."""
import gzip,hashlib,json,os,re,shutil,subprocess,tarfile,time,zipfile
from pathlib import Path
from remote_setup import cloud_only,digest

def main():
    cloud_only();base=Path.cwd();state=json.loads((base/'case_context.json').read_text())
    config=json.loads(gzip.decompress((base/'grade_config.json.gz').read_bytes()))
    assert state==config['expected_context'],'Prepared context changed'
    work=Path(state['work']);runtime=Path(state['runtime'])
    assert work.parent==base and work.name.startswith('cgl-task-')
    assert runtime.parent==Path('/tmp') and runtime.name.startswith('cgl-sock-')
    frozen=base/'case_frozen';frozen.touch(exist_ok=False)
    cli=state['cli'];container=state['container'];out=base/'output';out.mkdir(exist_ok=True)
    report={'original_verifier':True,'benchmark_pin':state['benchmark_pin'],'task':state['task'],'pre_grade_file_hashes':{},'original_source_hashes':{},'cleanup_errors':[]}
    def run(args,timeout=120):return subprocess.run(args,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=timeout)
    def file_sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
    try:
        # Export changed task files before exposing any verifier material.
        diff=run(cli+['diff',container]);assert diff.returncode==0
        roots={'root','app','workspace','workspaces','data','output','tmp','home'}
        excluded={'.cache','.git','.npm','.local','.venv','node_modules','__pycache__','.pytest_cache','bench_skills','.claude','.agents','.codex','.bash_history'}
        paths=[]
        for line in diff.stdout.splitlines():
            kind,path=line.split(' ',1);p=Path(path)
            if kind=='D' or len(p.parts)<3 or p.parts[1] not in roots or any(s in excluded for s in p.parts):continue
            status=run(cli+['exec',container,'/bin/sh','-c','test -f "$1" && test ! -L "$1"','sh',path],10)
            if status.returncode==0:paths.append(path)
        for path in sorted(set(paths)):
            target=out/'fs'/path.lstrip('/');target.parent.mkdir(parents=True,exist_ok=True)
            p=run(cli+['cp',container+':'+path,str(target)],60);assert p.returncode==0
            report['pre_grade_file_hashes'][path]=file_sha(target)
        assert digest(base/'original_verifier.tar.gz')==config['verifier_archive_sha256']
        verifier=work/'verifier'
        assert not any(verifier.iterdir()),'Verifier was available before freezing'
        with tarfile.open(base/'original_verifier.tar.gz','r:gz') as archive:archive.extractall(verifier,filter='data')
        expected=config['source_hashes']
        report['original_source_hashes']={p.relative_to(verifier).as_posix():file_sha(p) for p in verifier.rglob('*') if p.is_file()}
        assert report['original_source_hashes']==expected
        logs=work/'verifier-logs'
        for p in logs.iterdir():
            if p.is_dir():shutil.rmtree(p)
            else:p.unlink()
        command=cli+['exec','--user','0',container,'bash','/verifier/test.sh']
        graded=run(command,900)
        (work/'original_verifier_stdout.log').write_text(graded.stdout)
        report['original_returncode']=graded.returncode
        reward=logs/'reward.txt'
        if not reward.is_file():raise RuntimeError('Original verifier returned no reward; infrastructure error, not a zero score')
        value=float(reward.read_text().strip());assert 0<=value<=1
        report.update(original_reward=value,strict=int(value==1.0),tests=None,passed=None,failed=None,skipped=None)
        if (logs/'ctrf.json').is_file():
            summary=json.loads((logs/'ctrf.json').read_text())['results']['summary']
            for key in ['tests','passed','failed','skipped']:report[key]=summary.get(key,0)
        elif config['expects_ctrf']:
            raise RuntimeError('Original pytest report missing: preserve raw reward, mark grading infrastructure error')
        after={p.relative_to(verifier).as_posix():file_sha(p) for p in verifier.rglob('*') if p.is_file()}
        assert after==expected,'Verifier source changed'
        report['original_source_before_after_verified']=True
        report['answer_files_unchanged_by_grader']=True
        for path,expected_hash in report['pre_grade_file_hashes'].items():
            p=run(cli+['exec','--user','0',container,'sha256sum',path],20)
            if p.returncode or not p.stdout.startswith(expected_hash):report['answer_files_unchanged_by_grader']=False
    except Exception as e:report['infrastructure_error']=type(e).__name__+': '+str(e)
    finally:
        try:
            run(cli+['rm','-f',container],30)
            run(cli+['image','rm','-f',state['image_id']],60)
            pid=runtime/'d.pid'
            if pid.is_file():
                value=pid.read_text().strip();assert value.isdigit()
                cmdline=Path('/proc/'+value+'/cmdline')
                if cmdline.exists():
                    assert ('--data-root='+str(work/'data')).encode() in cmdline.read_bytes()
                    run(['sudo','-n','kill','-TERM',value],10)
            for _ in range(20):
                if not pid.is_file() or not Path('/proc/'+value+'/cmdline').exists():break
                time.sleep(.5)
            # Do not force removal of an OS-owned busy mount; remove only our files.
            cleaned=run(['sudo','-n','rm','-rf',str(work),str(runtime)],120)
            report['temporary_paths_removed']=not work.exists() and not runtime.exists()
            if cleaned.returncode:report['cleanup_errors'].append(cleaned.stdout[-1000:])
        except Exception as e:report['cleanup_errors'].append(str(e))
    (out/'score_receipt.json').write_text(json.dumps(report,indent=2))
    manifest={'input_sha256':config['verifier_archive_sha256'],'files':{p.relative_to(base).as_posix():file_sha(p) for p in out.rglob('*') if p.is_file() and not p.is_symlink()}}
    delivery=base/'outputs';delivery.mkdir(exist_ok=True)
    with zipfile.ZipFile(delivery/'deliverables.zip','w',compression=zipfile.ZIP_DEFLATED) as archive:
        for name in manifest['files']:archive.write(base/name,name)
        archive.writestr('manifest.json',json.dumps(manifest))
    print(json.dumps(report));print('SBP_NATIVE_ZIP_SHA256:'+file_sha(delivery/'deliverables.zip'));print('[OUTPUT] outputs/deliverables.zip')

if __name__=='__main__':main()
