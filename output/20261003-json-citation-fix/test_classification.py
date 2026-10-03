from pathlib import Path
import json,copy
P=Path(__file__).parent
ns={};exec((P/'格式与来源校验-完整替换.txt').read_text(),ns)
data=json.loads((P/'许可证题-实际完整输入.json').read_text())
checks=[]
def ck(n,v):assert v,n;checks.append(n)
a=ns['main'](**data)
ck('Actual full online license input renders supported complete categories',a['passed'])
ck('Classification intro cites both actual pages',a['result'].split('\n')[0].endswith('[1][2]。'))
ck('LGPL dynamic linking condition stays with LGPL','LGPL允许动态链接' in a['result'] and '直接修改该库' in a['result'])
ck('MPL file scope stays with MPL','MPL约束文件级修改' in a['result'])
ck('GPL publication trigger stays with GPL','书中以GNU通用公共许可证说明' in a['result'] and '修改并发布' in a['result'])
ck('Other category has network and content traits','网络应用时' in a['result'] and '而非软件本身' in a['result'])
ck('Source-bound repair audited','source_bound_license_classification' in a['evidence_audit'])
x=copy.deepcopy(data);d=json.loads(x['answer']);d['intro']['support']=[{'unit':'UNKNOWN'}];x['answer']=json.dumps(d);ck('Unknown selected model evidence still refused',not ns['main'](**x)['passed'])
x=copy.deepcopy(data);d=json.loads(x['answer']);d['intro']['support']=[];x['answer']=json.dumps(d);ck('Empty model support still refused',not ns['main'](**x)['passed'])
x=copy.deepcopy(data);d=json.loads(x['answer']);d['intro']['text']+='開';x['answer']=json.dumps(d);ck('Wrong script still refused',not ns['main'](**x)['passed'])
x=copy.deepcopy(data);x['retrieved']=[r for r in x['retrieved'] if '【片段编号】os60-0057' not in r['content']];ck('Missing actual source refused',not ns['main'](**x)['passed'])
x=copy.deepcopy(data);x['question']='GPL与MIT许可证有什么区别？';u={u['unit']:u for u in ns['build_evidence_units'](x['retrieved'])['units']};d=json.loads(x['answer']);doc,repair=ns['_book_license_classification'](d,u,x['retrieved'],x['question']);ck('Named-license comparison unchanged',doc==d and repair is None)
x=copy.deepcopy(data);x['question']='書中介紹的開源許可證有哪些類型，各有什麼特點？';d=json.loads(x['answer']);d['intro']['text']='書中認為，許可證可分類。'
for point in d['points']:
 for c in point['clauses']:c['text']='書中描述許可證的特點。'
x['answer']=json.dumps(d,ensure_ascii=False);r=ns['main'](**x);ck('Traditional classification and scoped traits pass',r['passed'] and 'LGPL允許' in r['result'] and 'MPL約束' in r['result'])
# Replay existing 35 checks against the merged code. Full-source 737 baseline
# remains preserved in the earlier policy report; renderer now intentionally
# replaces license category prose with source-bound scoped facts.
t=(P/'test_fix.py').read_text();t=t[:t.index("(P/'本地验证.json').write_text")];old={'__file__':str(P/'test_fix.py')};exec(t,old);checks+=old['checks']
(P/'分类范围验证.json').write_text(json.dumps({'passed':True,'count':len(checks),'checks':checks,'rendered_example':a,'scope':'Only generic four-category type-and-trait queries when all actual book evidence is retrieved. Other topics retain model review. Not universal semantic validation.','live_validated':False},ensure_ascii=False,indent=2))
print(json.dumps({'passed':True,'count':len(checks),'chars':a['body_chars']}))
