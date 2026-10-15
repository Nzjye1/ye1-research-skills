"""Use an explicitly selected existing Matplotlib Python, no installation."""
import os,sys,json,subprocess
from pathlib import Path

def plots(selected,pair,out,synthetic=False):
    out=Path(out); task=out/'graphics-input.local.json'
    task.write_text(json.dumps({'selected':[{k:float(v) if hasattr(v,'as_tuple') else v for k,v in r.items()} for r in selected],'pair':[{k:float(v) if hasattr(v,'as_tuple') else v for k,v in r.items()} for r in pair],'synthetic':synthetic}))
    executable=os.environ.get('DOCTOR_PAPER_GRAPHICS_PYTHON',sys.executable)
    subprocess.run([executable,str(Path(__file__).with_name('graphics_worker.py')),str(task),str(out)],check=True,capture_output=True,text=True)
    return ['figure-1','figure-2']
