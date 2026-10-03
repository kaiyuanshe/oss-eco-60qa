import fitz,json,re,hashlib,shutil
from pathlib import Path
P=Path(__file__).resolve().parents[1];O=P/'full-library';pdf=fitz.open(P/'project_sources/01-70443-PDF-20260921.pdf')
qs=json.loads((P/'questions.json').read_text());bounds=json.loads((P/'full-work/boundaries.json').read_text());figs=json.loads((P/'full-work/images.json').read_text());desc=json.loads((P/'full-work/figure-descriptions.json').read_text());samples={d['number']:d for d in json.loads((P/'samples/sample-data.json').read_text())}
assert [x['q'] for x in bounds]==list(range(1,61))
def clean(s):
 s=s or '';s=re.sub(r'(?<=[\u4e00-\u9fff])\s+(?=[\u4e00-\u9fff])','',s)
 return re.sub(r'\s+',' ',s).strip()
def join(a,b):
 return a+(' ' if a and re.search(r'[A-Za-z0-9]$',a) and re.match(r'[A-Za-z0-9]',b) else '')+b
cache={};tableaudit=[]
for pgno in range(19,250):
 page=pdf[pgno-1]; tables=[]
 for t in page.find_tables(strategy='lines_strict').tables:
  if t.row_count<2 or t.col_count<2:continue
  r=fitz.Rect(t.bbox)
  if r.x0<50 or r.x1>440:continue
  rows=[[clean(c) for c in row] for row in t.extract()]
  tables.append({'bbox':r,'rows':rows})
  tableaudit.append({'pdf':pgno,'bbox':list(r),'rows':len(rows),'cols':len(rows[0])})
 events=[]
 for b in page.get_text('dict')['blocks']:
  if b['type']!=0:continue
  for l in b['lines']:
   r=fitz.Rect(l['bbox']);text=''.join(s['text'] for s in l['spans']);sz=max(s['size'] for s in l['spans'])
   if r.x0<55 or r.x1>438 or r.y0<53 or r.y1>640 or not text.strip():continue
   if any(t['bbox'].contains(fitz.Point((r.x0+r.x1)/2,(r.y0+r.y1)/2)) for t in tables):continue
   events.append({'y':r.y0,'y1':r.y1,'text':text,'size':sz,'kind':'line'})
 for t in tables:events.append({'y':t['bbox'].y0,'y1':t['bbox'].y1,'kind':'table_group','rows':t['rows']})
 for f in figs:
  if f['pdf']==pgno:events.append({'y':f['bbox'][1],'y1':f['bbox'][3],'kind':'figure','file':f['file'],'caption':f['caption'].strip(),'text':desc[f['name']]})
 cache[pgno]=sorted(events,key=lambda x:x['y'])
