"""Small local project ledger for the host-led Ye1 workflow.

Records evidence and explicit decisions; does not perform scientific judgment,
authenticate a clinician, or generate a manuscript. All paths stay in the project.
"""

# All data-bearing streams stay behind the controlled local adapter.
if __name__ == '__main__':
    import sys as _privacy_sys
    if '--help' not in _privacy_sys.argv[1:]:
        from privacy_boundary import cli_local_entry
        cli_local_entry()

import argparse
import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

STAGES = {
    'existing_data': ['intake', 'qc', 'feasibility', 'plan', 'analysis', 'evidence', 'manuscript', 'review', 'delivery'],
    'plan_collection': ['intake', 'feasibility', 'plan', 'crf', 'collection', 'qc', 'analysis', 'evidence', 'manuscript', 'review', 'delivery'],
}
LABELS = dict(zip(['intake','qc','feasibility','plan','crf','collection','analysis','evidence','manuscript','review','delivery'],
                 ['目标与现有资料','数据质控与首反馈','研究问题与发表可行性','方案讨论与确认','CRF与变量字典','收集与返表','真实分析与图表','文献与主张核证','完整中英文稿','正文图表审阅件','版本确认与初稿包']))

def now(): return datetime.now(timezone.utc).isoformat()
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p): return json.loads(Path(p).read_text(encoding='utf8'))
def write(p, value): Path(p).write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n', encoding='utf8')

def local(root, path):
    root=Path(root).resolve(); p=Path(path)
    if not p.is_absolute(): p=root/p
    if not p.resolve().is_relative_to(root): raise ValueError('Evidence must be inside this project')
    current=p
    while current != root:
        if current.is_symlink(): raise ValueError('Symlink evidence is not supported')
        current=current.parent
    if not p.is_file(): raise ValueError('Missing evidence: '+str(p))
    return p

def frozen(root, paths):
    if not paths: raise ValueError('Actual output evidence is required')
    return {str(local(root,p).relative_to(Path(root).resolve())):sha(local(root,p)) for p in paths}

def load(root):
    state=read(Path(root)/'ye1-project.json')
    if state.get('schema')!='ye1-project/1': raise ValueError('Unsupported project ledger')
    return state

def drift(root, state):
    result={}
    for stage,record in state['stages'].items():
        changed=[]
        for rel,digest in record.get('evidence',{}).items():
            try: matches=sha(local(root,rel))==digest
            except ValueError: matches=False
            if not matches: changed.append(rel)
        if changed: result[stage]=changed
    return result

def check(root,state):
    changed=drift(root,state)
    if changed: raise ValueError('Recorded evidence changed; create a new revision: '+json.dumps(changed,ensure_ascii=False))
    return state

def save(root,state,event):
    root=Path(root); history=root/'history';history.mkdir(exist_ok=True)
    previous=root/'ye1-project.json'
    if previous.exists():
        target=history/f"project-{state['revision']:04d}.json"
        if target.exists(): raise ValueError('Preserve existing project revision')
        shutil.copyfile(previous,target)
    state['revision']+=1;state['updated_at']=now();state['events'].append({'at':state['updated_at'],**event})
    write(previous,state); progress(root,state)

def progress(root,state=None):
    root=Path(root);state=state or load(root);changed=drift(root,state)
    text=['# Ye1-科研全流程 当前进度','',state['goal'],'',
          '数据身份：'+('合成工程演示；所有模拟确认均不代表临床批准。' if state['synthetic'] else '用户研究资料；科学确认以实际答复为准。'),'',
          '| 步骤 | 当前状态 | 已有实物 |','| --- | --- | --- |']
    dirty=False
    for stage in STAGES[state['mode']]:
        record=state['stages'][stage];dirty=dirty or stage in changed
        status='STALE_REVIEW_REQUIRED' if dirty and record['status']=='COMPLETE' else record['status']
        links=' · '.join(f'[{Path(p).name}]({p})' for p in record.get('evidence',{})) or '尚未生成'
        text.append(f"| {LABELS[stage]} | {status} | {links} |")
    text+=['','下一步：'+state['next_step'],'','记录说明：COMPLETE表示宿主已提交所列实物；科学支持与实际阅读须核对应记录，状态字段本身不是审稿结论。']
    if changed:text+=['','检测到证据变动：'+json.dumps(changed,ensure_ascii=False)+'。请保留旧版并修订；旧下游不能继续当作当前结果。']
    (root/'进度.md').write_text('\n'.join(text)+'\n',encoding='utf8')
    return {'revision':state['revision'],'mode':state['mode'],'next_step':state['next_step'],'changed_evidence':changed,'stages':state['stages']}

