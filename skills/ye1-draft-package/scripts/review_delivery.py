"""Customer review -> explicitly confirmed draft. No automatic or inferred approval."""

# All data-bearing streams stay behind the controlled local adapter.
if __name__ == '__main__':
    import sys as _privacy_sys
    if '--help' not in _privacy_sys.argv[1:]:
        from privacy_boundary import cli_local_entry
        cli_local_entry()

import argparse,hashlib,json,zipfile,shutil,os
from pathlib import Path

def privacy_export(paths,out,*,names,expected,tree=False,validator=None):
    from privacy_boundary import export, Denied
    project=os.environ.get('YE1_PRIVACY_PROJECT')
    if not project:raise Denied('PROJECT_CHOICE_REQUIRED')
    root=Path(project).resolve();rels=[];mapping={};hashes={}
    for p in paths:
        p=Path(p)
        if p.is_symlink() or not p.resolve().is_relative_to(root):raise Denied('PROJECT_SCOPE_REQUIRED')
        rel=p.resolve().relative_to(root).as_posix();rels.append(rel);mapping[rel]=names[p];hashes[rel]=expected[p]
    return export(root,rels,out,os.environ.get('YE1_PRIVACY_PLATFORM',''),os.environ.get('YE1_PRIVACY_MODEL',''),os.environ.get('YE1_PRIVACY_PURPOSE',''),
                  test_only=os.environ.get('YE1_PRIVACY_SYNTHETIC_TEST')=='1',names=mapping,expected=hashes,tree=tree,validator=validator)


def snapshot(root,required_files=None):
    root=Path(root);files={}
    if not root.is_dir():raise ValueError('Review tree required')
    for p in sorted(root.rglob('*')):
        if p.is_symlink():raise ValueError('Review symlinks not supported')
        if p.is_file() and not any(part.startswith('.') or part=='__pycache__' for part in p.relative_to(root).parts) and 'render/page-' not in str(p):
            files[str(p.relative_to(root))]=hashlib.sha256(p.read_bytes()).hexdigest()
    actual=sorted(rel for rel in files if Path(rel).suffix in {'.docx','.pdf'} and not rel.startswith('support/'))
    # API default preserves old single-tree contract. CLI always receives explicit selection.
    legacy_selection=required_files is None
    if required_files is None:required_files=actual
    if not isinstance(required_files,list) or not required_files or any(not isinstance(r,str) for r in required_files):raise ValueError('Explicit nonempty format list required')
    if len(required_files)!=len(set(required_files)):raise ValueError('Duplicate confirmed file')
    if any(r not in files or Path(r).suffix not in {'.docx','.pdf','.md'} or r.startswith('support/') for r in required_files):raise ValueError('Selected manuscript format missing or unsupported')
    if {r for r in required_files if Path(r).suffix in {'.docx','.pdf'}}!=set(actual):raise ValueError('Required formats missing or extra unselected DOCX/PDF; prepare a review tree for the actual selected deliverables')
    docs={r for r in required_files if r.endswith('.docx')};pdfs={r for r in required_files if r.endswith('.pdf')}
    if legacy_selection and (not docs or not pdfs):raise ValueError('Default review requires DOCX and PDF; explicit selection is required for a limited-format delivery')
    matched=set()
    for rel in docs if (legacy_selection or pdfs) else []:
        p=Path(rel);possible={str(p.with_suffix('.pdf')),str(p.parent/'render'/p.with_suffix('.pdf').name)}
        partners=possible&pdfs
        if len(partners)!=1:raise ValueError('Missing or ambiguous matching PDF: '+rel)
        matched.update(partners)
    if (legacy_selection or docs) and matched!=pdfs:raise ValueError('Unpaired PDF or cross-language formats')
    required_files=sorted(required_files)
    version=hashlib.sha256(json.dumps({'files':files,'required_files':required_files},sort_keys=True).encode()).hexdigest()
    return {'version_sha256':version,'files':files,'required_files':required_files}

