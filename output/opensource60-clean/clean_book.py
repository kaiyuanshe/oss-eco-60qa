"""Reproducible extraction: PyMuPDF; no LLM rewriting of source text."""
import fitz,re,json,collections,hashlib,pathlib,zipfile
ROOT=pathlib.Path(__file__).resolve().parent
SRC=ROOT.parents[1]/'project_sources/01-70443-PDF-20260921.pdf'
doc=fitz.open(SRC)
records=[];heads=[];removed=[];pagecheck=[];visual=[]
state={'part':'','question_no':None,'question_title':'','section_no':'','section_title':''}

def normalize(t):
 t=re.sub(r'(?<=[\u4e00-\u9fff]) +(?=[\u4e00-\u9fff])','',t)
 return t.strip()
def join(lines):
 out=''
 for t in lines:
  t=normalize(t)
  if not t:
   if out and not out.endswith('\n'):out+='\n'
   continue
  if out and (re.match(r'^[●①②③④⑤⑥⑦⑧⑨]|^（\d+）|^[一二三四五六七八九十]+、',t) or out.endswith(('。','！','？','：','；'))):out+='\n'
  elif out and re.search(r'[A-Za-z0-9]$',out) and re.match(r'[A-Za-z0-9]',t):out+=' '
  out+=t
 return out

def emit(lines,page,kind='正文'):
 text=join(lines)
 if not text:return
 base=dict(state,pdf_page=page,book_page=page-18,kind=kind,text=text)
 records.append(base)

for idx in range(18,len(doc)):
 pg=doc[idx];pn=idx+1; entries=[]
 tables=[]
 if re.search(r'表\s*\d+[-－]\d+|续表',pg.get_text()):
  for tb in pg.find_tables(strategy='lines_strict').tables:
   rows=tb.extract()
   if len(rows)>1 and len(rows[0])>1:
    tables.append((tb.bbox,rows))
 for ti,(bb,rows) in enumerate(tables):
  clean=lambda v:normalize((v or '').replace('\n',''))
  columns=[clean(v) or f'第{k+1}列' for k,v in enumerate(rows[0])]
  tt='【表格文字（按原列对应；空白单元格不推断含义）】\n'
  tt+='\n'.join('；'.join(columns[k]+'：'+(clean(v) or '〔原表空白〕') for k,v in enumerate(row)) for row in rows[1:])
  entries.append({'t':tt,'size':10.5,'y':bb[1],'x':bb[0],'block':-100-ti,'table':True})
 for b in pg.get_text('dict')['blocks']:
  if b['type']!=0:continue
  for line in b['lines']:
   spans=[s for s in line['spans'] if s['text'].strip()]
   if not spans:continue
   x0,y0,x1,y1=line['bbox'];t=''.join(s['text'] for s in spans).strip()
   if x1<55 or x0>438 or y0<53 or y0>639:
    removed.append({'pdf_page':pn,'text':t,'bbox':list(line['bbox'])});continue
   if any(bb[0]-1<=x0 and x1<=bb[2]+1 and bb[1]-1<=y0 and y1<=bb[3]+1 for bb,rows in tables):continue
   size=collections.Counter(round(s['size'],2) for s in spans for c in s['text']).most_common(1)[0][0]
   entries.append({'t':t,'size':size,'y':y0,'x':x0,'block':b['number']})
 # Text block order is preserved for reading paragraphs; spatial sort across blocks.
 entries.sort(key=lambda e:(round(e['y']/3),e['x']))
 # Merge wrapped headings, including those in separate PDF text blocks.
 merged=[]
 for e in entries:
  if merged and any(abs(e['size']-v)<.08 for v in [13.98,16.02,18]) and abs(merged[-1]['size']-e['size'])<.08 and e['y']-merged[-1]['y']<35:
   merged[-1]['t']+=e['t'];merged[-1]['y']=e['y']
  else:merged.append(e.copy())
 raw=pg.get_text();nums=[]
 for b in pg.get_text('blocks'):
  if b[1]>620 and (b[0]<55 or b[0]>438) and re.fullmatch(r'\s*\d+\s*',b[4]):nums.append(int(b[4]))
 pagecheck.append({'pdf_page':pn,'book_page':pn-18,'printed_page_numbers':nums,'verified':pn-18 in nums,'first_page_without_number':pn==19 and not nums})
 vp=bool(pg.get_images()) or bool(re.search(r'(?:图|表)\s*\d+[-－]\d+',raw))
 if vp:visual.append(pn)
 buf=[];lastblock=None;foot=[]
 for e in merged:
  t=normalize(e['t']);sz=e['size'];q=re.match(r'^第\s*(\d+)\s*问\s*(.+)',t);s=re.match(r'^(\d+\.\d+)\s*(.+)',t)
  htype=None
  if q and abs(sz-16.02)<.08:htype='question'
  elif s and abs(sz-13.98)<.08:htype='section'
  elif sz>=17.9 and (t.startswith(('第','后记','附录'))):htype='part'
  if htype:
   emit(buf,pn);buf=[]
   if htype=='question':state.update(question_no=int(q[1]),question_title=q[2],section_no='',section_title='题目导语')
   elif htype=='section':state.update(section_no=s[1],section_title=s[2])
   else:state.update(part=t,question_no=None,question_title='',section_no='',section_title='')
   heads.append(dict(state,type=htype,pdf_page=pn,book_page=pn-18));lastblock=None;continue
  if sz<9.6 and ((e['y']>400 and e['x']<75 and re.match(r'^[①②③④⑤⑥⑦⑧⑨].{2,}',t)) or foot):foot.append(t);continue
  if lastblock is not None and e['block']!=lastblock:buf.append('\n')
  buf.append(t);lastblock=e['block']
 emit(buf,pn)
 manual=json.loads((ROOT/'image-table-transcription.json').read_text())
 for text in manual.get(str(pn),[]):emit([text],pn,'图片表格转写')
 if foot:
  # Footnotes are page-level evidence, not attributed to the last subsection.
  saved=state.copy();state.update(part='本页脚注',question_no=None,question_title='',section_no='',section_title='按脚注标记对应本页正文，不指定题目归属')
  emit(foot,pn,'脚注');state=saved