def start(root,goal,mode,source=None,synthetic=False):
    root=Path(root).resolve()
    if root.exists(): raise ValueError('Use a new project directory; resume existing projects with status')
    if mode not in STAGES or not goal.strip(): raise ValueError('A natural-language goal and valid starting mode are required')
    if mode=='existing_data' and source is None: raise ValueError('Existing-data mode requires an input file')
    if source and (not Path(source).is_file() or Path(source).is_symlink()):raise ValueError('A regular input file is required')
    root.mkdir(parents=True);(root/'inputs').mkdir();(root/'goal.txt').write_text(goal+'\n',encoding='utf8')
    state={'schema':'ye1-project/1','mode':mode,'goal':goal,'synthetic':synthetic,'revision':0,'created_at':now(),
           'stages':{s:{'status':'PENDING','evidence':{}} for s in STAGES[mode]},'confirmations':{},'events':[],
           'next_step':'读取原表并给出质控首反馈。' if source else '根据科室、常见患者和现实可收变量讨论研究方向。'}
    outputs=['goal.txt']
    if source:
        dest=root/'inputs'/('original'+Path(source).suffix.lower());shutil.copyfile(source,dest)
        state['source']={'path':str(dest.relative_to(root)),'sha256':sha(dest),'original_name':Path(source).name};outputs.append(state['source']['path'])
        if dest.suffix.lower() in {'.csv','.xlsx'}:
            try:
                from profile import profile
                write(root/'inputs/structure.json',profile(dest));outputs.append('inputs/structure.json')
            except ImportError:
                state['next_step']='已保存原表；现有环境不能解析此格式，等待已有可用读取工具，未完成全表质控。'
    state['stages']['intake']={'status':'COMPLETE','summary':'已保存目标与实际输入；结构盘点不等于语义质控。','evidence':frozen(root,outputs)}
    save(root,state,{'action':'start','mode':mode});return state

def complete(root,stage,outputs,summary,next_step):
    root=Path(root).resolve();state=check(root,load(root));order=STAGES[state['mode']]
    if stage not in order or stage in {'intake','plan','collection','delivery'}:raise ValueError('Use dedicated start, plan/confirm, returned-data, or delivery action')
    if state['stages'][stage]['status']=='COMPLETE':raise ValueError('Already complete; create a new revision instead of overwriting')
    prior=order[:order.index(stage)]
    if any(state['stages'][s]['status']!='COMPLETE' for s in prior):raise ValueError('Complete preceding stages with actual evidence first')
    if stage in {'analysis','manuscript'}:
        confirmation=state['confirmations'].get('plan')
        if not confirmation or sha(local(root,state['plan']['path']))!=confirmation['target_sha256']:raise ValueError('Current plan lacks explicit confirmation')
        if not state.get('source'):raise ValueError('Actual returned data required')
    if not summary.strip() or not next_step.strip():raise ValueError('Explain the actual outcome and next step')
    state['stages'][stage]={'status':'COMPLETE','summary':summary,'evidence':frozen(root,outputs),'record_kind':'HOST_RECORDED_ACTUAL_OUTPUTS'}
    state['next_step']=next_step;save(root,state,{'action':'complete','stage':stage});return state

def plan(root,path):
    root=Path(root).resolve();state=check(root,load(root))
    if state['stages']['feasibility']['status']!='COMPLETE':raise ValueError('First record the feasibility discussion')
    p=local(root,path);state['plan']={'path':str(p.relative_to(root)),'sha256':sha(p)}
    state['stages']['plan']={'status':'WAITING_USER_CONFIRMATION','evidence':frozen(root,[path])}
    state['next_step']='请确认当前研究问题、变量定义、研究单位和分析方案；宿主不能代签。'
    save(root,state,{'action':'plan_proposed'});return state

def confirm(root,record_path):
    root=Path(root).resolve();state=check(root,load(root));record=read(local(root,record_path))
    if state['stages']['plan']['status']!='WAITING_USER_CONFIRMATION':raise ValueError('No pending plan')
    if record.get('kind') not in {'user','simulated_user'}:raise ValueError('A user decision is required; host approval is not a scientific confirmation')
    if record['kind']=='user' and (record.get('source_kind')!='direct_user' or not record.get('source_locator')):raise ValueError('Unknown plan source; retain pending until a directly quotable user message is recorded')
    if record['kind']=='simulated_user' and not state['synthetic']:raise ValueError('Simulated confirmation forbidden for real data')
    for key in ['actor','quote','date_utc','source_path','target_sha256']:
        if not isinstance(record.get(key),str) or not record[key].strip():raise ValueError('Missing confirmation provenance: '+key)
    if record.get('decision')!='CONFIRM_PLAN' or record['target_sha256']!=state['plan']['sha256']:raise ValueError('Explicit confirmation must target this plan version')
    source=local(root,record['source_path'])
    if record['quote'] not in source.read_text(encoding='utf8'):raise ValueError('Decision quote is absent from the source record')
    state['confirmations']['plan']={**record,'record_path':str(local(root,record_path).relative_to(root)),'record_sha256':sha(local(root,record_path)),'source_sha256':sha(source)}
    state['stages']['plan']={'status':'COMPLETE','summary':'明确'+('模拟用户' if record['kind']=='simulated_user' else '用户')+'方案确认；不等于稿件版本确认。','evidence':frozen(root,[state['plan']['path'],record_path,record['source_path']])}
    state['next_step']='按确认方案生成CRF和字典。' if state['mode']=='plan_collection' else '按确认方案实际清洗、计算并出图。'
    save(root,state,{'action':'plan_confirmed','kind':record['kind']});return state

