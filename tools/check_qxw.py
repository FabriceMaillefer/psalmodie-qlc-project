#!/usr/bin/env python3
"""Controle de coherence d'un projet QLC+ (.qxw).

Rejoue automatiquement les verifications qui avaient revele les defauts de la
configuration 2026-Q1 :

  - XML bien forme
  - chevauchements et depassements d'adresses DMX
  - references a des fixtures absentes du patch
  - references a des tetes (heads) qui n'existent pas dans le mode utilise
    -> c'est ce defaut qui vidait les groupes "Retro - A" et "Retro - Barres"
  - canaux hors plage pour le mode de la fixture
  - canaux pilotes par plusieurs faders a la fois (HTP : le plus haut gagne)
    -> c'est ce defaut qui rendait le blanc chaud pur impossible
  - groupes vides ou non utilises, palettes et scenes orphelines
  - entrees MIDI assignees sur un univers de sortie

Usage : python3 tools/check_qxw.py "Mon Projet.qxw"
"""
import glob
import os
import re
import sys
import xml.etree.ElementTree as ET
from collections import defaultdict

NS = {'q': 'http://www.qlcplus.org/Workspace'}
FNS = {'f': 'http://www.qlcplus.org/FixtureDefinition'}
FIXTURE_DIRS = [
    os.path.expanduser('~/.qlcplus/fixtures'),
    '/usr/share/qlcplus/fixtures',
    os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'),
]

problems, notes = [], []


def fail(msg):
    problems.append(msg)


def note(msg):
    notes.append(msg)


# --------------------------------------------------------- bibliotheque fixtures
def load_library():
    """Retourne {(manufacturer, model): {mode: (nb_canaux, nb_tetes)}}."""
    lib = {}
    for d in FIXTURE_DIRS:
        for path in glob.glob(os.path.join(d, '**', '*.qxf'), recursive=True):
            try:
                root = ET.parse(path).getroot()
            except ET.ParseError:
                continue
            manu = root.findtext('f:Manufacturer', namespaces=FNS)
            model = root.findtext('f:Model', namespaces=FNS)
            if not manu or not model:
                continue
            modes = {}
            for m in root.findall('f:Mode', FNS):
                chans = m.findall('f:Channel', FNS)
                heads = m.findall('f:Head', FNS)
                # sans <Head> explicite, QLC+ cree une tete implicite n0
                modes[m.get('Name')] = (len(chans), max(1, len(heads)))
            lib.setdefault((manu, model), {}).update(modes)
    return lib


def mode_info(lib, manu, model, mode, declared_channels):
    """(nb_canaux, nb_tetes) pour une fixture du projet."""
    if (manu, model) == ('Generic', 'Generic'):
        # dimmer generique : une tete par canal, construit par l'engine
        return declared_channels, max(1, declared_channels)
    modes = lib.get((manu, model))
    if modes is None:
        fail(f'definition absente de la bibliotheque : {manu} {model}')
        return declared_channels, 1
    if mode not in modes:
        fail(f'mode "{mode}" inconnu pour {manu} {model} '
             f'(modes disponibles : {", ".join(sorted(modes))})')
        return declared_channels, 1
    return modes[mode]


