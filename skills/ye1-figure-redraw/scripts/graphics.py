"""Self-authored doctor-paper graphics adapter. No upstream Skill code copied.
Requires existing numpy + matplotlib. Call within theme() to scope all styling.
"""
from pathlib import Path
import os, json, hashlib, math, warnings, textwrap
from contextlib import contextmanager
from contextvars import ContextVar
LANGUAGE=ContextVar("graphics_language",default="en")
# Use a process-local cache rather than writing the installed Skill source tree.
if 'MPLCONFIGDIR' not in os.environ:
    import tempfile,atexit,shutil
    _graphics_cache=tempfile.mkdtemp(prefix='doctor-paper-graphics-')
    os.environ['MPLCONFIGDIR']=_graphics_cache
    atexit.register(shutil.rmtree,_graphics_cache,ignore_errors=True)
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager, ft2font
from matplotlib.text import Text
from matplotlib.ticker import MaxNLocator, NullLocator, NullFormatter

COLORS = {'model':'#0072B2','comparison':'#D55E00','positive':'#009E73','reference':'#626970','ink':'#22282D','grid':'#E8ECEF'}
MARKERS = ['o','s','^','D']

def finite(values, name='values'):
    a=np.asarray(values,dtype=float)
    if a.ndim != 1 or not len(a) or not np.all(np.isfinite(a)):
        raise ValueError(f'{name} must be a non-empty finite 1D array; resolve missingness upstream')
    return a

def font_for(text, preferred=None):
    """Require real glyph coverage; never silently replace Chinese with boxes."""
    needs={ord(c) for c in text if not c.isspace()}
    candidates=[]
    if preferred: candidates.append(Path(preferred))
    if any(v>127 for v in needs):
        candidates += [Path('/System/Library/Fonts/Supplemental/Arial Unicode.ttf')]
        names=['Noto Sans CJK SC','Microsoft YaHei','SimHei','Arial Unicode MS','DejaVu Sans']
    else: names=['Arial','Helvetica','DejaVu Sans']
    for name in names:
        try: candidates.append(Path(font_manager.findfont(name,fallback_to_default=False)))
        except ValueError: pass
    for path in dict.fromkeys(candidates):
        try:
            f=ft2font.FT2Font(str(path))
            if needs.issubset(f.get_charmap()):
                font_manager.fontManager.addfont(str(path))
                return {'family':f.family_name,'path':str(path),'coverage':'checked'}
        except (RuntimeError,OSError,FileNotFoundError):pass
    raise ValueError('No installed font covers requested labels. Preserve the requested language and frozen data; supply an approved existing font or leave the figure pending. Do not install automatically.')

@contextmanager
def theme(language='en', label_text='', preferred_font=None):
    sample=('中文合成数据预测风险临床队列校准曲线住院天数白蛋白首次末次' if language=='zh' else '')+label_text+'ABCDEFGHIJKLMNOPQRSTUVWXYZ abcdefghijklmnopqrstuvwxyz 0123456789 −ρ≥%()/'
    f=font_for(sample,preferred_font)
    rc={'font.family':f['family'],'font.size':10.5,'axes.labelsize':10.5,'axes.titlesize':12,
        'xtick.labelsize':10,'ytick.labelsize':10,'legend.fontsize':10,'text.color':COLORS['ink'],
        'axes.labelcolor':COLORS['ink'],'axes.edgecolor':COLORS['ink'],'axes.linewidth':.7,
        'xtick.color':COLORS['ink'],'ytick.color':COLORS['ink'],'xtick.major.width':.7,'ytick.major.width':.7,
        'axes.spines.top':False,'axes.spines.right':False,'axes.grid':False,
        'savefig.facecolor':'white','figure.facecolor':'white','svg.fonttype':'none','pdf.fonttype':42,
        'ps.fonttype':42,'text.usetex':False,'lines.linewidth':1.3}
    token=LANGUAGE.set(language)
    try:
        with plt.rc_context(rc): yield f
    finally: LANGUAGE.reset(token)

def canvas(title, subtitle='', width_mm=120, height_mm=95):
    fig,ax=plt.subplots(figsize=(width_mm/25.4,height_mm/25.4))
    fig.subplots_adjust(left=.19,right=.97,bottom=.19,top=.79)
    fig.text(.19,.94,title,ha='left',va='top',fontsize=12,fontweight='normal')
    fig.text(.19,.875,subtitle,ha='left',va='top',fontsize=10,color=COLORS['reference'])
    ax.set_axisbelow(True)
    return fig,ax

