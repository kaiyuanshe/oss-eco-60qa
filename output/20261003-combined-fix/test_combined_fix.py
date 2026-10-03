from pathlib import Path
import json,copy
ROOT=Path(__file__).resolve().parents[2]
OUT=Path(__file__).parent
old={};exec((ROOT/'output/重叠关系确定性修正/格式与来源校验-重叠关系完整修正版.txt').read_text(),old)
new={};exec((OUT/'格式与来源校验-完整替换.txt').read_text(),new)
chunks=[json.loads(x) for x in (ROOT/'output/opensource60-clean/chunks.jsonl').read_text().splitlines()]
ids=['os60-0324','os60-0325','os60-0326','os60-0327','os60-0328','os60-0331','os60-0332']
retrieved=[x for x in chunks if x['chunk_id'] in ids]
cat=new['build_evidence_units'](retrieved)
def unit(start):
 return next(u['unit'] for u in cat['units'] if start in u['text'])
def clause(t,*starts):return {'text':t,'support':[{'unit':unit(s)} for s in starts]}
doc={'status':'answer','intro':clause('書中認為，開源社區通常從幾個層面構建衝突管理策略，重點在於透過良好規則與治理做好預防，倡導透明、公開的溝通。','开源社区通常','要点在于'), 'points':[
 {'aspects':['reason'],'clauses':[
 clause('建立清晰的行為準則和社區規範是預防衝突的基礎，一份好的行為準則會明確規定社區禁止的行為，並倡導尊重與包容。','建立清晰的行为准则','一份好的行为准则'),
 clause('制定社區或組織章程、明確共同價值觀，有助成員在大方向上保持一致；許多社區經驗表明，擁有明確行為規範的社區，內部衝突發生頻率明顯降低。','此外，制定社区','许多社区的经验')]},
 {'aspects':['reason'],'clauses':[
 clause('清晰的流程能有效解決分歧，前提是定義社區成員的不同角色及其職責。','清晰的流程能','前提是需要定义'),
 clause('對於重要決策，採用提案—討論—評審的機制，例如Apache項目的RFC流程與「+1/−1」投票機制。','对于重要的决策','例如，Apache'),
 clause('當共識難以達成時，則啟動正式投票程序，由維護者團隊或專門委員會進行表決。','当共识难以达成')]},
 {'aspects':['reason'],'clauses':[
 clause('衝突發生時，逐步升級的解決流程往往很有效：從相關方小範圍討論開始，若無法解決則由負責人介入調解，若調解無效則上升到維護者團隊集體討論和投票，極端情況下可能需尋求基金會或中立第三方仲裁。','当冲突发生时','如果无法解决'),
 clause('實踐中鼓勵在公開的異步平台上討論以保持透明，強調就事論事、針對觀點辯論而非人身攻擊，並引導使用中性、建設性的語言表達分歧。','在实践中，有几个')]},
 {'aspects':['reason'],'clauses':[
 clause('衝突過後進行復盤很有價值，大家一起總結經驗教訓，看看是否需要更新行為準則或貢獻流程。','冲突过后进行'),
 clause('面對極端衝突，可考慮允許項目分叉、暫停涉事成員權限，或引入外部基金會等中立第三方進行調解和裁決。','无法调和的技术路线','严重违反行为准则','社区领导层危机')]}
 ],'comparison':{'overlap':'not_applicable'},'source_labels':{}}
sections={'0324':'衝突管理的總體思路','0325':'建立清晰的行為準則和社區規範','0326':'建立清晰的行為準則和社區規範','0327':'構建結構化的溝通與決策流程','0328':'實施協作式衝突解決機制','0331':'堅持公開透明與持續反思','0332':'應對極端衝突的策略'}
for ident in ids:doc['source_labels'][ident]={'question_title':'開源社區如何管理衝突和分歧','section_title':sections[ident[-4:]]}
q='書中如何建議開源社區管理衝突和分歧？'
def run(ns,d=doc):return ns['main'](json.dumps(d,ensure_ascii=False),retrieved,q)
checks=[]
def ck(name,c):assert c,name;checks.append(name)
a=run(old);b=run(new)
ck('reported answer reproduces 538-character rejection',not a['passed'] and a['issues']=='body_over_500' and a['body_chars']==538)
ck('same complete answer passes without truncation',b['passed'] and b['body_chars']==538)
ck('citations and selected evidence unchanged across limit adjustment',a['evidence_audit']==b['evidence_audit'])
x=copy.deepcopy(doc);x['points'][0]['clauses'][0]['support']=[{'unit':'E99999'}];ck('unknown evidence still rejected','unknown_evidence_unit' in run(new,x)['issues'])
x=copy.deepcopy(doc);x['intro']['text']+='开';ck('wrong script still rejected','regression_script_characters' in run(new,x)['issues'])
x=copy.deepcopy(doc);x['intro']['support']=[];ck('empty evidence still rejected','unit_support:intro' in run(new,x)['issues'])
x=copy.deepcopy(doc);x['intro']['text']+='長'*200;ck('ordinary answer above 700 still rejected',run(new,x)['issues']=='body_over_700')
# Re-run the existing meaningful overlap regression against the new guard,
# without changing its original source or saved report.
test=(ROOT/'output/重叠关系确定性修正/test_deterministic_overlap.py').read_text()
test=test.replace("OUT=Path(__file__).parent",'OUT=Path('+repr(str(ROOT/'output/重叠关系确定性修正'))+')')
test=test.replace("(OUT/'格式与来源校验-重叠关系完整修正版.txt')",'Path('+repr(str(OUT/'格式与来源校验-完整替换.txt'))+')')
test=test[:test.index("(OUT/'确定性重叠修正-本地验证.json').write_text")]
ns={'__file__':str(OUT/'test_combined_fix.py')};exec(test,ns)
checks+=['existing overlap regression: '+c for c in ns['checks']]
(OUT/'社区治理-538字回归样例.json').write_text(json.dumps({'question':q,'doc':doc,'retrieved_ids':ids,'note':'Original answer text retained; unit IDs rebuilt for local selected source subset, not claimed identical to live retrieval.'},ensure_ascii=False,indent=2))
(OUT/'集中修正本地验证.json').write_text(json.dumps({'passed':True,'count':len(checks),'checks':checks,'original_failure':a['issues'],'original_chars':a['body_chars'],'fixed_example':b,'live_validated':False,'limitation':'Length-policy repair; not universal semantic entailment. Local unit IDs rebuilt from cited chunks.'},ensure_ascii=False,indent=2))
print(json.dumps({'passed':True,'checks':len(checks),'original_chars':a['body_chars'],'new_chars':b['body_chars']},ensure_ascii=False))
