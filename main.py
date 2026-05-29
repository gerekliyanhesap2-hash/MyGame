import pygame
import sys
import time
import random
import os
import math

# ─── BAŞLATMA ────────────────────────────────────────────────────────────────
pygame.init()
pygame.mixer.init()

# Tam ekran – canvas/ölçekleme YOK, doğrudan telefon çözünürlüğü
ekran = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
W, H = ekran.get_size()
pygame.display.set_caption("LS Studio – Block Puzzle Ultimate")

# Oransal tasarım sabiti (her şey bu S değeriyle çarpılır)
# Referans: 450x800 tasarım → telefon ekranına oranla scale
S  = min(W / 450, H / 800)       # uniform scale
CX = W // 2                       # ekran merkezi X

def sc(v):   return int(v * S)    # boyut ölçekle
def sx(v):   return int(CX + (v - 225) * S)   # X koordinat (450 genişliğine göre ortalı)
def sy(v):   return int(v * S)    # Y koordinat (üstten)
def sr(x,y,w,h): return pygame.Rect(sx(x), sy(y), sc(w), sc(h))

# ─── DİL SİSTEMİ ─────────────────────────────────────────────────────────────
dil = "TR"

METIN = {
    "TR": {
        "baslik":"BLOCK PUZZLE", "klasik_mod":"▶  Klasik Mod",
        "tema_magaza":"◈  Tema Mağazası", "ayarlar":"⚙  Ayarlar",
        "geri":"← Geri", "magaza_baslik":"TEMA MAĞAZASI",
        "aktif":"✦ AKTİF", "sec":"► Seç", "bitti":"BİTTİ",
        "skor":"Skor", "en_iyi":"En İyi", "lobiye_don":"↩  Lobiye Dön",
        "ayarlar_baslik":"AYARLAR", "muzik":"🎵 Oyun Müziği",
        "muzik_ac":"AÇIK", "muzik_kapat":"KAPALI",
        "ses":"🔊 Ses Efektleri", "dil_sec":"🌐 Dil / Language",
        "level":"LV", "level_up":"SEVİYE ATLADI!", "studio":"LS Studio™",
        "muzik_yok":"music.mp3 bulunamadı – oyun klasörüne ekleyin",
    },
    "EN": {
        "baslik":"BLOCK PUZZLE", "klasik_mod":"▶  Classic Mode",
        "tema_magaza":"◈  Theme Shop", "ayarlar":"⚙  Settings",
        "geri":"← Back", "magaza_baslik":"THEME SHOP",
        "aktif":"✦ ACTIVE", "sec":"► Select", "bitti":"GAME OVER",
        "skor":"Score", "en_iyi":"Best", "lobiye_don":"↩  Main Menu",
        "ayarlar_baslik":"SETTINGS", "muzik":"🎵 Game Music",
        "muzik_ac":"ON", "muzik_kapat":"OFF",
        "ses":"🔊 Sound FX", "dil_sec":"🌐 Language / Dil",
        "level":"LV", "level_up":"LEVEL UP!", "studio":"LS Studio™",
        "muzik_yok":"music.mp3 not found – place it in the game folder",
    }
}
def M(k): return METIN[dil].get(k, k)

# ─── AYARLAR ─────────────────────────────────────────────────────────────────
muzik_acik     = True
ses_efekt_acik = True

# ─── SES ─────────────────────────────────────────────────────────────────────
def ses_yukle(f):
    if os.path.exists(f):
        try: return pygame.mixer.Sound(f)
        except: return None
    return None

def ses_cal(s):
    if s and ses_efekt_acik:
        try: s.play()
        except: pass

ses_tut   = ses_yukle("click.wav")
ses_koy   = ses_yukle("place.wav")
ses_patla = ses_yukle("score.wav")
ses_bitis = ses_yukle("gameover.wav")
MUZIK_DOSYA = "music.mp3"

def muzik_guncelle():
    if muzik_acik and os.path.exists(MUZIK_DOSYA):
        try:
            if not pygame.mixer.music.get_busy():
                pygame.mixer.music.load(MUZIK_DOSYA)
                pygame.mixer.music.set_volume(0.4)
                pygame.mixer.music.play(-1)
        except: pass
    else:
        try: pygame.mixer.music.stop()
        except: pass

