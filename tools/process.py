import json,math
t=json.load(open('track_raw.json'))['pts'];g=json.load(open('grid.json'))
lat0=43.9768;lon0=7.3918;R=6371000;cl=math.cos(math.radians(lat0))
def xy(lon,lat): return (math.radians(lon-lon0)*cl*R, -math.radians(lat-lat0)*R)
P=[list(xy(p[0],p[1]))+[p[2]] for p in t]
n=len(P)
# smooth xy lightly, elevation more
def smooth(arr,k):
    out=[]
    for i in range(len(arr)):
        a=max(0,i-k);b=min(len(arr),i+k+1);out.append(sum(arr[a:b])/(b-a))
    return out
X=smooth([p[0] for p in P],1);Z=smooth([p[1] for p in P],1);Y=smooth(smooth([p[2] for p in P],3),3)
X[0],Z[0]=P[0][0],P[0][1];X[-1],Z[-1]=P[-1][0],P[-1][1]
# cumulative distance
D=[0]
for i in range(1,n): D.append(D[-1]+math.hypot(X[i]-X[i-1],Z[i]-Z[i-1]))
# heading & curvature (signed, + = right turn in screen x east z south)
H=[math.atan2(X[i+1]-X[i],-(Z[i+1]-Z[i])) for i in range(n-1)];H.append(H[-1])
def wrap(a):
    while a>math.pi:a-=2*math.pi
    while a<-math.pi:a+=2*math.pi
    return a
K=[0]*n
for i in range(1,n-1):
    ds=(D[i+1]-D[i-1])/2 or 1
    K[i]=wrap(H[i]-H[i-1])/ds
Ks=smooth(K,2)
# corner detection
TH=1/250
notes=[];i=0
def grade(r,ang):
    if r<14 or abs(ang)>140: return 'hairpin'
    for g,lim in ((1,22),(2,35),(3,55),(4,85),(5,130),(6,250)):
        if r<lim: return str(g)
    return None
while i<n:
    if abs(Ks[i])>TH:
        s=1 if Ks[i]>0 else -1;j=i
        while j<n and Ks[j]*s>TH*0.7: j+=1
        seg=Ks[i:j];kmax=max(abs(k) for k in seg)
        ang=math.degrees(sum(Ks[m]*(D[min(m+1,n-1)]-D[m]) for m in range(i,j)))
        length=D[min(j,n-1)]-D[i]
        if abs(ang)>18:
            gr=grade(1/kmax,ang)
            if gr:
                notes.append({'d':round(D[i],1),'e':round(D[min(j,n-1)],1),'dir':'right' if s>0 else 'left','g':gr,'ang':round(ang),'long':length>90 and gr not in('hairpin',)})
        i=j
    else: i+=1
# phrase
def phrase(nt):
    if nt['g']=='hairpin': return f"hairpin {nt['dir']}"
    return f"{nt['dir']} {nt['g']}"+(' long' if nt['long'] else '')
for k,nt in enumerate(notes):
    nt['t']=phrase(nt)
    if k+1<len(notes):
        gap=notes[k+1]['d']-nt['e']
        nt['gap']=round(gap)
# split points
splits=[round(D[-1]*f) for f in (0.33,0.66)]
summit=max(range(n),key=lambda i:Y[i])
out={'x':[round(v,1) for v in X],'z':[round(v,1) for v in Z],'y':[round(v,1) for v in Y],'d':[round(v,1) for v in D],
'notes':notes,'len':round(D[-1]),'summit':summit}
# grid in local coords
gx0,gz1=xy(g['x0'],g['y0']);gx1,gz0=xy(g['x1'],g['y1'])
# grid rows j go south->north (y0..y1); convert so row 0 = north (min z)
h=g['h'];nx,ny=g['nx'],g['ny']
rows=[h[j*nx:(j+1)*nx] for j in range(ny)][::-1]
out['grid']={'x0':round(gx0),'x1':round(gx1),'z0':round(gz0),'z1':round(gz1),'nx':nx,'ny':ny,'h':[round(v) for r in rows for v in r]}
json.dump(out,open('track.json','w'),separators=(',',':'))
hp=[x for x in notes if x['g']=='hairpin']
print('len',round(D[-1]),'notes',len(notes),'hairpins',len(hp),'summit d',round(D[summit]),'y',round(Y[summit]))
print('hairpins after summit',len([x for x in hp if x['d']>D[summit]]))
from collections import Counter;print(Counter(x['g'] for x in notes))
