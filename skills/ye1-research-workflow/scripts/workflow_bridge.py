"""Thin host adapters for delivered modules; never scientific self-approval."""

# All data-bearing streams stay behind the controlled local adapter.
if __name__ == '__main__':
    import sys as _privacy_sys
    if '--help' not in _privacy_sys.argv[1:]:
        from privacy_boundary import cli_local_entry
        cli_local_entry()

import argparse,importlib.util,json
from pathlib import Path
import project

MAIN=Path(__file__).resolve().parents[1]
def module(group,slug,script):
    path=MAIN/'modules'/group/slug/'scripts'/script
    spec=importlib.util.spec_from_file_location('ye1_'+path.stem,path)
    value=importlib.util.module_from_spec(spec);spec.loader.exec_module(value);return value

def receive(root,handoff):
    root=Path(root).resolve();state=project.check(root,project.load(root));path=project.local(root,handoff)
    crf=module('study-design-crf','ye1-collection-resume','study_workpack.py')
    receipt=crf.validate_handoff(path);h=project.read(path)
    if (h['case_kind']=='SYNTHETIC')!=state['synthetic']:raise ValueError('Cannot change synthetic identity')
    source=project.local(root,(path.parent/h['source']['path']).resolve())
    project.returned(root,source,path)
    state=project.load(root)
    state['crf_handoff']={'path':str(path.relative_to(root)),'sha256':project.sha(path),'receipt':receipt,
        'findings':h['findings'],'ethics':h['ethics'],'scope':'Reception only; no analysis or publication permission'}
    project.save(root,state,{'action':'crf_handoff_received'})
    return receipt

def verify_review(root,data,dictionary,plan,review):
    root=Path(root).resolve();state=project.check(root,project.load(root));review_path=project.local(root,review);r=project.read(review_path)
    stages=project.STAGES[state['mode']];prior=stages[:stages.index('analysis')]
    if any(state['stages'][s]['status']!='COMPLETE' for s in prior):raise ValueError('Complete input/QC/feasibility/explicit plan confirmation before analysis')
    if state['confirmations']['plan']['target_sha256']!=project.sha(project.local(root,state['plan']['path'])):raise ValueError('Current user plan confirmation required')
    paths={k:project.local(root,v) for k,v in {'data':data,'dictionary':dictionary,'plan':plan}.items()}
    if r.get('schema')!='ye1-method-review/1' or not r.get('rationale'):raise ValueError('Actual host method and permission review required')
    if r.get('plan_confirmation_sha256')!=state['confirmations']['plan']['target_sha256']:raise ValueError('Method review targets another confirmed plan')
    if r.get('inputs')!={k:project.sha(p) for k,p in paths.items()}:raise ValueError('Method review/input mismatch')
    lineage=r.get('lineage',{})
    if state['source']['path'] not in lineage or lineage[state['source']['path']]!=state['source']['sha256']:raise ValueError('Original data lineage required')
    for rel,h in lineage.items():
        if project.sha(project.local(root,rel))!=h:raise ValueError('Data lineage changed')
    plan_data=project.read(paths['plan']);task_ids={t['id'] for t in plan_data['tasks']}
    if set(r.get('allowed_task_ids',[]))!=task_ids:raise ValueError('Every method needs explicit scope review')
    if state.get('crf_handoff'):
        hp=project.local(root,state['crf_handoff']['path'])
        module('study-design-crf','ye1-collection-resume','study_workpack.py').validate_handoff(hp)
        h=project.read(hp);blocked={a for f in h['findings'] if f['severity']=='CRITICAL' and f['status']!='RESOLVED' for a in f['affects']}
        requested=set(r.get('requested_activities',[]))
        if not requested or requested & blocked:raise ValueError('CRF activity restriction applies to requested analysis')
        if any(t['kind']!='describe' for t in plan_data['tasks']) and 'CONFIRMATORY' not in requested:raise ValueError('Inferential method activity must be explicitly reviewed')
    if r.get('synthetic_only') is not state['synthetic']:raise ValueError('Method review synthetic identity mismatch')
    return paths,r

def merge_patch(root,analysis_dir):
    root=Path(root).resolve();directory=Path(analysis_dir).resolve()
    patch_path=project.local(root,directory/'state-patch.json');analysis_path=project.local(root,directory/'analysis.json')
    patch=project.read(patch_path);analysis=project.read(analysis_path)
    if patch.get('schema')!='ye1-state-patch-v1' or patch['active_versions']['analysis']!=project.sha(analysis_path):raise ValueError('Analysis patch binding mismatch')
    for rel,h in analysis['frozen_files'].items():
        if project.sha(project.local(root,directory/rel))!=h:raise ValueError('Analysis supporting file changed')
    state=project.check(root,project.load(root))
    if analysis.get('definition_change'):raise ValueError('Use a newly confirmed project revision for changed methods/definitions')
    state['analysis_active_versions']=patch['active_versions']
    state.setdefault('facts',[]).extend(patch['facts'])
    state['analysis_pending']=patch['pending']
    state['analysis_impact']={k:patch[k] for k in ['invalidate_results','preserve_unaffected_results','invalidate_manuscript_confirmation']}
    state['analysis_patch']={'path':str(patch_path.relative_to(root)),'sha256':project.sha(patch_path)}
    if patch['invalidate_manuscript_confirmation']:
        for s in ['analysis','evidence','manuscript','review','delivery']:
            state['stages'][s]={'status':'PENDING','evidence':{},'reason':'Analysis update invalidated downstream; previous evidence is retained in history'}
        state['confirmations'].pop('manuscript',None)
        state['next_step']='新结果已登记；重核受影响图/主张/全文，旧稿确认失效。'
    project.save(root,state,{'action':'analysis_patch_merged','invalidated':patch['invalidate_manuscript_confirmation']})
    return state

def analyze(root,data,dictionary,plan,review,out,rscript=None):
    paths,r=verify_review(root,data,dictionary,plan,review)
    root=Path(root).resolve();target=(root/out).resolve()
    if not target.is_relative_to(root):raise ValueError('Keep analysis inside project')
    engine=module('data-analysis','ye1-association','data_engine.py')
    result=engine.analyze(paths['data'],project.read(paths['dictionary']),project.read(paths['plan']),target,rscript=rscript)
    merge_patch(root,target)
    return {'status':result['status'],'task_states':{x['id']:x['status'] for x in result['results']},'scientific_acceptance':False}

def main():
    p=argparse.ArgumentParser(description=__doc__);s=p.add_subparsers(dest='command',required=True)
    a=s.add_parser('receive');a.add_argument('root');a.add_argument('handoff')
    a=s.add_parser('merge-analysis');a.add_argument('root');a.add_argument('analysis')
    a=s.add_parser('analyze');a.add_argument('root')
    for n in ['data','dictionary','plan','review','out']:a.add_argument('--'+n,required=True)
    a.add_argument('--rscript')
    a=p.parse_args()
    try:
        if a.command=='receive':r=receive(a.root,a.handoff)
        elif a.command=='merge-analysis':r=merge_patch(a.root,a.analysis);r={'revision':r['revision']}
        else:r=analyze(a.root,a.data,a.dictionary,a.plan,a.review,a.out,a.rscript)
        print(json.dumps(r,ensure_ascii=False))
    except (ValueError,KeyError,OSError) as e:raise SystemExit('BLOCKED: '+str(e))
if __name__=='__main__':main()
