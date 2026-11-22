"""Builds the five period rally cars in Blender (bpy) and exports cars.blend,
one .glb per car, and ../cars.json for the game.
Run: python3 models/build_cars.py   (needs `pip install bpy`)

v2: bodies are lofted from cross-sections driven by side-profile and plan-view
curves set to each car's published dimensions (length, wheelbase, overhangs,
height, width). Proper greenhouse (windscreen, pillars, side and rear glass),
open wheel arches with flares, and per-car details: bumpers, intakes,
headlamp layout, rear lights, bonnet vents/scoops, wings, mirrors, mud flaps.
Smooth normals are exported per triangle corner.

Blender axes: X forward, Y left, Z up. Wheel centres at z=0.33 (tyre radius).
Liveries are original colour schemes in team colours: no logos or wordmarks."""
import bpy, bmesh, json, math, os
from mathutils import Matrix, Vector
HERE = os.path.dirname(os.path.abspath(__file__))
BODY, GLASS, C2, SILL, BLACK, C3, WHITE, LENS, FLAP, GREY, RED, AMBER, C4 = range(13)
RW, RA = 0.33, 0.385          # tyre radius, arch radius

# ---------- curve helpers ----------
def pchip(pts):
    """Monotone cubic through (x,v) points (any x order). Returns f(x)."""
    pts = sorted(pts)
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]; n = len(xs)
    h = [xs[i+1]-xs[i] for i in range(n-1)]; d = [(ys[i+1]-ys[i])/h[i] for i in range(n-1)]
    m = [0.0]*n
    if n == 2: m = [d[0], d[0]]
    else:
        m[0] = d[0]; m[-1] = d[-1]
        for i in range(1, n-1):
            if d[i-1]*d[i] <= 0: m[i] = 0
            else:
                w1, w2 = 2*h[i]+h[i-1], h[i]+2*h[i-1]
                m[i] = (w1+w2)/(w1/d[i-1]+w2/d[i])
    def f(x):
        if x <= xs[0]: return ys[0]
        if x >= xs[-1]: return ys[-1]
        i = max(k for k in range(n-1) if xs[k] <= x)
        t = (x-xs[i])/h[i]; t2, t3 = t*t, t*t*t
        return ((2*t3-3*t2+1)*ys[i] + (t3-2*t2+t)*h[i]*m[i] + (-2*t3+3*t2)*ys[i+1] + (t3-t2)*h[i]*m[i+1])
    return f
def lerp(a, b, t): return a+(b-a)*t
def sstep(a, b, v):
    t = min(1, max(0, (v-a)/(b-a))); return t*t*(3-2*t)

