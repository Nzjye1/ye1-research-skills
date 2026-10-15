"""Check host-declared downstream consumers against one frozen result version.
No semantic or identity certification. Only selected outputs are required.
"""

# All data-bearing streams stay behind the controlled local adapter.
if __name__ == '__main__':
    import sys as _privacy_sys
    if '--help' not in _privacy_sys.argv[1:]:
        from privacy_boundary import cli_local_entry
        cli_local_entry()

import argparse,hashlib,json
from pathlib import Path

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def local(root,path):
    root=Path(root).resolve();p=root/path
    if p.is_symlink() or not p.resolve().is_relative_to(root) or not p.is_file():raise ValueError('Missing/unsafe downstream consumer: '+path)
    return p

def check(root,manifest):
    result=local(root,manifest['analysis_path']);current=sha(result)
    if current!=manifest['analysis_sha256']:raise ValueError('Result version changed; all declared consumers pending review')
    roles=set(manifest['selected_roles'])
    if not roles or not roles<= {'table','figure','zh','en','docx','pdf','version'}:raise ValueError('Declare the actual selected delivery roles')
    consumers=manifest['consumers']
    if {c['role'] for c in consumers}!=roles:raise ValueError('Missing selected downstream role')
    for c in consumers:
        p=local(root,c['path'])
        if c.get('analysis_sha256')!=current or c.get('sha256')!=sha(p):raise ValueError('Stale downstream: '+c['path'])
        # Optional exact anchors are a targeted old-number check, never full scientific review.
        anchors=c.get('required_text',[])
        if anchors and any(t not in p.read_text(encoding='utf8') for t in anchors):raise ValueError('Current numeric/text anchor absent: '+c['path'])
    return {'status':'DECLARED_CONSUMERS_CURRENT','analysis_sha256':current,'roles':sorted(roles),'checked':len(consumers),'semantic_review':'HOST_REQUIRED','undeclared_consumers':'HOST_MUST_INVENTORY','approval':'PENDING_USER_VERSION_CONFIRMATION'}
if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('root',type=Path);a.add_argument('manifest',type=Path);v=a.parse_args();print(json.dumps(check(v.root,json.loads(v.manifest.read_text())),ensure_ascii=False,indent=2))
