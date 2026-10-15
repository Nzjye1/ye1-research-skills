"""Enforce current, evidence-bound activity permissions. No clinical inference."""
import json,hashlib
from pathlib import Path
import publication_gate as pg

def require_gate(gate,case,root,source,question,activity,synthetic_demo=False):
    if not all([gate,case,root,source,question]): raise ValueError('Current gate, case, evidence root, source and question are required before analysis/writing')
    actual=json.loads(Path(gate).read_text()); c=json.loads(Path(case).read_text())
    expected=pg.evaluate(c,root);expected['input_sha256']=pg.digest(case)
    if actual!=expected: raise ValueError('Gate stale/tampered: regenerate from current case and evidence')
    if c['source_fingerprint']!=pg.digest(source): raise ValueError('Source drift: new gate required')
    if c['question']!=question: raise ValueError('Question drift: new gate required')
    keys={'QC':'qc_allowed','DESCRIPTIVE':'descriptive_exploration_allowed','CONFIRMATORY':'confirmatory_effect_allowed','DRAFT':'research_draft_allowed'}
    if activity not in keys: raise ValueError('Unknown activity')
    allowed=actual[keys[activity]]
    if activity=='DRAFT' and synthetic_demo:
        allowed=actual['workflow_demo_allowed'] and actual['descriptive_exploration_allowed']
    if not allowed: raise ValueError('Requested activity blocked: '+activity)
    return actual
