"""Resume only frozen stage inputs in a new directory; never reanalyse or confirm."""

# All data-bearing streams stay behind the controlled local adapter.
if __name__ == '__main__':
    import sys as _privacy_sys
    if '--help' not in _privacy_sys.argv[1:]:
        from privacy_boundary import cli_local_entry
        cli_local_entry()

import argparse,hashlib,json,shutil,subprocess,sys
from pathlib import Path
import pipeline,materialize,environment
from graphics_bridge import plots
from decimal import Decimal

def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def resume_graphics(previous,out):
    previous=Path(previous);out=Path(out);cp=pipeline.load(previous/'checkpoint.json')
    manifest=pipeline.load(previous/'input-manifest.json')
    if cp['source_sha256']!=digest(previous/manifest['snapshot']) or cp['config_sha256']!=digest(previous/'config.json') or cp['results_sha256']!=digest(previous/'results.json'):raise ValueError('Checkpoint changed; re-evaluate affected source/plan')
    for key,name in [('selected_sha256','selected-records.local.json'),('cleaned_sha256','cleaned-records.local.json'),('quality_sha256','quality.json')]:
        if cp.get(key)!=digest(previous/name):raise ValueError('Frozen drawing inputs changed or were not bound; cannot resume')
    if out.exists():raise ValueError('Preserve prior version')
    selected=pipeline.load(previous/'selected-records.local.json')
    for r in selected:
        for k in ['age','crp_first','crp_last','stay_days']:
            if r[k] is not None:r[k]=Decimal(r[k])
    pair=[r for r in selected if r['crp_first'] is not None and r['crp_last'] is not None]
    out.mkdir(parents=True)
    for name in ['results.json','config.json','input-manifest.json','quality.json','selected-records.local.json','cleaned-records.local.json',manifest['snapshot'],'checkpoint.json']:shutil.copy2(previous/name,out/name)
    plots(selected,pair,out,synthetic=pipeline.load(previous/'config.json').get('synthetic',False))
    pipeline.save(out/'resume-receipt.json',{'stage':'GRAPHICS_READY','previous':str(previous),'results_sha256':digest(out/'results.json'),'reanalysis':False,'manuscript':'NOT_GENERATED'})
def resume_pages(pdf,tools,out):
    pdf=Path(pdf);out=Path(out)
    if out.exists():raise ValueError('Preserve prior version')
    if not pdf.read_bytes().startswith(b'%PDF-'):raise ValueError('PDF required')
    tool=materialize.explicit_tool(tools,'pdftoppm');out.mkdir(parents=True)
    subprocess.run([tool,'-png','-r','150',str(pdf.resolve()),str(out/'page')],check=True,timeout=120,capture_output=True)
    pages=list(out.glob('page-*.png'))
    if not pages:raise ValueError('No page images')
    from PIL import Image
    for p in pages:
        with Image.open(p) as im:im.verify()
    pipeline.save(out/'resume-receipt.json',{'stage':'PAGES_READY','pdf_sha256':digest(pdf),'visual':'REQUIRES_INSPECTION','manuscript_changed':False})
if __name__=='__main__':
    p=argparse.ArgumentParser();s=p.add_subparsers(dest='stage',required=True)
    g=s.add_parser('graphics');g.add_argument('previous');g.add_argument('--out',required=True)
    r=s.add_parser('pages');r.add_argument('pdf');r.add_argument('--tools',required=True);r.add_argument('--out',required=True)
    a=p.parse_args()
    try:
        if a.stage=='graphics':resume_graphics(a.previous,a.out)
        else:resume_pages(a.pdf,pipeline.load(a.tools),a.out)
    except (ImportError,OSError,subprocess.SubprocessError) as e:sys.exit(environment.failure(e,a.out))
    except (ValueError,KeyError) as e:raise SystemExit('暂停：'+str(e))