def prepare(source_root,manifest_path,out):
    """Build a review tree with selected documents and explicit non-row-level support.

    Classification is supplied and reviewed by the host, not a privacy classifier.
    Original patient rows are never automatically included.
    """
    source_root=Path(source_root).resolve();out=Path(out);manifest_path=Path(manifest_path);manifest_bytes=manifest_path.read_bytes();manifest=json.loads(manifest_bytes)
    if out.exists():raise ValueError('Preserve prior review version')
    if manifest.get('schema')!='ye1-review-selection/1':raise ValueError('Review selection schema required')
    entries=manifest.get('artifacts',[]);targets=set();resolved=[];selected=[]
    for entry in entries:
        if entry.get('classification') not in {'manuscript','aggregate','method','public_evidence','supplementary_aggregate'}:raise ValueError('Raw/local row-level or unclassified files cannot enter the delivery tree')
        rel=entry['target'];parts=Path(rel).parts
        if Path(rel).is_absolute() or '..' in parts or not parts or rel in targets:raise ValueError('Unsafe or duplicate review target')
        source=source_root/entry['source']
        if rel=='review-selection.json':raise ValueError('Reserved generated selection member')
        if source.is_symlink() or not source.resolve().is_relative_to(source_root) or not source.is_file():raise ValueError('Missing/unsafe review source')
        if hashlib.sha256(source.read_bytes()).hexdigest()!=entry['sha256']:raise ValueError('Review source version changed')
        if entry['classification']=='manuscript':
            if rel.startswith('support/'):raise ValueError('Selected manuscript cannot be hidden in support')
            selected.append(rel)
        elif not rel.startswith('support/'):raise ValueError('Supporting artifacts must be explicitly placed in support/')
        targets.add(rel);resolved.append((source,rel))
    if not selected:raise ValueError('Select at least one actual manuscript')
    paths=[source for source,rel in resolved]+[manifest_path]
    names={source:rel for source,rel in resolved};names[manifest_path]='review-selection.json'
    expected={source:entry['sha256'] for (source,rel),entry in zip(resolved,entries)};expected[manifest_path]=hashlib.sha256(manifest_bytes).hexdigest()
    # Validate exact final tree before one atomic publication under the project lock.
    receipt=privacy_export(paths,out,names=names,expected=expected,tree=True,validator=lambda staged:snapshot(staged,selected))
    return {'status':'CUSTOMER_REVIEW_PENDING','required_files':sorted(selected),**receipt['validation'],'scope':'Host-selected review outputs; no inferred customer approval'}


def provenance(kind, source_path=None, locator=None, quote=None):
    # Evidence classification, not authentication of the person or transcript.
    if kind not in {'direct_user', 'simulated', 'unknown'}:raise ValueError('Unknown confirmation source kind')
    if kind != 'direct_user':return {'kind':kind,'identity_authenticated':False}
    source=Path(source_path or '')
    if not source.is_file() or source.is_symlink() or not locator or not quote:raise ValueError('Direct user confirmation requires a quotable source file and message locator')
    if quote not in source.read_text(encoding='utf8'):raise ValueError('Confirmation quote absent from source')
    return {'kind':kind,'source_path':str(source.resolve()),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'locator':locator,'quote':quote,'identity_authenticated':False}

def confirmation(root,actor,statement,date,*,synthetic_test=None,required_files=None,source_kind=None,source_path=None,source_locator=None,source_quote=None):
    if not all(isinstance(v,str) and v.strip() for v in [actor,statement,date]):raise ValueError('Explicit actor, statement and date required')
    if statement not in {'确认此版本作为初稿','I confirm this version as the draft'}:raise ValueError('Explicit version approval statement required')
    kind=source_kind or ('simulated' if synthetic_test is True else 'unknown')
    if synthetic_test is True and kind!='simulated':raise ValueError('Synthetic identity cannot become a direct user approval')
    origin=provenance(kind,source_path,source_locator,source_quote or statement)
    return {'schema':'doctor-paper-review-confirmation/3','status':'CONFIRMED' if kind!='unknown' else 'SOURCE_UNKNOWN','actor':actor,'statement':statement,'date_utc':date,'synthetic_test':kind=='simulated','provenance':origin,**snapshot(root,required_files)}

