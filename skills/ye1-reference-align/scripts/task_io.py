"""Optional deterministic checks for host-authored text; no semantic or metadata verdicts."""

# All data-bearing streams stay behind the controlled local adapter.
if __name__ == '__main__':
    import sys as _privacy_sys
    if '--help' not in _privacy_sys.argv[1:]:
        from privacy_boundary import cli_local_entry
        cli_local_entry()

import argparse,hashlib,json,re,sys
from collections import Counter
from pathlib import Path
NUMBER=re.compile(r'[-+−]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?%?')
def numbers(s):return Counter(NUMBER.findall(s))
def word_count(s):return len(re.findall(r"\S+",s))
def save_task(source,replacement,out,*,start=0,end=None,skill='doctor-text-edit',preserve_numbers=True,previous=None):
    source=Path(source);source_bytes=source.read_bytes();old=source_bytes.decode('utf8');end=len(old) if end is None else end
    if not 0<=start<=end<=len(old):raise ValueError('Invalid exact character scope')
    if preserve_numbers and numbers(old[start:end])!=numbers(replacement):raise ValueError('NUMERIC_CHANGE: source/replacement differ; no automatic rewrite')
    target=Path(out)
    if target.exists():raise ValueError('Preserve previous version; choose a new directory')
    if previous:
        if Path(previous).resolve()!=source.parent.resolve():raise ValueError('Previous task must contain this source version')
        record=json.loads((Path(previous)/'receipt.json').read_text(encoding='utf8'))
        if record.get('result_sha256')!=hashlib.sha256(source_bytes).hexdigest():raise ValueError('Selected prior result changed; choose the actual version explicitly')
    target.mkdir(parents=True)
    text=old[:start]+replacement+old[end:]
    (target/'source.txt').write_bytes(source.read_bytes());(target/'result.md').write_bytes(text.encode('utf8'))
    receipt={'skill':skill,'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'result_sha256':hashlib.sha256(text.encode()).hexdigest(),'scope':{'start':start,'end':end},'outside_scope_unchanged':True,'numeric_tokens_preserved':numbers(old[start:end])==numbers(replacement),'previous':str(previous) if previous else None,'semantic_review':'HOST_REQUIRED','status':'REVIEW_PENDING'}
    (target/'receipt.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf8');return receipt
CITE=re.compile(r'\[((?:\d+\s*(?:[-–,，]\s*\d+\s*)*)?)\]')
def cited_ids(text):
    ids=[]
    for m in CITE.finditer(text):
        if not m[1]:continue
        for piece in re.split('[,，]',m[1]):
            span=re.split('[-–]',piece.strip());a=int(span[0]);b=int(span[-1])
            if b<a or b-a>500:raise ValueError('Ambiguous citation range')
            ids.extend(range(a,b+1))
    return ids

def align(body,references):
    # Supports numeric brackets only; other styles are a host task, explicitly marked.
    entries={};duplicate=[]
    for line in references.splitlines():
        m=re.match(r'^\s*\[(\d+)\]\s+(.+)',line)
        if m:
            n=int(m[1])
            if n in entries:duplicate.append(n)
            entries[n]=m[2]
    seen=cited_ids(body);order=list(dict.fromkeys(seen))
    return {'style':'numeric brackets only','cited_order':order,'missing_entries':sorted(set(seen)-entries.keys()),'unused_entries':sorted(entries.keys()-set(seen)),'duplicate_entry_numbers':duplicate,'first_appearance_mapping':{str(n):i for i,n in enumerate(order,1)},'identity_and_claim_support':'NOT_CHECKED','status':'REVIEW_PENDING','reference_entries':entries}
def main():
    p=argparse.ArgumentParser();sub=p.add_subparsers(dest='cmd',required=True)
    w=sub.add_parser('count');w.add_argument('text',type=Path);w.add_argument('--mode',choices=['words','characters'],default='words')
    a=sub.add_parser('align');a.add_argument('body',type=Path);a.add_argument('references',type=Path)
    t=sub.add_parser('save');t.add_argument('source',type=Path);t.add_argument('replacement',type=Path);t.add_argument('--out',required=True);t.add_argument('--start',type=int,default=0);t.add_argument('--end',type=int);t.add_argument('--skill',default='doctor-text-edit');t.add_argument('--previous',type=Path)
    args=p.parse_args()
    if args.cmd=='count':print(json.dumps({'count':word_count(args.text.read_text()) if args.mode=='words' else len(re.sub(r'\s','',args.text.read_text())),'method':'Whitespace-separated tokens (numbers/hyphens kept)' if args.mode=='words' else 'Non-whitespace characters including punctuation','journal_specific':False}))
    elif args.cmd=='align':print(json.dumps(align(args.body.read_text(),args.references.read_text()),ensure_ascii=False,indent=2))
    else:print(json.dumps(save_task(args.source,args.replacement.read_text(),args.out,start=args.start,end=args.end,skill=args.skill,previous=args.previous),ensure_ascii=False,indent=2))

if __name__=='__main__':
    try:main()
    except (ValueError,KeyError,UnicodeError,OSError) as e:
        print(json.dumps({'status':'BLOCKED_VALIDATION' if isinstance(e,(ValueError,KeyError)) else 'BLOCKED_ENVIRONMENT','reason':str(e),'next_step':'保留原件；核所选范围/数字或文件访问，再另存新版本。'},ensure_ascii=False),file=sys.stderr)
        sys.exit(2 if isinstance(e,(ValueError,KeyError)) else 3)
