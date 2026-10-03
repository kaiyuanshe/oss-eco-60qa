from pathlib import Path
import json,copy
P=Path(__file__).parent
code=P/'格式与来源校验-完整替换.txt'
old={};exec((P/'格式与来源校验-700字旧版.txt').read_text(),old)
data=json.loads((P/'许可证题-实际完整输入.json').read_text())
checks=[]
def ck(n,v):assert v,n;checks.append(n)
a=old['main'](**data)
ck('Actual full online input reproduces body_over_700 at 737',a['issues']=='body_over_700' and a['body_chars']==737)
s=(P/'格式与来源校验-700字旧版.txt').read_text().replace("    if not detailed and chars > 700:\n        errors.append('body_over_700')","    # Length is a presentation warning; it must not discard cited content.")
s=s.replace("        result['evidence_audit'] = json.dumps({'selected_units': selection_audit,", "        if result['passed'] and result['body_chars'] > 700:\n            selection_audit.append({'warning': 'body_length_above_target', 'body_chars': result['body_chars'], 'target_max': 700})\n        result['evidence_audit'] = json.dumps({'selected_units': selection_audit,")
new={};exec(s,new)
b=new['main'](**data)
ck('Same complete 737-character answer passes with warning',b['passed'] and b['body_chars']==737 and 'body_length_above_target' in b['evidence_audit'])
ck('First sentence cites both real pages',b['result'].split('\n')[0].endswith('[1][2]。'))
ck('Evidence quotes unchanged',json.loads(a['evidence_audit'])['source_evidence']==json.loads(b['evidence_audit'])['source_evidence'])
x=copy.deepcopy(data);d=json.loads(x['answer']);d['intro']['support']=[{'unit':'UNKNOWN'}];x['answer']=json.dumps(d);ck('Unknown evidence still refused',not new['main'](**x)['passed'])
x=copy.deepcopy(data);d=json.loads(x['answer']);d['intro']['text']+='開';x['answer']=json.dumps(d);ck('Script mismatch still refused','regression_script_characters' in new['main'](**x)['issues'])
x=copy.deepcopy(data);d=json.loads(x['answer']);d['intro']['support']=[];x['answer']=json.dumps(d);ck('Empty evidence still refused',not new['main'](**x)['passed'])
# Existing 35 regression checks, with one policy expectation explicitly revised.
t=(P/'test_fix.py').read_text().replace("exec((P/'格式与来源校验-完整替换.txt').read_text(),ns)","exec(MERGED_CODE,ns)")
t=t.replace("t=t[:t.index(\"(OUT/'社区治理-538字回归样例.json').write_text\")]", "t=t[:t.index(\"(OUT/'社区治理-538字回归样例.json').write_text\")]\nt=t.replace(\"ck('ordinary answer above 700 still rejected',run(new,x)['issues']=='body_over_700')\",\"ck('ordinary answer above 700 gets length warning',run(new,x)['passed'] and 'body_length_above_target' in run(new,x)['evidence_audit'])\")")
# Existing combined test loads code from disk; stage merged code before replay.
# Keep the released merged code unchanged during historical policy replay.
t=t[:t.index("(P/'本地验证.json').write_text")]
ns={'__file__':str(P/'test_fix.py'),'MERGED_CODE':s};exec(t,ns);checks+=ns['checks']
(P/'篇幅策略验证.json').write_text(json.dumps({'passed':True,'count':len(checks),'checks':checks,'actual_old':a,'actual_new':b,'scope':'Full supplied online license input replay; not universal semantic review.'},ensure_ascii=False,indent=2))
(P/'许可证题-修复后回放.md').write_text(b['result'])
print(json.dumps({'passed':True,'count':len(checks),'body_chars':b['body_chars']}))
