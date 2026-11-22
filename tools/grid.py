import json,time,urllib.request,sys
t=json.load(open('track_raw.json'))['pts']
lo=[p[0] for p in t];la=[p[1] for p in t]
pad=0.012
x0,x1=min(lo)-pad,max(lo)+pad;y0,y1=min(la)-pad,max(la)+pad
NX,NY=44,40
pts=[(x0+(x1-x0)*i/(NX-1),y0+(y1-y0)*j/(NY-1)) for j in range(NY) for i in range(NX)]
el=[]
for k in range(0,len(pts),100):
    loc='|'.join(f"{p[1]:.5f},{p[0]:.5f}" for p in pts[k:k+100])
    for a in range(4):
        try:
            r=json.load(urllib.request.urlopen(f"https://api.opentopodata.org/v1/eudem25m?locations={loc}",timeout=30))
            if r['status']=='OK':break
        except Exception as e: print(e,file=sys.stderr);time.sleep(3)
    el+=[x['elevation'] if x['elevation'] is not None else 0 for x in r['results']]
    time.sleep(1.1)
json.dump({'x0':x0,'x1':x1,'y0':y0,'y1':y1,'nx':NX,'ny':NY,'h':el},open('grid.json','w'))
print(len(el),min(el),max(el))
