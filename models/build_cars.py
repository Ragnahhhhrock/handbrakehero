"""Builds the five stylised low-poly rally cars in Blender (bpy) and exports
cars.blend, one .glb per car, and ../cars.json for the game.
Run: python3 models/build_cars.py   (needs `pip install bpy`)
Blender axes: X forward, Y left, Z up. Liveries are original colour schemes: no logos or wordmarks."""
import bpy, bmesh, json, math, os
from mathutils import Matrix, Vector
HERE=os.path.dirname(os.path.abspath(__file__))
BODY,GLASS,C2,SILL,BLACK,C3,WHITE,LENS,FLAP,GREY=range(10)
N=None
CARS={
 'imp':dict(L2=2.17,A=1.26,B=1.26,pal=[0x1b3f96,0x0e1620,0xf2c318,0x0f2260,0x111111,0xf2c318,0xf1f1ec,0xd9dde2,0xb71c25,0x8a8d91],
  st=[(2.17,.36,.56,.70,N,0),(2.06,.30,.63,.84,N,0),(1.5,.30,.73,.87,N,0),(0.95,.30,.79,.88,N,0),(0.48,.30,.83,.88,1.27,.62),(-0.52,.30,.85,.88,1.29,.62),(-1.1,.30,.86,.87,N,0),(-2.05,.30,.85,.85,N,0),(-2.17,.38,.80,.74,N,0)],
  pillar=-0.05,wing=dict(z=1.36,x=-1.95,w=1.6,d=.45,h=.16),
  planes=[((0,.10,0),(0,1,0)),((0,.26,0),(0,1,0)),((0,-.10,0),(0,1,0)),((0,-.26,0),(0,1,0))],
  liv=lambda c,top,side:C2 if top and .10<abs(c.y)<.26 else N),
 'del':dict(L2=1.975,A=1.22,B=1.26,pal=[0xf1f1ec,0x0e1620,0x20386e,0x20386e,0x111111,0x20386e,0xf1f1ec,0xd9dde2,0xb71c25,0x8a8d91],
  st=[(1.975,.36,.58,.72,N,0),(1.87,.30,.65,.85,N,0),(1.4,.30,.76,.88,N,0),(0.86,.30,.82,.89,N,0),(0.5,.30,.86,.89,1.33,.66),(-1.42,.30,.9,.89,1.36,.66),(-1.86,.30,1.0,.87,N,0),(-1.975,.36,.96,.80,N,0)],
  pillar=-0.3,pillar2=-1.2,wing=dict(z=1.4,x=-1.5,w=1.4,d=.3,h=.0),flare=.06,
  planes=[((0,0,.5),(0,0,1)),((0,0,.66),(0,0,1)),((0,.2,0),(0,1,0)),((0,-.2,0),(0,1,0))],
  liv=lambda c,top,side:C2 if (side and .5<c.z<.66) or (top and abs(c.y)<.2) else N),
 'esc':dict(L2=2.14,A=1.3,B=1.31,pal=[0xf0f0ea,0x0e1620,0x1a4fb0,0x1a4fb0,0x111111,0x79aeea,0xf1f1ec,0xd9dde2,0xb71c25,0x8a8d91],
  st=[(2.14,.36,.55,.72,N,0),(2.03,.30,.62,.85,N,0),(1.5,.30,.71,.88,N,0),(0.95,.30,.78,.89,N,0),(0.5,.30,.83,.89,1.30,.63),(-0.55,.30,.86,.89,1.33,.63),(-1.55,.30,.97,.87,N,0),(-2.05,.30,.93,.85,N,0),(-2.14,.38,.88,.76,N,0)],
  pillar=-0.05,wing=dict(z=1.14,x=-1.95,w=1.72,d=.6,h=.2),wing2=dict(z=1.42,x=-1.75,w=1.5,d=.3),
  planes=[((0,0,.52),(.11,0,1)),((0,0,.60),(.11,0,1)),((0,0,.66),(.11,0,1))],
  liv=lambda c,top,side:(C2 if c.z+.11*c.x<.52 else C3 if .60<c.z+.11*c.x<.66 else N) if side else N),
 'lan':dict(L2=2.15,A=1.25,B=1.27,pal=[0xf2f2ee,0x0e1620,0xb71c25,0xb71c25,0x111111,0xb71c25,0xf1f1ec,0xd9dde2,0x222222,0x8a8d91],
  st=[(2.15,.36,.58,.72,N,0),(2.05,.30,.64,.84,N,0),(1.55,.30,.73,.86,N,0),(0.95,.30,.79,.87,N,0),(0.52,.30,.83,.87,1.26,.63),(-0.5,.30,.85,.87,1.28,.63),(-1.08,.30,.85,.86,N,0),(-2.05,.30,.86,.84,N,0),(-2.15,.38,.82,.74,N,0)],
  pillar=-0.03,wing=dict(z=1.36,x=-1.95,w=1.5,d=.4,h=.16),
  planes=[((u,0,0),(1,0,.9)) for u in(-1.15,-.95,-.8,-.6,-.45,-.25)],
  liv=lambda c,top,side:C2 if side and any(a<c.x+.9*c.z<b for a,b in((-1.15,-.95),(-.8,-.6),(-.45,-.25))) else N),
 'cel':dict(L2=2.15,A=1.28,B=1.3,pal=[0xf1f1ec,0x0e1620,0x1e7a3c,0xc4262e,0x111111,0xc4262e,0xf1f1ec,0xd9dde2,0x1e7a3c,0x8a8d91],
  st=[(2.15,.36,.50,.70,N,0),(2.02,.30,.56,.84,N,0),(1.45,.30,.65,.87,N,0),(0.85,.30,.71,.88,N,0),(0.22,.30,.78,.88,1.2,.60),(-0.72,.30,.82,.88,1.24,.60),(-1.6,.30,.88,.86,N,0),(-2.05,.30,.85,.84,N,0),(-2.15,.38,.80,.74,N,0)],
  pillar=-0.25,wing=dict(z=1.28,x=-1.98,w=1.55,d=.4,h=.16),
  planes=[((-.55,0,0),(1,0,.6)),((-.43,0,0),(1,0,.6))],
  liv=lambda c,top,side:(C2 if c.x+.6*c.z<-.55 else C3 if c.x+.6*c.z<-.43 else N) if (top or side) else N),
}
def ring(s):
    x,zb,zs,w,zr,wr=s;h=zs-zb
    p=[(0,zb),(w*.93,zb),(w,zb+min(.14,h*.3)),(w,zs-min(.10,h*.25)),(w*.94,zs)]
    p+=[(wr,zr),(0,zr+.03)] if zr else [(w*.78,zs+.025),(0,zs+.045)]
    full=p+[(-y,z) for y,z in p[5:0:-1]]
    return [Vector((x,y,z)) for y,z in full]
