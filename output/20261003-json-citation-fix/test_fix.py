from pathlib import Path
import json,copy
P=Path(__file__).parent
ns={};exec((P/'格式与来源校验-完整替换.txt').read_text(),ns)
load=ns['_load_review_json']; raw=(P/'企业题-实际无效JSON.txt').read_text()
checks=[]
def ck(n,v):assert v,n;checks.append(n)
def rejects(s):
 try:load(s);return False
 except json.JSONDecodeError:return True
try:json.loads(raw)
except json.JSONDecodeError as e:ck('Actual failure reproduced at character 692',e.pos==692)
doc,repair=load(raw)
ck('Actual missing bracket recovered',repair['repair']=='missing_points_closing_bracket')
ck('Only one bracket inserted, all text and support preserved',json.loads(raw[:repair['position']]+']'+raw[repair['position']:])==doc)
ck('Valid JSON unchanged, no repair',load(json.dumps(doc,ensure_ascii=False))==(doc,None))
ck('Other missing commas still rejected',rejects(raw.replace('"status":"answer",','"status":"answer"')))
ck('Additional missing bracket still rejected',rejects(raw[:-1]))
ck('Unescaped quote still rejected',rejects(raw.replace('开源项目中存在','开源"项目中存在')))
x=copy.deepcopy(doc);x['intro']['text']='文字中的 ,"comparison": 不能作为修复目标'
ck('String marker cannot trigger repair',load(json.dumps(x,ensure_ascii=False))==(x,None))
x=copy.deepcopy(doc);x['points'][0]['clauses'][0]['support']=[{'unit':'E99999'}]
bad=json.dumps(x,ensure_ascii=False).replace('], "comparison":',', "comparison":')
r=ns['main'](bad,[],'企业为什么需要建立开源治理机制？')
ck('Repaired JSON still subject to actual source verification',not r['passed'] and r['issues']!='')
# Existing community/length/evidence/overlap regressions against merged code.
t= (P.parent/'20261003-combined-fix/test_combined_fix.py').read_text()
t=t.replace('OUT=Path(__file__).parent','OUT=Path('+repr(str(P.resolve()))+')')
t=t[:t.index("(OUT/'社区治理-538字回归样例.json').write_text")]
t=t.replace("ck('ordinary answer above 700 still rejected',run(new,x)['issues']=='body_over_700')","ck('ordinary answer above 700 gets length warning',run(new,x)['passed'] and 'body_length_above_target' in run(new,x)['evidence_audit'])")
tns={'__file__':str(P/'test_fix.py')};exec(t,tns)
checks+=tns['checks']
# Four classification headings must complete intro citations without altering body.
root=P.parent/'opensource60-clean/chunks.jsonl'
chunks=[json.loads(l) for l in root.read_text().splitlines()]
retr=[c for c in chunks if c['chunk_id'] in ['os60-0056','os60-0057']]
cat=ns['build_evidence_units'](retr)
heads=[next(u for u in cat['units'] if u['text'].replace(' ','').lower().startswith(prefix)) for prefix in ['一、宽松','二、强','三、弱','四、其他']]
d={'status':'answer','intro':{'text':'书中认为，许可证分为宽松许可证、强copyleft许可证、弱copyleft许可证及其他特色类许可证。','support':[{'unit':heads[0]['unit']}]},'points':[{'aspects':['reason'],'clauses':[{'text':h['text'].replace('\n',' '),'support':[{'unit':h['unit']}]}]} for h in heads],'comparison':{'overlap':'not_applicable'},'source_labels':{c['chunk_id']:{'question_title':c['question_title'],'section_title':c['section_title']} for c in retr}}
r=ns['main'](json.dumps(d,ensure_ascii=False),retr,'开源许可证有哪些类型？')
ck('Four-category intro uses both actual book pages',r['passed'] and r['result'].split('\n')[0].endswith('[1][2]。'))
ck('Citation completion audited', 'license_category_intro_sources_completed' in r['evidence_audit'])
x=copy.deepcopy(d);x['intro']['support']=[{'unit':'UNKNOWN'}];r=ns['main'](json.dumps(x),retr,'开源许可证有哪些类型？')
ck('License repair preserves invalid-unit rejection',not r['passed'])
(P/'本地验证.json').write_text(json.dumps({'passed':True,'checks':checks,'count':len(checks),'live_validated':False,'limitations':['Only repairs one missing points-array closing bracket before comparison; other malformed JSON fails.','Actual online evidence-unit IDs require online retrieval; no claim of full actual enterprise evidence replay.','Source selection is not universal semantic entailment validation.']},ensure_ascii=False,indent=2))
print(json.dumps({'passed':True,'count':len(checks)}))
