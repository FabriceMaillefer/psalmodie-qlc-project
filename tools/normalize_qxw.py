#!/usr/bin/env python3
"""Filtre git "clean" pour les projets QLC+ (.qxw) : ordre stable de la console.

QLC+ 5 enregistre les widgets d'un cadre de la console virtuelle dans l'ordre de
leur adresse memoire (VCFrame garde ses enfants dans un QMap<VCWidget*, int>,
voir qmlui/virtualconsole/vcframe.cpp) : a chaque sauvegarde, meme sans rien
modifier, les widgets changent de place dans le fichier et le diff git en est
illisible. Ce filtre les remet dans l'ordre de leur ID, cadre par cadre.

Seul l'ordre des blocs change, jamais leur contenu : QLC+ positionne chaque
widget d'apres son <WindowState>, l'ordre ne decide que de celui qui passe
dessus quand deux widgets se chevauchent (il n'y en a aucun dans ce projet).
Le texte est reordonne ligne a ligne, sans repasser par un parseur XML, pour
garder la mise en forme exacte de QLC+.

Installation (une fois par clone, la config git n'est pas versionnee) :

    git config filter.qxw.clean "python3 tools/normalize_qxw.py"

Le .gitattributes du depot applique deja le filtre aux fichiers *.qxw. Usage
direct : python3 tools/normalize_qxw.py < projet.qxw > projet-trie.qxw
"""
import re
import sys

# Balises de widgets de la console virtuelle (enfants d'un Frame/SoloFrame).
WIDGETS = ('Frame', 'SoloFrame', 'Button', 'Slider', 'Knob', 'Label', 'Clock',
           'CueList', 'XYPad', 'SpeedDial', 'AudioTriggers', 'Matrix',
           'Animation', 'Audio')
OPEN = re.compile(r'^( *)<(%s)\b[^>]*\bID="(\d+)"[^>]*?(/?)>\s*$' % '|'.join(WIDGETS))


def element_end(lines, i):
    """Index de la ligne qui ferme l'element ouvert ligne i (meme indentation)."""
    m = OPEN.match(lines[i])
    if m.group(4) == '/':
        return i
    close = '%s</%s>' % (m.group(1), m.group(2))
    for j in range(i + 1, len(lines)):
        if lines[j].rstrip('\r\n') == close:
            return j
    raise ValueError('balise <%s ID="%s"> jamais fermee' % (m.group(2), m.group(3)))


def sort_range(lines, start, end):
    """Trie les widgets enfants des lignes [start, end) et, recursivement, les leurs.

    Les widgets d'un cadre viennent apres ses proprietes (WindowState, Appearance...),
    les uns a la suite des autres : on trie chaque suite contigue de widgets de meme
    indentation, sans toucher a ce qui l'entoure.
    """
    out = []
    i = start
    while i < end:
        m = OPEN.match(lines[i])
        if not m:
            out.append(lines[i])
            i += 1
            continue
        indent = m.group(1)
        run = []
        while i < end:
            m = OPEN.match(lines[i])
            if not m or m.group(1) != indent:
                break
            j = element_end(lines, i)
            body = [lines[i]] + sort_range(lines, i + 1, j) + ([lines[j]] if j > i else [])
            run.append((int(m.group(3)), body))
            i = j + 1
        for _, body in sorted(run, key=lambda r: r[0]):
            out.extend(body)
    return out


def normalize(text):
    lines = text.splitlines(keepends=True)
    try:
        vc_start = next(k for k, l in enumerate(lines) if l.strip() == '<VirtualConsole>')
        vc_end = next(k for k, l in enumerate(lines) if l.strip() == '</VirtualConsole>')
    except StopIteration:
        return text
    return ''.join(lines[:vc_start + 1] + sort_range(lines, vc_start + 1, vc_end) + lines[vc_end:])


def main():
    data = sys.stdin.buffer.read()
    try:
        result = normalize(data.decode('utf-8')).encode('utf-8')
    except (UnicodeDecodeError, ValueError) as e:
        # Un filtre clean qui echoue bloquerait `git add` : on laisse passer tel quel.
        print('normalize_qxw : fichier laisse tel quel (%s)' % e, file=sys.stderr)
        result = data
    sys.stdout.buffer.write(result)


if __name__ == '__main__':
    main()
