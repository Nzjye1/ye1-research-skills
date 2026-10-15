"""Materialize host-authored bilingual prose with explicit result placeholders.
Not an automatic scientific author or reference verifier. No raw data consumed.
"""

# All data-bearing streams stay behind the controlled local adapter.
if __name__ == '__main__':
    import sys as _privacy_sys
    if '--help' not in _privacy_sys.argv[1:]:
        from privacy_boundary import cli_local_entry
        cli_local_entry()

import argparse,json,re,subprocess
from pathlib import Path
from pipeline import load,save,sha,Blocked
import materialize
from references import bind
from gate_contract import require_gate

def compose(result_dir,draft,output,gate=None,case=None,evidence_root=None,source=None,question=None,synthetic_demo=False):
    permission=require_gate(gate,case,evidence_root,source,question,"DRAFT",synthetic_demo)
    base=Path(result_dir); out=Path(output); data=load(draft); results=load(base/'results.json')
    manifest=base/'input-manifest.json'
    bound_source=results.get('input_sha256') if not manifest.exists() else load(manifest).get('source_sha256')
    if bound_source!=sha(source): raise Blocked('Results source fingerprint mismatch')
    if out.exists(): raise Blocked('Output already exists; preserve prior version.')
    def resolve(key):
        v=results
        for part in key.split('.'): v=v[part]
        return v
    if synthetic_demo and data.get('scientific_confirmation')!='simulated': raise Blocked('Synthetic demo requires explicit simulated confirmation')
    if not synthetic_demo and data.get('scientific_confirmation')!='confirmed': raise Blocked('Host must record actual plan confirmation, not infer it.')
    if data.get('reference_review')!='identity_and_content_checked': raise Blocked('Identity and content checks required; metadata alone is insufficient.')
    data,reference_qc=bind(data,base)
    docs={};claims=[]
    for lang in ['zh','en']:
        doc=data[lang]; headings=set()
        for p in doc['paragraphs']:
            if p['text'] in {'摘要','引言','方法','结果','讨论','局限','参考文献','Abstract','Introduction','Methods','Results','Discussion','Limitations','References'}: headings.add(p['text'])
            tpl=p['text']
            for key,precision in re.findall(r'\{\{([\w.]+):(\d+)\}\}',tpl):
                v=resolve(key); display='NA' if v is None else f'{v:.{int(precision)}f}'
                p['text']=p['text'].replace('{{'+key+':'+precision+'}}',display)
                claims.append({'lang':lang,'key':key,'source_value':v,'display':display})
            if '{{' in p['text']: raise Blocked('Unresolved result placeholder.')
        needed={'摘要','引言','方法','结果','讨论','局限','参考文献'} if lang=='zh' else {'Abstract','Introduction','Methods','Results','Discussion','Limitations','References'}
        if not needed<=headings: raise Blocked('Incomplete manuscript sections.')
        doc['source_package_ref']=sha(base/'results.json')
        # Figure assets must originate from the selected result version.
        for fig in doc['figures']:
            actual=base/fig['relative_path']
            if fig['sha256']!=sha(actual): raise Blocked('Figure version/hash mismatch.')
        materialize.validate(doc); docs[lang]=doc
    out.mkdir(parents=True); save(out/'reference-qc.json',reference_qc);save(out/'host-draft.json',data);save(out/'numeric-claims.json',claims)
    failures=[]
    for lang,doc in docs.items():
        try: materialize.materialize(doc,base,out/lang)
        except (ImportError,OSError,subprocess.SubprocessError) as e: failures.append(e)
    if failures:
        save(out/'receipt.json',{'status':'PARTIAL_READY','stage':'TEXT_READY_DOCX_PENDING','languages_with_text':[lang for lang in docs if (out/lang/'manuscript.md').exists()],'source_results_sha256':sha(base/'results.json')})
        raise failures[0]
    save(out/'receipt.json',{'status':'MATERIALIZED','stage':'CUSTOMER_REVIEW_PENDING','scope':'Host-authored prose and user-supplied evidence; declared placeholders validated only. Does not discover all semantic/numeric errors. Render and doctor scientific review remain required.','source_results_sha256':sha(base/'results.json')})

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('result_dir');p.add_argument('draft');p.add_argument('--out',required=True);
    for flag in ['gate','case','evidence-root','source','question']: p.add_argument('--'+flag,required=True)
    p.add_argument('--synthetic-demo',action='store_true');a=p.parse_args()
    try: compose(a.result_dir,a.draft,a.out,a.gate,a.case,a.evidence_root,a.source,a.question,a.synthetic_demo)
    except (Blocked,KeyError,ValueError) as e: raise SystemExit('BLOCKED: '+str(e))
