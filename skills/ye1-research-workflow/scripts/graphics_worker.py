# Pure help exits before data reads, directory writes or plotting imports.
if __name__ == '__main__':
    import sys as _privacy_sys
    _privacy_args = _privacy_sys.argv[1:]
    if _privacy_args in (['--help'], ['-h']):
        print('Usage: graphics_worker.py INPUT_JSON OUTPUT_DIR')
        raise SystemExit(0)
    from privacy_boundary import cli_local_entry
    cli_local_entry()
    if len(_privacy_args) != 2 or any(a in {'--help', '-h'} for a in _privacy_args):
        print('INVALID_ARGUMENTS: use --help alone for usage')
        raise SystemExit(2)

import sys,json,shutil
from pathlib import Path
from integration_adapter import plots
x=json.loads(Path(sys.argv[1]).read_text());out=Path(sys.argv[2])
for lang in ['en','zh']:
    target=out/'graphics'/lang;target.mkdir(parents=True)
    plots(x['selected'],x['pair'],target,language=lang,synthetic=x['synthetic'])
for p in (out/'graphics/en').iterdir():shutil.copy(p,out/p.name)
