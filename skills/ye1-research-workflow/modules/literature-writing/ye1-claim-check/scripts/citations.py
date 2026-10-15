"""Adapted from v03 references.bind: stdlib structural checks, never semantic review.

The host prepares these optional records from natural materials. No network calls.
"""

# All data-bearing streams stay behind the controlled local adapter.
if __name__ == '__main__':
    import sys as _privacy_sys
    if '--help' not in _privacy_sys.argv[1:]:
        from privacy_boundary import cli_local_entry
        cli_local_entry()

import argparse
import copy
import hashlib
import json
import re
import sys
import unicodedata
from pathlib import Path

MARKER = re.compile(r'\[\[([A-Za-z][A-Za-z0-9_-]*)\]\]')
READ_LEVELS = {'METADATA', 'ABSTRACT', 'EXCERPT', 'FULL_TEXT_RELEVANT_SECTIONS', 'MAIN_FULL_TEXT'}


class ValidationError(ValueError):
    pass


def digest(value):
    return hashlib.sha256(value if isinstance(value, bytes) else value.encode('utf8')).hexdigest()


def asset(root, entry):
    """Retain v03 asset path, symlink and frozen hash protections, without docx."""
    if not isinstance(entry, dict) or set(entry) != {'relative_path', 'sha256'}:
        raise ValidationError('FROZEN_SOURCE_REQUIRED')
    relative = entry['relative_path']
    if not isinstance(relative, str) or ':' in relative or '\\' in relative or any(p in {'', '.', '..'} for p in relative.split('/')):
        raise ValidationError('UNSAFE_ASSET_PATH')
    target = Path(root)
    for part in relative.split('/'):
        target /= part
        if target.is_symlink():
            raise ValidationError('SYMLINK_ASSET')
    if not target.resolve().is_relative_to(Path(root).resolve()) or not target.is_file():
        raise ValidationError('MISSING_ASSET')
    if digest(target.read_bytes()) != entry['sha256']:
        raise ValidationError('SOURCE_CHANGED_REVIEW_REQUIRED')
    return target


def normalize_doi(value):
    value = str(value or '').strip().lower()
    return re.sub(r'^(?:https?://(?:dx\.)?doi\.org/|doi:\s*)', '', value)


def normal(value):
    if isinstance(value, list):
        value = ' | '.join(str(x) for x in value)
    return re.sub(r'\s+', ' ', unicodedata.normalize('NFKC', str(value)).casefold()).strip()


def compare_metadata(submitted, authority):
    """Compare supplied records, not attest to their trustworthiness or new retrieval."""
    fields = ['doi', 'title', 'authors', 'year', 'journal']
    differences, missing = {}, []
    record = authority.get('record', {})
    for key in fields:
        if not submitted.get(key) or not record.get(key):
            missing.append(key)
            continue
        f = normalize_doi if key == 'doi' else normal
        if f(submitted[key]) != f(record[key]):
            differences[key] = {'submitted': submitted[key], 'record': record[key]}
    provenance = all(authority.get(k) for k in ['url', 'accessed_at', 'mode'])
    status = 'MISMATCH' if differences and provenance else 'UNVERIFIED' if missing or not provenance else 'MATCH'
    return {'status': status, 'differences': differences, 'missing_fields': missing,
            'record_provenance_present': bool(provenance), 'source': {k: authority.get(k) for k in ['url', 'accessed_at', 'mode']},
            'verification': 'SUPPLIED_RECORD_COMPARISON_ONLY', 'content_support': 'NOT_CHECKED',
            'note': 'Host must verify authority, versions and retrieval. A cached record is not fresh verification.'}