# ─── TEMALAR ─────────────────────────────────────────────────────────────────
TEMALAR = {
    "Tüylü Küp":     {"fiyat":0,    "satin":True,
                      "bg_top":(20,10,40),  "bg_bot":(60,20,90),
                      "b1":(249,115,22), "b2":(234,179,8),  "glow":(249,115,22), "accent":(254,240,138)},
    "Neon Siber":    {"fiyat":5000, "satin":False,
                      "bg_top":(5,0,15),   "bg_bot":(10,20,40),
                      "b1":(0,255,242),  "b2":(0,140,255),  "glow":(0,255,242),  "accent":(0,220,255)},
    "Piksel Retro":  {"fiyat":5000, "satin":False,
                      "bg_top":(20,20,20), "bg_bot":(50,30,10),
                      "b1":(34,197,94),  "b2":(234,179,8),  "glow":(34,197,94),  "accent":(250,204,21)},
    "Kozmik Galaksi":{"fiyat":5000, "satin":False,
                      "bg_top":(5,0,25),   "bg_bot":(30,10,60),
                      "b1":(147,51,234), "b2":(79,70,229),  "glow":(168,85,247), "accent":(216,180,254)},
    "Erimiş Lav":    {"fiyat":5000, "satin":False,
                      "bg_top":(20,0,0),   "bg_bot":(50,10,0),
                      "b1":(239,68,68),  "b2":(249,115,22), "glow":(255,80,0),   "accent":(253,186,116)},
    "Buzul Çağı":    {"fiyat":5000, "satin":False,
                      "bg_top":(0,20,50),  "bg_bot":(10,60,100),
                      "b1":(56,189,248), "b2":(14,165,233), "glow":(56,189,248), "accent":(186,230,253)},
    "Antik Mısır":   {"fiyat":5000, "satin":False,
                      "bg_top":(30,20,0),  "bg_bot":(70,50,0),
                      "b1":(202,138,4),  "b2":(161,98,7),   "glow":(250,204,21), "accent":(253,224,71)},
    "Altın Lüks":    {"fiyat":5000, "satin":False,
                      "bg_top":(10,8,0),   "bg_bot":(30,20,0),
                      "b1":(250,204,21), "b2":(194,65,12),  "glow":(250,204,21), "accent":(254,240,138)},
    "Grafiti Sokak": {"fiyat":5000, "satin":False,
                      "bg_top":(15,10,20), "bg_bot":(35,25,45),
                      "b1":(236,72,153), "b2":(168,85,247), "glow":(236,72,153), "accent":(249,168,212)},
    "Derin Okyanus": {"fiyat":5000, "satin":False,
                      "bg_top":(0,15,30),  "bg_bot":(5,50,70),
                      "b1":(20,184,166), "b2":(6,182,212),  "glow":(20,184,166), "accent":(153,246,228)},
    "Çizgi Roman":   {"fiyat":5000, "satin":False,
                      "bg_top":(30,0,10),  "bg_bot":(80,10,30),
                      "b1":(251,113,133),"b2":(253,186,116),"glow":(251,113,133),"accent":(254,205,211)},
    "Zombi İstilası":{"fiyat":5000, "satin":False,
                      "bg_top":(5,15,5),   "bg_bot":(15,35,10),
                      "b1":(101,163,13), "b2":(22,101,52),  "glow":(132,204,22), "accent":(187,247,208)},
    "Doğa & Orman":  {"fiyat":5000, "satin":False,
                      "bg_top":(0,20,10),  "bg_bot":(5,60,30),
                      "b1":(132,204,22), "b2":(34,197,94),  "glow":(132,204,22), "accent":(187,247,208)},
    "Şeker Diyarı":  {"fiyat":5000, "satin":False,
                      "bg_top":(40,0,30),  "bg_bot":(90,10,70),
                      "b1":(244,114,182),"b2":(192,38,211), "glow":(244,114,182),"accent":(249,168,212)},
    "Geleceğin Mek": {"fiyat":5000, "satin":False,
                      "bg_top":(10,10,40), "bg_bot":(25,25,80),
                      "b1":(129,140,248),"b2":(99,102,241), "glow":(129,140,248),"accent":(199,210,254)},
}
TEMA_SIRASI = list(TEMALAR.keys())
aktif_tema = TEMA_SIRASI[0]

# ─── RENK YARDIMCILARI ───────────────────────────────────────────────────────
def lerp(a, b, t): return tuple(int(a[i]+(b[i]-a[i])*t) for i in range(3))
def parlat(c, k=1.4): return tuple(min(255,int(x*k)) for x in c)

def grad_rect(surf, rect, c1, c2, dikey=True):
    x,y,w,h = rect
    n = h if dikey else w
    for i in range(n):
        col = lerp(c1, c2, i/max(n,1))
        if dikey: pygame.draw.line(surf, col, (x,y+i),(x+w-1,y+i))
        else:     pygame.draw.line(surf, col, (x+i,y),(x+i,y+h-1))

def glow_rect(surf, rect, renk, radius=12, steps=8):
    x,y,w,h = rect
    for i in range(steps,0,-1):
        a = int(60*(i/steps)**2)
        exp = (steps-i+1)*2
        gs = pygame.Surface((w+exp*2,h+exp*2), pygame.SRCALPHA)
        pygame.draw.rect(gs, (*renk,a),(0,0,w+exp*2,h+exp*2), border_radius=radius+exp)
        surf.blit(gs,(x-exp,y-exp))

