"""Freeze evidence and materialize stable reference IDs. Technical QC, not semantic peer review."""
import hashlib,json,re,copy
from pathlib import Path
from materialize import asset,MaterializationBlocked
MARKER=re.compile(r'\[\[([A-Za-z][A-Za-z0-9_-]*)\]\]')

def bind(draft,root):
    draft=copy.deepcopy(draft)
    entry=draft.get('reference_evidence')
    if not isinstance(entry,dict) or set(entry)!={'relative_path','sha256'}:raise MaterializationBlocked('FROZEN_REFERENCE_LEDGER_REQUIRED')
    ledger=json.loads(asset(root,entry['relative_path'],entry['sha256']).read_text())
    refs={r['id']:r for r in ledger['references']}
    if len(refs)!=len(ledger['references']):raise MaterializationBlocked('DUPLICATE_REFERENCE_ID')
    identities=set()
    for ref in refs.values():
        doi=str(ref.get('doi') or '').lower().strip()
        doi=re.sub(r'^(?:https?://(?:dx\.)?doi\.org/|doi:\s*)','',doi)
        for key,value in [('doi',doi),('pmid',str(ref.get('pmid') or '').strip())]:
            if value:
                if (key,value) in identities:raise MaterializationBlocked('DUPLICATE_SOURCE_IDENTITY_MERGE_REQUIRED')
                identities.add((key,value))
        for key in ['title','verified_date','citation','content_evidence','read_level','limitations']:
            if not ref.get(key):raise MaterializationBlocked('INCOMPLETE_REFERENCE_EVIDENCE:'+key)
        if not any(ref.get(k) for k in ['doi','pmid','url']):raise MaterializationBlocked('SOURCE_IDENTITY_REQUIRED')
        if ref['read_level'] not in {'FULL_TEXT_RELEVANT_SECTIONS_READ','MAIN_FULL_TEXT_READ'}:raise MaterializationBlocked('CONTENT_READ_REQUIRED_NOT_METADATA')
        asset(root,ref['local_source'],ref['source_sha256'])
    maps={};claims=ledger['claims']
    for lang in ['zh','en']:
        doc=draft[lang];doc['language']=lang
        ps=doc['paragraphs'];heading='参考文献' if lang=='zh' else 'References'
        cut=next((i for i,p in enumerate(ps) if p['text']==heading),len(ps));ps=ps[:cut]
        order=[]
        for p in ps:
            ids=MARKER.findall(p['text'])
            if any(x not in refs for x in ids):raise MaterializationBlocked('UNRESOLVED_REFERENCE_ID')
            if re.search(r'\[\d+(?:[,–-]\d+)*\]',p['text']):raise MaterializationBlocked('USE_STABLE_REFERENCE_MARKERS')
            if ids:
                linked=[c for c in claims if p['evidence_ref'] in c.get('paragraph_refs',[]) and c.get('status') in {'supported','supported_with_scope'} and c.get('evidence_location')]
                supported={r for c in linked for r in c['reference_ids']}
                if not set(ids)<=supported:raise MaterializationBlocked('CLAIM_SUPPORT_LINK_REQUIRED')
            for rid in ids:
                if rid not in order:order.append(rid)
        maps[lang]=order;number={rid:i for i,rid in enumerate(order,1)}
        for p in ps:p['text']=MARKER.sub(lambda m:'['+str(number[m[1]])+']',p['text'])
        doc['paragraphs']=ps+[{'text':heading,'evidence_ref':'h'}]+[{'text':f'[{number[r]}] '+refs[r]['citation'],'evidence_ref':'ref-'+r} for r in order]
    if maps['zh']!=maps['en']:raise MaterializationBlocked('BILINGUAL_REFERENCE_ORDER_MISMATCH')
    if set(maps['zh'])!=set(refs):raise MaterializationBlocked('UNUSED_BIBLIOGRAPHY_SOURCE')
    return draft,{'status':'PASS_TECHNICAL_REFERENCE_LINKS','display_order':maps['zh'],'ledger_sha256':entry['sha256'],'scope':'Frozen source hashes, declared content-reading and paragraph support links; host must inspect actual content. No automatic semantic endorsement.'}