# ---------- the cars (real dimensions, metres) ----------
# zt top centre line, zs shoulder/beltline, zb underside, ws shoulder half-width,
# gh greenhouse: wsb windscreen base, rf roof front, rb roof back, rsb rear-glass base,
# ze roof-edge height, wr roof half-width; win: side-glass x ranges between pillars.
CARS = {
 # Subaru Impreza 555 (GC8 4-door): L 4340, WB 2520, H ~1405 (lowered ~1370)
 'imp': dict(xf=2.19, xr=-2.15, A=1.26, B=1.26, fl=0.05, flare='round',
  zt=[(2.19,.58),(2.15,.66),(2.02,.71),(1.5,.79),(0.93,.855),(0.6,1.05),(0.08,1.345),(-0.3,1.37),(-0.85,1.35),(-1.15,1.2),(-1.43,1.0),(-1.7,.99),(-2.04,.975),(-2.15,.9)],
  zs=[(2.19,.55),(2.08,.65),(1.6,.75),(0.93,.82),(0,.855),(-1.0,.895),(-1.55,.935),(-2.05,.93),(-2.15,.87)],
  zb=[(2.19,.22),(2.0,.21),(1.5,.25),(-1.8,.27),(-2.15,.33)],
  ws=[(2.19,.68),(2.1,.78),(1.8,.835),(1.2,.845),(0,.855),(-1.5,.855),(-2.0,.835),(-2.15,.77)],
  gh=dict(wsb=.93, rf=.08, rb=-.85, rsb=-1.43, ze=1.30, wr=.62), win=[(.82,-.22),(-.31,-1.08)],
  pal=[0x1b3f96,0x10161e,0xf2c318,0x0f2260,0x141414,0xf1f1ec,0xf4f4f0,0xdfe6ee,0xf1f1ec,0x8a8d91,0x8a1010,0xe08a1a,0xd2ac2e]),
 # Lancia Delta HF Integrale Evo 2: L 3900, WB 2480, W 1770, H 1365, FOH 762, ROH 657
 'del': dict(xf=1.98, xr=-1.92, A=1.22, B=1.26, fl=0.075, flare='box',
  zt=[(1.98,.66),(1.94,.73),(1.5,.785),(0.88,.84),(0.5,1.08),(0.28,1.33),(-0.4,1.345),(-1.52,1.34),(-1.66,1.18),(-1.81,1.0),(-1.9,.97),(-1.92,.92)],
  zs=[(1.98,.64),(1.85,.72),(1.4,.78),(0.88,.835),(0,.86),(-1.5,.9),(-1.92,.89)],
  zb=[(1.98,.24),(1.7,.25),(-1.7,.27),(-1.92,.31)],
  ws=[(1.98,.77),(1.9,.835),(1.2,.85),(0,.85),(-1.6,.85),(-1.92,.82)],
  gh=dict(wsb=.88, rf=.28, rb=-1.52, rsb=-1.81, ze=1.31, wr=.665), win=[(.76,-.27),(-.37,-1.08),(-1.17,-1.5)],
  pal=[0xf1f1ec,0x10161e,0x1d2f66,0x1d2f66,0x141414,0xc4262e,0xf4f4f0,0xdfe6ee,0xc4262e,0x8a8d91,0x8a1010,0xe08a1a,0x5aa2dc]),
 # Ford Escort RS Cosworth: L 4211, WB 2552, W 1738, H 1405
 'esc': dict(xf=2.15, xr=-2.06, A=1.27, B=1.28, fl=0.05, flare='round',
  zt=[(2.15,.57),(2.1,.65),(1.6,.75),(0.95,.85),(0.6,1.05),(0.18,1.345),(-0.3,1.36),(-0.85,1.335),(-1.3,1.17),(-1.76,.985),(-1.98,.955),(-2.06,.89)],
  zs=[(2.15,.55),(2.05,.64),(1.6,.74),(0.95,.825),(0,.865),(-1.2,.915),(-1.8,.92),(-2.06,.88)],
  zb=[(2.15,.22),(1.9,.22),(1.5,.25),(-1.8,.27),(-2.06,.32)],
  ws=[(2.15,.70),(2.05,.80),(1.5,.845),(0,.855),(-1.5,.86),(-2.0,.82),(-2.06,.78)],
  gh=dict(wsb=.95, rf=.18, rb=-.85, rsb=-1.76, ze=1.305, wr=.63), win=[(.83,-.6),(-.7,-1.45)],
  pal=[0xf0f0ea,0x10161e,0x1a4fb0,0x1a4fb0,0x141414,0x79aeea,0xf4f4f0,0xdfe6ee,0x1a4fb0,0x8a8d91,0x8a1010,0xe08a1a,0xf0f0ea]),
 # Mitsubishi Lancer Evolution III: L 4310, WB 2510, W 1695 (+flares), H 1420
 'lan': dict(xf=2.20, xr=-2.11, A=1.25, B=1.26, fl=0.045, flare='round',
  zt=[(2.20,.55),(2.15,.64),(2.0,.70),(1.6,.765),(0.95,.85),(0.6,1.06),(0.05,1.35),(-0.35,1.37),(-0.85,1.35),(-1.13,1.2),(-1.40,1.0),(-1.75,.995),(-2.05,.98),(-2.11,.9)],
  zs=[(2.20,.53),(2.08,.63),(1.6,.74),(0.95,.82),(0,.85),(-1.0,.88),(-1.6,.925),(-2.11,.88)],
  zb=[(2.20,.19),(2.0,.2),(1.5,.25),(-1.8,.27),(-2.11,.33)],
  ws=[(2.20,.70),(2.08,.80),(1.6,.84),(0,.85),(-1.6,.85),(-2.0,.82),(-2.11,.77)],
  gh=dict(wsb=.95, rf=.05, rb=-.85, rsb=-1.40, ze=1.30, wr=.61), win=[(.82,-.24),(-.33,-1.05)],
  pal=[0xf2f2ee,0x10161e,0xb71c25,0x1c1c1c,0x141414,0x1c1c1c,0xf4f4f0,0xdfe6ee,0xb71c25,0x8a8d91,0x8a1010,0xe08a1a,0xf2f2ee]),
 # Toyota Celica GT-Four ST205: L 4420, WB 2535, W 1750, H 1305
 'cel': dict(xf=2.27, xr=-2.155, A=1.27, B=1.27, fl=0.045, flare='round',
  zt=[(2.27,.5),(2.22,.58),(2.05,.64),(1.6,.70),(0.85,.795),(0.4,1.03),(-0.15,1.27),(-0.45,1.28),(-0.75,1.255),(-1.25,1.1),(-1.75,.955),(-2.05,.94),(-2.155,.86)],
  zs=[(2.27,.48),(2.15,.57),(1.6,.68),(0.85,.775),(0,.815),(-1.2,.865),(-1.9,.88),(-2.155,.84)],
  zb=[(2.27,.2),(2.0,.21),(1.5,.25),(-1.8,.27),(-2.155,.32)],
  ws=[(2.27,.64),(2.18,.76),(1.8,.84),(1.2,.86),(0,.865),(-1.5,.865),(-2.0,.83),(-2.155,.76)],
  gh=dict(wsb=.85, rf=-.15, rb=-.75, rsb=-1.75, ze=1.225, wr=.6), win=[(.7,-.64),(-.75,-1.42)],
  pal=[0xf1f1ec,0x10161e,0x1e7a3c,0xc4262e,0x141414,0xc4262e,0xf4f4f0,0xdfe6ee,0x1e7a3c,0x8a8d91,0x8a1010,0xe08a1a,0xf1f1ec]),
}

