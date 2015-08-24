#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import os
from pygame import *
import subprocess
font.init()
from math import cos,radians
try: import GetEvent
except: from . import GetEvent

def menu(
         menu,                          # iterable of str as ("item",) or ("item::tooltip",)
         font1      = None,             # font object|None(pygame default font): unhighlighted item font
         font2      = None,             # font object|None(font1): highlighted item font
         color1     = (128,128,128),    # (int,int,int)|color object: unhighlighted item color
         color2     = None,             # (int,int,int)|color object|None(calculated from the light arg): highlighted/neon item color
         interline  = 5,                # int: items spacing
         justify    = True,             # boolean
         light      = 5,                # int in range [-10,10]: use if color2 is None
         speed      = 300,              # int (0 = no sliding): anim speed
         lag        = 30,               # int in range [0,90]
         neon       = True,             # boolean: set neon effect
         tooltipfont= None,             # font object|None(pygame default font)
         tooltiptime= 2000,             # int
         cursor_img = None,
         hotspot    = (0,0),
         x          = None,
         y          = None,
         topleft    = None,
         midtop     = None,
         topright   = None,
         midleft    = None,
         center     = None,
         midright   = None,
         bottomleft = None,
         midbottom  = None,
         bottomright= None,
         centerx    = None,
         centery    = None,
         menu_item_idx = 0  # currently selected menu_item_idx
        ):
    """
    menu(
         menu,                          # iterable of str as ("item",) or ("item::tooltip",)
         font1      = None,             # font object|None(pygame default font): unhighlighted item font
         font2      = None,             # font object|None(font1): highlighted item font
         color1     = (128,128,128),    # (int,int,int)|color object: unhighlighted item color
         color2     = None,             # (int,int,int)|color object|None(calculated from the light arg): highlighted/neon item color
         interline  = 5,                # int: items spacing
         justify    = True,             # boolean
         light      = 5,                # int in range [-10,10]: use if color2 is None
         speed      = 300,              # int (0 = no sliding): anim speed
         lag        = 30,               # int in range [0,90]
         neon       = True,             # boolean: set neon effect
         tooltipfont= None,             # font object|None(pygame default font)
         tooltiptime= 2000              # int
         cursor_img = None,
         hotspot    = (0,0),
         x          = None,
         y          = None,
         topleft    = None,
         midtop     = None,
         topright   = None,
         midleft    = None,
         center     = None,
         midright   = None,
         bottomleft = None,
         midbottom  = None,
         bottomright= None,
         centerx    = None,
         centery    = None

    return: (None,None) if hit escape else (item,index)

    """
    global hold_bg_cursor
    shad = 100 # test

    class Item(Rect,object):
        def __init__(self,rect,label,tooltip):
            Rect.__init__(self,rect)
            self.label = label
            render1 = font1.render(label,1,color1)
            if justify: self.centerx = r1.centerx
            self.render1 = Surface(render1.get_rect().inflate(3,3).size,SRCALPHA)
            self.render1.blit(render1,(3,3))
            self.render1.fill((0,0,0,shad),special_flags=BLEND_RGBA_MIN)
            #sub1 = scr.subsurface(self.move(3,3)).copy().convert_alpha()       # test uncomment
            #surfarray.pixels_alpha(sub1)[:] = surfarray.array_alpha(render1)   # test uncomment
            sub1 = render1                                                      # test comment
            self.render1.blit(sub1,(0,0))
            self.render2 = font2.render(label,1,color2)
            self.white = self.render2.copy()
            self.white.fill((255,255,255,0),special_flags=BLEND_RGBA_MAX)
            if neon:
                render2 = font2.render(label,1,color1)
                renderneon = self.render2.copy()
                self.render2 = Surface(render2.get_rect().inflate(2,2).size,SRCALPHA)
                for pos in ((0,0),(0,1),(0,2),(1,0),(2,0),(0,2),(1,2),(2,2)):
                    self.render2.blit(renderneon,pos)
                self.render2.blit(render2,(1,1))
            if tooltip:
                tooltip = tooltipfont.render(tooltip,1,(200,200,200))
                r = tooltip.get_rect().inflate(11,7)
                self.tooltip = Surface(r.size,SRCALPHA)
                r = self.tooltip.fill((0,0,0,shad),(3,3,r.w-3,r.h-3))
                r = self.tooltip.fill((200,200,200,30),r.move(-3,-3))
                self.tooltip.fill((0,0,0,200),r.inflate(-2,-2))
                self.tooltip.blit(tooltip,(4,2))
            else:
                self.tooltip = None

    def show():
        i = Rect((0,0),menu[idx].render2.get_size())
        if justify: i.center = menu[idx].center
        else: i.midleft = menu[idx].midleft
        del_cursor()
        scr.blit(bg,r2,r2)
        [scr.blit(item.render1,item) for item in menu if item!=menu[idx]]
        scr.blit(menu[idx].white,i)
        show_cursor()
        display.update(r2)
        time.wait(50)
        del_cursor()
        r = scr.blit(menu[idx].render2,i)
        show_cursor()
        display.update(r.inflate(2,2))
        return r

    def anim():
        a = [menu[0]] if lag else menu[:]
        c = 0
        while a:
            for i in a:
                g = i.__copy__()
                i.x = i.animx.pop(0)
                r = scr.blit(i.render1,i).inflate(6,6)
                display.update((g,r))
                scr.blit(bg,r,r)
            c +=1
            if not a[0].animx:
                a.pop(0)
                if not lag: break
            if lag:
                foo,bar = divmod(c,lag)
                if not bar and foo < len(menu):
                    a.append(menu[foo])
            clk.tick(speed)

    def del_cursor():
        return scr.blit(hold_bg_cursor,scrrect.clip(hold_rect_cursor))

    def show_cursor():
        # Hack to disable mouse cursor.
        pass
        # global hold_bg_cursor
        # hold_bg_cursor = scr.subsurface(scrrect.clip(hold_rect_cursor)).copy()
        # return scr.blit(cursor_img,hold_rect_cursor)

    was_visible = mouse.set_visible(not cursor_img)
    tooltip_offset = mouse.get_cursor()[0] if not cursor_img else (cursor_img.get_width()-hotspot[0],cursor_img.get_height()-hotspot[1])
    events = event.get()
    scr = display.get_surface()
    scrrect = scr.get_rect()
    bg = scr.copy()
    if not font1: font1 = font.Font(None,scrrect.h//len(menu)//3)
    if not font2: font2 = font1
    if not color1: color1 = (128,128,128)
    if not color2: color2 = list(map(lambda x:x+int(((255-x)if light>0 else x)*(light/10.)),color1))
    if not tooltipfont: tooltipfont = font.Font(None,int(font1.size('')[1]//1.5))

    menu,tooltip = zip(*[i.partition('::')[0::2]for i in menu])

    m = max(menu,key=font1.size)
    r1 = Rect((0,0),font1.size(m))
    ih = r1.size[1]
    r2 = Rect((0,0),font2.size(m))
    r2.union_ip(r1)
    w,h = r2.w-r1.w,r2.h-r1.h
    r1.h = (r1.h+interline)*len(menu)-interline
    r2 = r1.inflate(w,h).inflate(6,6)

    pos = {"x":x,
           "y":y,
           "topleft":topleft,
           "midtop":midtop,
           "topright":topright,
           "midleft":midleft,
           "center":center,
           "midright":midright,
           "bottomleft":bottomleft,
           "midbottom":midbottom,
           "bottomright":bottomright,
           "centerx":centerx,
           "centery":centery}

    r2.center = scrrect.center
    for k,v in pos.items():
        if v != None:
           setattr(r2,k,v)

    if justify: r1.center = r2.center
    else : r1.midleft = r2.midleft

    menu = [Item(((r1.x,r1.y+e*(ih+interline)),font1.size(i)),i,tooltip[e]) for e,i in enumerate(menu)if i]

    clk  = time.Clock()
    clkt = 0
    if speed:
        for i in menu:
            z = r1.w-i.x+r1.x
            i.animx = [cos(radians(x))*(i.x+z)-z for x in list(range(90,-1,-1))]
            i.x = i.animx.pop(0)
        anim()
        for i in menu:
            z = scrrect.w+i.x-r1.x
            i.animx = [cos(radians(x))*(-z+i.x)+z for x in list(range(0,-91,-1))]
            i.x = i.animx.pop(0)


    # set currently selected menu item
    idx = menu_item_idx % len(menu)

    mouse.set_pos(menu[idx].center)
    hold_rect_cursor = Rect((-100,-100),cursor_img.get_size() if cursor_img else (0,0))
    hold_bg_cursor   = Surface((0,0))
    if not cursor_img:
        cursor_img   = Surface((0,0))
    # idx = 0
    tooltip_seen = 0
    r = show()
    dirty = ()

    while True:
        ev = GetEvent.poll()
        # if ev.type == NOEVENT and ev.inactiv >= tooltiptime:
        #     if not tooltip_seen and menu[idx].tooltip and r.collidepoint(mouse.get_pos()):
        #         rr0 = del_cursor()
                #rcom = menu[idx].tooltip.get_rect(topleft=mouse.get_pos()).inflate(4,4).move(tooltip_offset).clamp(scrrect).clip(scrrect)
                #combg = scr.subsurface(rcom).copy()
                #scr.blit(menu[idx].tooltip,rcom)
                #dirty += (rr0,rcom,show_cursor())
                #tooltip_seen = 1
        # if ev.type == MOUSEMOTION:
        #     idx_ = Rect(ev.pos,(0,0)).collidelist(menu)
        #     if idx_ != idx:
        #         if tooltip_seen and (not r.collidepoint(mouse.get_pos()) or idx_ > -1):
        #             dirty += (del_cursor(),scr.blit(combg,rcom),show_cursor())
        #             tooltip_seen = 0
        #         if idx_ > -1:
        #             idx = idx_
        #             r = show()
        #     rr0 = del_cursor()
        #     hold_rect_cursor.topleft = ev.pos
        #     hold_rect_cursor.move_ip(-hotspot[0],-hotspot[1])
        #     dirty += (rr0,show_cursor())

        # elif ev.type == MOUSEBUTTONUP and ev.button == 1 and r.collidepoint(ev.pos):
        #     ret = menu[idx].label,idx
        #     break
        if ev.type == KEYDOWN:
            try:
                # Arrow keys
                idx = (idx + {K_UP:-1,K_DOWN:1,K_KP_MINUS:-1,K_KP_PLUS:1}[ev.key])%len(menu)
                if tooltip_seen:
                    dirty += (del_cursor(),scr.blit(combg,rcom),show_cursor())
                    tooltip_seen = 0
                r = show()
            except:
                if ev.key in (K_RETURN,K_KP_ENTER):
                    ret = menu[idx].label,idx,tooltip[idx]
                    break
                elif ev.key == K_ESCAPE:
                    ret = None,None
                    break
                elif ev.key == 256:  # numeric 0, what's the pygame constant?
                    idx = 0
                    r = show()
                elif ev.key == 257:  # numeric 1, what's the pygame constant?
                    idx = 0
                    r = show()
                elif ev.key == 258:  # numeric 2, what's the pygame constant?
                    idx = 1
                    r = show()
                elif ev.key == 259:  # numeric 3, what's the pygame constant?
                    idx = 2
                    r = show()
                elif ev.key == 260:  # numeric 4, what's the pygame constant?
                    idx = 3
                    r = show()
                elif ev.key == 261:  # numeric 5, what's the pygame constant?
                    idx = 4
                    r = show()
                elif ev.key == 262:  # numeric 6, what's the pygame constant?
                    idx = 5
                    r = show()
                elif ev.key == 263:  # numeric 7, what's the pygame constant?
                    idx = 6
                    r = show()
                elif ev.key == 264:  # numeric 8, what's the pygame constant?
                    idx = 7
                    r = show()
                elif ev.key == 265:  # numeric 9, what's the pygame constant?
                    idx = 8
                    r = show()
                else:
                    print 'unhandled keypress: %r' % ev
        clkt += clk.tick()
        if clkt >= 20 and dirty:
            display.update(dirty)
            dirty = ()
            clkt = 0

    display.update(del_cursor())

    if tooltip_seen:
        display.update(scr.blit(combg,rcom))
    scr.blit(bg,r2,r2)

    if speed:
        [scr.blit(i.render1,i) for i in menu]
        display.update(r2)
        anim()
    else: display.update(r2)

    for ev in events: event.post(ev)
    mouse.set_visible(was_visible)
    return ret

if __name__ == '__main__':
    from os.path import dirname,join
    here = dirname(__file__)
    scr = display.set_mode((0,0),FULLSCREEN)
    bg = image.load(join(here,'bg.png'))
    #center = scr.get_rect().center
    center = (1024, 384)  # stereo image!!
    scr.blit(bg, bg.get_rect(center=center))
    display.flip();print(menu.__doc__)

    # defaults for current menu and item
    current_menu = 0  # 0, 1
    menu_item_idx = 0

    try:
        if os.path.exists('slide_menu_memory.json'):
            with open('slide_menu_memory.json', 'r') as f:
                slide_menu_memory = json.loads(f.read())
                current_menu = slide_menu_memory['menu']
                menu_item_idx = slide_menu_memory['menu_item']
    except:
        pass

    # Note that the folders contain some typos. They are matched with the
    # actual system.
    menus = {
        0:
            ['1 Ellemeet/Renesse (Schouwen-Duiveland)::EllemeetRenesse',  # name::folder/ini name
             '2 Kerkwerve (Schouwen-Duiveland)::Kerkwerve',
             '3 Ouwerkerk (Schouwen-Duiveland)::Ouwerkerk',
             '4 Bruinisse (Schouwen-Duiveland)::Bruinisse',
             '5 St. Philipsland (Tholen en St. Philipsland)::St.Philipsland',
             '6 Stavenisse (Tholen en St. Philipsland)::Stavenisse',
             '7 Poortvliet (Tholen en St. Philipsland)::Poortvliet',
             '8 Banjaard (Noord-Beveland)::Banjaard',
             '9 Colijnsplaat (Noord-Beveland)::Colijnsplaat',
             '10 Katspolder (Noord-Beveland)::Katspolder',
             '11 Domburg (Walcheren)::Domburg',
             '12 Westkapelle (Walcheren)::Westkapelle',
             '13 Vlissingen (Walcheren)::Vlissingen',
             '14 Ritthem-Middelburg (Walcheren)::RitthemMiddelburg',
             '15 Borssele (Zuid-Beveland - west)::Borssele',
             'volgende'
             ],
        1:
            ['vorige',
             '16 Hansweert (Zuid-Beveland - west)::Hansweert',
             '17 Kapelse Moer (Zuid-Beveland - west)::KapelseMoer',
             '18 Kruiningen-Waarde (Zuid-Beveland - oost)::KruiningenWaarde',
             '19 Rilland-Bath (Zuid-Beveland - oost)::RillandBath',
             '20 Krabbendijke (Zuid-Beveland - oost)::Krabbendijke',
             '21 Yersekemoer (Zuid-Beveland - oost)::Yersekemoer',
             '22 Breskens (Zeeuws-Vlaanderen)::Breskens',
             '23 Dow-Terneuzen (Zeeuws-Vlaanderen)::DowTerneuzen',
             '24 Kloosterzande (Zeeuws-Vlaanderen)::Kloosterzande',
             '25 Baalhoek-Hulst (Zeeuws-Vlaanderen)::BaalhoekHulst',
             #'26 Schouwen-Duiveland (Klimaat scenario)::SchouwenDuivenlandKlimaat',
             #'27 Tholen en St. Philipsland (Klimaat scenario)::TholenStPhilipslandKlimaat',
             #'28 Noord-Beveland (Klimaat scenario)NoordBeverlandKlimaat',
             #'29 Walcheren (Klimaat scenario)::WalcherenKlimaat',
             #'30 Zuid-Beveland - west (Klimaat scenario)::ZuidBeverlandWestKlimaat',
             #'31 Zuid-Beveland - oost (Klimaat scenario)::ZuidBerverlandOostklimaat',
             #'32 Zeeuws-Vlaanderen (Klimaat scenario)::ZeeuwsVlaanderenKlimaat',
             ]
        }

    while True:
        resp = menu(
            menus[current_menu],
            font1      = font.Font(join(here,'BebasNeue.otf'),25),
            font2      = font.Font(join(here,'BebasNeue.otf'),30),
            color1     = (205,205,205),
            light      = -10,
            centerx=512,
            centery=384,
            cursor_img = image.load('mouse.png'),  # We load it so we can disable it.
            menu_item_idx=menu_item_idx
            )

        print resp
        if resp[0] is None: # ESC
            break
        elif resp[0] == 'volgende':
            current_menu += 1
        elif resp[0] == 'vorige':
            current_menu -= 1
        else:
            try:
                slide_menu_memory = {'menu': current_menu, 'menu_item': resp[1]}
                with open('slide_menu_memory.json', 'w') as f:
                    json.dump(slide_menu_memory, f)
            except:
                pass
            # Try to open scenario
            display.toggle_fullscreen() # Get out of full screen
            subprocess.call([
                    '/home/user/hg/FloodViz/vrmeer/app/python/3di/r.sh',
                    resp[2]])
            display.toggle_fullscreen() # Get into full screen
            # subprocess.call([
            #         'python',
            #         '3di.py',
            #         '--use-config',
            #         #'configurations/test_museum.ini',
            #         'museum/%s.ini' % resp[2],  # i.e. TholenStPhilipslandKlimaat
            #         '-VR'])
    print(resp)
    quit()