def scatter(x,y,xlabel,ylabel,title,subtitle='',identity=False):
    x=finite(x,'x');y=finite(y,'y')
    if len(x)!=len(y): raise ValueError('x/y length mismatch')
    fig,ax=canvas(title,subtitle)
    # Multiplicity at identical coordinates is encoded in area; no fabricated jitter.
    points,counts=np.unique(np.column_stack([x,y]),axis=0,return_counts=True)
    ax.scatter(points[:,0],points[:,1],s=17*counts,facecolor=COLORS['model'],edgecolor='white',linewidth=.35,alpha=.85)
    ax.set(xlabel=xlabel,ylabel=ylabel)
    ax.xaxis.set_major_locator(MaxNLocator(5));ax.yaxis.set_major_locator(MaxNLocator(5))
    if identity:
        lower=min(0,float(x.min()),float(y.min())); upper=max(float(x.max()),float(y.max()))*1.08
        ax.plot([lower,upper],[lower,upper],color=COLORS['reference'],ls='--',lw=.9,label=('等值线：末次 = 首次' if LANGUAGE.get()=='zh' else 'Equality: y = x'))
        ax.set(xlim=(lower,upper),ylim=(lower,upper));ax.set_aspect('equal',adjustable='box')
        ax.legend(loc='upper left',frameon=False)
    return fig,{'x':x.tolist(),'y':y.tolist(),'multiplicity':counts.tolist(),'identity':identity}

def histogram(values,edges,xlabel,title,subtitle=''):
    a=finite(values);edges=finite(edges,'edges')
    if len(edges)<2 or np.any(np.diff(edges)<=0):raise ValueError('Strictly increasing bin edges required')
    if a.min()<edges[0] or a.max()>edges[-1]:raise ValueError('Bins would silently omit observations')
    counts,_=np.histogram(a,bins=edges)
    fig,ax=canvas(title,subtitle)
    ax.bar(edges[:-1],counts,width=np.diff(edges),align='edge',color=COLORS['model'],edgecolor='white',linewidth=.7)
    for left,right,count in zip(edges[:-1],edges[1:],counts):
        if count:ax.text((left+right)/2,count+.4,str(int(count)),ha='center',va='bottom',fontsize=10)
    ax.set(xlabel=xlabel,ylabel=('人数（例）' if LANGUAGE.get()=='zh' else 'Admissions (n)'),xlim=(edges[0],edges[-1]),ylim=(0,max(counts)*1.18+1))
    ax.set_xticks(edges);ax.yaxis.set_major_locator(MaxNLocator(5,integer=True))
    return fig,{'values':a.tolist(),'edges':edges.tolist(),'counts':counts.tolist(),'last_bin_right_closed':True}

def group_distribution(groups,labels,ylabel,title,subtitle='',seed=104):
    if len(groups)!=len(labels) or not 1<=len(groups)<=4:raise ValueError('1–4 named groups required')
    arrays=[finite(g) for g in groups];fig,ax=canvas(title,subtitle)
    bp=ax.boxplot(arrays,patch_artist=True,widths=.46,showfliers=False,
        medianprops={'color':COLORS['ink'],'linewidth':1.4},whiskerprops={'linewidth':.8},capprops={'linewidth':.8})
    rng=np.random.default_rng(seed)
    for i,(a,box) in enumerate(zip(arrays,bp['boxes'])):
        col=[COLORS['model'],COLORS['comparison'],COLORS['positive'],COLORS['reference']][i]
        box.set(facecolor=col,alpha=.18,edgecolor=col)
        ax.scatter(i+1+rng.uniform(-.13,.13,len(a)),a,s=9,c=col,marker=MARKERS[i],alpha=.65,edgecolor='none')
    ax.set_xticks(np.arange(1,len(labels)+1),[f'{l}\nn={len(a)}' for l,a in zip(labels,arrays)])
    ax.set_ylabel(ylabel)
    # Signed measures (change scores, residuals) must never be clipped at zero.
    if all(np.min(a)>=0 for a in arrays):ax.set_ylim(bottom=0)
    return fig,{'groups':[a.tolist() for a in arrays],'labels':labels,'quartiles':[np.quantile(a,[.25,.5,.75]).tolist() for a in arrays], 'whiskers':'1.5 IQR; all raw observations shown; horizontal jitter only','seed':seed}

