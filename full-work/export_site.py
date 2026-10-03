import json,re,base64,shutil
from pathlib import Path
P=Path(__file__).resolve().parents[1];O=P/'full-library';D=json.loads((O/'questions-data.json').read_text());website=P/'prototype/开源生态60问-网站原型.html';s=website.read_text()
# Keep the established appearance; replace only corpus and reading/search behaviors.
embedded={str(d['number']):d for d in json.loads(json.dumps(D))}
for d in embedded.values():
 for b in d['blocks']:
  if b['kind']=='figure':b['image']='data:image/png;base64,'+base64.b64encode((O/b['file']).read_bytes()).decode()
s=re.sub(r'const SAMPLES=.*?;\nconst cats=',lambda m:'const SAMPLES='+json.dumps(embedded,ensure_ascii=False,separators=(',',':'))+';\nconst cats=',s,flags=re.S)
s=s.replace("+SAMPLES[q.id].aliases.join(' ')","+SAMPLES[q.id].aliases.join(' ')+SAMPLES[q.id].keywords.join(' ')")
s=s.replace('搜索目录与3问正文','搜索60问全文').replace('3问正文已收录 · 原文检索','60问全文已收录 · 原文检索').replace('原型 v2 · 第1、20、35问可检索正文','原型 v3 · 60问全文已收录').replace('60问真实目录＋3问正文','60问全文与原书图表').replace('第1、20、35问现已收录正文。','60问现已全部收录正文。')
# Update catalog subsection metadata from the complete extraction, fixing wrapped TOC entries.
catalog=json.loads((P/'questions.json').read_text())
for q,d in zip(catalog,D):q['sections']=[{'title':b['text'],'page':b['page_start']} for b in d['blocks'] if b['kind']=='heading']
s=re.sub(r'const DATA=.*?;\nconst SAMPLES=',lambda m:'const DATA='+json.dumps(catalog,ensure_ascii=False,separators=(',',':'))+';\nconst SAMPLES=',s,flags=re.S)
s=s.replace("h.b.text.replace(/\\*\\*/g,'')", "h.excerpt.replace(/\\*\\*/g,'')")
s=s.replace('节选自所提供原书，未使用模型生成答案。','以下为原文检索结果；图示说明会另行标注。')
s=s.replace('<blockquote>${esc(h.excerpt', '<p class="muted">${h.b.kind===\'figure\'?\'图示说明（整理转述）\':\'原书节选\'}</p><blockquote>${esc(h.excerpt')
start=s.index('function renderFull(');end=s.index("$('search').addEventListener",start)
new=r'''
function renderFull(id){const d=SAMPLES[id];const intro=document.querySelector('.detail .intro');if(!d){intro.textContent='章节导览：本问暂未收录完整正文。';$('fullbody').innerHTML='';return}intro.textContent='原书正文与图表。保留原书观点与历史案例；摘要及图示说明为新增整理内容。';let out='<div class="sample-summary"><strong>编辑摘要（非原文）</strong><p>'+esc(d.summary)+'</p></div>';let inTable=false;d.blocks.forEach((b,i)=>{const hint=`<span class="pagehint">书内第${b.page_start}${b.page_end!==b.page_start?'–'+b.page_end:''}页 · PDF第${b.page_start+18}页起</span>`;if(b.kind==='table'){if(/^\|[\s:-]+\|/.test(b.text))return;if(!inTable){out+='<div class="tablewrap"><table>';inTable=true}out+=`<tr id="passage-${i}">`+b.text.split('|').slice(1,-1).map(v=>'<td>'+esc(v.trim())+'</td>').join('')+'</tr>';return}if(inTable){out+='</table></div>';inTable=false}if(b.kind==='table_group'){out+=`<section id="passage-${i}">${hint}<div class="tablewrap"><table><thead><tr>`+b.rows[0].map(c=>'<th scope="col">'+esc(c)+'</th>').join('')+'</tr></thead><tbody>'+b.rows.slice(1).map(row=>'<tr>'+row.map(c=>'<td>'+esc(c)+'</td>').join('')+'</tr>').join('')+'</tbody></table></div></section>';return}if(b.kind==='figure'){out+=`<figure id="passage-${i}">${hint}<img src="${b.image}" alt="${esc(b.text)}" loading="lazy"><figcaption>${esc(b.caption)}</figcaption><p class="muted">图示说明（整理转述）：${esc(b.text)}</p></figure>`;return}out+=`<section id="passage-${i}">${hint}${b.kind==='heading'||b.kind==='subheading'?'<h3>':'<p>'}${esc(b.text.replace(/\*\*/g,''))}${b.kind==='heading'||b.kind==='subheading'?'</h3>':'</p>'}</section>`});if(inTable)out+='</table></div>';$('fullbody').innerHTML=out}
function retrieve(text,forced){const t=text.toLowerCase().replace(/\s+/g,'');const synonyms={'赚钱':['盈利','收入','商业模式'],'不会编程':['写代码','文档','贡献方式'],'不会写代码':['写代码','文档','贡献方式'],'ospo':['开源项目办公室'],'开源办公室':['开源项目办公室'],'许可证':['许可'],'基金会':['基金会'],'全球化':['全球化'],'政府支持':['政府','政策'],'供应链安全':['供应链','安全'],'可持续':['可持续'],'人工智能':['ai','人工智能']};let keys=[];for(const [k,v] of Object.entries(synonyms))if(t.includes(k))keys.push(...v);keys.push(...(t.match(/[a-z][a-z0-9.+/-]{1,}/g)||[]));const stop=new Set(['如何','什么','开源','软件','哪些','一个','可以','为何','怎么','是什','么是','的区','区别','做什','么的','请问','介绍']);for(let i=0;i<t.length-1;i++){const k=t.slice(i,i+2);if(!stop.has(k)&&/^[\u4e00-\u9fff]{2}$/.test(k))keys.push(k)}keys=[...new Set(keys)];if(!keys.length&&!forced)return[];let hits=[];Object.values(SAMPLES).forEach(d=>{if(forced&&d.number!==forced)return;const title=(d.title+' '+d.aliases.join(' ')).toLowerCase().replace(/\s+/g,'');const relevance=keys.reduce((n,k)=>n+(title.includes(k)?(k.length>2?3:1):0),0);d.blocks.forEach((b,i)=>{if(['heading','subheading','caption'].includes(b.kind)||b.text.length<20||/^\|[\s:-]+\|/.test(b.text))return;let snippets=[b.text];if(b.kind==='table_group'){snippets=b.rows.slice(1).map(row=>row.map((c,j)=>(b.rows[0][j]||'列'+(j+1))+'：'+c).join('；'))}for(const excerpt of snippets){const value=excerpt.toLowerCase().replace(/\s+/g,'');const matched=keys.filter(k=>value.includes(k));const matchScore=matched.reduce((n,k)=>n+(k.length>2?3:1),0);if(matchScore<(keys.length===1?1:2))continue;const score=matchScore/Math.sqrt(Math.max(1,value.length/240))+Math.min(relevance,8)*1.5;hits.push({d,b,i,score,excerpt})}})});hits.sort((a,b)=>b.score-a.score);const chosen=[];for(const h of hits){if(chosen.every(x=>x.d.id!==h.d.id||x.i!==h.i))chosen.push(h);if(chosen.length===2)break}return chosen}
'''.replace('\\\\','\\')
s=s[:start]+new+'\n'+s[end:]
s=s.replace('</style>','#fullbody figure{margin:24px 0}#fullbody figure img{max-width:100%;height:auto;background:white}#fullbody figcaption{font-size:14px;color:#65738a;text-align:center;margin-top:8px}#fullbody .tablewrap{margin:15px 0}#fullbody th{background:#edf2ff}.detail{overflow-wrap:anywhere}</style>')
website.write_text(s)
# Generate source-preserving retrieval chunks. Tables are exported row by row with column names.
chunks=[];manifest=[]
for d in D:
 sec=d['title'];header=[]
 for i,b in enumerate(d['blocks']):
  if b['kind']=='heading':sec=b['text'];continue
  snippets=[b['text']]
  if b['kind']=='table_group':
   snippets=['；'.join((b['rows'][0][j] or f'列{j+1}')+'：'+c for j,c in enumerate(row)) for row in b['rows'][1:]]
  elif b['kind']=='table':
   if re.match(r'\|[\s:-]+\|',b['text']):continue
   row=[c.strip() for c in b['text'].split('|')[1:-1]]
   if row and row[0] in ['模式','公司','贡献方式','语言/方向']:header=row;continue
   snippets=['；'.join((header[j] if j<len(header) else f'列{j+1}')+'：'+c for j,c in enumerate(row))]
  if b['kind'] in ['caption','subheading']:continue
  for j,text in enumerate(snippets):
   if not text.strip():continue
   # Bound long paragraphs at sentence boundaries without discarding text.
   parts=[];acc=''
   for piece in re.split(r'(?<=[。！？；])',text):
    if len(acc)+len(piece)>900 and acc:parts.append(acc);acc=''
    acc+=piece
   if acc:parts.append(acc)
   for k,part in enumerate(parts):
    cid=f'{d["id"]}-p{i:03}-r{j:02}-s{k:02}';kind='图示说明（整理转述）' if b['kind']=='figure' else '原书转录（未更新核验历史事实）'
    entry=f"片段ID：{cid}\n问题：第{d['number']}问 {d['title']}\n篇章：{d['chapter']}\n小节：{sec}\n来源：《{d['source_title']}》，{d['source_author']}\n书内页码：{b['page_start']}–{b['page_end']}；PDF页码：{b['page_start']+18}–{b['page_end']+18}\n拟定网页路径：{d['url_path']}（未发布）\n内容类型：{kind}\n内容：\n{part}"
    chunks.append(entry);manifest.append({'id':cid,'question_id':d['id'],'block':i,'print_pages':[b['page_start'],b['page_end']],'pdf_pages':[b['page_start']+18,b['page_end']+18],'type':kind,'text':part})
(O/'Dify-60问原文片段.txt').write_text('\n\n-----\n\n'.join(chunks));(P/'full-work/chunk-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False))
print('Website bytes',website.stat().st_size,'Knowledge chunks',len(chunks))
