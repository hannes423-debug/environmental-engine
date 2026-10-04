import json, base64
import os; S=os.path.dirname(os.path.abspath(__file__))+'/'
p=S+'../index(1).html'; L=open(p,encoding='utf8').read().split('\n')
a=L.index('window.TREE_ART.spruce = {'); b=a
while L[b]!='};': b+=1
meta=json.load(open(S+'spruce.meta.json'))
b64=base64.b64encode(open(S+'spruce.webp','rb').read()).decode()
chunks=[b64[i:i+4000] for i in range(0,len(b64),4000)]
lines=['window.TREE_ART.spruce = {','meta: {"version":2,"ppu":90,"atlas":'+json.dumps(meta['atlas'])+',"sprites":{']
ks=list(meta['sprites'])
for i,k in enumerate(ks): lines.append(json.dumps(k)+':'+json.dumps(meta['sprites'][k],separators=(',',':'))+(',' if i<len(ks)-1 else ''))
lines+=['}},','atlas: ["data:image/webp;base64,"]+[]' if False else 'atlas: ["data:image/webp;base64,",']
lines+=['"'+c+'"'+(',' if j<len(chunks)-1 else '') for j,c in enumerate(chunks)]
lines+=['].join("")','};']
L[a:b+1]=lines
open(p,'w',encoding='utf8').write('\n'.join(L)); print('replaced',b-a+1,'with',len(lines))
