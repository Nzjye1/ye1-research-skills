"""Draw or style-redraw frozen, source-bound statistical data with existing graphics.

No model fitting, scientific permission, or clinical validity is inferred.
"""

# All data-bearing streams stay behind the controlled local adapter.
if __name__ == '__main__':
    import sys as _privacy_sys
    if '--help' not in _privacy_sys.argv[1:]:
        from privacy_boundary import cli_local_entry
        cli_local_entry()

import argparse,copy,hashlib,json,os
from pathlib import Path

def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p):return json.loads(Path(p).read_text(encoding='utf8'))
def save(p,v):Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf8')

def draw(spec_path,out):
    import graphics as g
    spec_path=Path(spec_path).resolve();spec=load(spec_path);out=Path(out)
    if out.exists():raise ValueError('Use a new output version')
    if spec.get('schema')!='ye1-figure/1':raise ValueError('Expected ye1-figure/1')
    source=(spec_path.parent/spec['source']['path']).resolve()
    if not source.is_file() or source.is_symlink() or digest(source)!=spec['source']['sha256']:raise ValueError('Source missing or changed; frozen figure data must be reviewed again')
    kind=spec['kind'];context=spec['context'];data=spec['data'];style=spec['style']
    language=style['language']
    if language not in {'zh','en'}:raise ValueError('Explicit zh/en figure language required')
    if kind=='histogram':route='distribution'
    else:route=kind
    g.route(route,context)
    science=hashlib.sha256(json.dumps({**{k:spec[k] for k in ['kind','data','context']},'source_sha256':spec['source']['sha256']},sort_keys=True,ensure_ascii=False).encode()).hexdigest()
    title=style['title'];subtitle=style.get('subtitle','');font=style.get('existing_font')
    if style.get('font_scale',1) not in [1,1.1,1.2]:raise ValueError('Readable font scales must be 1/1.1/1.2')
    with g.theme(language,label_text=json.dumps(style,ensure_ascii=False),preferred_font=font):
        if kind=='scatter':fig,values=g.scatter(data['x'],data['y'],style['xlabel'],style['ylabel'],title,subtitle,identity=data.get('identity',False))
        elif kind=='histogram':fig,values=g.histogram(data['values'],data['edges'],style['xlabel'],title,subtitle)
        elif kind=='distribution':fig,values=g.group_distribution(data['groups'],style['group_labels'],style['ylabel'],title,subtitle)
        elif kind=='forest':
            fig,values=g.forest(style['row_labels'],data['estimate'],data['lower'],data['upper'],title,subtitle,measure=style['measure_label'])
            values['interval']=context['interval method']
        elif kind=='difference':
            fig,values=g.difference_forest(style['row_labels'],data['estimate'],data['lower'],data['upper'],title,subtitle,measure=style['measure_label'])
            values['interval']=context['interval method']
        elif kind=='flow':fig,values=g.cohort_flow(data['counts'],title,subtitle)
        elif kind in {'roc','pr','calibration','dca'}:fig,values=g.prediction_plot(kind,data['y'],data['p'],title,subtitle,thresholds=data.get('thresholds'))
        else:raise ValueError('Unsupported figure; provide an actual audited method rather than a decorative substitute')
        if style.get('font_scale',1)!=1:
            from matplotlib.text import Text
            for text in fig.findobj(match=Text):text.set_fontsize(text.get_fontsize()*style['font_scale'])
        # These are presentation changes only. Existing coordinates and values remain frozen.
        if 'width_mm' in style or 'height_mm' in style:
            width=style.get('width_mm',fig.get_figwidth()*25.4);height=style.get('height_mm',fig.get_figheight()*25.4)
            if not 100<=width<=190 or not 65<=height<=150:raise ValueError('Figure size outside supported review range')
            fig.set_size_inches(width/25.4,height/25.4)
        receipt=g.export(fig,values,out,'figure');g.plt.close(fig)
    saved=copy.deepcopy(spec);saved['source']['path']=os.path.relpath(source,out.resolve())
    save(out/'request.json',saved)
    save(out/'receipt.json',{'status':'DRAWN','request_sha256':digest(out/'request.json'),'scientific_data_sha256':science,'source_sha256':digest(source),'figure_files':receipt['files'],'language':language,'scope':'Real plotting of supplied data; no automatic scientific acceptance or model validation'})
    return receipt

def redraw(previous,style_path,out):
    previous=Path(previous);receipt=load(previous/'receipt.json')
    if digest(previous/'request.json')!=receipt['request_sha256']:raise ValueError('Previous frozen request changed')
    for name,value in receipt['figure_files'].items():
        if digest(previous/name)!=value:raise ValueError('Previous figure changed')
    spec=load(previous/'request.json');spec['source']['path']=str((previous/spec['source']['path']).resolve());style=load(style_path)
    if set(style)-{'language','title','subtitle','xlabel','ylabel','group_labels','row_labels','measure_label','existing_font','font_scale','width_mm','height_mm'}:raise ValueError('Redraw accepts presentation only; use a new analysis version for data changes')
    spec['style']={**spec['style'],**style}
    import tempfile
    with tempfile.TemporaryDirectory(prefix='ye1-redraw-') as tmp:
        path=Path(tmp)/'request.json';save(path,spec);result=draw(path,out)
    save(Path(out)/'redraw.json',{'previous_request_sha256':receipt['request_sha256'],'previous_figure_files':receipt['figure_files'],'preserved_scientific_fields':['kind','data','context','source'],'scope':'Style only; labels require host semantic/units review'})
    return result

def main():
    p=argparse.ArgumentParser(description=__doc__);s=p.add_subparsers(dest='action',required=True)
    a=s.add_parser('draw');a.add_argument('request');a.add_argument('--out',required=True)
    a=s.add_parser('redraw');a.add_argument('previous');a.add_argument('style');a.add_argument('--out',required=True)
    a=p.parse_args()
    if a.action=='draw':draw(a.request,a.out)
    else:redraw(a.previous,a.style,a.out)
    print('DRAWN: '+a.out+'; inspect the actual figure before delivery')
if __name__=='__main__':
    import sys
    try: main()
    except (ImportError, OSError) as exc:
        print(json.dumps({'status':'BLOCKED_ENVIRONMENT','reason':str(exc),'next_step':'Preserve frozen inputs and existing results. Resume plotting in an already available NumPy/Matplotlib environment; no automatic installation.'},ensure_ascii=False),file=sys.stderr)
        raise SystemExit(3)
    except (ValueError, KeyError, TypeError) as exc:
        print(json.dumps({'status':'BLOCKED_VALIDATION','reason':str(exc)},ensure_ascii=False),file=sys.stderr)
        raise SystemExit(2)
