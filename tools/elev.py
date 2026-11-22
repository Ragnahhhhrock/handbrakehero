import json,math,time,urllib.request,sys
d=json.load(open('route.json'));pts=d['routes'][0]['geometry']['coordinates']
# dedupe & resample every 15 m
R=6371000
def dist(a,b):
    x=math.radians(b[0]-a[0])*math.cos(math.radians((a[1]+b[1])/2));y=math.radians(b[1]-a[1]);return R*math.hypot(x,y)
clean=[pts[0]]
for p in pts[1:]:
    if dist(clean[-1],p)>0.5: clean.append(p)
out=[clean[0]];step=15.0;acc=0
for i in range(1,len(clean)):
    a,b=clean[i-1],clean[i];L=dist(a,b);t=step-acc
    while t<=L:
        f=t/L;out.append([a[0]+(b[0]-a[0])*f,a[1]+(b[1]-a[1])*f]);t+=step
    acc=(acc+L)%step if False else L-(t-step)
out.append(clean[-1])
print(len(out),file=sys.stderr)
ds=sys.argv[1]
elev=[]
for i in range(0,len(out),100):
    chunk=out[i:i+100];loc='|'.join(f"{p[1]:.6f},{p[0]:.6f}" for p in chunk)
    for attempt in range(3):
        try:
            r=json.load(urllib.request.urlopen(f"https://api.opentopodata.org/v1/{ds}?locations={loc}",timeout=30))
            if r['status']=='OK': break
        except Exception as e: print(e,file=sys.stderr); time.sleep(2)
    elev+= [x['elevation'] for x in r['results']]
    time.sleep(1.1)
json.dump({'pts':[[p[0],p[1],e] for p,e in zip(out,elev)]},open('track_raw.json','w'))
print(min(elev),max(elev),elev[0],elev[-1])