# ---------- liveries: (centre, strip, side?) -> palette index or None ----------
def liv_imp(c, top, side):
    if side and 0.48 < c.z + 0.05*c.x < 0.56: return C2                                         # yellow waist sweep
    if top and 0.12 < abs(c.y) < 0.24 and c.x > -2.0: return C3                              # twin stripes
    return None
def liv_del(c, top, side):
    if side and 0.50 < c.z < 0.58: return C2
    if side and 0.58 < c.z < 0.62: return C3
    if side and 0.62 < c.z < 0.66: return C4
    if top and abs(c.y) < 0.12: return C2
    if top and 0.12 < abs(c.y) < 0.16: return C3
    if top and 0.16 < abs(c.y) < 0.20: return C4
    return None
def liv_esc(c, top, side):
    k = c.z + 0.11*c.x
    if side and k < 0.52: return C2
    if side and 0.60 < k < 0.66: return C3
    if top and c.x > 1.0 and abs(c.y) < 0.22: return C2
    return None
def liv_lan(c, top, side):
    if side and c.z < 0.42: return C3
    u = c.x + 0.9*c.z
    if (side or top) and any(a < u < b for a, b in ((-1.15,-.95),(-.8,-.6),(-.45,-.25))): return C2
    return None
def liv_cel(c, top, side):
    u = c.x + 0.6*c.z
    if (top or side) and u < -0.55: return C2
    if (top or side) and u < -0.43: return C3
    return None
CUTS = {
 'imp': [((0,0,.48),(.05,0,1)),((0,0,.56),(.05,0,1))]+[((0,y,0),(0,1,0)) for y in (.12,.24,-.12,-.24)],
 'del': [((0,0,z),(0,0,1)) for z in (.5,.58,.62,.66)]+[((0,y,0),(0,1,0)) for y in (.12,.16,.2,-.12,-.16,-.2)],
 'esc': [((0,0,z),(.11,0,1)) for z in (.52,.6,.66)]+[((0,y,0),(0,1,0)) for y in (.22,-.22)]+[((1.0,0,0),(1,0,0))],
 'lan': [((0,0,.42),(0,0,1))]+[((u,0,0),(1,0,.9)) for u in (-1.15,-.95,-.8,-.6,-.45,-.25)],
 'cel': [((u,0,0),(1,0,.6)) for u in (-.55,-.43)],
}
LIV = dict(imp=liv_imp, **{'del': liv_del}, esc=liv_esc, lan=liv_lan, cel=liv_cel)

# ---------- body loft ----------
NR = 14   # points per half ring, bottom centre .. top centre
def profile(d):
    P = {k: pchip(d[k]) for k in ('zt', 'zs', 'zb', 'ws')}
    g = d['gh']
    def gh_edge(x):
        """roof-edge height and roof half width (None outside greenhouse)."""
        zs, ws = P['zs'](x), P['ws'](x)
        if x >= g['wsb'] or x <= g['rsb']: return zs+0.03, ws-0.09
        if x > g['rf']:   t = (g['wsb']-x)/(g['wsb']-g['rf']); return lerp(zs+0.03, g['ze'], t**0.9), lerp(ws-0.11, g['wr'], t)
        if x >= g['rb']:  t = (g['rf']-x)/(g['rf']-g['rb']); return g['ze']+0.015*math.sin(t*math.pi), g['wr']-0.02*t
        t = (g['rb']-x)/(g['rb']-g['rsb']); return lerp(g['ze'], zs+0.03, t**1.1), lerp(g['wr']-0.02, ws-0.11, t)
    def flare(x):
        f = 0
        for wx in (d['A'], -d['B']):
            dx = abs(x-wx)
            if d['flare'] == 'box': f = max(f, d['fl']*(1-sstep(RA+0.02, RA+0.32, dx)))
            else: f = max(f, d['fl']*(1-sstep(RA-0.1, RA+0.25, dx)))
        return f
    def arch(x):
        z = 0
        for wx in (d['A'], -d['B']):
            dx = abs(x-wx)
            if dx < RA: z = max(z, RW+math.sqrt(RA*RA-dx*dx))
        return z
    def ring(x):
        zt, zs, zb, ws = P['zt'](x), P['zs'](x), P['zb'](x), P['ws'](x)
        ze, wr = gh_edge(x); fl = flare(x); wm = ws+0.018+fl; wsf = ws+fl*0.7
        zt = max(zt, ze+0.01)
        hz = zs-zb
        pts = [(0, zb), (wm*0.55, zb), (wm*0.93, zb+0.012), (wm*0.99, zb+min(0.08, hz*0.2)),
               (wm, zb+hz*0.42), (wsf*0.995+0.004, zs-0.07), (wsf, zs-0.012), (wsf-0.035, zs+0.012)]
        # greenhouse / bonnet crown
        gb = (wsf-0.075, zs+0.03)
        pts += [gb, (lerp(gb[0], wr, 0.5)+0.006, lerp(gb[1], ze, 0.5)), (wr, ze), (wr*0.9, lerp(ze, zt, 0.6)), (wr*0.5, zt-0.006), (0, zt)]
        a = arch(x)
        lifted = [False]*len(pts)
        if a:
            cap = zs-0.09
            for k in (1, 2, 3, 4, 5):
                y, z = pts[k]
                if z < a: pts[k] = (y, min(a, cap) if k > 1 else min(a, cap)-0.02); lifted[k] = True
        return pts, lifted
    return P, ring

