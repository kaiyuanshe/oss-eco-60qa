import fitz,re,json
from pathlib import Path
P=Path(__file__).resolve().parents[1];pdf=fitz.open(P/'project_sources/01-70443-PDF-20260921.pdf');out=[]
for idx in range(18,249):
 page=pdf[idx];images=page.get_image_info();groups=[]
 for im in images:
  r=fitz.Rect(im['bbox'])
  if groups and r.y0-groups[-1].y1<12 and r.y0>=groups[-1].y0 and abs(r.x0-groups[-1].x0)<60:groups[-1]|=r
  else:groups.append(r)
 for j,r in enumerate(groups):
  if idx+1 in [21,97,98]:continue
  after=page.get_text(clip=fitz.Rect(55,r.y1,438,min(640,r.y1+85)))
  match=re.search(r'图\s*(\d+)\s*[-－]\s*(\d+)\s*([^\n]*)',after)
  name=f'fig{match[1]}-{match[2]}' if match else f'fig-p{idx+1}-{j+1}'
  path=P/'full-library'/f'{name}.png';page.get_pixmap(matrix=fitz.Matrix(2.5,2.5),clip=r).save(path)
  out.append({'name':name,'file':path.name,'pdf':idx+1,'page':idx-17,'bbox':list(r),'caption':match[0] if match else '图3-3 分图：OpenRank变化','q':int(match[1]) if match else 3})
(P/'full-work/images.json').write_text(json.dumps(out,ensure_ascii=False,indent=2));print([(x['name'],x['pdf'],x['caption']) for x in out])
