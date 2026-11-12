"""Pure selection, integrity and bounded transport helpers; no API calls."""
import hashlib,io,json,re,shlex,tarfile
from pathlib import Path,PurePosixPath

MAX_ARCHIVE=50_000_000
CHUNK_SIZE=450000
BLOCKED={'reportlab','fpdf','fpdf2','python-pptx','pptxgenjs'}
LEGACY={'workdir':'/root','copies':[['gdp.xlsx','/root/gdp.xlsx']], 'apt':['gnumeric','libreoffice-calc'],'pip':[]}

def sha(raw):return hashlib.sha256(raw).hexdigest()

def registry(path=None):
    return json.loads(Path(path or Path(__file__).with_name('task_specs.json')).read_text())

def task_spec(task,path=None):
    if task=='weighted-gdp-calc':return LEGACY
    specs=registry(path)
    if task not in specs:raise ValueError('Unreviewed native task: '+task)
    return specs[task]

def safe_name(name):
    p=PurePosixPath(name)
    if not name or p.is_absolute() or '..' in p.parts or str(p)!=name:raise ValueError('Unsafe archive name: '+name)
    return p

def select_rows(rows,spec):
    by={n:(n,b,m) for n,b,m in rows}
    if len(by)!=len(rows) or 'Dockerfile' not in by:raise ValueError('Duplicate source or missing Dockerfile')
    # Review literal COPY statements, not comments, RUN commands or inferred inputs.
    found=[]
    for line in by['Dockerfile'][1].decode().splitlines():
        if re.match(r'^\s*COPY\s',line,re.I):
            parts=shlex.split(line,comments=True)
            if len(parts)!=3 or parts[1].startswith('--'):raise ValueError('Unreviewed COPY syntax')
            found.append(parts[1:])
    if found!=spec['copies']:raise ValueError('Pinned Dockerfile COPY statements differ from reviewed registry')
    chosen={'Dockerfile'}
    for source,dest in spec['copies']:
        safe_name(source)
        if source in spec.get('directory_sources',[]):
            members={n for n in by if n.startswith(source.rstrip('/')+'/')}
            if not members:raise ValueError('Empty/missing COPY directory: '+source)
            if 'public_input_files' in spec and members!={n for n in spec['public_input_files'] if n.startswith(source+'/')}:
                raise ValueError('Directory COPY differs from reviewed public manifest')
            chosen.update(members)
        else:
            if source not in by:raise ValueError('Missing COPY input: '+source)
            chosen.add(source)
    for n in chosen:safe_name(n)
    return [by[n] for n in sorted(chosen)]

def input_manifest(rows):return {n:{'sha256':sha(b),'size':len(b),'mode':m} for n,b,m in rows}

def choose_target(rows,target,expected=None):
    name='skills/'+target+'/SKILL.md'
    matches=[b for n,b,m in rows if n==name]
    if len(matches)!=1:raise ValueError('Requested target skill is absent: '+target)
    raw=matches[0]
    if expected is not None and (not re.fullmatch('[0-9a-f]{64}',expected) or sha(raw)!=expected):
        raise ValueError('Frozen parent SKILL.md hash mismatch')
    return raw.decode()

class BoundedBuffer(io.BytesIO):
    def write(self,data):
        if self.tell()+len(data)>MAX_ARCHIVE:raise ValueError('Complete archive exceeds 50 MB RAM limit')
        return super().write(data)

def archive_rows(rows,empty_skills=False):
    out=BoundedBuffer()
    with tarfile.open(fileobj=out,mode='w:gz') as archive:
        if empty_skills:
            info=tarfile.TarInfo('skills');info.type=tarfile.DIRTYPE;info.mode=0o755;archive.addfile(info)
        for name,raw,mode in rows:
            safe_name(name)
            if empty_skills and PurePosixPath(name).parts[0]=='skills':continue
            info=tarfile.TarInfo(name);info.size=len(raw);info.mode=mode;archive.addfile(info,io.BytesIO(raw))
    return out.getvalue()

def transport_pieces(data):
    if len(data)>MAX_ARCHIVE:raise ValueError('Complete archive exceeds 50 MB')
    pieces=[];manifest=[]
    for i,start in enumerate(range(0,len(data),CHUNK_SIZE)):
        raw=data[start:start+CHUNK_SIZE]
        name='task_environment.tar.gz' if len(data)<=CHUNK_SIZE else 'task_environment.part%04d'%i
        pieces.append((name,raw));manifest.append({'name':name,'size':len(raw),'sha256':sha(raw)})
    return pieces,manifest

def read_transport(base,meta):
    entries=meta['transport'];total=sum(e['size'] for e in entries)
    if not entries or total>MAX_ARCHIVE:raise ValueError('Invalid transport size')
    expected_names=['task_environment.tar.gz'] if len(entries)==1 else ['task_environment.part%04d'%i for i in range(len(entries))]
    if [e['name'] for e in entries]!=expected_names:raise ValueError('Transport pieces are out of order')
    out=BoundedBuffer()
    for entry in entries:
        if not 0<entry['size']<=CHUNK_SIZE:raise ValueError('Invalid piece size')
        path=base/entry['name']
        if path.is_symlink() or path.stat().st_size!=entry['size']:raise ValueError('Piece size mismatch')
        raw=path.read_bytes()
        if sha(raw)!=entry['sha256']:raise ValueError('Piece hash mismatch')
        out.write(raw)
    if sha(out.getbuffer())!=meta['input_sha256']:raise ValueError('Archive hash mismatch')
    out.seek(0)
    return out

def extract_inputs(buffer,destination,manifest):
    with tarfile.open(fileobj=buffer,mode='r:gz') as archive:
        entries=archive.getmembers()
        if len(entries)!=len(manifest) or {i.name for i in entries}!=set(manifest):raise ValueError('Archive membership mismatch')
        for info in entries:
            safe_name(info.name)
            expected=manifest[info.name]
            if not info.isfile() or info.size!=expected['size'] or info.mode!=expected['mode']:raise ValueError('Archive metadata mismatch')
            if info.size>MAX_ARCHIVE:raise ValueError('Oversized input')
            raw=archive.extractfile(info).read()
            if sha(raw)!=expected['sha256']:raise ValueError('Input hash mismatch')
            target=destination/info.name;target.parent.mkdir(parents=True,exist_ok=True)
            target.write_bytes(raw);target.chmod(info.mode)

def copy_targets(spec,names):
    result={}
    for source,destination in spec['copies']:
        if source in spec.get('directory_sources',[]):
            for name in names:
                if name.startswith(source+'/'):result[name]=destination.rstrip('/')+'/'+name[len(source)+1:]
        else:result[source]=destination+PurePosixPath(source).name if destination.endswith('/') else destination
    if len(set(result.values()))!=len(result):raise ValueError('Overlapping COPY destinations')
    return result
