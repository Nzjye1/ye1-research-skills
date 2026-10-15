"""Stage boundary for CLIs: preserve diagnostics without traceback in UI."""

allowed={'pipeline','profile','compose','render','materialize','graphics_worker','nutrition_graphics','review_delivery','publication_gate','resume','task_io','project','figure_task'}
# Only exact help requests bypass data execution; forwarded stage help exits in its parser.
if __name__ == '__main__':
    import sys as _privacy_sys
    _privacy_args = _privacy_sys.argv[1:]
    if _privacy_args in (['--help'], ['-h']):
        print('Usage: safe_run.py STAGE [ARGS]; stages: ' + ', '.join(sorted(allowed)))
        raise SystemExit(0)
    _stage_help = len(_privacy_args) == 2 and _privacy_args[0] in allowed and _privacy_args[1] in {'--help', '-h'}
    if not _stage_help:
        from privacy_boundary import cli_local_entry
        cli_local_entry()

import runpy,sys,subprocess,json
from pathlib import Path
import environment
if len(sys.argv)<2 or sys.argv[1] not in allowed:raise SystemExit('Choose an existing stage: '+', '.join(sorted(allowed)))
if sys.version_info<(3,11):
    print('BLOCKED_ENVIRONMENT：本包脚本需Python 3.11+；文本任务可由宿主继续，不自动安装。',file=sys.stderr);sys.exit(3)
name=sys.argv.pop(1);sys.argv[0]=str(Path(__file__).with_name(name+'.py'))
out=None
for flag in ['--out','--output-root']:
    if flag in sys.argv and sys.argv.index(flag)+1<len(sys.argv):out=sys.argv[sys.argv.index(flag)+1]
try:runpy.run_path(sys.argv[0],run_name='__main__')
except (ImportError,OSError,subprocess.SubprocessError) as e:sys.exit(environment.failure(e,out))
except (ValueError,KeyError,AssertionError) as e:
    print(json.dumps({'status':'BLOCKED_VALIDATION','reason':str(e),'next_step':'核对当前材料、合同或科学条件；不自动修改来源。'},ensure_ascii=False),file=sys.stderr);sys.exit(2)
