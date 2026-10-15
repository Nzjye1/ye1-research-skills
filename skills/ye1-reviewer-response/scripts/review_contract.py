"""Optional host-prepared fact/declaration/revision contracts. No semantic attestation."""

# All data-bearing streams stay behind the controlled local adapter.
if __name__ == '__main__':
    import sys as _privacy_sys
    if '--help' not in _privacy_sys.argv[1:]:
        from privacy_boundary import cli_local_entry
        cli_local_entry()

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path


def frozen_text(root, entry):
    relative = entry.get('relative_path', '')
    if ':' in relative or '\\' in relative or any(x in {'', '.', '..'} for x in relative.split('/')):
        raise ValueError('UNSAFE_RECORD_PATH')
    target = Path(root)
    for x in relative.split('/'):
        target /= x
        if target.is_symlink():
            raise ValueError('SYMLINK_RECORD')
    if not target.resolve().is_relative_to(Path(root).resolve()) or not target.is_file():
        raise ValueError('RECORD_MISSING')
    data = target.read_bytes()
    if hashlib.sha256(data).hexdigest() != entry.get('sha256'):
        raise ValueError('RECORD_CHANGED_REVIEW_REQUIRED')
    return data.decode('utf8')


def compare_facts(rows):
    """Compare already mapped facts; equal tags cannot certify equivalent prose."""
    if not rows:
        raise ValueError('NO_FACTS_MAPPED')
    fields = ['value', 'unit', 'denominator', 'time', 'reference_group', 'relation', 'polarity']
    groups, conflicts, incomplete = {}, [], []
    for row in rows:
        if not row.get('id') or not row.get('location') or not row.get('quote'):
            raise ValueError('FACT_ID_LOCATION_AND_QUOTE_REQUIRED')
        if any(k not in row for k in fields):
            incomplete.append(row['location'])
        groups.setdefault(row['id'], []).append(row)
    for fid, variants in groups.items():
        base = variants[0]
        for row in variants[1:]:
            differences = {k: [base.get(k), row.get(k)] for k in fields if base.get(k) != row.get(k)}
            if differences:
                conflicts.append({'id': fid, 'locations': [base['location'], row['location']], 'differences': differences})
    return {'status': 'MAPPED_FACT_CONFLICT' if conflicts else 'INCOMPLETE_MAPPING' if incomplete else 'NO_MAPPED_DIFFERENCE',
            'conflicts': conflicts, 'incomplete': incomplete, 'semantic_review': 'HOST_REQUIRED',
            'scope': 'Only host-mapped facts compared; no automatic extraction, full-text coverage, or semantic equivalence claim.'}


def declarations(rows):
    allowed = {'CONFIRMED', 'OPEN', 'DISPUTED'}
    pending, seen = [], set()
    for row in rows:
        if row.get('id') in seen or not row.get('id'):
            raise ValueError('DECLARATION_ID_REQUIRED_UNIQUE')
        seen.add(row['id'])
        if row.get('status') not in allowed:
            raise ValueError('DECLARATION_STATUS_REQUIRED')
        if row['status'] == 'CONFIRMED':
            confirmation = row.get('confirmation', {})
            if not all(confirmation.get(k) for k in ['source', 'date', 'quote']):
                raise ValueError('UNCONFIRMED_DECLARATION')
        else:
            if row.get('asserted_as_fact') is not False or not re.search(r'待.*确认|pending.*confirm|to be confirmed', row.get('draft_text', ''), re.I):
                raise ValueError('UNKNOWN_DECLARATION_ASSERTED')
            pending.append(row['id'])
    required = {'ethics', 'author_agreement', 'conflicts_of_interest', 'exclusive_submission'}
    pending.extend(sorted(required - seen))
    return {'status': 'DRAFT_PENDING' if pending else 'DECLARED_CONFIRMATIONS_RECORDED', 'pending': pending,
            'scope': 'Confirmation field presence only; host must check the actual user statement and manuscript version.', 'submitted': False}


COMPLETED = re.compile(r'\bwe\s+(?:(?:have|also)\s+)?(?:performed|conducted|completed|added|revised)\b|(?:已|已经)(?:完成|开展|补做|新增|修改|修订|实施)', re.I)


def responses(rows, root):
    if not rows:
        raise ValueError('NO_REVIEW_POINTS')
    pending, verified, seen = [], [], set()
    for row in rows:
        rid = row.get('id')
        if not rid or rid in seen or not row.get('comment') or not row.get('response'):
            raise ValueError('REVIEW_POINT_REQUIRED_UNIQUE')
        seen.add(rid)
        status = row.get('status')
        if status == 'PLANNED':
            if row.get('asserts_completed') is not False or COMPLETED.search(row['response']):
                raise ValueError('UNPERFORMED_WORK_CLAIMED_COMPLETE')
            if row.get('changes'):
                raise ValueError('SPLIT_PARTIAL_RESPONSE_INTO_SUBPOINTS')
            pending.append(rid)
            continue
        if status == 'NO_CHANGE':
            if not row.get('rationale') or row.get('changes') or row.get('asserts_completed') is not False or COMPLETED.search(row['response']):
                raise ValueError('NO_CHANGE_REQUIRES_HONEST_RATIONALE')
            verified.append(rid)
            continue
        if status != 'COMPLETED' or row.get('asserts_completed') is not True:
            raise ValueError('RESPONSE_STATUS_REQUIRED')
        if row.get('kind') not in {'text', 'analysis', 'experiment'}:
            raise ValueError('COMPLETED_WORK_KIND_REQUIRED')
        if not row.get('changes'):
            raise ValueError('ACTUAL_REVISION_REQUIRED')
        for change in row['changes']:
            before, after = frozen_text(root, change['before']), frozen_text(root, change['after'])
            if before == after or not change.get('location') or not change.get('version'):
                raise ValueError('ACTUAL_CHANGED_VERSION_AND_LOCATION_REQUIRED')
            old, new = change.get('old_quote'), change.get('new_quote')
            if not old or old not in before or not new or new not in after or old == new:
                raise ValueError('REVISION_QUOTE_NOT_IN_ACTUAL_FILES')
        if row.get('kind') in {'analysis', 'experiment'}:
            evidence = row.get('execution_evidence')
            if not evidence or not row.get('execution_quote') or row['execution_quote'] not in frozen_text(root, evidence):
                raise ValueError('EXECUTION_RESULT_EVIDENCE_REQUIRED')
        verified.append(rid)
    return {'status': 'DRAFT_PENDING' if pending else 'PASS_RECORDED_REVISION_LINKS', 'verified_links': verified, 'pending': pending,
            'semantic_review': 'HOST_REQUIRED', 'scope': 'Frozen files, actual text differences and recorded locations; not proof of experiment execution or response adequacy.', 'submitted': False}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('command', choices=['facts', 'declarations', 'responses']); p.add_argument('records', type=Path); p.add_argument('--root', type=Path)
    a = p.parse_args(); rows = json.loads(a.records.read_text(encoding='utf8'))
    if a.command == 'responses' and a.root is None:
        p.error('--root is required for frozen revision files')
    result = compare_facts(rows) if a.command == 'facts' else declarations(rows) if a.command == 'declarations' else responses(rows, a.root)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 2 if result['status'] in {'MAPPED_FACT_CONFLICT', 'INCOMPLETE_MAPPING', 'DRAFT_PENDING'} else 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (ValueError, KeyError, TypeError, OSError) as exc:
        print(json.dumps({'status': 'BLOCKED_VALIDATION', 'reason': str(exc)}, ensure_ascii=False), file=sys.stderr)
        sys.exit(2)