def build(cid, d):
    bm = bmesh.new()
    strip = bm.faces.layers.int.new('strip')
    P, ring = profile(d); g = d['gh']
    keys = {d['xf'], d['xr'], g['wsb'], g['rf'], g['rb'], g['rsb']}
    for a, b in d['win']: keys |= {a, b}
    for wx in (d['A'], -d['B']):
        for k in range(-8, 9): keys.add(wx + RA*k/8)
    n = 64; xs = sorted({round(d['xr'] + (d['xf']-d['xr'])*i/n, 4) for i in range(n+1)} | {round(k, 4) for k in keys}, reverse=True)
    xs = [x for x in xs if d['xr'] <= x <= d['xf']]
    # drop stations too close together
    sx = [xs[0]]
    for x in xs[1:]:
        if sx[-1]-x > 0.012 or x in keys: sx.append(x)
    xs = sx
    rings, lifts = [], []
    for i, x in enumerate(xs):
        pts, lifted = ring(x)
        # round the nose and tail in plan and profile
        e = 1.0
        if i == 0 or i == len(xs)-1: e = 0.965
        full = pts + [(-y, z) for y, z in pts[-2:0:-1]]
        lf = lifted + lifted[-2:0:-1]
        zc = (pts[0][1]+pts[-1][1])/2
        rings.append([bm.verts.new((x, y*e, zc+(z-zc)*(1 if e == 1 else 0.985))) for y, z in full]); lifts.append(lf)
    M = len(rings[0]); half = NR-1
    def strip_of(k):  # segment k..k+1 -> strip index measured from bottom centre
        return k if k < half else (M-1-k)
    for i in range(len(rings)-1):
        for k in range(M):
            f = bm.faces.new((rings[i][k], rings[i][(k+1) % M], rings[i+1][(k+1) % M], rings[i+1][k]))
            s = strip_of(k)
            f[strip] = s + (100 if (lifts[i][k] or lifts[i][(k+1) % M] or lifts[i+1][k] or lifts[i+1][(k+1) % M]) else 0)
    for r in (rings[0], rings[-1][::-1]):
        f = bm.faces.new(r); f[strip] = 50
    for co, no in CUTS[cid]:
        bmesh.ops.bisect_plane(bm, geom=bm.verts[:]+bm.edges[:]+bm.faces[:], dist=1e-5, plane_co=Vector(co), plane_no=Vector(no).normalized())
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    liv = LIV[cid]
    def in_win(x):
        return any(b < x < a for a, b in d['win'])
    for f in bm.faces:
        c = f.calc_center_median(); s = f[strip]; lifted = s >= 100; s %= 100
        if s == 50: f.material_index = BODY; continue
        if lifted and s <= 2: f.material_index = BLACK; continue
        if s <= 1: f.material_index = BLACK; continue
        if s == 2: f.material_index = SILL; continue
        if s in (8, 9) and in_win(c.x): f.material_index = GLASS; continue
        if s in (11, 12) and (g['rf'] < c.x < g['wsb']-0.03 or g['rsb']+0.02 < c.x < g['rb']): f.material_index = GLASS; continue
        if s in (8, 9) and g['rsb'] < c.x < g['wsb'] and not in_win(c.x): f.material_index = BLACK if cid in ('cel',) and c.x < g['rb'] else BODY
        r = liv(c, s >= 10 or (s >= 7 and not (g['rsb'] < c.x < g['wsb'])), 3 <= s <= 7)
        f.material_index = BODY if r is None else r
    ctx = dict(bm=bm, P=P, ring=ring)
    details(cid, d, ctx)
    # wheel-arch lips
    for wx in (d['A'], -d['B']):
        for sg in (1, -1):
            ang = [math.pi*i/12 for i in range(13)]
            def wy(x):
                pts, _ = ring(x); return pts[4][0]
            q = [[bm.verts.new((wx+r*math.cos(a), (wy(wx+r*math.cos(a))+dy)*sg, RW+r*math.sin(a))) for a in ang] for r, dy in ((RA, 0.012), (RA+0.045, 0.004), (RA+0.06, -0.02))]
            for j in range(2):
                for i in range(12):
                    v = (q[j][i], q[j][i+1], q[j+1][i+1], q[j+1][i])
                    bm.faces.new(v if sg > 0 else v[::-1]).material_index = BODY if not (cid == 'lan' or cid == 'esc') else SILL
    bmesh.ops.triangulate(bm, faces=bm.faces[:], quad_method='BEAUTY', ngon_method='BEAUTY')
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    bm.verts.ensure_lookup_table(); bm.verts.index_update()
    me = bpy.data.meshes.new(cid)
    for i, h in enumerate(d['pal']):
        m = bpy.data.materials.new(f'{cid}_{i}'); m.diffuse_color = (((h >> 16) & 255)/255, ((h >> 8) & 255)/255, (h & 255)/255, 1); me.materials.append(m)
    bm.to_mesh(me); bm.free()
    me.set_sharp_from_angle(angle=math.radians(38))
    # material borders are not creases: keep smooth across them unless angle says otherwise
    cn = me.corner_normals
    V = [round(c*1000) for v in me.vertices for c in (-v.co.y, v.co.z, -v.co.x)]
    T, C, N = [], [], []
    for p in me.polygons:
        T += [me.loops[li].vertex_index for li in p.loop_indices]; C.append(p.material_index)
        for li in p.loop_indices:
            nv = cn[li].vector; N += [round(-nv.y*100), round(nv.z*100), round(-nv.x*100)]
    nose = P['zs'](d['xf']-0.05)
    # brake-light glow rectangles (game coords): [x, y, z, w, h]
    tails = ctx.get('tails', [])
    out = dict(v=V, t=T, c=C, n=N, pal=d['pal'], lampY=round(ctx.get('lampY', nose-0.02), 3),
               zf=round(-d['xf'], 3), zr=round(-d['xr'], 3), A=d['A'], B=d['B'],
               tail=[[round(-y, 3), round(z, 3), round(-x, 3), round(w, 3), round(h, 3)] for x, y, z, w, h in tails],
               exY=ctx.get('exY', 0.3), exX=ctx.get('exX', [0.42]))
    ob = bpy.data.objects.new(cid, me); bpy.context.scene.collection.objects.link(ob)
    return out, ob