def package(root,record,out,*,test_only=False):
    if record.get('status')!='CONFIRMED':raise ValueError('Customer review pending; draft package forbidden')
    origin=record.get('provenance',{})
    if origin.get('kind') not in {'direct_user','simulated'}:raise ValueError('Unknown source cannot authorize delivery; obtain directly quotable user confirmation')
    if record.get('synthetic_test') is not (origin['kind']=='simulated'):raise ValueError('Confirmation source classification conflicts with synthetic flag')
    if origin['kind']=='simulated' and not test_only:raise ValueError('Synthetic confirmation cannot authorize a real draft package')
    if origin['kind']=='direct_user':
        checked=provenance('direct_user',origin.get('source_path'),origin.get('locator'),origin.get('quote'))
        if checked!=origin:raise ValueError('Confirmation source changed; obtain a fresh confirmation')
    if record.get('statement') not in {'确认此版本作为初稿','I confirm this version as the draft'} or not record.get('actor') or not record.get('date_utc'):raise ValueError('Invalid explicit approval')
    if not isinstance(record.get('required_files'),list):raise ValueError('Confirmation lacks selected format contract; obtain version-specific confirmation')
    now=snapshot(root,record['required_files'])
    if now['version_sha256']!=record.get('version_sha256') or now['files']!=record.get('files') or now['required_files']!=record.get('required_files'):raise ValueError('Version changed; prior confirmation invalid')
    if 'VERSION_CONFIRMATION.json' in now['files']:raise ValueError('Version confirmation is generated by the packager and cannot be selected as a source-tree file')
    out=Path(out)
    if out.exists():raise ValueError('Preserve prior package')
    if out.resolve().is_relative_to(Path(root).resolve()):raise ValueError('Package must be outside review tree')
    project=Path(os.environ['YE1_PRIVACY_PROJECT'])
    content=json.dumps(record,ensure_ascii=False,indent=2).encode()
    generated=project/'.ye1-privacy'/('package-confirmation-'+hashlib.sha256(content).hexdigest()+'.json')
    # Local staging only; its exact generated bytes require a separate privacy grant.
    if not generated.exists():
        with generated.open('xb') as f:f.write(content)
    paths=[Path(root)/rel for rel in now['files']]+[generated]
    names={Path(root)/rel:rel for rel in now['files']};names[generated]='VERSION_CONFIRMATION.json'
    expected={Path(root)/rel:h for rel,h in record['files'].items()};expected[generated]=hashlib.sha256(content).hexdigest()
    # Same transaction/export as new paths: capture approved bytes, then validate
    # the actual ZIP against the draft confirmation before atomic publication.
    privacy_export(paths,out,names=names,expected=expected,validator=archive_manifest)
    return out


def archive_manifest(archive_path):
    """Return an external hash inventory of every ZIP member, including generated confirmation."""
    archive_path=Path(archive_path)
    members=[]
    with zipfile.ZipFile(archive_path) as z:
        names=z.namelist()
        if len(names)!=len(set(names)):raise ValueError('Duplicate ZIP member names')
        if 'VERSION_CONFIRMATION.json' not in names:raise ValueError('Version confirmation member missing')
        for info in sorted(z.infolist(),key=lambda i:i.filename):
            if info.is_dir():continue
            data=z.read(info.filename)
            members.append({'path':info.filename,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),
              'role':'generated_confirmation' if info.filename=='VERSION_CONFIRMATION.json' else 'version_snapshot_member'})
        confirmation=json.loads(z.read('VERSION_CONFIRMATION.json'))
    snapshot_files={m['path']:m['sha256'] for m in members if m['path']!='VERSION_CONFIRMATION.json'}
    if snapshot_files!=confirmation.get('files'):raise ValueError('ZIP members do not match the confirmation version snapshot')
    version=hashlib.sha256(json.dumps({'files':snapshot_files,'required_files':confirmation.get('required_files')},sort_keys=True).encode()).hexdigest()
    if version!=confirmation.get('version_sha256'):raise ValueError('ZIP version confirmation fingerprint mismatch')
    provenance=confirmation.get('provenance',{})
    return {'schema':'doctor-paper-zip-member-manifest/1','archive_sha256':hashlib.sha256(archive_path.read_bytes()).hexdigest(),
      'archive_bytes':archive_path.stat().st_size,'member_count':len(members),'members':members,
      'version_confirmation':{'path':'VERSION_CONFIRMATION.json','version_sha256':confirmation.get('version_sha256'),
        'synthetic_test':confirmation.get('synthetic_test'),'provenance_kind':provenance.get('kind'),
        'identity_authenticated':provenance.get('identity_authenticated'),'status':confirmation.get('status'),
        'notice':confirmation.get('notice'),'inventory_reason':'Generated during packaging after the review-tree preparation receipt; its exact ZIP-member SHA-256 is listed above.'}}