assert [h['question_no'] for h in heads if h['type']=='question']==list(range(1,61))
assert all(not p['printed_page_numbers'] or p['verified'] for p in pagecheck)
for p in pagecheck: p['basis']='印刷页码核对' if p['verified'] else '篇章起始页未印页码，按相邻连续页推定'
# Split long text at sentence boundaries. Each chunk has its own explicit hierarchy and exact source page.
chunks=[]
for r in records:
 text=r['text'];parts=[]
 while len(text)>1100:
  cut=max(text.rfind(c,400,1100) for c in ['。','；','\n'])
  if cut<400:cut=1099
  parts.append(text[:cut+1]);text=text[cut+1:]
 if text.strip():parts.append(text)
 for body in parts:
  rr=dict(r,text=body.strip(),chunk_id=f'os60-{len(chunks)+1:04d}',visual_page=r['pdf_page'] in visual)
  title=f"第{r['question_no']}问 {r['question_title']}" if r['question_no'] else r['part']
  header=f"【来源】《解码开源：开源生态60问》\n【题目】{title}\n【小节】{r['section_no']} {r['section_title']}\n【页码】书内第{r['book_page']}页；PDF第{r['pdf_page']}页\n【片段编号】{rr['chunk_id']}"
  if rr['kind']=='脚注':header+='\n【类型】页级脚注，不归属本页最后一个小节'
  rr['content']=header+'\n\n'+rr['text'];chunks.append(rr)
(ROOT/'knowledge-import.txt').write_text('\n\n<<<OS60_CHUNK>>>\n\n'.join(c['content'] for c in chunks),encoding='utf-8')
(ROOT/'chunks.jsonl').write_text('\n'.join(json.dumps(c,ensure_ascii=False) for c in chunks)+'\n',encoding='utf-8')
(ROOT/'hierarchy.json').write_text(json.dumps(heads,ensure_ascii=False,indent=2),encoding='utf-8')
(ROOT/'page-map.json').write_text(json.dumps(pagecheck,ensure_ascii=False,indent=2),encoding='utf-8')
(ROOT/'removed-margins.json').write_text(json.dumps(removed,ensure_ascii=False,indent=2),encoding='utf-8')
md=['# 解码开源：开源生态60问 — 清洗文本','正文范围：书内1–238页，PDF19–256页。前言、目录和版权页未混入正文检索。','图表提示：本文件为文字层提取；图形关系和表格单元格对应须以原PDF或配套页面图为准。']
for c in chunks:md.append('---\n\n'+c['content'])
(ROOT/'clean-book.md').write_text('\n\n'.join(md),encoding='utf-8')
(ROOT/'visual-pages').mkdir(exist_ok=True)
for pn in visual:
 doc[pn-1].get_pixmap(matrix=fitz.Matrix(1.3,1.3)).save(ROOT/'visual-pages'/f'pdf-{pn:03d}-book-{pn-18:03d}.png')
qa={'source_sha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),'pdf_pages':len(doc),'body_pages':len(pagecheck),'questions':60,'sections':sum(h['type']=='section' for h in heads),'chunks':len(chunks),'max_chunk_chars':max(len(c['content']) for c in chunks),'visual_reference_pages':visual,'printed_page_verifications':sum(p['verified'] for p in pagecheck),'page_number_exception':[p['pdf_page'] for p in pagecheck if not p['verified']],'limitations':['检测到边界的表格转换为列名与单元格配对文字；复杂合并单元格仍需原页复核。图片内文字与图中连线语义未转写，不能视作完整图像知识库。','跨页小节按页保留并重复完整层级；跨页句子可能分布于相邻片段。','未改变原书观点、历史叙述或事实错误；没有加入模型摘要。']}
(ROOT/'validation.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(qa,ensure_ascii=False))
