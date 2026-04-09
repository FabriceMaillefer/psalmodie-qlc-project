# Psalmo Light — éclairage QLC+

Configuration d'éclairage pour les célébrations (psalmodie) : pilotage ArtNet d'un
parc de 8 projecteurs LED, console virtuelle jouée en direct depuis une surface de
contrôle MIDI **Behringer X-Touch Compact**.

Fichier projet : `Psalmo Light 2026_4.qxw`

---

## Démarrage

1. Copier les deux `.qxf` de ce dossier dans `~/.qlcplus/fixtures/` (Linux),
   `%HOMEPATH%/QLC+/fixtures` (Windows) ou
   `~/Library/Application Support/QLC+/fixtures` (macOS). Sans eux, 6 des
   8 projecteurs ne se patchent pas.
2. Régler le réseau de l'ordinateur sur le sous-réseau `169.254.31.x`
   (le nœud ArtNet est en `169.254.31.100`).
3. Brancher la X-Touch Compact **avant** de lancer QLC+.
4. Lancer QLC+ et ouvrir `Psalmo Light 2026_4.qxw`.
5. Monter le fader `MASTER`.

---

## Univers

| ID | Nom | Rôle |
|---|---|---|
| 0 | `Psalmo` | sortie DMX — ArtNet vers `169.254.31.100`, ligne 5 |
| 1 | `USB (Salle)` | raccordement au système de la salle d'accueil |
| 2 | `MIDI Input` | entrée X-Touch Compact |

## Adressage DMX (univers 0)

| Projecteur | Modèle | Mode | DMX |
|---|---|---|---|
| Bar RGBW A | OXO LED Bar PixyLine150 RGBW | 5 Channel | 1–5 |
| Bar RGBW B | OXO LED Bar PixyLine150 RGBW | 5 Channel | 7–11 |
| Spot RGB A | Showtec Spectral M800 IPX | AR1.D | 13–16 |
| Spot RGB B | Showtec Spectral M800 IPX | AR1.D | 18–21 |
| Spot W Gauche | Elation OPTI TRI WHITE PAR | 6 Channels | 50–55 |
| Spot W Centre | Elation OPTI TRI WHITE PAR | 6 Channels | 60–65 |
| Spot W Droite | Elation OPTI TRI WHITE PAR | 6 Channels | 70–75 |
| Spot W Instrument | Elation OPTI TRI WHITE PAR | 6 Channels | 80–85 |

42 canaux sur 512.

### Implantation des canaux

| Appareil | 0 | 1 | 2 | 3 | 4 | 5 |
|---|---|---|---|---|---|---|
| OXO PixyLine150 | Dimmer | Red | Green | Blue | White | — |
| Showtec Spectral M800 | Dimmer | Red | Green | Blue | — | — |
| Elation OPTI TRI WHITE | Cool White | Warm White | Amber | MACROS | Strobe | Master Dimmer |

---

## Structure

**Zones** — `FACE - Chorale` (Gauche + Droite), `FACE - Discours` (Centre),
`FACE - Instru`, `Retro - A` (spots RGB), `Retro - Barres` (barres RGBW).

**18 palettes** : 17 couleurs + 1 intensité à 100 %.

**39 scènes**, toutes de type `Scene` : 34 couleurs (17 × 2 bus) et 5 intensités.
Aucun chaser ni effet, tout se joue en direct.

---

## Console virtuelle

Une page, 1920 × 1080.

- **SoloFrames `Couleur Spot` / `Couleur Barres`** — 17 boutons couleur chacun, en
  *Toggle*, une seule couleur active à la fois par bus.
- **Faders d'intensité** — `Intensité Spot`, `Intensité Barre`, et pour la face
  `Chorale`, `Instru`, `Discours`.
- **Faders de mélange** — R/G/B sur les spots, R/G/B/W sur les barres.
- **Frame `Chaleur du Blanc`** — `Cold`, `Warm`, `Amber`, `Macro K` sur les 4 PAR.
- **Blackout**, **Stop**, **MASTER** en Grand Master.

## Mapping MIDI (X-Touch Compact, univers 2)

| Canal | Contrôle |
|---|---|
| 1 / 2 | Intensité Spot / Intensité Barre |
| 7 / 8 / 9 | Face Discours / Instru / Chorale |
| 15 / 16 / 17 | Cold / Warm / Amber |
| 18 / 20 / 22 | Spots : Red / Green / Blue |
| 19 / 21 / 23 / 25 | Barres : Red / Green / Blue / White |
| 136–141, 143 | Remise à zéro des faders de mélange |
| 181 / 182 | Stop / Blackout |
