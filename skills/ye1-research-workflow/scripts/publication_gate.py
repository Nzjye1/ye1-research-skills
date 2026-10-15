"""Evidence-bound pre-analysis contract; clinical judgments are supplied by host.
Stdlib only. No scientific scoring, searching, modeling, or manuscript generation.
"""

# All data-bearing streams stay behind the controlled local adapter.
if __name__ == '__main__':
    import sys as _privacy_sys
    if '--help' not in _privacy_sys.argv[1:]:
        from privacy_boundary import cli_local_entry
        cli_local_entry()

import argparse
import hashlib
import json
from pathlib import Path

AXES = ('data_analyzability', 'clinical_value', 'nearest_neighbor_increment',
        'design_bias', 'evidence_sufficiency', 'research_depth', 'target_fit')
RATINGS = {'SUPPORTED', 'CONDITIONAL', 'UNKNOWN', 'UNSUPPORTED'}
LABELS = dict(zip(AXES, ('数据能否分析', '临床问题价值', '最近邻与增量',
                        '设计和关键偏倚', '证据充分性', '研究体量', '目标期刊适配')))
RATING_LABELS = {'SUPPORTED': '已有依据', 'CONDITIONAL': '有条件',
                 'UNKNOWN': '待核', 'UNSUPPORTED': '当前不支持'}


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def evaluate(case, root):
    """Check evidence references and derive conservative execution permissions.
    Does not verify that a host's interpretation of evidence is scientifically true.
    """
    if case.get('status') == 'RETIRED_HISTORICAL_CASE':
        raise ValueError('RETIRED_HISTORICAL_CASE: use a new case with complete evidence; historical conclusions are not executable input')
    root = Path(root).resolve()
    if case.get('schema_version') != '0.2.0':
        raise ValueError('unsupported schema_version')
    for key in ('case_id', 'question', 'date_utc', 'source_fingerprint',
                'synthetic', 'purpose', 'evidence', 'axes', 'search', 'conditions',
                'doctor_first_feedback', 'known_unavailable', 'target', 'case_kind',
                'plan_confirmed', 'findings', 'publication_advice', 'readiness'):
        if key not in case:
            raise ValueError('missing ' + key)
    if type(case['synthetic']) is not bool:
        raise ValueError('synthetic must be boolean')
    if case['purpose'] not in ('RESEARCH', 'WORKFLOW_TEST'):
        raise ValueError('invalid purpose')
    if case['case_kind'] not in ('REAL_STUDY', 'SYNTHETIC', 'DESIGN_FIXTURE'):
        raise ValueError('invalid case_kind')
    if case['synthetic'] != (case['case_kind'] == 'SYNTHETIC'):
        raise ValueError('inconsistent data identity')
    if type(case['plan_confirmed']) is not bool:
        raise ValueError('plan_confirmed must be boolean')
    refs = {}
    for item in case['evidence']:
        if item['id'] in refs:
            raise ValueError('duplicate evidence id')
        f = (root / item['path']).resolve()
        if not f.is_relative_to(root) or not f.is_file():
            raise ValueError('evidence path missing or outside module')
        if f.suffix.lower() == '.json':
            try: marker = json.loads(f.read_text(encoding='utf-8'))
            except (ValueError, UnicodeError): marker = None
            if isinstance(marker, dict) and marker.get('status') in {'QUARANTINED_NOT_RUNTIME_INPUT', 'RETIRED_HISTORICAL_CASE'}:
                raise ValueError('NON_EXECUTABLE_HISTORICAL_EVIDENCE: ' + item['id'])
        if digest(f) != item['sha256']:
            raise ValueError('evidence drift: ' + item['id'])
        refs[item['id']] = item
    def bound(ids):
        if not ids or any(i not in refs for i in ids):
            raise ValueError('unbound evidence')
    for name in AXES:
        axis = case['axes'].get(name, {})
        if axis.get('rating') not in RATINGS or not axis.get('rationale'):
            raise ValueError('incomplete judgment: ' + name)
        bound(axis.get('evidence_refs', []))
    search = case['search']
    if search['status'] not in ('ADEQUATE_FOR_DECISION', 'LIMITED', 'NOT_DONE'):
        raise ValueError('invalid search status')
    if search['status'] != 'NOT_DONE':
        bound(search['evidence_refs'])
        if not search.get('date_utc') or not search.get('coverage_limits'):
            raise ValueError('search needs date and limitations')
    for c in case['conditions']:
        if c['status'] not in ('OPEN', 'VERIFIED', 'UNAVAILABLE'):
            raise ValueError('invalid condition')
        if not c.get('required_evidence'):
            raise ValueError('condition needs concrete evidence')
        if c['status'] == 'VERIFIED':
            bound(c.get('evidence_refs', []))
    # Seven ratings describe evidence; they do not vote on execution permissions.
    # A host must identify the specific consequential gap and its affected activity.
    scopes = {'QC', 'DESCRIPTIVE', 'CONFIRMATORY', 'PUBLICATION'}
    for f in case['findings']:
        if f.get('severity') not in ('CRITICAL', 'ADVISORY'):
            raise ValueError('finding needs explicit severity')
        if f.get('status') not in ('OPEN', 'UNAVAILABLE', 'RESOLVED'):
            raise ValueError('invalid finding status')
        if not f.get('rationale') or not set(f.get('affects', [])) <= scopes:
            raise ValueError('finding needs rationale and valid affected activities')
        if f['severity'] == 'CRITICAL' and not f.get('affects'):
            raise ValueError('critical finding needs affected activities')
        bound(f.get('evidence_refs', []))
    advice = case['publication_advice']
    if advice.get('recommendation') not in ('CONTINUE', 'NEED_EVIDENCE', 'STOP') or not advice.get('rationale'):
        raise ValueError('publication advice needs reasoned recommendation')
    bound(advice.get('evidence_refs', []))
    readiness = case['readiness']
    for k in ('authorized_use_confirmed', 'definitions_confirmed', 'exploration_prespecified'):
        if type(readiness.get(k)) is not bool:
            raise ValueError('readiness needs boolean ' + k)
    bound(readiness.get('evidence_refs', []))
    unresolved = [f for f in case['findings'] if f['severity'] == 'CRITICAL' and f['status'] != 'RESOLVED']
    blocked = {scope for f in unresolved for scope in f['affects']}
    reasons = [f['rationale'] for f in unresolved]
    fatal_publication = any(f['status'] == 'UNAVAILABLE' and 'PUBLICATION' in f['affects'] for f in unresolved)
    if case['synthetic']:
        reasons.append('SYNTHETIC_NOT_CLINICAL_RESEARCH')
    if case['synthetic'] or fatal_publication or advice['recommendation'] == 'STOP':
        decision = 'STOP_CURRENT_PUBLICATION'
    elif 'PUBLICATION' in blocked or advice['recommendation'] == 'NEED_EVIDENCE':
        decision = 'NEED_EVIDENCE'
    elif unresolved or case['case_kind'] == 'DESIGN_FIXTURE' or not case['plan_confirmed']:
        decision = 'CONDITIONAL_CONTINUE'
    else:
        decision = 'CONTINUE_RESEARCH'
    local = readiness['authorized_use_confirmed']
    # QC needs permitted data access, descriptive work also needs settled definitions
    # and a declared exploratory scope. Neither depends on journal selection.
    qc = local and 'QC' not in blocked
    descriptive = qc and readiness['definitions_confirmed'] and readiness['exploration_prespecified'] and 'DESCRIPTIVE' not in blocked
    confirmatory = qc and readiness['definitions_confirmed'] and case['plan_confirmed'] and case['case_kind'] == 'REAL_STUDY' and 'CONFIRMATORY' not in blocked
    return {'schema_version': '0.2.0', 'case_id': case['case_id'],
            'decision': decision, 'reasons': reasons, 'axes': case['axes'],
            'qc_allowed': qc, 'descriptive_exploration_allowed': descriptive,
            'confirmatory_effect_allowed': confirmatory,
            'formal_analysis_allowed': confirmatory,
            'submission_manuscript_allowed': False, 'submission_ready': False,
            'research_draft_allowed': confirmatory and decision != 'STOP_CURRENT_PUBLICATION' and 'PUBLICATION' not in blocked,
            'findings': case['findings'], 'publication_advice': advice,
            'workflow_demo_allowed': case['synthetic'] and case['purpose'] == 'WORKFLOW_TEST',
            'acceptance_guarantee': False, 'source_fingerprint': case['source_fingerprint'],
            'conditions': case['conditions'], 'target': case['target'],
            'case_kind': case['case_kind'],
            'scope': 'Host evidence appraisal + deterministic contract, not independent scientific review; fixture permissions are contract simulations only'}


