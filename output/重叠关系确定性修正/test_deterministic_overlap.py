from pathlib import Path
import json,copy
OUT=Path(__file__).parent
ROOT=OUT.parent/'校验流程候选'
ns={};exec((OUT/'格式与来源校验-重叠关系完整修正版.txt').read_text(),ns)
chunks=[json.loads(s) for s in (OUT.parent/'opensource60-clean/chunks.jsonl').read_text().splitlines()]
lookup={c['chunk_id']:c for c in chunks};retrieved=[lookup[k] for k in ['os60-0006','os60-0007']]
catalog=ns['build_evidence_units'](retrieved)
def u(s):return next(c for c in catalog['units'] if s in c['text'])
def cl(t,*us):return {'text':t,'support':[{'unit':c['unit']} for c in us]}
open_u=u('开放源代码始终');collab=u('其次是社区');enemy=u('共同的“敌人”');users=u('自由软件的用户是');bridge=u('自由软件运动是一种');purpose=u('前者（自由）');business=u('“对商业更加友好”');overlap=u('因为很多软件')
labels={k:{'question_title':'開源軟件與自由軟件有何區別','section_title':'從自由軟件到開源軟件的不變與變'} for k in ['os60-0006','os60-0007']}
doc={'status':'answer','intro':cl('書中認為，兩者共享開放源代碼與開放式協作，但在用戶範圍與理念上有所不同。',open_u,collab,users,bridge),'points':[{'aspects':['common'],'clauses':[cl('開放源代碼是兩者不變的追求。',open_u),cl('兩者都強調開放式協作。',collab),cl('兩者共同的敵人是專有軟件及其封閉與壟斷。',enemy)]},{'aspects':['difference'],'clauses':[cl('兩者用戶範圍有所不同。',users)]},{'aspects':['difference'],'clauses':[cl('自由軟件運動帶有倫理和社會責任感，追求更多自由，自由本身就是目的；開源更強調實用性與商業價值，開源只是手段。',bridge,purpose)]},{'aspects':['difference'],'clauses':[cl('開源對商業更加友好，帶來更寬鬆的許可證和更高市場接受度。',business)]}],'comparison':{'overlap':'stated','overlap_clause':{'point':0,'clause':0}},'source_labels':labels}
def run(x,source=retrieved,q='開源軟件與自由軟件有何區別？'):return ns['main'](json.dumps(x,ensure_ascii=False),source,q)
checks=[]
def ck(t,c):assert c,t;checks.append(t)
res=run(doc);ck('reported missing-overlap and wrong-pointer shape repaired',res['passed']);ck('real overlap with actual source citation','很多軟件同時屬於自由軟件和開源軟件[1]' in res['result']);ck('repair auditable','book_overlap_inserted' in res['evidence_audit']);ck('correct position audited','"clause": 3' in res['evidence_audit']);ck('dual page evidence retained','手段[1][2]' in res['result'])
x=copy.deepcopy(doc);x['points'][0]['clauses'].append(cl('很多軟件同時屬於自由軟件和開源軟件。',overlap));x['comparison']['overlap_clause']={'point':0,'clause':3};rr=run(x);ck('valid original clause not duplicated',rr['passed'] and rr['result'].count('很多軟件同時屬於')==1 and 'book_overlap_inserted' not in rr['evidence_audit'])
x=copy.deepcopy(doc);x['comparison']={'overlap':'not_stated'};ck('false absence repaired',run(x)['passed'])
for supports,issue,name in [([{'unit':'E99999'}],'unknown_evidence_unit','unknown ID rejected'),([], 'unit_support:intro','empty support rejected'),([{'unit':open_u['unit']}]*9,'unit_support:intro','upper bound retained'),([{'id':'os60-0006','quote':'invented'}],'unit_only_support','model written quote rejected')]:
 x=copy.deepcopy(doc);x['intro']['support']=supports;ck(name,issue in run(x)['issues'])
x=copy.deepcopy(doc);x['points'][0]['clauses'].append(cl('兩者都有開放的基礎。',open_u));ck('full capacity fails explicitly','book_overlap_no_clause_capacity' in run(x)['issues'])
x=copy.deepcopy(doc);x['comparison']={'overlap':'not_applicable'};ck('other questions not repaired','book_overlap_inserted' not in run(x,q='請說明書中的開源理念。')['evidence_audit'])
modified=copy.deepcopy(retrieved)
for item in modified:
 for key in ['content','text']:item[key]=item[key].replace('因为很多软件，既属于自由软件，也属于开源软件。','')
cat2=ns['build_evidence_units'](modified);mapping={old['unit']:next(c['unit'] for c in cat2['units'] if c['text']==old['text']) for old in catalog['units'] if old['unit']!=overlap['unit']}
x=copy.deepcopy(doc)
for c in [x['intro']]+[c for p in x['points'] for c in p['clauses']]:
 for s in c['support']:s['unit']=mapping[s['unit']]
x['comparison']={'overlap':'not_stated'};rr=run(x,source=modified);ck('no source means no inserted book fact',rr['passed'] and '很多軟件同時屬於' not in rr['result'])
# Create a meaningful simplified-language case without a generic script converter.
x=copy.deepcopy(doc);x['intro']['text']='书中认为，两者有共同基础，也有不同的理念。';x['points'][0]['clauses']=[cl('两者都坚持开放源代码。',open_u)];x['points'][1]['clauses']=[cl('两者用户范围有所不同。',users)];x['points'][2]['clauses']=[cl('自由软件追求更多自由，开源关注实用性和商业价值。',bridge)];x['points'][3]['clauses']=[cl('开源对商业更加友好。',business)];x['source_labels']={k:{'question_title':'开源软件与自由软件有何区别','section_title':'从自由软件到开源软件的不变与变'} for k in labels};rr=run(x,q='开源软件与自由软件有何区别？');ck('simplified insertion follows question script',rr['passed'] and '很多软件同时属于自由软件和开源软件[1]' in rr['result'])
x=copy.deepcopy(doc);x['intro']['text']='書中認為，使用開源沒有任何風險。';ck('general semantic limitation remains visible',run(x)['passed'])
(OUT/'确定性重叠修正-本地验证.json').write_text(json.dumps({'checks':checks,'count':len(checks),'example':res,'live_validated':False,'limitation':'Book-specific repair only; not a universal semantic checker.'},ensure_ascii=False,indent=2))
print(json.dumps({'checks':len(checks),'passed':True},ensure_ascii=False))