print('Pages parsed:',len(cache),'tables:',len(tableaudit),flush=True)
allData=[]
for ix,q in enumerate(qs):
 num=q['id'];start=bounds[ix];end=bounds[ix+1] if ix<59 else {'pdf':250,'bbox':[0,0,0,0]}
 if num in samples:
  d=samples[num];d['version']=1;d['file']=f'q{num:03}.md';allData.append(d);shutil.copyfile(P/'samples/final'/d['file'],O/d['file']);continue
 blocks=[];buf='';bufstart=q['page'];page=q['page'];bullet=False;chapterstop=False;firstbody=False
 def flush(kind='paragraph'):
  global buf
  if buf.strip():blocks.append({'text':buf.strip(),'page_start':bufstart,'page_end':page,'kind':kind})
  buf=''
 for pgno in range(start['pdf'],min(end['pdf'],249)+1):
  if chapterstop:break
  page=pgno-18
  for ev in cache[pgno]:
   if pgno==start['pdf'] and ev['y']<=start['bbox'][3]-1:continue
   if pgno==end['pdf'] and ev['y']>=end['bbox'][1]-1:break
   if ev['kind']=='line':
    text=ev['text'].strip()
    if re.match(r'第\s*[1-6]\s*篇',text) or text=='后记':chapterstop=True;break
    # Continuation lines of a two-line question title.
    if not firstbody and ev['size']>=15.5:continue
    firstbody=True
    hm=re.match(rf'({num}\.\d+)\s+(.+)',text)
    if hm:
     flush();bufstart=page;buf=text;flush('heading');continue
    # A wrapped subsection heading keeps the large heading font.
    if not buf and blocks and blocks[-1]['kind']=='heading' and 13<=ev['size']<15.5:
     blocks[-1]['text']=join(blocks[-1]['text'],text);blocks[-1]['page_end']=page;continue
    if text in ['●','•']:
     flush();bullet=True;continue
    if re.match(r'^(图|表)\s*\d+[-－]\d+\s',text) or text=='续表':
     flush();bufstart=page;buf=text;flush('caption');continue
    if re.match(r'^[一二三四五六七八九十]+、',text):
     flush();bufstart=page;buf=text;flush('subheading');continue
    if not buf:bufstart=page;buf='- ' if bullet else '';bullet=False
    buf=join(buf,text)
    if ev['text'].endswith(' '):flush()
   else:
    flush();b={'text':ev.get('text',''),'page_start':page,'page_end':page,'kind':ev['kind']}
    if ev['kind']=='table_group':
     b['rows']=ev['rows'];b['text']='\n'.join('| '+' | '.join(row)+' |' for row in ev['rows'])
    else:b.update(file=ev['file'],caption=ev['caption'])
    blocks.append(b)
 flush()
 while blocks and not blocks[-1]['text'].strip():blocks.pop()
 headings=[re.sub(r'^\d+\.\d+\s*','',b['text']) for b in blocks if b['kind']=='heading']
 summary='本问围绕“'+q['title']+'”展开，依次讨论'+ '；'.join(headings[:4])+('等内容。' if len(headings)>4 else '。')
 aliases=[q['title']+'？']+[f'请介绍{x}。' for x in headings[:3]]
 keywords=[q['cat']]+headings[:6]
 d={'id':f'q{num:03}','number':num,'title':q['title'],'chapter':q['cat'],'summary':summary,'keywords':keywords,'aliases':aliases,'source_title':'解码开源：开源生态60问','source_author':'庄表伟','source_file':'70443-PDF-20260921.pdf','source_library_id':'libfile_99447eeb2bb881918365025199c91133','source_pages':[blocks[0]['page_start'],blocks[-1]['page_end']],'pdf_pages':[blocks[0]['page_start']+18,blocks[-1]['page_end']+18],'url_path':f'/questions/q{num:03}/','version':1,'updated_at':'2026-09-25','status':'source_transcription_not_fact_checked','file':f'q{num:03}.md','blocks':blocks}
 allData.append(d)
 front={k:v for k,v in d.items() if k not in ['blocks','number','file','aliases']}
 lines=['---']+[f'{k}: {json.dumps(v,ensure_ascii=False)}' for k,v in front.items()]+['---','',f'# 第{num}问 {q["title"]}','','## 编辑摘要（新增，非原文）','',summary,'','## 常见问法（新增检索辅助）','']+['- '+x for x in aliases]+['','## 原书正文（转录）','','> 保留原书观点与历史案例，未作当前事实更新。正文页码按书内印刷页码；PDF页码从1起，等于书内页码加18。图示保留原图，文字说明标为整理转述。','']
 current=None
 for i,b in enumerate(blocks):
  pg=str(b['page_start']) if b['page_start']==b['page_end'] else f"{b['page_start']}–{b['page_end']}"
  if current!=pg:lines+=['',f'<!-- source: q{num:03}; print_pages: {pg}; pdf_pages: {b["page_start"]+18}–{b["page_end"]+18} -->',''];current=pg
  if b['kind']=='table_group':
   rows=b['rows'];lines+=['| '+' | '.join(c.replace('|','\\|') for c in row)+' |' for row in rows[:1]]+['| '+' | '.join(['---']*len(rows[0]))+' |']+['| '+' | '.join(c.replace('|','\\|') for c in row)+' |' for row in rows[1:]]+['']
  elif b['kind']=='figure':lines += [f'![{b["caption"]}]({b["file"]})','',f'**图示文字说明（整理转述）**：{b["text"]}','']
  else:lines+=[('### ' if b['kind']=='heading' else '#### ' if b['kind']=='subheading' else '')+b['text'],'']
 lines+=['','## 来源与整理说明','',f'来源：《解码开源：开源生态60问》，庄表伟，第{num}问；书内第{d["source_pages"][0]}–{d["source_pages"][1]}页；PDF第{d["pdf_pages"][0]}–{d["pdf_pages"][1]}页。',f'拟定网页路径：`{d["url_path"]}`（尚未发布）。','摘要、关键词、常见问法与图示说明为新增整理内容；正文与表格保留原稿内容。']
 (O/d['file']).write_text('\n'.join(lines))
(O/'questions-data.json').write_text(json.dumps(allData,ensure_ascii=False,separators=(',',':')))
(O/'index.json').write_text(json.dumps({'version':2,'question_count':60,'source_pdf_sha256':hashlib.sha256((P/'project_sources/01-70443-PDF-20260921.pdf').read_bytes()).hexdigest(),'questions':[{k:v for k,v in d.items() if k!='blocks'} for d in allData]},ensure_ascii=False,indent=2))
(P/'full-work/table-audit.json').write_text(json.dumps(tableaudit,ensure_ascii=False,indent=2))
print('Questions',len(allData),'blocks',sum(len(d['blocks']) for d in allData),'characters',sum(sum(len(b['text']) for b in d['blocks']) for d in allData),flush=True)
