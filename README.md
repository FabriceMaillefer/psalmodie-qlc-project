# Psalmo Light — éclairage QLC+

Configuration d'éclairage pour les célébrations (psalmodie). **Version finale
utilisée au premier trimestre 2026.**

Fichier projet : `Psalmo Light 2026_14.qxw`

---

## Démarrage

1. Régler le réseau de l'ordinateur sur le sous-réseau `192.168.1.x`
   (le nœud ArtNet est en `192.168.1.104`).
2. Brancher l'interface **DMX USB PRO** si la salle fournit son propre système
   d'éclairage (voir *Univers* ci-dessous).
3. Brancher la X-Touch Compact **avant** de lancer QLC+.
4. Lancer QLC+ et ouvrir `Psalmo Light 2026_14.qxw`.
5. Monter le fader `MASTER`.

Rien à installer côté définitions de projecteurs : Chauvet, Showtec et les dimmers
génériques sont tous fournis avec QLC+.

L'interface web démarre automatiquement : la console est aussi pilotable depuis un
téléphone ou une tablette sur le même réseau.

---

## Univers

| ID | Nom | Rôle | Contenu |
|---|---|---|---|
| 0 | `Psalmo` | ArtNet → `192.168.1.104` ligne 8 (sortie IP `192.168.1.20`, univers 1) | les 10 barres + le spot — **44 canaux** |
| 1 | `USB (Salle)` | DMX USB PRO (S/N EN507410), 125 canaux | les 29 dimmers de la salle — **29 canaux** |
| 2 | `MIDI Input` | X-Touch Compact, **avec retour** (`Feedback`) | — |

Le retour MIDI est actif : les faders motorisés et les LED de la X-Touch suivent
l'état de la console.

---

## Adressage DMX

### Univers 0 — barres et spot (ArtNet)

| Projecteur | DMX |
|---|---|
| Bar Jardin 01 / 02 / 03 | 50–53, 55–58, 60–63 |
| Bar Fond 01 / 02 / 03 / 04 | 65–68, 70–73, 75–78, 80–83 |
| Bar Cour 01 / 02 / 03 | 95–98, 90–93, 85–88 |
| Spot RGB A | 100–103 |

Les 10 barres sont des **Chauvet ColorBand Pix IP** en mode 4 canaux
(`Red`, `Green`, `Blue`, `Dimmer`). Le spot est un **Showtec Spectral M800 IPX** en
AR1.D (`Dimmer`, `Red`, `Green`, `Blue`).

⚠️ **L'ordre des canaux diffère entre les barres et le spot** : c'est le piège à
retenir pour toute modification manuelle.

### Univers 1 — dimmers de la salle (DMX USB)

29 dimmers génériques à 1 canal : `Face Salle` (Solo, Chorale, Instrument) en 1–6 et
12–16, les réglages en 55–59, `Face Cameo` en 101–105, `Top` en 106–109, 113, 117,
121, 125.

---

## Structure

**Zones** — `FACE - Chorale` (8), `FACE - Instru` (4), `FACE - Discours` (2),
`FACE - Skye` (1), `TOP - Chorale` (5), `Retro - Spot` (1), `Retro - Barres` (10),
`Réglages` (10 dimmers de réserve).

**18 palettes** : 17 couleurs + 1 intensité à 100 %.

**47 fonctions** — 42 scènes (34 couleurs sur 2 bus, 8 intensités) et
**5 RGBMatrix** : `RGB - Retro - Sunset`, `Cold`, `Abstract` et `Test Pattern` sur
les barres, `RGB - Spot - Abstract` sur le spot. Les boutons d'effet sont placés dans
les mêmes SoloFrames que les couleurs fixes, donc un effet et une couleur statique
s'excluent mutuellement.

---

## Console virtuelle

- **Page 1** — cadre `Retro` (les deux SoloFrames de couleurs et d'effets, les faders
  de mélange R/G/B, `Intensité Spot`, `Intensité Barre`), cadre `Facades`
  (`Chorale`, `Instru`, `Discours`, `TOP Chorale`, `Skye`), une horloge,
  `Blackout`, `Stop`, `MASTER`.
- **Page 2** — un fader de niveau sur les 10 dimmers de réserve.

## Mapping MIDI (univers 2)

| Canal | Contrôle |
|---|---|
| 1 / 2 | Intensité Spot / Intensité Barre |
| 5 / 6 | TOP Chorale / Skye |
| 7 / 8 / 9 | Face Discours / Instru / Chorale |
| 18 / 20 / 22 | Spots : Red / Green / Blue |
| 19 / 21 / 23 | Barres : Red / Green / Blue |
| 136–141 | Remise à zéro des faders de mélange |
| 168, 169, 174, 175, 176 | boutons d'effets et de couleurs |
| 181 / 182 | Stop / Blackout |

---

## Contrôle de cohérence

```bash
python3 tools/check_qxw.py "Psalmo Light 2026_14.qxw"
```

Croise le `.qxw` avec les définitions de projecteurs installées et signale :
chevauchements d'adresses, références à des projecteurs ou des têtes inexistants,
canaux hors plage, canaux pilotés par plusieurs faders à la fois, appareils présents
dans plusieurs groupes, groupes vides, palettes orphelines, entrées MIDI assignées
par erreur sur un univers de sortie. Code de sortie non nul s'il trouve un problème.

Il relève **6 points** sur cette version, laissés en l'état puisque c'est la
configuration réellement utilisée :

| | Constat |
|---|---|
| 1 | `Face Salle Instrument 1` appartient à la fois à `FACE - Skye` et `FACE - Chorale` : les deux scènes d'intensité se disputent son canal (HTP, le plus haut gagne). |
| 2 | Les faders de mélange `Red` / `Green` / `Blue` des spots référencent encore la fixture ID 1, supprimée du patch — entrées mortes. |
| 3 | Les boutons `Couleur - Vert` et `Couleur - Rouge` du bus spots ont leur entrée MIDI sur l'**univers 0**, qui est une sortie : ils ne peuvent pas déclencher. |
| 4 | Les scènes Rouge et Vert ont un fondu de 0 ms quand les 15 autres couleurs sont à 1000 ms → saut visible. |
| 5 | Le groupe `Facade` est vide ; `Réglages` n'est utilisé par aucune fonction (voulu, ce sont des réserves). |
| 6 | La palette 19 vaut `#ff00ff`, du magenta pur, mais garde le nom « Violet très clair ». |

Restes de travail en cours : la scène `New Scene`, le fader `Fader 78` et la
RGBMatrix `Test Pattern`.
