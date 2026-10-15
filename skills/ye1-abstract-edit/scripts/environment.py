"""Request-specific checks using stdlib; no installations or research-data probes."""

# All data-bearing streams stay behind the controlled local adapter.
if __name__ == '__main__':
    import sys as _privacy_sys
    if '--help' not in _privacy_sys.argv[1:]:
        from privacy_boundary import cli_local_entry
        cli_local_entry()

import argparse,importlib,json,os,subprocess,sys,tempfile,traceback
from pathlib import Path
from datetime import datetime,timezone
CAPS={'text':[], 'r':[], 'xlsx':['openpyxl'], 'docx':['docx'], 'graphics':['numpy','matplotlib'], 'pages':['PIL']}
def check(request='all',runtime=None):
    if request not in {*CAPS,'pdf','all'}:raise ValueError('Unknown capability request')
    if request=='all':
        parts={name:check(name,runtime) for name in ['text','xlsx','docx','r','pdf','pages']}
        graphics=os.environ.get('DOCTOR_PAPER_GRAPHICS_PYTHON')
        if graphics and Path(graphics).resolve()!=Path(sys.executable).resolve():
            try:
                r=subprocess.run([graphics,'-B',str(Path(__file__).resolve()),'--request','graphics'],capture_output=True,text=True,timeout=30)
                parts['graphics']=json.loads(r.stdout)
                if r.returncode:parts['graphics']['status']='BLOCKED_ENVIRONMENT'
            except (OSError,subprocess.SubprocessError,ValueError) as e:parts['graphics']={'status':'BLOCKED_ENVIRONMENT','reason':str(e),'executable':graphics}
        else:parts['graphics']=check('graphics',runtime)
        ready=all(r['status']=='READY' for r in parts.values())
        return {'date_utc':datetime.now(timezone.utc).isoformat(),'request':'all','status':'READY' if ready else 'PARTIAL_READY','capabilities':parts,'verification':'import/version only; no file/glyph/method/visual acceptance','next_step':'按当前任务选择可用能力；缺项不自动安装。'}
    deps={}
    # Matplotlib cache belongs to a temporary task probe, never the installed Skill.
    with tempfile.TemporaryDirectory(prefix='doctor-paper-probe-') as cache:
        old=os.environ.get('MPLCONFIGDIR')
        if request=='graphics':os.environ['MPLCONFIGDIR']=cache
        try:
            for name in CAPS.get(request,[]):
                try:
                    m=importlib.import_module(name);deps[name]={'available':True,'version':getattr(m,'__version__','unknown')}
                except (ImportError,OSError,RuntimeError) as e:deps[name]={'available':False,'reason':str(e)}
        finally:
            if old is None:os.environ.pop('MPLCONFIGDIR',None)
            else:os.environ['MPLCONFIGDIR']=old
    external={}
    if request=='r':
        import shutil
        candidate=os.environ.get('YE1_RSCRIPT') or shutil.which('Rscript')
        try:
            if not candidate:raise OSError('No existing Rscript; Python-only and text tasks may remain available')
            run=subprocess.run([candidate,'--vanilla','-e',"stopifnot(requireNamespace('jsonlite',quietly=TRUE));cat(R.version.string)"],capture_output=True,text=True,timeout=15,check=True)
            external['Rscript']={'available':True,'path':candidate,'version':run.stdout.strip()}
        except (OSError,subprocess.SubprocessError) as e:external['Rscript']={'available':False,'reason':str(e)}
    if request in {'pdf','pages'}:
        for name in (['soffice'] if request=='pdf' else ['pdftoppm']):
            p=Path(runtime or '')/'dependencies/bin/override'/name
            try:
                if not runtime or not p.is_file() or not os.access(p,os.X_OK):raise OSError('Explicit existing runtime tool unavailable')
                r=subprocess.run([str(p.resolve()),'--version' if name=='soffice' else '-v'],capture_output=True,text=True,timeout=10,check=True)
                external[name]={'available':True,'path':str(p.resolve()),'version':(r.stdout+r.stderr).strip()}
            except (OSError,subprocess.SubprocessError) as e:external[name]={'available':False,'reason':str(e)}
    ready=sys.version_info>=(3,11) and all(x['available'] for x in list(deps.values())+list(external.values()))
    return {'date_utc':datetime.now(timezone.utc).isoformat(),'python':sys.version,'executable':sys.executable,'request':request,'dependencies':deps,'tools':external,'status':'READY' if ready else 'BLOCKED_ENVIRONMENT','python_supported':sys.version_info>=(3,11),'text_host_possible':True,'verification':'import/version only; no file, glyph, method or visual acceptance','next_step':'Proceed with this request' if ready else '保留文本/已成功检查点，选择已有可用环境续接缺失步骤；不自动安装。'}
def failure(exc,out=None):
    r={'status':'BLOCKED_ENVIRONMENT','error_type':type(exc).__name__,'reason':str(exc),'next_step':'保留实际已成功的文本/结果；使用已有可用环境续接，不自动安装。','diagnostic_saved':False}
    if out is not None:
        p=Path(out)
        if p.is_dir():
            try:
                # Do not overwrite earlier attempts, including a pre-existing output tree.
                with tempfile.NamedTemporaryFile(mode='w',prefix='environment-',suffix='.log',dir=p,delete=False,encoding='utf8') as f:
                    f.write(traceback.format_exc())
                    if isinstance(exc,subprocess.CalledProcessError):f.write('\nSUBPROCESS STDERR:\n'+str(exc.stderr or ''))
                    r['diagnostic_saved']=True;r['diagnostic_file']=Path(f.name).name
            except OSError:pass
    print(json.dumps(r,ensure_ascii=False),file=sys.stderr);return 3
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--request',choices=[*CAPS,'pdf','all'],default='all');p.add_argument('--runtime-root');a=p.parse_args()
    r=check(a.request,a.runtime_root);print(json.dumps(r,ensure_ascii=False,indent=2));sys.exit(0 if r['status']=='READY' else 3)