def forest(labels,estimate,lower,upper,title,subtitle='',measure='Odds ratio'):
    est=finite(estimate);lo=finite(lower);hi=finite(upper)
    if not(len(labels)==len(est)==len(lo)==len(hi)) or np.any(lo<=0) or np.any(lo>est) or np.any(est>hi):raise ValueError('Positive ordered ratio confidence intervals required')
    fig,ax=canvas(title,subtitle,width_mm=145,height_mm=75)
    fig.subplots_adjust(left=.32,right=.76)
    pos=np.arange(len(labels));ax.axvline(1,ls='--',lw=.9,c=COLORS['reference'])
    ax.errorbar(est,pos,xerr=[est-lo,hi-est],fmt='s',ms=4,color=COLORS['model'],capsize=2,lw=1.1)
    ax.set_yticks(pos,labels);ax.invert_yaxis();ax.set_xscale('log');ax.set_xlabel(measure+' (95% CI)')
    ax.set_xlim(min(lo.min()*.8,.5),max(hi.max()*1.1,2));ax.set_xticks([.5,1,2,4]);ax.set_xticklabels(['0.5','1','2','4']);ax.xaxis.set_minor_locator(NullLocator());ax.xaxis.set_minor_formatter(NullFormatter())
    for i,(a,b,c) in enumerate(zip(est,lo,hi)):ax.text(1.03,i,f'{a:.2f} [{b:.2f}, {c:.2f}]',transform=ax.get_yaxis_transform(),va='center',fontsize=10)
    return fig,{'labels':labels,'estimate':est.tolist(),'lower':lo.tolist(),'upper':hi.tolist(),'measure':measure,'interval':'95% Wald CI'}

def difference_forest(labels,estimate,lower,upper,title,subtitle='',measure='Mean difference'):
    est=finite(estimate);lo=finite(lower);hi=finite(upper)
    if not(len(labels)==len(est)==len(lo)==len(hi)) or np.any(lo>est) or np.any(est>hi):
        raise ValueError('Ordered additive effect confidence intervals required')
    if not labels or not isinstance(measure,str) or not measure.strip():raise ValueError('Named outcome/contrast and measure required')
    fig,ax=canvas(title,subtitle,width_mm=170,height_mm=max(75,30+17*len(labels)))
    fig.subplots_adjust(left=.43,right=.97,bottom=.22,top=.79)
    pos=np.arange(len(labels));ax.axvline(0,ls='--',lw=.9,c=COLORS['reference'])
    ax.errorbar(est,pos,xerr=[est-lo,hi-est],fmt='s',ms=5,color=COLORS['model'],capsize=3,lw=1.3)
    rendered_labels=[textwrap.fill(str(label),width=26,replace_whitespace=False,break_long_words=True,break_on_hyphens=False) for label in labels]
    ax.set_yticks(pos,rendered_labels);ax.invert_yaxis();ax.set_xlabel(measure+' (95% CI)')
    span=max(float(hi.max()-lo.min()),1e-9);margin=.14*span
    ax.set_xlim(min(float(lo.min()),0)-margin,max(float(hi.max()),0)+margin)
    return fig,{'labels':labels,'rendered_labels':rendered_labels,'estimate':est.tolist(),'lower':lo.tolist(),'upper':hi.tolist(),
        'measure':measure,'interval':'95% CI as supplied; no recomputation','null_value':0}

def cohort_flow(counts,title='Cohort selection',subtitle='Synthetic screening ledger'):
    keys=['screened','excluded','eligible','train','validation']
    if any(k not in counts or not isinstance(counts[k],int) or counts[k]<0 for k in keys):raise ValueError('Nonnegative integer counts required')
    if counts['screened']-counts['excluded']!=counts['eligible'] or counts['train']+counts['validation']!=counts['eligible']:raise ValueError('Flow counts do not reconcile')
    fig,ax=canvas(title,subtitle);ax.set_axis_off();ax.set(xlim=(0,1),ylim=(0,1))
    def box(x,y,t,w=.44):ax.text(x,y,t,ha='center',va='center',fontsize=10.5,bbox={'boxstyle':'round,pad=.5','facecolor':'#F4F7F9','edgecolor':COLORS['reference'],'linewidth':.7})
    def arrow(a,b):ax.annotate('',xy=b,xytext=a,arrowprops={'arrowstyle':'->','color':COLORS['reference'],'lw':.9})
    box(.37,.88,f"Screened\nn={counts['screened']}");box(.79,.64,f"Excluded\nn={counts['excluded']}")
    arrow((.37,.79),(.37,.47));arrow((.37,.64),(.64,.64));box(.37,.38,f"Eligible\nn={counts['eligible']}")
    arrow((.37,.28),(.23,.15));arrow((.37,.28),(.73,.15))
    box(.23,.05,f"Training\nn={counts['train']}");box(.73,.05,f"Hold-out\nn={counts['validation']}")
    return fig,dict(counts)

