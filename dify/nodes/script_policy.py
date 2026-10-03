"""Create source-preserving evidence units from the actual retrieval result."""
import json
import re


def build_evidence_units(retrieved):
    fragments = []
    seen = {}
    for item in retrieved or []:
        content = item.get('content', '') if isinstance(item, dict) else ''
        ident = re.search(r'【片段编号】\s*([^\s]+)', content)
        q = re.search(r'【题目】第(\d+)问\s*(.*)', content)
        sec = re.search(r'【小节】\s*(\d+\.\d+)\s*(.*)', content)
        pages = re.search(r'【页码】书内第(\d+)页；PDF第(\d+)页', content)
        if not (ident and q and sec and pages):
            continue
        body = content[ident.end():].strip()
        fragment = {'id': ident[1], 'q': q[1], 'sec': sec[1], 'book': int(pages[1]), 'pdf': int(pages[2]),
                    'question_title': q[2].strip(), 'section_title': sec[2].strip(), 'body': body}
        if ident[1] in seen:
            if seen[ident[1]] != fragment:
                raise ValueError('ambiguous_chunk:' + ident[1])
            continue
        seen[ident[1]] = fragment
        fragments.append(fragment)
    fragments.sort(key=lambda x: (int(x['q']), tuple(map(int, x['sec'].split('.'))), x['book'], x['pdf'], x['id']))
    units = []
    previous = None
    for fragment in fragments:
        pieces = [m.group().strip() for m in re.finditer(r'.+?(?:[。！？][”’」』]?|$)', fragment['body'], flags=re.S) if m.group().strip()]
        adjacent = (previous is not None and previous['q'] == fragment['q'] and previous['sec'] == fragment['sec']
                    and previous['book'] + 1 == fragment['book'] and previous['pdf'] + 1 == fragment['pdf'])
        if pieces and adjacent and units and not units[-1]['complete']:
            # Keep the exact two source pieces; do not invent a single-page quote.
            first = pieces.pop(0)
            units[-1]['pieces'].append({'id': fragment['id'], 'quote': first})
            units[-1]['text'] += first
            units[-1]['complete'] = bool(re.search(r'[。！？][”’」』]?$', first))
        for piece in pieces:
            units.append({'pieces': [{'id': fragment['id'], 'quote': piece}], 'text': piece,
                          'complete': bool(re.search(r'[。！？][”’」』]?$', piece))})
        previous = fragment
    for i, unit in enumerate(units):
        unit['unit'] = 'E' + str(i + 1).zfill(3)
    return {'sources': {f['id']: {k: f[k] for k in ['q', 'sec', 'book', 'pdf', 'question_title', 'section_title']} for f in fragments},
            'units': units}


def evidence_catalog_text(retrieved):
    data = build_evidence_units(retrieved)
    # Source quotes appear once in this prompt. The model selects unit IDs only.
    readable = {'sources': data['sources'], 'units': [
        {'unit': x['unit'], 'source_ids': [p['id'] for p in x['pieces']], 'complete': x['complete'], 'text': x['text']}
        for x in data['units']]}
    return json.dumps(readable, ensure_ascii=False)


import re
TRADITIONAL = '質軟開問頁許協眾變術隱權專閉壟寬業審規碼計錄護風險應選識蹤聲'

def main(question: str, retrieved: list) -> dict:
    if re.search(r'繁体|繁體|正體', question):
        traditional = True
    elif re.search(r'简体|簡體', question):
        traditional = False
    else:
        traditional = any(c in question for c in TRADITIONAL)
    return {'output_script': '繁体中文' if traditional else '简体中文', 'evidence_catalog': evidence_catalog_text(retrieved)}