# ---------- detail geometry ----------
def details(cid, d, ctx):
    bm, P, ring = ctx['bm'], ctx['P'], ctx['ring']
    xf, xr, A, B = d['xf'], d['xr'], d['A'], d['B']
    def mat_all(verts, idx):
        for f in {f for v in verts for f in v.link_faces}: f.material_index = idx
    def box(x, y, z, sx, sy, sz, idx, mirror=False, rx=0, ry=0, rz=0):
        for sg in ((1, -1) if mirror else (1,)):
            m = Matrix.Translation((x, y*sg, z)) @ Matrix.Rotation(rz*sg, 4, 'Z') @ Matrix.Rotation(ry, 4, 'Y') @ Matrix.Rotation(rx*sg, 4, 'X') @ Matrix.Diagonal((sx, sy, sz, 1))
            r = bmesh.ops.create_cube(bm, size=1, matrix=m); mat_all(r['verts'], idx)
    def cyl(x, y, z, r, depth, idx, mirror=False, axis='X', seg=14, r2=None):
        for sg in ((1, -1) if mirror else (1,)):
            rot = Matrix.Rotation(math.pi/2, 4, 'Y') if axis == 'X' else Matrix.Rotation(math.pi/2, 4, 'X') if axis == 'Y' else Matrix.Identity(4)
            m = Matrix.Translation((x, y*sg, z)) @ rot
            res = bmesh.ops.create_cone(bm, cap_ends=True, segments=seg, radius1=r, radius2=r if r2 is None else r2, depth=depth, matrix=m); mat_all(res['verts'], idx)
    def prism(pts, y0, y1, idx, mirror=False):
        """polygon pts [(x,z)] extruded between y0 and y1."""
        for sg in ((1, -1) if mirror else (1,)):
            a = [bm.verts.new((x, y0*sg, z)) for x, z in pts]; b = [bm.verts.new((x, y1*sg, z)) for x, z in pts]
            fs = [bm.faces.new(a[::-1]), bm.faces.new(b)]
            for i in range(len(pts)):
                j = (i+1) % len(pts); fs.append(bm.faces.new((a[i], a[j], b[j], b[i])))
            for f in fs: f.material_index = idx
    def surf_w(x, z):
        """approximate half width of the body at x, height z."""
        pts, _ = ring(x); best = 0
        for (y0, z0), (y1, z1) in zip(pts, pts[1:]):
            if min(z0, z1) <= z <= max(z0, z1) and z1 != z0: best = max(best, y0+(y1-y0)*(z-z0)/(z1-z0))
        return best
    zsF = P['zs'](xf-0.02); zbF = P['zb'](xf); wF = P['ws'](xf)
    tails = []; ctx['tails'] = tails
    # common: mirrors, mud flaps, exhaust, roof vent, wipers
    g = d['gh']; xm = g['wsb']-0.2; zm = P['zs'](xm)
    wm = surf_w(xm, zm+0.02)
    box(xm, wm+0.05, zm+0.1, 0.07, 0.04, 0.03, BLACK, True)                                      # mirror stalk
    box(xm-0.01, wm+0.11, zm+0.12, 0.09, 0.14, 0.1, C2 if cid in ('del', 'esc', 'lan') else BODY, True, rz=0.15)
    for wx in (A, -B):
        box(wx-0.43, surf_w(wx-0.43, 0.3)-0.08, 0.2, 0.025, 0.3, 0.26, FLAP, True)
    for k, sx in enumerate(d.get('exX', [0.42])): pass
    xv = (g['rf']+g['rb'])/2-0.05
    box(xv, 0, g['ze']+0.07, 0.36, 0.3, 0.05, BLACK); box(xv+0.19, 0, g['ze']+0.06, 0.03, 0.3, 0.07, BLACK)  # roof vent
    for sy in (0.12, -0.38):
        box(g['wsb']-0.06, sy, P['zt'](g['wsb'])+0.03, 0.02, 0.48, 0.015, BLACK, rz=0.08)             # wipers
    def tail_lens(x, y, z, w, h, mirror=True, idx=RED):
        box(x-0.022, y, z, 0.02, w, h, idx, mirror)
        tails.append((x-0.034, y, z, w, h))
        if mirror: tails.append((x-0.034, -y, z, w, h))
    xR = xr+0.005
    if cid == 'imp':
        # front: body-coloured bumper with big central intake, angled headlamps, fogs
        box(xf-0.06, 0, 0.33, 0.14, 1.66, 0.22, BODY); box(xf+0.005, 0, 0.32, 0.03, 0.66, 0.14, BLACK)
        box(xf+0.0, 0.62, 0.31, 0.03, 0.18, 0.1, BLACK, True); box(xf+0.01, 0, 0.215, 0.05, 1.5, 0.03, BLACK)
        box(xf-0.04, 0.52, 0.56, 0.05, 0.33, 0.1, LENS, True, ry=0.25); box(xf-0.03, 0.27, 0.56, 0.045, 0.14, 0.08, BLACK, True)
        box(xf-0.03, 0, 0.57, 0.04, 0.38, 0.06, BLACK)                                            # grille
        box(xf-0.04, 0.73, 0.505, 0.04, 0.08, 0.05, AMBER, True)
        box(1.35, 0, P['zt'](1.35)+0.025, 0.42, 0.5, 0.06, BLACK, ry=-0.04); box(1.15, 0, P['zt'](1.15)+0.06, 0.04, 0.5, 0.06, BLACK)  # bonnet scoop
        box(1.6, 0.36, P['zt'](1.6)+0.004, 0.22, 0.12, 0.012, BLACK, True)
        # rear: boot lid, tall wing on uprights with endplates, wraparound lamps
        tail_lens(xR+0.01, 0.6, 0.8, 0.28, 0.12); box(xR+0.01, 0.42, 0.8, 0.03, 0.08, 0.1, AMBER, True)
        box(xR-0.02, 0, 0.44, 0.12, 1.6, 0.2, BODY); box(xR-0.05, 0, 0.36, 0.06, 0.4, 0.08, BLACK)
        foil = [(-1.72, 1.36), (-1.86, 1.38), (-2.12, 1.355), (-2.14, 1.33), (-1.88, 1.335), (-1.73, 1.33)]
        prism(foil, -0.78, 0.78, BODY)
        prism([(-1.70, 1.25), (-2.15, 1.29), (-2.15, 1.42), (-1.70, 1.40)], 0.78, 0.81, BODY, True)
        prism([(-1.86, P['zt'](-1.86)), (-2.02, P['zt'](-2.02)), (-2.05, 1.34), (-1.9, 1.34)], 0.52, 0.55, BLACK, True)
        ctx['lampY'] = 0.55
    elif cid == 'del':
        # front: black bumper with intakes, four round lamps in a black grille band
        box(xf-0.03, 0, 0.36, 0.12, 1.64, 0.25, BLACK); box(xf+0.02, 0, 0.3, 0.03, 1.1, 0.1, BLACK)
        box(xf+0.03, 0.58, 0.33, 0.03, 0.22, 0.12, GREY, True)
        box(xf-0.02, 0, 0.6, 0.04, 1.42, 0.13, BLACK)
        for yy in (0.2, 0.5): cyl(xf-0.0, yy, 0.6, 0.06, 0.04, LENS, True)
        box(xf-0.01, 0, 0.6, 0.045, 0.16, 0.08, GREY)
        box(xf-0.02, 0.76, 0.48, 0.04, 0.06, 0.1, AMBER, True)
        for k in range(5): box(1.3-0.06*k, 0.32, P['zt'](1.3-0.06*k)+0.004, 0.025, 0.24, 0.01, BLACK, True)  # bonnet louvres
        box(1.7, 0, P['zt'](1.7)+0.012, 0.2, 0.36, 0.02, BLACK)
        # rear: big roof spoiler over hatch, adjustable blade
        prism([(-1.48, 1.35), (-1.72, 1.4), (-1.76, 1.37), (-1.5, 1.33)], -0.68, 0.68, C2)
        prism([(-1.47, 1.30), (-1.77, 1.33), (-1.77, 1.43), (-1.5, 1.37)], 0.68, 0.7, BLACK, True)
        tail_lens(xR+0.01, 0.52, 0.8, 0.42, 0.11); box(xR+0.012, 0, 0.8, 0.03, 0.62, 0.1, BLACK)
        box(xR-0.0, 0, 0.42, 0.12, 1.66, 0.2, BLACK)
        ctx['lampY'] = 0.6
    elif cid == 'esc':
        # front: deep body bumper, oval grille, rectangular lamps, splitter
        box(xf-0.06, 0, 0.32, 0.14, 1.62, 0.22, BODY); box(xf+0.005, 0, 0.29, 0.03, 0.9, 0.12, BLACK)
        box(xf+0.03, 0, 0.2, 0.08, 1.56, 0.025, BLACK)
        box(xf-0.03, 0.5, 0.53, 0.05, 0.36, 0.11, LENS, True, ry=0.2); box(xf-0.025, 0, 0.53, 0.04, 0.5, 0.08, BLACK)
        box(xf-0.03, 0.74, 0.48, 0.04, 0.08, 0.05, AMBER, True)
        for sy in (0.25,): box(1.25, sy, P['zt'](1.25)+0.012, 0.32, 0.18, 0.02, BLACK, True)           # bonnet vents
        # rear: the whale tail on the hatch plus the upper wing
        tz = P['zt'](-1.8)
        prism([(-1.66, tz+0.05), (-2.08, tz+0.10), (-2.16, tz+0.18), (-2.12, tz+0.2), (-2.02, tz+0.13), (-1.68, tz+0.08)], -0.82, 0.82, BODY)
        prism([(-1.62, tz+0.02), (-2.16, tz+0.13), (-2.16, tz+0.25), (-1.66, tz+0.12)], 0.82, 0.86, C2, True)
        prism([(-1.35, 1.38), (-1.62, 1.4), (-1.65, 1.38), (-1.38, 1.365)], -0.7, 0.7, C2)
        prism([(-1.4, P['zt'](-1.4)), (-1.48, P['zt'](-1.48)), (-1.58, 1.38), (-1.5, 1.38)], 0.52, 0.55, BLACK, True)
        tail_lens(xR+0.01, 0.6, 0.74, 0.26, 0.15); box(xR+0.012, 0.6, 0.66, 0.031, 0.26, 0.03, AMBER, True)
        box(xR-0.02, 0, 0.42, 0.12, 1.62, 0.2, BODY); box(xR-0.06, 0, 0.36, 0.06, 0.5, 0.08, BLACK)
        ctx['lampY'] = 0.53
    elif cid == 'lan':
        # front: huge body-coloured bumper with three intakes, rectangular lamps, fog pods
        box(xf-0.07, 0, 0.32, 0.16, 1.68, 0.24, BODY); box(xf+0.01, 0, 0.31, 0.03, 0.7, 0.15, BLACK)
        box(xf+0.0, 0.6, 0.31, 0.03, 0.24, 0.13, BLACK, True); box(xf+0.03, 0, 0.18, 0.08, 1.6, 0.03, BLACK)
        box(xf-0.04, 0.53, 0.53, 0.05, 0.34, 0.1, LENS, True, ry=0.25); box(xf-0.035, 0, 0.53, 0.04, 0.48, 0.07, BLACK)
        box(xf-0.04, 0.74, 0.47, 0.04, 0.07, 0.05, AMBER, True)
        box(1.45, 0.3, P['zt'](1.45)+0.01, 0.3, 0.16, 0.02, BLACK, True); box(1.65, 0, P['zt'](1.65)+0.008, 0.2, 0.3, 0.016, BLACK)
        # rear: big boot wing with endplates and a lower lip
        foil = [(-1.72, 1.24), (-1.86, 1.27), (-2.13, 1.25), (-2.14, 1.22), (-1.88, 1.225), (-1.73, 1.22)]
        prism(foil, -0.74, 0.74, BODY)
        prism([(-1.72, 1.15), (-2.15, 1.18), (-2.15, 1.3), (-1.72, 1.28)], 0.74, 0.77, BLACK, True)
        prism([(-1.86, P['zt'](-1.86)), (-2.0, P['zt'](-2.0)), (-2.03, 1.23), (-1.9, 1.23)], 0.5, 0.53, BLACK, True)
        tail_lens(xR+0.01, 0.5, 0.8, 0.52, 0.11)
        box(xR-0.02, 0, 0.42, 0.12, 1.62, 0.2, BODY); box(xR-0.05, 0, 0.36, 0.06, 0.4, 0.08, BLACK)
        ctx['lampY'] = 0.52
    elif cid == 'cel':
        # front: low nose, four round lamps, big lower intake, round fogs
        box(xf-0.07, 0, 0.3, 0.14, 1.62, 0.2, BODY); box(xf+0.0, 0, 0.29, 0.03, 0.8, 0.14, BLACK)
        for yy in (0.6,): cyl(xf-0.02, yy, 0.3, 0.055, 0.04, LENS, True)
        box(xf+0.02, 0, 0.19, 0.08, 1.5, 0.025, BLACK)
        for yy, zz in ((0.44, 0.5), (0.62, 0.48)):
            cyl(xf-0.1, yy, zz, 0.075, 0.06, BLACK, True); cyl(xf-0.075, yy, zz, 0.062, 0.02, LENS, True)
        box(xf-0.12, 0.74, 0.44, 0.04, 0.06, 0.04, AMBER, True)
        box(1.55, 0, P['zt'](1.55)+0.012, 0.3, 0.28, 0.02, BLACK)
        # rear: liftback wing on two pillars, full-width lamp bar
        tz = P['zt'](-1.85)
        prism([(-1.74, tz+0.2), (-1.86, tz+0.225), (-2.1, tz+0.2), (-2.11, tz+0.175), (-1.86, tz+0.18), (-1.75, tz+0.175)], -0.76, 0.76, BODY)
        prism([(-1.72, tz+0.1), (-2.12, tz+0.12), (-2.12, tz+0.25), (-1.72, tz+0.24)], 0.76, 0.79, BLACK, True)
        prism([(-1.84, P['zt'](-1.84)-0.01), (-1.97, P['zt'](-1.97)-0.01), (-1.99, tz+0.19), (-1.87, tz+0.19)], 0.45, 0.48, BLACK, True)
        tail_lens(xR+0.01, 0.48, 0.8, 0.56, 0.1); box(xR+0.012, 0, 0.8, 0.03, 0.4, 0.09, BLACK)
        box(xR-0.02, 0, 0.42, 0.12, 1.6, 0.2, BODY); box(xR-0.05, 0, 0.35, 0.06, 0.5, 0.08, BLACK)
        ctx['lampY'] = 0.46
    # exhausts
    ex = 0.52 if cid in ('imp', 'lan') else 0.42
    cyl(xr-0.03, ex, 0.3, 0.045, 0.14, GREY, axis='X'); cyl(xr-0.095, ex, 0.3, 0.032, 0.02, BLACK, axis='X')
    ctx['exY'] = 0.3; ctx['exX'] = [-ex]

# ---------- run ----------
for o in list(bpy.data.objects): bpy.data.objects.remove(o)
res = {}; obs = {}
for i, (cid, d) in enumerate(CARS.items()):
    res[cid], obs[cid] = build(cid, d); obs[cid].location.y = i*2.6
    print(cid, 'tris', len(res[cid]['c']), 'verts', len(res[cid]['v'])//3)
json.dump(res, open(os.path.join(HERE, '..', 'cars.json'), 'w'), separators=(',', ':'))
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(HERE, 'cars.blend'))
try:
    for cid, ob in obs.items():
        for o in obs.values(): o.select_set(o is ob)
        y = ob.location.y; ob.location.y = 0
        bpy.ops.export_scene.gltf(filepath=os.path.join(HERE, cid+'.glb'), use_selection=True); ob.location.y = y
except Exception as e: print('glb export skipped:', e)