def bind(payload, root):
    """Materialize stable IDs in one or more host-authored language documents."""
    out = copy.deepcopy(payload)
    entry = payload.get('reference_evidence')
    ledger = json.loads(asset(root, entry).read_text(encoding='utf8'))
    refs = {r['id']: r for r in ledger['references']}
    if len(refs) != len(ledger['references']):
        raise ValidationError('DUPLICATE_REFERENCE_ID')
    # Unused candidates may remain incomplete in the library; only current citations
    # consume identity/content evidence, so one unrelated gap cannot stop all writing.
    requested = {rid for doc in payload['documents'].values() for p in doc['paragraphs'] for rid in MARKER.findall(p['text'])}
    identities = set()
    for ref in refs.values():
        if not re.fullmatch(r'[A-Za-z][A-Za-z0-9_-]*', ref['id']):
            raise ValidationError('INVALID_REFERENCE_ID')
        if ref['id'] not in requested:
            continue
        for key, value in [('doi', normalize_doi(ref.get('doi'))), ('pmid', str(ref.get('pmid') or '').strip())]:
            if value:
                if (key, value) in identities:
                    raise ValidationError('DUPLICATE_SOURCE_IDENTITY_MERGE_REQUIRED')
                identities.add((key, value))
        if not any(ref.get(k) for k in ['doi', 'pmid', 'url']):
            raise ValidationError('SOURCE_IDENTITY_REQUIRED')
        if not ref.get('citation') or ref.get('read_level') not in READ_LEVELS:
            raise ValidationError('REFERENCE_READING_SCOPE_REQUIRED')
        asset(root, ref['source'])
        # A real DOI must not be treated as content support, or a mismatch quietly ignored.
        identity = ref.get('identity', {})
        if identity.get('status') != 'MATCH' or not all(identity.get(k) for k in ['record_url', 'checked_at', 'mode']):
            raise ValidationError('IDENTITY_UNRESOLVED_REVIEW_REQUIRED')
    claims = {c['id']: c for c in ledger['claims']}
    if len(claims) != len(ledger['claims']):
        raise ValidationError('DUPLICATE_CLAIM_ID')
    documents = out['documents']
    if not documents or not set(documents) <= {'zh', 'en'}:
        raise ValidationError('DOCUMENT_LANGUAGE_REQUIRED')
    primary = out.get('numbering_language', next(iter(documents)))
    if primary not in documents:
        raise ValidationError('NUMBERING_LANGUAGE_MISSING')
    orders, linked_by_lang = {}, {}
    for lang, doc in documents.items():
        order, links, pids = [], set(), set()
        for p in doc['paragraphs']:
            pid, text = p['id'], p['text']
            if pid in pids:
                raise ValidationError('DUPLICATE_PARAGRAPH_ID')
            pids.add(pid)
            ids = MARKER.findall(text)
            if '[[' in MARKER.sub('', text) or re.search(r'\[\d+(?:\s*[,，–-]\s*\d+)*\]', text):
                raise ValidationError('UNRESOLVED_OR_MIXED_CITATION_STYLE')
            if any(r not in refs for r in ids):
                raise ValidationError('UNRESOLVED_REFERENCE_ID')
            supported = set()
            for cid in p.get('claim_ids', []):
                if cid not in claims:
                    raise ValidationError('UNKNOWN_CLAIM_ID')
                c = claims[cid]
                if c.get('locations', {}).get(lang) != pid or c.get('text_sha256', {}).get(lang) != digest(text):
                    raise ValidationError('CLAIM_TEXT_OR_LOCATION_CHANGED_REVIEW_REQUIRED')
                if c.get('status') not in {'supported', 'supported_with_scope', 'local_result_only'}:
                    raise ValidationError('UNSUPPORTED_CLAIM_REVISE_BEFORE_BINDING')
                rids = c.get('reference_ids', [])
                if c['status'] == 'local_result_only' and rids:
                    raise ValidationError('LOCAL_RESULT_NOT_EXTERNAL_SUPPORT')
                if not set(rids) <= set(ids):
                    raise ValidationError('CLAIM_CITATION_MISSING')
                for rid in rids:
                    if rid not in refs:
                        raise ValidationError('UNKNOWN_CLAIM_REFERENCE')
                    evidence = [e for e in c.get('evidence', []) if e.get('reference_id') == rid and e.get('location')]
                    if not evidence:
                        raise ValidationError('EVIDENCE_LOCATION_REQUIRED')
                    level = refs[rid]['read_level']
                    if level == 'METADATA':
                        raise ValidationError('METADATA_IS_NOT_CONTENT')
                    allowed = {'abstract'} if level == 'ABSTRACT' else {'excerpt'} if level == 'EXCERPT' else {'abstract', 'excerpt', 'methods', 'results', 'discussion', 'table', 'figure'}
                    if any(e.get('scope') not in allowed for e in evidence):
                        raise ValidationError('READING_SCOPE_EXCEEDED')
                supported.update(rids)
                links.add(cid)
            if not set(ids) <= supported:
                raise ValidationError('CLAIM_SUPPORT_LINK_REQUIRED')
            order.extend(r for r in ids if r not in order)
        orders[lang], linked_by_lang[lang] = list(dict.fromkeys(order)), links
    if len(documents) > 1:
        if any(set(x) != set(orders[primary]) for x in orders.values()) or any(x != linked_by_lang[primary] for x in linked_by_lang.values()):
            raise ValidationError('BILINGUAL_CLAIM_OR_REFERENCE_MISMATCH')
    order = orders[primary]
    number = {rid: i for i, rid in enumerate(order, 1)}
    bibliography = [{'id': rid, 'number': number[rid], 'text': f'[{number[rid]}] ' + refs[rid]['citation']} for rid in order]
    for doc in documents.values():
        for p in doc['paragraphs']:
            p['text'] = MARKER.sub(lambda m: '[' + str(number[m[1]]) + ']', p['text'])
        doc['bibliography'] = copy.deepcopy(bibliography)
    return out, {'status': 'PASS_TECHNICAL_REFERENCE_LINKS', 'numbering_language': primary,
                 'display_order': order, 'unused_library_ids': sorted(set(refs) - set(order)),
                 'ledger_sha256': entry['sha256'], 'semantic_review': 'HOST_REQUIRED',
                 'scope': 'Declared identity/support, read scopes, exact paragraph hashes and frozen source files only.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    m = sub.add_parser('metadata'); m.add_argument('submitted', type=Path); m.add_argument('authority', type=Path)
    b = sub.add_parser('bind'); b.add_argument('payload', type=Path); b.add_argument('--root', type=Path, required=True); b.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    if args.command == 'metadata':
        result = compare_metadata(json.loads(args.submitted.read_text()), json.loads(args.authority.read_text()))
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if result['status'] == 'MATCH' else 2
    bound, result = bind(json.loads(args.payload.read_text()), args.root)
    args.out.mkdir(parents=True, exist_ok=False)
    (args.out / 'bound.json').write_text(json.dumps(bound, ensure_ascii=False, indent=2), encoding='utf8')
    (args.out / 'receipt.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf8')
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (ValueError, KeyError, TypeError, OSError) as exc:
        print(json.dumps({'status': 'BLOCKED_VALIDATION', 'reason': str(exc), 'next_step': '保留原件；核对相应来源/字段/范围后另存新版本。'}, ensure_ascii=False), file=sys.stderr)
        sys.exit(2)