def binary_input(y,p):
    y=finite(y,'outcomes');p=finite(p,'probabilities')
    if len(y)!=len(p) or not np.all(np.isin(y,[0,1])) or set(y)!={0,1}:raise ValueError('Matched binary outcomes with both classes required')
    if np.any((p<0)|(p>1)):raise ValueError('Probabilities must lie in [0,1]')
    return y,p

def binary_metrics(y,p):
    y,p=binary_input(y,p);order=np.argsort(-p,kind='stable');ys=y[order];ps=p[order]
    # Group identical scores before thresholding; never depend on tie ordering.
    idx=np.r_[np.flatnonzero(np.diff(ps)),len(ps)-1]
    tp=np.cumsum(ys)[idx];fp=(idx+1)-tp
    tpr=np.r_[0,tp/y.sum()];fpr=np.r_[0,fp/(len(y)-y.sum())]
    recall=np.r_[0,tp/y.sum()];precision=np.r_[1,tp/(tp+fp)]
    return {'thresholds':np.r_[np.inf,ps[idx]],'tpr':tpr,'fpr':fpr,'recall':recall,'precision':precision,
        'auc':float(np.trapezoid(tpr,fpr)),'ap':float(np.sum(np.diff(recall)*precision[1:])),
        'prevalence':float(y.mean()),'brier':float(np.mean((p-y)**2)),'n':len(y),'events':int(y.sum())}

def wilson(k,n):
    z=1.959963984540054;p=k/n;den=1+z*z/n;mid=(p+z*z/(2*n))/den;half=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/den
    return (0. if k==0 else max(0.,mid-half)), (1. if k==n else min(1.,mid+half))

def calibration_bins(y,p,bins=8):
    y,p=binary_input(y,p)
    if not isinstance(bins,int) or bins<2 or bins>len(y):raise ValueError('2..n calibration bins required')
    chunks=np.array_split(np.argsort(p,kind='stable'),bins);rows=[]
    for ix in chunks:
        lo,hi=wilson(int(y[ix].sum()),len(ix));rows.append({'n':len(ix),'events':int(y[ix].sum()),'predicted':float(p[ix].mean()),'observed':float(y[ix].mean()),'lo':lo,'hi':hi})
    return rows

def net_benefit(y,p,thresholds):
    y,p=binary_input(y,p);t=finite(thresholds,'thresholds')
    if np.any((t<=0)|(t>=1)):raise ValueError('DCA thresholds must lie strictly inside (0,1)')
    positive=p[:,None]>=t[None,:];tp=np.sum(positive*y[:,None],axis=0);fp=np.sum(positive*(1-y[:,None]),axis=0)
    return (tp-fp*t/(1-t))/len(y),y.mean()-(1-y.mean())*t/(1-t)