# ------------------------------------------------------------------------ main
def main(path):
    try:
        root = ET.parse(path).getroot()
    except ET.ParseError as e:
        print(f'XML invalide : {e}')
        return 1
    lib = load_library()

    # Attention : <Fixture>, <FixtureGroup> et <Function> apparaissent aussi comme
    # simples references (<FixtureGroup ID="5"/> dans une scene, <Function ID="15"/>
    # dans un bouton). Seuls les enfants directs de <Engine> sont des definitions.
    engine = root.find('q:Engine', NS)
    if engine is None:
        print('pas de bloc <Engine> : fichier .qxw inattendu')
        return 1

    # ---- fixtures
    fx = {}
    for f in engine.findall('q:Fixture', NS):
        fid = int(f.findtext('q:ID', namespaces=NS))
        declared = int(f.findtext('q:Channels', namespaces=NS))
        manu = f.findtext('q:Manufacturer', namespaces=NS)
        model = f.findtext('q:Model', namespaces=NS)
        mode = f.findtext('q:Mode', namespaces=NS)
        nchan, nheads = mode_info(lib, manu, model, mode, declared)
        if nchan != declared:
            fail(f'fixture {fid} "{f.findtext("q:Name", namespaces=NS)}" : '
                 f'{declared} canaux declares mais le mode "{mode}" en compte {nchan}')
        fx[fid] = {
            'name': f.findtext('q:Name', namespaces=NS),
            'uni': int(f.findtext('q:Universe', namespaces=NS)),
            'addr': int(f.findtext('q:Address', namespaces=NS)),
            'chan': nchan, 'heads': nheads,
            'label': f'{manu} {model} [{mode}]',
        }
    print(f'{len(fx)} fixtures, {sum(v["chan"] for v in fx.values())} canaux DMX')

    # ---- chevauchements d'adresses
    occupied = defaultdict(dict)
    for fid, v in sorted(fx.items()):
        if v['addr'] + v['chan'] > 512:
            fail(f'fixture {fid} "{v["name"]}" depasse l\'univers '
                 f'(adresse {v["addr"]+1} + {v["chan"]} canaux > 512)')
        for c in range(v['addr'], v['addr'] + v['chan']):
            if c in occupied[v['uni']]:
                other = occupied[v['uni']][c]
                fail(f'conflit DMX univers {v["uni"]} canal {c+1} : '
                     f'"{v["name"]}" et "{fx[other]["name"]}"')
            occupied[v['uni']][c] = fid

    # ---- groupes : fixtures et tetes valides
    groups = {}
    for g in engine.findall('q:FixtureGroup', NS):
        gid = int(g.get('ID'))
        name = g.findtext('q:Name', namespaces=NS)
        heads = []
        for h in g.findall('q:Head', NS):
            hf, hh = int(h.get('Fixture')), int(h.text)
            if hf not in fx:
                fail(f'groupe {gid} "{name}" reference la fixture {hf}, absente du patch')
            elif hh >= fx[hf]['heads']:
                fail(f'groupe {gid} "{name}" reference la tete {hh} de "{fx[hf]["name"]}" '
                     f'qui n\'en a que {fx[hf]["heads"]} ({fx[hf]["label"]}) '
                     f'-> cette entree ne pilote rien')
            else:
                heads.append((hf, hh))
        groups[gid] = {'name': name, 'heads': heads}
        if not heads:
            note(f'groupe {gid} "{name}" est vide')

    # une tete dans plusieurs groupes : si deux scenes d'intensite pilotent ces
    # groupes, elles se disputent le meme canal (HTP, le plus haut gagne)
    membership = defaultdict(list)
    for gid, g in groups.items():
        for head in g['heads']:
            membership[head].append(gid)
    for (hf, hh), gids in sorted(membership.items()):
        if len(gids) > 1:
            where = ', '.join(f'{g} "{groups[g]["name"]}"' for g in gids)
            fail(f'"{fx[hf]["name"]}" appartient a {len(gids)} groupes a la fois '
                 f'({where}) -> leurs scenes d\'intensite se disputeront le canal')

    # ---- fonctions
    used_groups, used_palettes = set(), set()
    kinds = defaultdict(int)
    for fn in engine.findall('q:Function', NS):
        kinds[fn.get('Type')] += 1
        for fg in fn.findall('q:FixtureGroup', NS):
            # une Scene ecrit <FixtureGroup ID="5"/>, une RGBMatrix <FixtureGroup>5</FixtureGroup>
            raw = fg.get('ID') if fg.get('ID') is not None else (fg.text or '').strip()
            if not raw:
                fail(f'fonction {fn.get("ID")} "{fn.get("Name")}" a un '
                     f'<FixtureGroup> sans groupe designe')
                continue
            gid = int(raw)
            used_groups.add(gid)
            if gid not in groups:
                fail(f'fonction {fn.get("ID")} "{fn.get("Name")}" utilise '
                     f'le groupe {gid}, inexistant')
        for p in fn.findall('q:Palette', NS):
            used_palettes.add(int(p.get('ID')))
    palettes = {int(p.get('ID')) for p in engine.findall('q:Palette', NS)}
    nfunc = sum(kinds.values())
    detail = ', '.join(f'{n} {k}' for k, n in sorted(kinds.items()))
    print(f'{len(groups)} groupes, {len(palettes)} palettes, '
          f'{nfunc} fonctions ({detail})')
    for gid in sorted(set(groups) - used_groups):
        note(f'groupe {gid} "{groups[gid]["name"]}" n\'est utilise par aucune fonction')
    for pid in sorted(used_palettes - palettes):
        fail(f'palette {pid} utilisee par une scene mais absente du projet')
    for pid in sorted(palettes - used_palettes):
        note(f'palette {pid} n\'est utilisee par aucune scene')

    # ---- console virtuelle : faders de niveau
    writers = defaultdict(list)
    for sl in root.iter(f'{{{NS["q"]}}}Slider'):
        cap, sid = sl.get('Caption'), sl.get('ID')
        for ch in sl.iter(f'{{{NS["q"]}}}Channel'):
            cf, cc = int(ch.get('Fixture')), int(ch.text)
            if cf not in fx:
                fail(f'fader "{cap}" (ID {sid}) reference la fixture {cf}, '
                     f'absente du patch')
                continue
            if cc >= fx[cf]['chan']:
                fail(f'fader "{cap}" (ID {sid}) ecrit le canal {cc} de '
                     f'"{fx[cf]["name"]}" qui n\'en a que {fx[cf]["chan"]}')
                continue
            writers[(cf, cc)].append(f'"{cap}" (ID {sid})')
    for (cf, cc), who in sorted(writers.items()):
        if len(who) > 1:
            fail(f'canal {cc} de "{fx[cf]["name"]}" pilote par {len(who)} faders '
                 f'simultanement ({", ".join(who)}) -> HTP, le plus haut gagne')

    # ---- univers d'entree / de sortie
    out_uni = {int(u.get('ID')) for u in root.iter(f'{{{NS["q"]}}}Universe')
               if u.find('q:Output', NS) is not None}
    in_uni = {int(u.get('ID')) for u in root.iter(f'{{{NS["q"]}}}Universe')
              if u.find('q:Input', NS) is not None}
    for el in root.iter():
        if not el.tag.endswith('}Input'):
            continue
        u = el.get('Universe')
        if u is None:
            continue
        u = int(u)
        if u in out_uni and u not in in_uni:
            fail(f'une assignation externe pointe sur l\'univers {u}, '
                 f'qui est une SORTIE (canal {el.get("Channel")}) -> ne declenchera pas')

    # ---- rapport
    print()
    if problems:
        print(f'{len(problems)} probleme(s) :')
        for p in problems:
            print(f'  [!] {p}')
    else:
        print('Aucun probleme detecte.')
    if notes:
        print(f'\n{len(notes)} remarque(s) :')
        for n in notes:
            print(f'  [i] {n}')
    return 1 if problems else 0


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(2)
    sys.exit(main(sys.argv[1]))