def report(case, result):
    lines = ['# 写作前发表可行性报告', '',
             case['doctor_first_feedback'], '',
             '当前决定：`' + result['decision'] + '`。不保证SCI或中文核心录用。', '',
             '| 判断 | 状态 | 证据与理由 |', '| --- | --- | --- |']
    for name in AXES:
        a = case['axes'][name]
        lines.append(f"| {LABELS[name]} | {RATING_LABELS[a['rating']]} / {a['rating']} | {a['rationale']}（{', '.join(a['evidence_refs'])}） |")
    lines += ['', '已知补不到：' + '；'.join(case['known_unavailable']), '',
              '需要补证据／升级前提：', '']
    lines += ['- ' + c['required_evidence'] + ' [' + c['status'] + ']' for c in case['conditions']]
    lines += ['', '科学建议：' + case['publication_advice']['rationale'], '', '关键阻断与普通提示：', '']
    lines += ['- ' + f['severity'] + ' / ' + f['status'] + '：' + f['rationale'] + '；涉及 ' + ', '.join(f['affects']) for f in case['findings']]
    lines += ['', '目标：' + json.dumps(case['target'], ensure_ascii=False), '',
              '可做数据QC：' + str(result['qc_allowed']),
              '可做预设描述性探索：' + str(result['descriptive_exploration_allowed']),
              '可做已确认方案的确认性效应分析：' + str(result['confirmatory_effect_allowed']),
              '可写可审阅研究草稿：' + str(result['research_draft_allowed']),
              '已具备投稿资格：False（本评估不授予）',
              '合成流程演示许可：' + str(result['workflow_demo_allowed']), '',
              '源指纹：' + case['source_fingerprint'], '',
              '改变题目、人群、结局或设计需新版本；不继承原结论。不靠加图或反复检索追通过。']
    return '\n'.join(lines) + '\n'


def main():
    p = argparse.ArgumentParser()
    p.add_argument('case')
    p.add_argument('--root', required=True)
    p.add_argument('--out', required=True)
    args = p.parse_args()
    case_path = Path(args.case)
    case = json.loads(case_path.read_text())
    result = evaluate(case, args.root)
    result['input_sha256'] = digest(case_path)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=False)
    (out / 'gate.json').write_text(json.dumps(result, ensure_ascii=False, indent=2))
    (out / '发表可行性报告.md').write_text(report(case, result))
    print(result['decision'])


if __name__ == '__main__':
    import sys
    try: main()
    except (ValueError, KeyError, TypeError) as exc:
        print(json.dumps({'status':'BLOCKED_VALIDATION','reason':str(exc)},ensure_ascii=False),file=sys.stderr)
        raise SystemExit(2)
    except OSError as exc:
        print(json.dumps({'status':'BLOCKED_ENVIRONMENT','reason':str(exc)},ensure_ascii=False),file=sys.stderr)
        raise SystemExit(3)