def prediction_plot(kind,y,p,title=None,subtitle='Synthetic hold-out; fixed model',thresholds=None):
    m=binary_metrics(y,p);names={'roc':'ROC discrimination','pr':'Precision–recall','calibration':'Risk calibration','dca':'Decision curve analysis'}
    if kind not in names:raise ValueError('Unsupported prediction plot')
    fig,ax=canvas(title or names[kind],subtitle)
    data={k:(v.tolist() if isinstance(v,np.ndarray) else v) for k,v in m.items() if k!='thresholds'}
    if kind=='roc':
        ax.plot(m['fpr'],m['tpr'],c=COLORS['model'],label=f"Model: AUC {m['auc']:.3f}")
        ax.plot([0,1],[0,1],ls='--',c=COLORS['reference'],label='No discrimination')
        ax.set(xlabel='False positive rate',ylabel='True positive rate',xlim=(0,1),ylim=(0,1));ax.set_aspect('equal')
        ax.legend(loc='lower right',frameon=False)
    elif kind=='pr':
        ax.step(m['recall'],m['precision'],where='pre',c=COLORS['model'],label=f"Model: AP {m['ap']:.3f}")
        ax.axhline(m['prevalence'],ls='--',c=COLORS['reference'],label=f"Prevalence: {m['prevalence']:.3f}")
        ax.set(xlabel='Recall / sensitivity',ylabel='Precision / PPV',xlim=(0,1),ylim=(0,1.02));ax.legend(loc='upper right',frameon=False)
    elif kind=='calibration':
        rows=calibration_bins(y,p);px=np.array([r['predicted'] for r in rows]);oy=np.array([r['observed'] for r in rows])
        ax.plot([0,1],[0,1],ls='--',c=COLORS['reference'],label='Ideal calibration')
        ax.errorbar(px,oy,yerr=[oy-[r['lo'] for r in rows],[r['hi'] for r in rows]-oy],fmt='o',c=COLORS['model'],capsize=2,label='8 groups; 95% Wilson CI')
        ax.plot(p,np.full(len(p),-.025),'|',color=COLORS['model'],ms=3,alpha=.25)
        ax.set(xlabel='Mean predicted risk',ylabel='Observed event proportion',xlim=(0,1),ylim=(-.05,1.02));ax.legend(loc='upper left',frameon=False)
        data['bins']=rows;data['interval']='95% Wilson, conditional on fixed prediction groups'
    else:
        if thresholds is None:raise ValueError('Provide a prespecified clinically plausible threshold range; no automatic DCA')
        t=finite(thresholds);nb,allnb=net_benefit(y,p,t)
        ax.plot(t,nb,c=COLORS['model'],label='Model');ax.plot(t,allnb,ls='--',c=COLORS['comparison'],label='Treat all');ax.axhline(0,ls=':',c=COLORS['reference'],label='Treat none')
        ax.set(xlabel='Risk threshold probability',ylabel='Net benefit per patient',xlim=(t.min(),t.max()))
        ax.xaxis.set_major_locator(MaxNLocator(5));ax.legend(loc='lower left',frameon=False);data.update(thresholds=t.tolist(),model_nb=nb.tolist(),treat_all_nb=allnb.tolist(),treat_none_nb=[0.]*len(t))
    return fig,data

ROUTES={'distribution':['continuous observations','units','independent groups or pairing specified'],
    'scatter':['matched observations','units','association plan if inferential'],
    'forest':['effect measure','estimates','interval method','reference levels','adjustment set'],
    'difference':['effect measure','estimates','interval method','units','null value'],
    'flow':['source counts','reconciled exclusions','analysis unit'],
    'roc':['binary observed outcome','fixed scores','prediction horizon','validation role'],
    'pr':['binary observed outcome','fixed scores','prevalence','validation role'],
    'calibration':['observed outcome at horizon','absolute probabilities','validation role'],
    'dca':['absolute risk','observed outcome','clinical action','threshold range','validation role']}

def route(kind,context):
    if kind not in ROUTES:raise ValueError('Unsupported route; survival requires a separate audited module')
    missing=[k for k in ROUTES[kind] if k not in context or context[k] is None or context[k]=='']
    if missing:raise ValueError('Scientific prerequisites missing: '+', '.join(missing))
    if kind in {'roc','pr','calibration','dca'}:
        if context['validation role'] not in {'apparent training','internal hold-out','external validation'}:raise ValueError('Explicit validation role required')
        if context.get('censored'):raise ValueError('Ordinary binary graphics do not handle censoring; use time-dependent audited methods')
    if kind=='distribution' and context['independent groups or pairing specified'] not in {'independent','paired','single group'}:raise ValueError('Specify observational dependence')
    if kind=='difference' and context['null value']!=0:raise ValueError('Additive difference plot requires null value 0')
    return {'kind':kind,'prerequisites':context,'status':'ready for host review, not scientific approval'}

