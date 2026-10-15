"""Integrated v0.2 CRP plotting hook. Preserves source points for data replay."""
import json
from pathlib import Path
import graphics as g
from matplotlib import pyplot as plt

def plots(selected,pair,out,language='en',synthetic=False):
    out=Path(out);cn=language=='zh';names=[]
    with g.theme(language):
        for name,points,paired in [
            ('figure-1',[(float(x['crp_first']),float(x['stay_days']),x['person']) for x in selected if x['crp_first'] is not None and x['stay_days'] is not None],False),
            ('figure-2',[(float(x['crp_first']),float(x['crp_last']),x['person']) for x in pair],True)]:
            if not points:raise ValueError('No complete records; report missingness, do not fabricate an empty figure')
            file=out/(name+'-data.json')
            if file.exists():raise FileExistsError('Preserve old figure source')
            subtitle=(('合成数据 · ' if synthetic else '')+f'完整记录 n={len(points)}') if cn else (('Synthetic; ' if synthetic else '')+f'first admissions; complete records n={len(points)}')
            fig,data=g.scatter([p[0] for p in points],[p[1] for p in points],
                '首次记录CRP (mg/L)' if cn else 'First recorded CRP (mg/L)',
                ('末次记录CRP (mg/L)' if paired else '住院记录天数（天）') if cn else ('Last recorded CRP (mg/L)' if paired else 'Recorded stay (days)'),
                ('首末CRP配对' if paired else 'CRP与住院天数') if cn else ('First and last CRP' if paired else 'CRP and recorded stay'),subtitle,identity=paired)
            g.export(fig,data,out,name)
            # Old point schema retained for numeric replay, not SVG tag counting.
            file.write_text(json.dumps({'points':points,'x_unit':'mg/L','y_unit':'mg/L' if paired else 'days','x_max':float(fig.axes[0].get_xlim()[1]),'y_max':float(fig.axes[0].get_ylim()[1]),'encoding':'identical points merged; marker area proportional to multiplicity'},indent=2))
            plt.close(fig);names.append(name)
    return names