def build(cid,d):
    bm=bmesh.new();strip=bm.faces.layers.int.new('strip');gl=bm.faces.layers.int.new('glass')
    rings=[[bm.verts.new(v) for v in ring(s)] for s in d['st']]
    for i in range(len(rings)-1):
        a,b=d['st'][i][4] is not None,d['st'][i+1][4] is not None
        for k in range(12):
            f=bm.faces.new((rings[i][k],rings[i][(k+1)%12],rings[i+1][(k+1)%12],rings[i+1][k]));sk=k if k<6 else 11-k;f[strip]=sk
            f[gl]=1 if ((a or b) and sk==4) or ((a!=b) and sk==5) else 0
    for r in (rings[0],rings[-1][::-1]):
        f=bm.faces.new(r);f[strip]=9
    bmesh.ops.recalc_face_normals(bm,faces=bm.faces[:])
    planes=list(d['planes'])
    for key in('pillar','pillar2'):
        if key in d:planes+=[((d[key]-.045,0,0),(1,0,0)),((d[key]+.045,0,0),(1,0,0))]
    for co,no in planes:
        bmesh.ops.bisect_plane(bm,geom=bm.verts[:]+bm.edges[:]+bm.faces[:],dist=1e-5,plane_co=Vector(co),plane_no=Vector(no).normalized())
    for f in bm.faces:
        c=f.calc_center_median();s=f[strip]
        if f[gl]:
            pil=s==4 and any(k in d and abs(c.x-d[k])<.045 for k in('pillar','pillar2'))
            f.material_index=BODY if pil else GLASS;continue
        if s==0:f.material_index=BLACK;continue
        if s==1:f.material_index=SILL;continue
        r=d['liv'](c,s in(4,5),s in(2,3));f.material_index=BODY if r is None else r
    L2,A,B=d['L2'],d['A'],d['B'];st=d['st'];nose=st[0][2];W=max(s[3] for s in st)
    def box(x,y,z,sx,sy,sz,idx,mirror=False,rot=0):
        for sg in((1,-1) if mirror else (1,)):
            m=Matrix.Translation((x,y*sg,z))@Matrix.Rotation(rot,4,'Y')@Matrix.Diagonal((sx,sy,sz,1))
            r=bmesh.ops.create_cube(bm,size=1,matrix=m)
            for f in {f for v in r['verts'] for f in v.link_faces}:f.material_index=idx
    box(L2-.03,0,.36,.2,1.72,.18,BLACK);box(L2+.03,0,.27,.16,1.5,.04,BLACK)            # bumper, splitter
    box(-L2+.03,0,.4,.16,1.7,.18,BODY)                                                  # rear bumper
    box(L2-.01,0,nose-.07,.06,.62,.1,BLACK);box(L2-.01,.52,nose-.07,.06,.36,.12,LENS,True)  # grille, headlights
    cow=next(s for s in st if s[4] is not None)
    box(cow[0]+.28,W+.06,cow[2]+.08,.1,.16,.1,C2 if cid!='imp' else BODY,True)          # mirrors
    box((cow[0]-.45),0,cow[4]+.065,.42,.36,.07,BLACK)                                   # roof vent
    for wx in(A,-B):box(wx-.44,.8,.2,.03,.28,.3,FLAP,True)                              # mud flaps
    box(-L2-.02,.42,.36,.12,.09,.09,GREY,True)                                          # exhausts
    w=d['wing'];box(w['x'],0,w['z'],w['d'],w['w'],.05,C2 if cid!='imp' else BODY,rot=-.1)
    if w['h']:
        box(w['x'],w['w']/2,w['z']-w['h']/2+.03,w['d']+.06,.04,w['h']+.06,BLACK,True)
        dz=w['z']-.86;box(w['x']+.03,.5,.86+dz/2,.09,.06,dz,BLACK,True)
    if 'wing2' in d:
        w2=d['wing2'];box(w2['x'],0,w2['z'],w2['d'],w2['w'],.045,C2,rot=-.12);box(w2['x'],.55,(w2['z']+1.3)/2-.02,.07,.05,w2['z']-1.26,BLACK,True)
    if cid=='imp':box(1.35,.3,.76,.3,.12,.03,BLACK,True);box(1.15,0,.79,.35,.4,.05,BLACK)  # bonnet vents, scoop
    if cid=='cel':box(1.35,0,.69,.5,.5,.04,BLACK)
    if cid=='lan':box(1.4,.28,.76,.4,.14,.03,BLACK,True)
    # wheel-arch wells and flares
    fl=d.get('flare',.045);ro=.50
    for wx in(A,-B):
        for sg in(1,-1):
            yb=(W-.012)*sg;yo=(W+fl)*sg;ang=[math.pi*i/8 for i in range(9)]
            cen=bm.verts.new((wx,yb+.004*sg,.33));arc=[bm.verts.new((wx+.42*math.cos(a),yb+.004*sg,.33+.42*math.sin(a))) for a in ang]
            for i in range(8):bm.faces.new((cen,arc[i],arc[i+1])).material_index=BLACK
            q=[[bm.verts.new((wx+r*math.cos(a),y,.33+r*math.sin(a))) for a in ang] for r,y in((.42,yo),(ro,yo),(ro+.02,yb))]
            for j in range(2):
                for i in range(8):bm.faces.new((q[j][i],q[j][i+1],q[j+1][i+1],q[j+1][i])).material_index=BODY
    bmesh.ops.triangulate(bm,faces=bm.faces[:])
    bm.verts.ensure_lookup_table();bm.verts.index_update()
    out=dict(v=[round(c*1000) for v in bm.verts for c in(-v.co.y,v.co.z,-v.co.x)],t=[v.index for f in bm.faces for v in f.verts],c=[f.material_index for f in bm.faces],pal=d['pal'],lampY=round(nose+.07,3))
    me=bpy.data.meshes.new(cid)
    for i,h in enumerate(d['pal']):
        m=bpy.data.materials.new(f'{cid}_{i}');m.diffuse_color=(((h>>16)&255)/255,((h>>8)&255)/255,(h&255)/255,1);me.materials.append(m)
    bm.to_mesh(me);bm.free();ob=bpy.data.objects.new(cid,me);bpy.context.scene.collection.objects.link(ob)
    return out,ob
for o in list(bpy.data.objects):bpy.data.objects.remove(o)
res={};obs={}
for i,(cid,d) in enumerate(CARS.items()):
    res[cid],obs[cid]=build(cid,d);obs[cid].location.y=i*2.6
    print(cid,'tris',len(res[cid]['c']),'verts',len(res[cid]['v'])//3)
json.dump(res,open(os.path.join(HERE,'..','cars.json'),'w'),separators=(',',':'))
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(HERE,'cars.blend'))
try:
    for cid,ob in obs.items():
        for o in obs.values():o.select_set(o is ob)
        y=ob.location.y;ob.location.y=0
        bpy.ops.export_scene.gltf(filepath=os.path.join(HERE,cid+'.glb'),use_selection=True);ob.location.y=y
except Exception as e:print('glb export skipped:',e)