def audit_figure(fig):
    """Physical canvas and actual font glyph checks at export size; not a semantic review."""
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter('always');fig.canvas.draw()
    if any('Glyph' in str(w.message) for w in caught):raise ValueError('Missing glyph at render')
    renderer=fig.canvas.get_renderer();bounds=fig.bbox;checked=[]
    texts=list(fig.texts)
    for ax in fig.axes:
        texts.extend(ax.texts)
        if ax.axison:
            texts.extend([ax.xaxis.label,ax.yaxis.label,ax.title])
            for axis,limits in [(ax.xaxis,ax.get_xlim()),(ax.yaxis,ax.get_ylim())]:
                lo,hi=sorted(limits)
                for tick in axis.get_major_ticks()+axis.get_minor_ticks():
                    if lo-1e-12<=tick.get_loc()<=hi+1e-12:texts.extend([tick.label1,tick.label2])
                texts.append(axis.get_offset_text())
        if ax.get_legend() is not None:texts.extend(ax.get_legend().get_texts())
    for t in texts:
        if not t.get_visible() or not t.get_text():continue
        # Hidden offset/tick artists on disabled flow axes are not rendered.
        if t.axes is not None and not t.axes.axison and t not in t.axes.texts:continue
        prop=t.get_fontproperties();path=font_manager.findfont(prop);char=ft2font.FT2Font(path).get_charmap()
        missing=[c for c in t.get_text() if not c.isspace() and ord(c) not in char]
        if missing:raise ValueError('Missing glyphs: '+repr(missing))
        b=t.get_window_extent(renderer)
        if t.get_fontsize()<10-1e-8:raise ValueError('Figure label below 10 pt minimum: '+t.get_text())
        if b.x0 < bounds.x0-1 or b.y0<bounds.y0-1 or b.x1>bounds.x1+1 or b.y1>bounds.y1+1:raise ValueError('Label outside canvas: '+t.get_text())
        checked.append({'text':t.get_text(),'size_pt':t.get_fontsize(),'font':path})
    for ax in fig.axes:
        if not ax.axison:continue
        for axis,limits in [(ax.xaxis,ax.get_xlim()),(ax.yaxis,ax.get_ylim())]:
            low,high=sorted(limits);boxes=[]
            for tick in axis.get_major_ticks()+axis.get_minor_ticks():
                if low-1e-12<=tick.get_loc()<=high+1e-12:
                    for label in [tick.label1,tick.label2]:
                        if label.get_visible() and label.get_text():boxes.append((label.get_text(),label.get_window_extent(renderer)))
            for i,(a,b) in enumerate(boxes):
                for c,d in boxes[i+1:]:
                    if b.overlaps(d):raise ValueError('Overlapping tick labels: '+a+' / '+c)
    return {'text_count':len(checked),'glyphs':'pass','canvas_bounds':'pass','tick_overlap':'pass','labels':checked,
        'width_mm':float(fig.get_figwidth()*25.4),'height_mm':float(fig.get_figheight()*25.4)}

def export(fig,data,out,stem):
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    paths=[out/(stem+ext) for ext in ['.png','.svg','.pdf','.json']]
    if any(p.exists() for p in paths):raise FileExistsError('Use a new output directory/version')
    if LANGUAGE.get()=='zh':
        replacements={'ROC discrimination': 'ROC区分能力', 'Precision–recall': '精确率与召回率', 'Risk calibration': '风险校准', 'Decision curve analysis': '决策曲线分析', 'Synthetic hold-out; fixed model': '合成验证集；固定模型', 'No discrimination': '无区分能力', 'False positive rate': '假阳性率', 'True positive rate': '真阳性率', 'Recall / sensitivity': '召回率／敏感度', 'Precision / PPV': '精确率／阳性预测值', 'Prevalence:': '结局发生比例：', 'Ideal calibration': '理想校准', '8 groups; 95% Wilson CI': '8组；95% Wilson区间', 'Mean predicted risk': '平均预测风险', 'Observed event proportion': '实际结局比例', 'Risk threshold probability': '风险阈值概率', 'Net benefit per patient': '每位患者净获益', 'Treat all': '全部干预', 'Treat none': '均不干预', 'Model': '模型', 'Odds ratio': '比值比', ' (95% CI)': '（95%置信区间）', 'Cohort selection': '队列筛选', 'Synthetic screening ledger': '合成筛选记录', 'Screened': '筛选', 'Excluded': '排除', 'Eligible': '符合条件', 'Training': '训练集', 'Hold-out': '验证集'}
        for text in fig.findobj(match=Text):
            value=text.get_text()
            for before,after in replacements.items():value=value.replace(before,after)
            text.set_text(value)
    audit=audit_figure(fig)
    for ext in ['png','svg','pdf']:
        fig.savefig(out/f'{stem}.{ext}',dpi=300) # fixed page size; never bbox_inches=tight
    payload={'schema':'doctor-paper-graphics/0.2','data':data,'audit':audit,'files':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in paths[:3]}}
    paths[3].write_text(json.dumps(payload,ensure_ascii=False,indent=2,allow_nan=False))
    return payload
