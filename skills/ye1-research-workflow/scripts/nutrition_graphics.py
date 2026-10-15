# Pure help exits before data reads, directory writes or plotting imports.
if __name__ == '__main__':
    import sys as _privacy_sys
    _privacy_args = _privacy_sys.argv[1:]
    if _privacy_args in (['--help'], ['-h']):
        print('Usage: nutrition_graphics.py OUTPUT_DIR')
        raise SystemExit(0)
    from privacy_boundary import cli_local_entry
    cli_local_entry()
    if len(_privacy_args) != 1 or any(a in {'--help', '-h'} for a in _privacy_args):
        print('INVALID_ARGUMENTS: use --help alone for usage')
        raise SystemExit(2)

"""Restricted synthetic nutrition fixture plotting, not a clinical modeling engine."""
import sys,json
from pathlib import Path
import graphics as g
from matplotlib import pyplot as plt
out=Path(sys.argv[1]);r=json.loads((out/'results.json').read_text());fd=json.loads((out/'figure-data.json').read_text())
for lang in ['zh','en']:
 cn=lang=='zh'
 with g.theme(lang):
  x,y=zip(*fd['scatter_pairs'])
  fig,data=g.scatter(x,y,'入院白蛋白 (g/L)' if cn else 'Admission albumin (g/L)','住院天数（天）' if cn else 'Length of stay (days)','白蛋白与住院天数' if cn else 'Albumin and length of stay','合成数据 · 完整记录 n=76' if cn else 'Synthetic complete records; n=76')
  g.export(fig,data,out/'graphics'/lang,'albumin-stay');plt.close(fig)
  fig,data=g.histogram(fd['stay_days'],r['histogram']['edges'],'住院天数（天）' if cn else 'Length of stay (days)','住院天数分布' if cn else 'Length-of-stay distribution','合成数据 · 有效 n=79' if cn else 'Synthetic available records; n=79')
  g.export(fig,data,out/'graphics'/lang,'stay-distribution');plt.close(fig)