def returned(root,source,report):
    root=Path(root).resolve();state=check(root,load(root))
    if state['mode']!='plan_collection' or state['stages']['crf']['status']!='COMPLETE':raise ValueError('A confirmed collection project and generated CRF are required')
    if state.get('source'):raise ValueError('Preserve this return; use a new project revision for further data')
    p=local(root,source);r=local(root,report)
    state['source']={'path':str(p.relative_to(root)),'sha256':sha(p),'original_name':p.name}
    state['stages']['collection']={'status':'COMPLETE','evidence':frozen(root,[p,r]),'summary':'实际返表已收到；下一步核对字典、单位、时间与完整性。'}
    state['next_step']='按已确认字典检查返表并给出QC首反馈；不直接跳到分析。'
    save(root,state,{'action':'returned_data'});return state

def deliver(root,review,record_path,out,test_only=False):
    root=Path(root).resolve();state=check(root,load(root))
    if any(v['status']!='COMPLETE' for k,v in state['stages'].items() if k!='delivery'):raise ValueError('Actual workflow/review evidence must be complete before delivery')
    record=read(local(root,record_path))
    if bool(record.get('synthetic_test',True))!=state['synthetic']:raise ValueError('Confirmation cannot change the project synthetic identity')
    target=root/out;tree=(root/review).resolve()
    if not tree.is_relative_to(root) or not target.resolve().is_relative_to(root):raise ValueError('Keep the delivery evidence inside this project')
    from review_delivery import package
    package(tree,record,target,test_only=test_only)
    state['stages']['delivery']={'status':'COMPLETE','summary':'模拟确认测试包；非真实临床批准。' if test_only else '用户确认版本初稿包。','evidence':frozen(root,[record_path,target])}
    state['next_step']='已交对应版本的'+('合成测试包；无临床投稿资格。' if test_only else '初稿包；后续修改另存版本。')
    save(root,state,{'action':'delivery','test_only':test_only});return state

def main():
    p=argparse.ArgumentParser(description=__doc__);s=p.add_subparsers(dest='action',required=True)
    a=s.add_parser('start');a.add_argument('root');a.add_argument('--goal',required=True);a.add_argument('--mode',choices=STAGES,required=True);a.add_argument('--source');a.add_argument('--synthetic',action='store_true')
    a=s.add_parser('status');a.add_argument('root')
    a=s.add_parser('complete');a.add_argument('root');a.add_argument('stage');a.add_argument('--outputs',nargs='+',required=True);a.add_argument('--summary',required=True);a.add_argument('--next',required=True)
    for name,arg in [('plan','path'),('confirm-plan','record')]:
        a=s.add_parser(name);a.add_argument('root');a.add_argument(arg)
    a=s.add_parser('returned-data');a.add_argument('root');a.add_argument('source');a.add_argument('report')
    a=s.add_parser('deliver');a.add_argument('root');a.add_argument('review');a.add_argument('record');a.add_argument('--out',required=True)
    a=p.parse_args()
    try:
        if a.action=='start':result=start(a.root,a.goal,a.mode,a.source,a.synthetic)
        elif a.action=='status':result=progress(a.root)
        elif a.action=='complete':result=complete(a.root,a.stage,a.outputs,a.summary,a.next)
        elif a.action=='plan':result=plan(a.root,a.path)
        elif a.action=='confirm-plan':result=confirm(a.root,a.record)
        elif a.action=='returned-data':result=returned(a.root,a.source,a.report)
        else:result=deliver(a.root,a.review,a.record,a.out)
        print(json.dumps({'status':'RECORDED','revision':result['revision'],'next_step':result['next_step']},ensure_ascii=False))
    except (ValueError,KeyError) as e:raise SystemExit('BLOCKED: '+str(e))
if __name__=='__main__':main()