def draw_cube(surf, x, y, boyut, c1, c2, gw, tutuldu=False):
    glow_rect(surf,(x,y,boyut,boyut),gw,radius=sc(4),steps=10 if tutuldu else 5)
    kare = pygame.Surface((boyut,boyut), pygame.SRCALPHA)
    grad_rect(kare,(0,0,boyut,boyut),c1,c2)
    lw = max(1,boyut//12)
    pk = parlat(c1,1.5)
    dk = lerp(c2,(0,0,0),0.4)
    pygame.draw.line(kare,pk,(0,0),(0,boyut-1),lw)
    pygame.draw.line(kare,pk,(0,0),(boyut-1,0),lw)
    pygame.draw.line(kare,dk,(boyut-1,0),(boyut-1,boyut-1),lw)
    pygame.draw.line(kare,dk,(0,boyut-1),(boyut-1,boyut-1),lw)
    pygame.draw.rect(kare,(*gw,180),(0,0,boyut,boyut),1)
    surf.blit(kare,(x,y))

def glass(surf, rect, a=60, ba=100, renk=(255,255,255), r=16):
    x,y,w,h = rect
    g = pygame.Surface((w,h), pygame.SRCALPHA)
    pygame.draw.rect(g,(*renk,a),(0,0,w,h),border_radius=r)
    pygame.draw.rect(g,(*renk,ba),(0,0,w,h),width=1,border_radius=r)
    surf.blit(g,(x,y))

def neon_btn(surf, rect, txt, fnt, hover, pasif=False, accent=(96,165,250)):
    x,y,w,h = rect.x,rect.y,rect.width,rect.height
    if pasif:
        glass(surf,(x,y,w,h),a=30,ba=40,renk=(100,100,120))
        yz = fnt.render(txt,True,(120,130,150))
    elif hover:
        glow_rect(surf,(x,y,w,h),accent,radius=sc(14),steps=8)
        glass(surf,(x,y,w,h),a=80,ba=200,renk=accent,r=sc(14))
        yz = fnt.render(txt,True,(255,255,255))
    else:
        glass(surf,(x,y,w,h),a=50,ba=120,renk=accent,r=sc(14))
        yz = fnt.render(txt,True,(220,230,255))
    surf.blit(yz, yz.get_rect(center=rect.center))

def draw_toggle(surf, rect, aktif, accent):
    x,y,w,h = rect.x,rect.y,rect.width,rect.height
    renk = accent if aktif else (80,90,110)
    glass(surf,(x,y,w,h),a=80 if aktif else 40,ba=180 if aktif else 80,renk=renk,r=h//2)
    dr = h//2-sc(3)
    dx = x+w-dr-sc(5) if aktif else x+dr+sc(5)
    pygame.draw.circle(surf,(255,255,255),(dx,y+h//2),dr)

# ─── PARTİKEL ────────────────────────────────────────────────────────────────
parcalar = []

def parca_patla(x, y, renk, n=18):
    for _ in range(n):
        a = random.uniform(0,2*math.pi)
        h2 = random.uniform(2,7)*S
        parcalar.append({"x":x,"y":y,"vx":math.cos(a)*h2,"vy":math.sin(a)*h2,
                         "renk":renk,"omur":random.uniform(0.4,0.9),
                         "t0":time.time(),"boyut":random.randint(sc(3),sc(7))})

def parca_ciz(surf):
    olecek=[]
    su=time.time()
    for p in parcalar:
        g=su-p["t0"]
        if g>p["omur"]: olecek.append(p); continue
        t2=g/p["omur"]
        p["x"]+=p["vx"]; p["y"]+=p["vy"]; p["vy"]+=0.15*S
        a=int(255*(1-t2)); b=max(1,int(p["boyut"]*(1-t2*0.5)))
        ps=pygame.Surface((b*2,b*2),pygame.SRCALPHA)
        pygame.draw.circle(ps,(*p["renk"],a),(b,b),b)
        surf.blit(ps,(int(p["x"])-b,int(p["y"])-b))
    for p in olecek: parcalar.remove(p)

# ─── FONT (ölçekli) ──────────────────────────────────────────────────────────
def mk_font(boyut):
    try:    return pygame.font.SysFont("segoeuisymbol", sc(boyut))
    except: return pygame.font.Font(None, sc(boyut))

fk = mk_font(21)   # küçük
fo = mk_font(30)   # orta
fb = mk_font(48)   # büyük
fd = mk_font(100)  # dev

# ─── IZGARA ──────────────────────────────────────────────────────────────────
SATIR = 8; SUTUN = 8
KARE  = sc(46)
IZG_W = SUTUN * KARE
IZG_X = (W - IZG_W) // 2
IZG_Y = sy(240)

oyun_alani = [[None]*SUTUN for _ in range(SATIR)]

SEKILLER = [
    [[1]],[[1,1]],[[1],[1]],[[1,1,1]],[[1],[1],[1]],
    [[1,1,1,1]],[[1],[1],[1],[1]],[[1,1,1,1,1]],[[1],[1],[1],[1],[1]],
    [[1,1],[1,1]],[[1,1,1],[1,1,1],[1,1,1]],
    [[1,0],[1,1]],[[0,1],[1,1]],[[1,1,1],[1,0,0]],[[1,1,1],[0,0,1]],
    [[1,1,1],[0,1,0]],[[0,1,0],[1,1,1]],[[1,1,0],[0,1,1]],[[0,1,1],[1,1,0]]
]

# ─── OYUN DEĞİŞKENLERİ ───────────────────────────────────────────────────────
skor=0; rekor=0; coin=0; son_skor=0; skor_anim_t=0
aktif_patlamalar=[]; oyun_durumu="SPLASH"; splash_t=time.time()
shop_scroll_y=0; TEMA_H=sc(88)
xp=0; level=1; toplam_xp=0
rozet_bildirim=[]
level_up_goster=False; level_up_t=0

ROZETLER=[
    {"id":"ilk_adim","emoji":"★","kazanildi":False,"kosul":lambda s,l,x,r:r>=1},
    {"id":"yuz_skor","emoji":"◆","kazanildi":False,"kosul":lambda s,l,x,r:s>=100},
    {"id":"bin_skor","emoji":"▲","kazanildi":False,"kosul":lambda s,l,x,r:s>=1000},
    {"id":"bes_bin", "emoji":"◈","kazanildi":False,"kosul":lambda s,l,x,r:s>=5000},
    {"id":"lvl5",    "emoji":"✦","kazanildi":False,"kosul":lambda s,l,x,r:l>=5},
    {"id":"lvl10",   "emoji":"✶","kazanildi":False,"kosul":lambda s,l,x,r:l>=10},
    {"id":"lvl20",   "emoji":"♛","kazanildi":False,"kosul":lambda s,l,x,r:l>=20},
    {"id":"xp_5k",   "emoji":"♦","kazanildi":False,"kosul":lambda s,l,x,r:x>=5000},
    {"id":"xp_20k",  "emoji":"♚","kazanildi":False,"kosul":lambda s,l,x,r:x>=20000},
    {"id":"rekor_2k","emoji":"♜","kazanildi":False,"kosul":lambda s,l,x,r:r>=2000},
]

# ─── VERİ YÜKLEMESİ ──────────────────────────────────────────────────────────
if os.path.exists("rekor.txt"):
    try: rekor=int(open("rekor.txt").read())
    except: pass
if os.path.exists("shop_data.txt"):
    try:
        sat=open("shop_data.txt").read().splitlines()
        if sat: coin=int(sat[0])
        for k in TEMALAR:
            if k in sat: TEMALAR[k]["satin"]=True
        if sat and sat[-1] in TEMALAR: aktif_tema=sat[-1]
    except: pass
if os.path.exists("xp_data.txt"):
    try:
        xd=open("xp_data.txt").read().splitlines()
        xp=int(xd[0]); level=int(xd[1]); toplam_xp=int(xd[2])
        for roz in ROZETLER:
            if roz["id"] in xd: roz["kazanildi"]=True
    except: pass
if os.path.exists("ayarlar.txt"):
    try:
        ad=open("ayarlar.txt").read().splitlines()
        muzik_acik=ad[0]=="True"; ses_efekt_acik=ad[1]=="True"
        if len(ad)>2 and ad[2] in ("TR","EN"): dil=ad[2]
    except: pass

muzik_guncelle()

# ─── YARDIMCI FONKSİYONLAR ───────────────────────────────────────────────────
def xp_gereken(l): return l*500

def kaydet():
    open("rekor.txt","w").write(str(rekor))
    with open("shop_data.txt","w") as f:
        f.write(f"{coin}\n")
        for k,v in TEMALAR.items():
            if v["satin"]: f.write(f"{k}\n")
        f.write(aktif_tema)
    with open("xp_data.txt","w") as f:
        f.write(f"{xp}\n{level}\n{toplam_xp}\n")
        for roz in ROZETLER:
            if roz["kazanildi"]: f.write(f"{roz['id']}\n")
    with open("ayarlar.txt","w") as f:
        f.write(f"{muzik_acik}\n{ses_efekt_acik}\n{dil}\n")

def rozet_kontrol(s):
    for roz in ROZETLER:
        if not roz["kazanildi"]:
            try:
                if roz["kosul"](s,level,toplam_xp,rekor):
                    roz["kazanildi"]=True
                    rozet_bildirim.append({"roz":roz,"t0":time.time()})
            except: pass

def oyun_bitis_xp(s):
    global xp,level,toplam_xp,level_up_goster,level_up_t
    kaz=max(10,s//10); xp+=kaz; toplam_xp+=kaz
    while xp>=xp_gereken(level):
        xp-=xp_gereken(level); level+=1
        level_up_goster=True; level_up_t=time.time()
    rozet_kontrol(s); kaydet()

def sigar(sekil,r,c):
    if r<0 or r+len(sekil)>SATIR: return False
    if c<0 or c+len(sekil[0])>SUTUN: return False
    for dr in range(len(sekil)):
        for dc in range(len(sekil[dr])):
            if sekil[dr][dc] and oyun_alani[r+dr][c+dc] is not None: return False
    return True

def herhangi_sigar(sekil):
    return any(sigar(sekil,r,c) for r in range(SATIR) for c in range(SUTUN))

def yeni_blok(idx):
    tv=TEMALAR[aktif_tema]
    gec=[s for s in SEKILLER if herhangi_sigar(s)]
    sekil=random.choice(gec) if gec else random.choice(SEKILLER)
    km=random.uniform(0.2,0.8)
    c1=lerp(tv["b1"],tv["b2"],km); c2=lerp(tv["b1"],tv["b2"],1-km)
    # Alt blok pozisyonları – 3 blok yan yana, ekran genişliğine orantılı
    slot_w = W // 3
    ox = slot_w*idx + slot_w//2 - sc(22)
    oy = sy(648)
    return {"sekil":sekil,"r1":c1,"r2":c2,"glow":tv["glow"],
            "x":ox,"y":oy,"ox":ox,"oy":oy,"tutuldu":False,"aktif":True}

alttaki=[yeni_blok(0),yeni_blok(1),yeni_blok(2)]
secilen=None; fark_x=fark_y=0

def yer_var():
    aktifler=[b for b in alttaki if b["aktif"]]
    if not aktifler: return True
    return any(sigar(b["sekil"],r,c) for b in aktifler for r in range(SATIR) for c in range(SUTUN))

def satir_kontrol():
    global skor,coin
    sil_r=[r for r in range(SATIR) if all(oyun_alani[r][c] is not None for c in range(SUTUN))]
    sil_c=[c for c in range(SUTUN) if all(oyun_alani[r][c] is not None for r in range(SATIR))]
    n=len(sil_r)+len(sil_c)
    if n>0:
        ses_cal(ses_patla)
        tv=TEMALAR[aktif_tema]
        for r in sil_r:
            for c in range(SUTUN):
                parca_patla(IZG_X+c*KARE+KARE//2,IZG_Y+r*KARE+KARE//2,tv["glow"])
                oyun_alani[r][c]=None
        for c in sil_c:
            for r in range(SATIR):
                if oyun_alani[r][c] is not None:
                    parca_patla(IZG_X+c*KARE+KARE//2,IZG_Y+r*KARE+KARE//2,tv["glow"])
                    oyun_alani[r][c]=None
        aktif_patlamalar.append({"r":list(sil_r),"c":list(sil_c),"t0":time.time()})
        skor+=n*100; coin+=n*5
    return n

# ─── UI RECT (ölçekli, ortalı) ───────────────────────────────────────────────
# Ana menü butonları
BTN_CLASSIC  = sr(90,320,270,58)
BTN_SHOP     = sr(90,398,270,58)
BTN_SETTINGS = sr(90,476,270,58)
BTN_LOBI     = sr(100,500,250,62)
BTN_GERI     = sr(25,38,90,40)
# Ayarlar toggleları
TGL_MUZIK    = sr(290,230,80,38)
TGL_SES      = sr(290,310,80,38)
BTN_TR       = sr(130,388,80,42)
BTN_EN       = sr(240,388,80,42)

saat = pygame.time.Clock()

# ─── ANA DÖNGÜ ───────────────────────────────────────────────────────────────
while True:
    saat.tick(60)
    fare = pygame.mouse.get_pos()
    su = time.time()

    if skor > son_skor: son_skor=skor; skor_anim_t=su

    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            kaydet(); pygame.quit(); sys.exit()
        if e.type == pygame.KEYDOWN:
            if e.key in (pygame.K_ESCAPE, pygame.K_AC_BACK):
                if oyun_durumu in ("GAME","SHOP","SETTINGS","GAME_OVER"):
                    oyun_durumu="MAIN_MENU"; kaydet()
                else:
                    kaydet(); pygame.quit(); sys.exit()

        if e.type == pygame.MOUSEBUTTONDOWN:
            if oyun_durumu=="SHOP":
                if e.button==4: shop_scroll_y=min(0,shop_scroll_y+sc(30))
                elif e.button==5:
                    mn=-max(0,len(TEMALAR)*TEMA_H-sy(470))
                    shop_scroll_y=max(mn,shop_scroll_y-sc(30))

            if e.button==1:
                # ANA MENÜ
                if oyun_durumu=="MAIN_MENU":
                    if BTN_CLASSIC.collidepoint(fare):
                        oyun_alani=[[None]*SUTUN for _ in range(SATIR)]
                        skor=son_skor=0
                        alttaki=[yeni_blok(0),yeni_blok(1),yeni_blok(2)]
                        parcalar.clear(); oyun_durumu="GAME"
                    elif BTN_SHOP.collidepoint(fare): oyun_durumu="SHOP"
                    elif BTN_SETTINGS.collidepoint(fare): oyun_durumu="SETTINGS"

                # MAĞAZA
                elif oyun_durumu=="SHOP":
                    if BTN_GERI.collidepoint(fare): oyun_durumu="MAIN_MENU"; kaydet()
                    else:
                        by2=sy(225)+shop_scroll_y
                        for i,(tid,tv) in enumerate(TEMALAR.items()):
                            row=pygame.Rect(sx(25),by2+i*TEMA_H,sc(400),sc(78))
                            if row.collidepoint(fare) and sy(205)<row.centery<sy(730):
                                if tv["satin"]: aktif_tema=tid
                                elif coin>=tv["fiyat"]:
                                    coin-=tv["fiyat"]; tv["satin"]=True; aktif_tema=tid

                # AYARLAR
                elif oyun_durumu=="SETTINGS":
                    if BTN_GERI.collidepoint(fare): oyun_durumu="MAIN_MENU"; kaydet()
                    elif TGL_MUZIK.collidepoint(fare):
                        muzik_acik=not muzik_acik; muzik_guncelle(); kaydet()
                    elif TGL_SES.collidepoint(fare):
                        ses_efekt_acik=not ses_efekt_acik; kaydet()
                    elif BTN_TR.collidepoint(fare): dil="TR"; kaydet()
                    elif BTN_EN.collidepoint(fare): dil="EN"; kaydet()

                # GAME OVER
                elif oyun_durumu=="GAME_OVER":
                    if BTN_LOBI.collidepoint(fare): oyun_durumu="MAIN_MENU"

                # OYUN – blok tut
                elif oyun_durumu=="GAME":
                    for b in alttaki:
                        if not b["aktif"]: continue
                        k2=sc(22)
                        bw=len(b["sekil"][0])*k2; bh=len(b["sekil"])*k2
                        if pygame.Rect(b["x"],b["y"],bw,bh).collidepoint(fare):
                            ses_cal(ses_tut); b["tutuldu"]=True; secilen=b
                            fark_x=(len(b["sekil"][0])*KARE)//2
                            fark_y=(len(b["sekil"])*KARE)//2
                            break

        if e.type==pygame.MOUSEBUTTONUP and e.button==1:
            if oyun_durumu=="GAME" and secilen:
                secilen["tutuldu"]=False
                sc2=round((secilen["x"]-IZG_X)/KARE)
                sr2=round((secilen["y"]-IZG_Y)/KARE)
                if sigar(secilen["sekil"],sr2,sc2):
                    ses_cal(ses_koy); kn=0
                    for dr in range(len(secilen["sekil"])):
                        for dc in range(len(secilen["sekil"][dr])):
                            if secilen["sekil"][dr][dc]:
                                oyun_alani[sr2+dr][sc2+dc]=(secilen["r1"],secilen["r2"],secilen["glow"])
                                kn+=1
                    secilen["aktif"]=False; skor+=kn*10; coin+=max(0,int(kn*0.25))
                    if random.random()<0.25: coin+=1
                    satir_kontrol()
                    if skor>rekor: rekor=skor
                else:
                    secilen["x"]=secilen["ox"]; secilen["y"]=secilen["oy"]
                secilen=None
                if all(not b["aktif"] for b in alttaki):
                    alttaki=[yeni_blok(0),yeni_blok(1),yeni_blok(2)]

    if oyun_durumu=="GAME" and secilen and secilen["tutuldu"]:
        secilen["x"]=fare[0]-fark_x; secilen["y"]=fare[1]-fark_y

    # ── ÇİZİM ────────────────────────────────────────────────────────────────
    tv=TEMALAR[aktif_tema]

    # Gradient arka plan – tam ekran
    grad_rect(ekran,(0,0,W,H),tv["bg_top"],tv["bg_bot"])

    # Hafif noise
    ns=pygame.Surface((W,H),pygame.SRCALPHA)
    for yy in range(0,H,max(1,sc(4))):
        pygame.draw.line(ns,(255,255,255,random.randint(0,5)),(0,yy),(W,yy))
    ekran.blit(ns,(0,0))

    # ── SPLASH ───────────────────────────────────────────────────────────────
    if oyun_durumu=="SPLASH":
        gec=su-splash_t
        sal=math.sin(gec*9)*12
        alf=min(255,int(gec*300))
        for rad in range(sc(120),sc(20),-sc(8)):
            a2=int(80*(1-rad/sc(120)))
            gs=pygame.Surface((rad*2,rad*2),pygame.SRCALPHA)
            pygame.draw.circle(gs,(*tv["glow"],a2),(rad,rad),rad)
            ekran.blit(gs,(CX-rad,H//2-rad))
        t1=fd.render("LS",True,(*tv["accent"],alf))
        t2=fb.render("STUDIO",True,(220,220,255,alf))
        tr=pygame.transform.rotate(t1,sal)
        ekran.blit(tr,tr.get_rect(center=(CX,H//2-sc(30))))
        ekran.blit(t2,t2.get_rect(center=(CX,H//2+sc(60))))
        if gec>2.8: oyun_durumu="MAIN_MENU"

    # ── ANA MENÜ ─────────────────────────────────────────────────────────────
    elif oyun_durumu=="MAIN_MENU":
        for gw in [6,4,2]:
            gt=fb.render(M("baslik"),True,tv["glow"]); gt.set_alpha(40)
            ekran.blit(gt,gt.get_rect(center=(CX+gw,sy(165))))
            ekran.blit(gt,gt.get_rect(center=(CX-gw,sy(165))))
        bas=fb.render(M("baslik"),True,(240,245,255))
        ekran.blit(bas,bas.get_rect(center=(CX,sy(165))))
        alt=fk.render(M("studio"),True,(*tv["accent"],180))
        ekran.blit(alt,alt.get_rect(center=(CX,sy(210))))
        for i in range(5):
            a=su*0.4+i*1.25
            bx2=CX+int(math.cos(a)*sc(160)); by3=sy(160)+int(math.sin(a*0.7)*sc(80))
            bsz=sc(18)+int(math.sin(a*1.3)*sc(6))
            draw_cube(ekran,bx2-bsz//2,by3-bsz//2,bsz,tv["b1"],tv["b2"],tv["glow"])
        neon_btn(ekran,BTN_CLASSIC, M("klasik_mod"), fo,BTN_CLASSIC.collidepoint(fare), accent=tv["accent"])
        neon_btn(ekran,BTN_SHOP,    M("tema_magaza"),fo,BTN_SHOP.collidepoint(fare),    accent=tv["accent"])
        neon_btn(ekran,BTN_SETTINGS,M("ayarlar"),    fo,BTN_SETTINGS.collidepoint(fare),accent=tv["accent"])
        ct=fk.render(f"◈ {coin} Coin",True,tv["accent"])
        ekran.blit(ct,ct.get_rect(center=(CX,sy(558))))

    # ── AYARLAR ──────────────────────────────────────────────────────────────
    elif oyun_durumu=="SETTINGS":
        glass(ekran,(0,0,W,sy(195)),a=70,renk=(20,20,40))
        bt=fb.render(M("ayarlar_baslik"),True,(240,245,255))
        ekran.blit(bt,bt.get_rect(center=(CX,sy(100))))
        neon_btn(ekran,BTN_GERI,M("geri"),fk,BTN_GERI.collidepoint(fare),accent=tv["accent"])

        glass(ekran,(sx(20),sy(205),sc(410),sy(420)),a=40,ba=80,renk=(200,220,255),r=sc(20))

        # Müzik satırı
        glass(ekran,(sx(30),sy(218),sc(390),sc(66)),a=30,renk=(255,255,255),r=sc(14))
        ekran.blit(fo.render(M("muzik"),True,(220,230,255)),(sx(50),sy(238)))
        md=fk.render(M("muzik_ac") if muzik_acik else M("muzik_kapat"),True,
                     tv["accent"] if muzik_acik else (150,160,180))
        ekran.blit(md,md.get_rect(midright=(TGL_MUZIK.left-sc(8),TGL_MUZIK.centery)))
        draw_toggle(ekran,TGL_MUZIK,muzik_acik,tv["accent"])

        # Ses satırı
        glass(ekran,(sx(30),sy(298),sc(390),sc(66)),a=30,renk=(255,255,255),r=sc(14))
        ekran.blit(fo.render(M("ses"),True,(220,230,255)),(sx(50),sy(318)))
        sd=fk.render(M("muzik_ac") if ses_efekt_acik else M("muzik_kapat"),True,
                     tv["accent"] if ses_efekt_acik else (150,160,180))
        ekran.blit(sd,sd.get_rect(midright=(TGL_SES.left-sc(8),TGL_SES.centery)))
        draw_toggle(ekran,TGL_SES,ses_efekt_acik,tv["accent"])

        # Dil satırı
        glass(ekran,(sx(30),sy(378),sc(390),sc(80)),a=30,renk=(255,255,255),r=sc(14))
        ekran.blit(fo.render(M("dil_sec"),True,(220,230,255)),(sx(50),sy(388)))
        neon_btn(ekran,BTN_TR,"TR",fo,BTN_TR.collidepoint(fare) or dil=="TR",
                 accent=tv["accent"] if dil=="TR" else (100,120,160))
        neon_btn(ekran,BTN_EN,"EN",fo,BTN_EN.collidepoint(fare) or dil=="EN",
                 accent=tv["accent"] if dil=="EN" else (100,120,160))

        if not os.path.exists(MUZIK_DOSYA):
            nt=fk.render(M("muzik_yok"),True,(180,100,100))
            ekran.blit(nt,nt.get_rect(center=(CX,sy(495))))

    # ── MAĞAZA ───────────────────────────────────────────────────────────────
    elif oyun_durumu=="SHOP":
        glass(ekran,(0,0,W,sy(195)),a=70,renk=(20,20,40))
        bt=fb.render(M("magaza_baslik"),True,(240,245,255))
        ekran.blit(bt,bt.get_rect(center=(CX,sy(90))))
        ct=fo.render(f"◈  {coin} Coin",True,tv["accent"])
        ekran.blit(ct,ct.get_rect(center=(CX,sy(145))))
        neon_btn(ekran,BTN_GERI,M("geri"),fk,BTN_GERI.collidepoint(fare),accent=tv["accent"])

        clip=pygame.Rect(0,sy(200),W,sy(540))
        ekran.set_clip(clip)
        by2=sy(225)+shop_scroll_y
        for i,(tid,tv2) in enumerate(TEMALAR.items()):
            ry=by2+i*TEMA_H
            row=pygame.Rect(sx(25),ry,sc(400),sc(78))
            if row.bottom<sy(200) or row.top>sy(745): continue
            pr=lerp(tv2["b1"],tv2["b2"],0.5)
            iak=(aktif_tema==tid)
            ba2=220 if iak else (140 if row.collidepoint(fare) else 70)
            glass(ekran,(row.x,row.y,row.w,row.h),a=80 if iak else 45,ba=ba2,renk=pr,r=sc(14))
            if iak: glow_rect(ekran,(row.x,row.y,row.w,row.h),tv2["glow"],radius=sc(14),steps=6)
            for ci,cr in enumerate([tv2["b1"],tv2["b2"],tv2["glow"]]):
                pygame.draw.circle(ekran,cr,(row.x+sc(18)+ci*sc(16),row.centery),sc(6))
                pygame.draw.circle(ekran,(255,255,255),(row.x+sc(18)+ci*sc(16),row.centery),sc(6),1)
            ekran.blit(fk.render(tid,True,(240,245,255)),(row.x+sc(70),row.y+sc(15)))
            if iak:   d,dc=M("aktif"),tv2["accent"]
            elif tv2["satin"]: d,dc=M("sec"),(180,200,255)
            else:     d,dc=f"◈ {tv2['fiyat']:,}",tv2["accent"]
            dt=fk.render(d,True,dc)
            ekran.blit(dt,dt.get_rect(midright=(row.right-sc(15),row.centery)))
        ekran.set_clip(None)
        sh=pygame.Surface((W,sy(40)),pygame.SRCALPHA)
        for yy in range(sy(40)): pygame.draw.line(sh,(0,0,0,int(150*yy/sy(40))),(0,yy),(W,yy))
        ekran.blit(sh,(0,sy(200)))
        sh2=pygame.Surface((W,sy(40)),pygame.SRCALPHA)
        for yy in range(sy(40)): pygame.draw.line(sh2,(0,0,0,int(150*(1-yy/sy(40)))),(0,yy),(W,yy))
        ekran.blit(sh2,(0,sy(735)))

    # ── OYUN & GAME OVER ─────────────────────────────────────────────────────
    elif oyun_durumu in ("GAME","GAME_OVER"):
        # HUD
        glass(ekran,(IZG_X-sc(5),sy(20),IZG_W+sc(10),sy(55)),a=50,renk=(255,255,255),r=sc(14))
        ekran.blit(fk.render(f"⬆ {rekor}",True,(180,190,220)),(IZG_X+sc(5),sy(38)))
        ct=fk.render(f"◈ {coin}",True,tv["accent"])
        ekran.blit(ct,ct.get_rect(midright=(IZG_X+IZG_W-sc(5),sy(48))))

        # XP bar
        bx2,by4,bw,bh=IZG_X,sy(82),IZG_W,sc(14)
        glass(ekran,(bx2-sc(2),by4-sc(2),bw+sc(4),bh+sc(4)),a=40,renk=(200,220,255),r=sc(8))
        xpr=min(1.0,xp/max(1,xp_gereken(level)))
        if xpr>0:
            dw=int(bw*xpr)
            ds=pygame.Surface((dw,bh),pygame.SRCALPHA)
            grad_rect(ds,(0,0,dw,bh),tv["b1"],tv["glow"],dikey=False)
            ds.set_alpha(220); ekran.blit(ds,(bx2,by4))
        ekran.blit(fk.render(f"{M('level')} {level}",True,tv["accent"]),(bx2,by4+bh+sc(3)))
        xt=fk.render(f"{xp}/{xp_gereken(level)} XP",True,(160,170,200))
        ekran.blit(xt,xt.get_rect(right=bx2+bw,top=by4+bh+sc(3)))

        # Level UP anim
        if level_up_goster:
            lg=su-level_up_t
            if lg<2.0:
                la=int(255*(1-lg/2.0)); ly=int(sy(150)-lg*sc(60))
                ls=fb.render(f"{M('level_up')} {M('level')}{level}",True,tv["accent"]); ls.set_alpha(la)
                ekran.blit(ls,ls.get_rect(center=(CX,ly)))
            else: level_up_goster=False

        # Skor
        ai=min(1.0,(su-skor_anim_t)/0.35)
        sf=int(sc(68)+(1-ai)*sc(18))
        sfnt=pygame.font.Font(None,sf)
        ss=sfnt.render(str(skor),True,(255,255,255))
        gs2=sfnt.render(str(skor),True,tv["glow"]); gs2.set_alpha(80)
        ekran.blit(gs2,gs2.get_rect(center=(CX+2,IZG_Y-sc(55)+2)))
        ekran.blit(ss,ss.get_rect(center=(CX,IZG_Y-sc(55))))

        # Izgara arka planı
        sh3=pygame.Surface((IZG_W+sc(20),IZG_W+sc(20)),pygame.SRCALPHA)
        pygame.draw.rect(sh3,(0,0,0,80),(0,0,IZG_W+sc(20),IZG_W+sc(20)),border_radius=sc(12))
        ekran.blit(sh3,(IZG_X-sc(10),IZG_Y-sc(5)))
        glass(ekran,(IZG_X-sc(4),IZG_Y-sc(4),IZG_W+sc(8),IZG_W+sc(8)),a=40,ba=80,renk=(200,220,255),r=sc(10))

        for r in range(SATIR):
            for c in range(SUTUN):
                kx=IZG_X+c*KARE; ky=IZG_Y+r*KARE
                if oyun_alani[r][c] is not None:
                    c1,c2,gw=oyun_alani[r][c]; draw_cube(ekran,kx,ky,KARE,c1,c2,gw)
                else:
                    bg=pygame.Surface((KARE,KARE),pygame.SRCALPHA)
                    pygame.draw.rect(bg,(255,255,255,12),(0,0,KARE,KARE))
                    pygame.draw.rect(bg,(255,255,255,30),(0,0,KARE,KARE),1)
                    ekran.blit(bg,(kx,ky))

        # Patlama animasyonları
        for pat in list(aktif_patlamalar):
            gp=su-pat["t0"]
            if gp>0.45: aktif_patlamalar.remove(pat); continue
            gw2=int(gp*sc(50)); a3=int(255*(1-gp/0.45))
            for r in pat["r"]:
                ry=IZG_Y+r*KARE
                rs=pygame.Surface((IZG_W+gw2*2,KARE+gw2*2),pygame.SRCALPHA)
                pygame.draw.rect(rs,(*tv["glow"],a3),(0,0,IZG_W+gw2*2,KARE+gw2*2),width=sc(3),border_radius=sc(6))
                ekran.blit(rs,(IZG_X-gw2,ry-gw2))
            for c in pat["c"]:
                cx3=IZG_X+c*KARE
                cs=pygame.Surface((KARE+gw2*2,IZG_W+gw2*2),pygame.SRCALPHA)
                pygame.draw.rect(cs,(*tv["glow"],a3),(0,0,KARE+gw2*2,IZG_W+gw2*2),width=sc(3),border_radius=sc(6))
                ekran.blit(cs,(cx3-gw2,IZG_Y-gw2))

        parca_ciz(ekran)

        # Alt blok paneli
        glass(ekran,(sc(10),sy(625),W-sc(20),sy(145)),a=45,ba=70,renk=(200,220,255),r=sc(18))

        for b in alttaki:
            if not b["aktif"]: continue
            k2=KARE if b["tutuldu"] else sc(22)
            for dr in range(len(b["sekil"])):
                for dc in range(len(b["sekil"][dr])):
                    if b["sekil"][dr][dc]:
                        draw_cube(ekran,b["x"]+dc*k2,b["y"]+dr*k2,k2,b["r1"],b["r2"],b["glow"],tutuldu=b["tutuldu"])

        # Önizleme
        if oyun_durumu=="GAME" and secilen and secilen["tutuldu"]:
            pc=round((secilen["x"]-IZG_X)/KARE)
            pr2=round((secilen["y"]-IZG_Y)/KARE)
            if sigar(secilen["sekil"],pr2,pc):
                for dr in range(len(secilen["sekil"])):
                    for dc in range(len(secilen["sekil"][dr])):
                        if secilen["sekil"][dr][dc]:
                            pv=pygame.Surface((KARE,KARE),pygame.SRCALPHA)
                            pygame.draw.rect(pv,(*secilen["r1"],90),(0,0,KARE,KARE))
                            pygame.draw.rect(pv,(*secilen["glow"],160),(0,0,KARE,KARE),sc(2))
                            ekran.blit(pv,(IZG_X+(pc+dc)*KARE,IZG_Y+(pr2+dr)*KARE))

        if oyun_durumu=="GAME" and not yer_var():
            ses_cal(ses_bitis); oyun_durumu="GAME_OVER"; oyun_bitis_xp(skor)

    # ── GAME OVER OVERLAY ────────────────────────────────────────────────────
    if oyun_durumu=="GAME_OVER":
        ov=pygame.Surface((W,H),pygame.SRCALPHA); ov.fill((5,8,20,230)); ekran.blit(ov,(0,0))
        for rad in range(sc(160),sc(20),-sc(12)):
            a4=int(45*(1-rad/sc(160)))
            gs3=pygame.Surface((rad*2,rad*2),pygame.SRCALPHA)
            pygame.draw.circle(gs3,(*tv["glow"],a4),(rad,rad),rad)
            ekran.blit(gs3,(CX-rad,sy(310)-rad))
        bg2=fd.render(M("bitti"),True,tv["glow"]); bg2.set_alpha(55)
        bt2=fd.render(M("bitti"),True,(239,68,68))
        ekran.blit(bg2,bg2.get_rect(center=(CX+sc(3),sy(313))))
        ekran.blit(bt2,bt2.get_rect(center=(CX,sy(310))))
        ekran.blit(fo.render(f"{M('skor')}: {skor}",True,(220,225,255)),
                   fo.render(f"{M('skor')}: {skor}",True,(220,225,255)).get_rect(center=(CX,sy(400))))
        rg=fo.render(f"{M('en_iyi')}: {rekor}",True,tv["accent"])
        ekran.blit(rg,rg.get_rect(center=(CX,sy(445))))
        neon_btn(ekran,BTN_LOBI,M("lobiye_don"),fo,BTN_LOBI.collidepoint(fare),accent=tv["accent"])

    pygame.display.flip()