def main():
    p=argparse.ArgumentParser(description=__doc__);sub=p.add_subparsers(dest='action',required=True)
    v=sub.add_parser('version');v.add_argument('root',type=Path)
    c=sub.add_parser('confirm');c.add_argument('root',type=Path);c.add_argument('--actor',required=True);c.add_argument('--statement',required=True);c.add_argument('--date-utc',required=True);c.add_argument('--record',type=Path,required=True);c.add_argument('--required-files',type=Path,required=True);c.add_argument('--source-kind',choices=['direct_user','simulated','unknown'],default='unknown');c.add_argument('--source-path',type=Path);c.add_argument('--source-locator');c.add_argument('--source-quote')
    b=sub.add_parser('package');b.add_argument('root',type=Path);b.add_argument('--record',type=Path,required=True);b.add_argument('--out',type=Path,required=True);b.add_argument('--receipt',type=Path);b.add_argument('--test-only',action='store_true',help='Permit a clearly simulated TEST_ONLY confirmation; never authorizes real delivery')
    a=sub.add_parser('prepare');a.add_argument('root',type=Path);a.add_argument('--selection',type=Path,required=True);a.add_argument('--out',type=Path,required=True);a.add_argument('--receipt',type=Path,required=True)
    a=p.parse_args()
    if a.action=='prepare':
        if a.receipt.exists() or a.receipt.resolve().is_relative_to(a.out.resolve()):raise ValueError('Keep a fresh preparation receipt outside the review tree')
        a.receipt.write_text(json.dumps(prepare(a.root,a.selection,a.out),ensure_ascii=False,indent=2));return
    if a.action=='version':print(json.dumps(snapshot(a.root),indent=2));return
    if a.record.resolve().is_relative_to(a.root.resolve()):raise ValueError('Confirmation record must stay outside version tree')
    if a.action=='confirm':
        if a.record.exists():raise ValueError('Preserve prior confirmation')
        a.record.write_text(json.dumps(confirmation(a.root,a.actor,a.statement,a.date_utc,required_files=json.loads(a.required_files.read_text()),source_kind=a.source_kind,source_path=a.source_path,source_locator=a.source_locator,source_quote=a.source_quote),ensure_ascii=False,indent=2))
    else:
        package(a.root,json.loads(a.record.read_text()),a.out,test_only=a.test_only)
        if a.receipt:
            if a.receipt.resolve().is_relative_to(a.root.resolve()):raise ValueError('Package-member receipt must be external to review tree')
            if a.receipt.exists():raise ValueError('Preserve prior package receipt')
            a.receipt.parent.mkdir(parents=True,exist_ok=True)
            a.receipt.write_text(json.dumps(archive_manifest(a.out),ensure_ascii=False,indent=2))
if __name__=='__main__':
    try:main()
    except Exception:
        print(json.dumps({'status':'BLOCKED_LOCAL_REVIEW','reason':'Check privacy choice, local inputs and host support'}))
        raise SystemExit(4)
