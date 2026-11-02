# Psalmo Light — éclairage QLC+

Configuration courante : **`Concert Light 2026_1.qxw`**, pour la série de concerts.

La configuration des célébrations, dans sa version finale du 1ᵉʳ trimestre 2026,
reste conservée dans l'historique git au tag `2026-Q1` :

```bash
git show 2026-Q1:"Psalmo Light 2026_14.qxw" > "Psalmo Light 2026_14.qxw"
git checkout 2026-Q1          # ou revenir entièrement à cet état
```

---

## Démarrage

1. **Adresser les projecteurs** selon le tableau plus bas (à faire une seule fois).
2. **Brancher la X-Touch Compact en USB**, puis l'allumer.
3. **Régler le réseau** de l'ordinateur en IP fixe `192.168.1.104` : c'est l'interface
   par laquelle QLC+ envoie l'ArtNet, vers le nœud en `192.168.1.20`.
4. **Lancer QLC+ 5.3**, puis ouvrir `Concert Light 2026_1.qxw`.
   La console virtuelle s'affiche directement.
5. **Vérifier les entrées/sorties** (onglet Entrées/Sorties) — à reconnecter chaque fois
   que le projet vient d'un autre ordinateur, ou a été enregistré sans le matériel
   branché (QLC+ remplace alors les périphériques absents par « None ») :
   - univers `Psalmo` : sortie **ArtNet**, interface `192.168.1.104`, IP de sortie
     `192.168.1.20`, univers ArtNet 1 ;
   - univers `MIDI Input` : entrée **et** retour sur `X-TOUCH COMPACT`.
6. **Monter le fader MASTER** à fond — sans lui, rien ne sort.

Rien à installer côté définitions de projecteurs : elles sont fournies avec QLC+ 5.3.

L'interface web démarre automatiquement : la console est aussi pilotable depuis un
téléphone ou une tablette sur le même réseau. Les faders motorisés et les LED de la
X-Touch suivent l'état de la console (retour MIDI actif).

---

## Jouer la console

### Lumière de face (les 8 fresnels blancs)

Trois faders dans le cadre **Facades**, un par zone. Ce sont des blancs fixes, il n'y
a pas de réglage de couleur ni de température.

| Fader écran | Fader X-Touch | Pilote |
|---|---|---|
| `Chorale` | 9 | les 4 fresnels de la chorale |
| `Instru` | 8 | les 2 fresnels de l'instrument |
| `Discours` | 7 | les 2 fresnels du discours |

⚠️ **L'ordre à l'écran n'est pas l'ordre sur la X-Touch.** À l'écran, de gauche à
droite : Chorale, Instru, Discours. Sur la surface : Discours, Instru, Chorale.

### Rétro-éclairage couleur (le fond de scène)

Deux bus indépendants, chacun avec son cadre de boutons et son fader d'intensité :

- **Spots** — les 8 Spectral. Cadre `Couleur Spot`, intensité sur le fader
  `Intensité Spot` (X-Touch n° 1).
- **Barres** — les 6 ColorBand. Cadre `Couleur Barres`, intensité sur le fader
  `Intensité Barre` (X-Touch n° 2).

17 couleurs par bus, fondu d'une seconde dans les deux sens. **Une seule couleur à la
fois par bus** : cliquer une couleur désactive la précédente.

### Les effets animés

Dans les mêmes cadres que les couleurs, mélangés aux boutons :

| Bouton | Sur | Effet |
|---|---|---|
| `RGB - Retro - Sunset` | les 6 barres | dégradé chaud qui se déplace |
| `RGB - Retro - Cold` | les 6 barres | dégradé froid qui se déplace |
| `RGB - Retro - Abstract` | les 6 barres | dégradé abstrait |
| `RGB - Spot - Abstract` | les 8 spots | dégradé abstrait |
| `Test Pattern` | les 6 barres | remplissage progressif — **vérification du patch** |

Les effets sont dans le même cadre que les couleurs fixes, donc **un effet et une
couleur statique s'excluent** : cliquer un effet coupe la couleur, et inversement.

`Test Pattern` sert au montage : il allume les barres une par une, ce qui permet de
vérifier d'un coup d'œil que les 6 adresses sont correctes et dans le bon ordre.

### Retouche de couleur à la main

Les cadres `Melange Spot` et `Melange Barres` donnent des faders Rouge / Vert / Bleu
par bus, avec un bouton de remise à zéro.

⚠️ Ces faders **ajoutent** de la couleur par-dessus la couleur active — ils ne
peuvent pas l'assombrir ni la retirer. Pour repartir propre : remettre les faders à
zéro, ou désactiver le bouton de couleur.

### Arrêts d'urgence

| Bouton | X-Touch | Effet |
|---|---|---|
| `Blackout` | 182 | coupe toute la sortie DMX, instantanément |
| `Stop` | 181 | arrête toutes les scènes et tous les effets en cours |
| `MASTER` | — | limiteur général de niveau |

---

## En cas de problème

| Symptôme | À vérifier |
|---|---|
| Rien ne s'allume | Le fader `MASTER` est-il en haut ? Le `Blackout` est-il enclenché ? |
| Rien ne s'allume, MASTER en haut | Ordinateur en `192.168.1.104` ? Câble du nœud ArtNet ? Sortie ArtNet de l'univers `Psalmo` bien sélectionnée (Entrées/Sorties) ? |
| La X-Touch ne répond pas | Elle doit être branchée **avant** le lancement de QLC+. Relancer QLC+, puis vérifier qu'elle est bien choisie en entrée et en retour de l'univers `MIDI Input`. |
| Un projecteur reste noir ou prend la mauvaise couleur | Son adresse DMX, à comparer au tableau ci-dessous. Lancer `Test Pattern` pour les barres. |
| Les effets animés ne bougent pas | Les barres doivent avoir des adresses **différentes** (voir la note sur les adresses partagées) |
| Une couleur ne part pas | Désactiver le bouton de couleur, et remettre à zéro les faders de mélange |

---

## Technique

### Univers

| ID | Nom | Rôle |
|---|---|---|
| 0 | `Psalmo` | sortie DMX principale — ArtNet par l'interface `192.168.1.104` (IP de l'ordinateur, ligne 8) vers le nœud `192.168.1.20`, univers 1 |
| 1 | `USB (Salle)` | DMX USB PRO (S/N EN507410) — raccordement au système de la salle d'accueil, non utilisé par ce patch |
| 2 | `MIDI Input` | X-Touch Compact, avec retour (`Feedback`) |

### Adressage DMX (univers 0)

| Projecteur | Modèle | Mode | Adresse |
|---|---|---|---|
| Face Chorale — **les 4 ensemble** | Axente FresnelLED WW | 1 canal | **1** |
| Face Discours — **les 2 ensemble** | Axente FresnelLED WW | 1 canal | **2** |
| Face Instru — **les 2 ensemble** | Axente FresnelLED WW | 1 canal | **3** |
| Bar Fond 01 → 06 | Chauvet ColorBand Pix IP | 4 Channel | **10, 15, 20, 25, 30, 35** |
| Retro Spot 1 → 8 | Showtec Spectral M800 IPX | AR1.D | **40, 45, 50, 55, 60, 65, 70, 75** |

22 projecteurs, 59 canaux sur 512.

**Toutes les adresses du fond vont de 5 en 5**, en une seule séquence continue : les
6 barres de 10 à 35, puis les 8 spots de 40 à 75. Chaque appareil occupe 4 canaux, il
reste donc un canal libre après chacun. Rien à calculer sur place : on avance de 5 en
5 dans l'ordre du plan.

**Les projecteurs de face partagent leur adresse par zone** : les 4 fresnels de la
chorale sont tous sur l'adresse 1, les 2 du discours sur la 2, les 2 de l'instrument
sur la 3. Trois adresses à régler au lieu de huit, et comme une zone est toujours
pilotée d'un seul fader, on ne perd aucun contrôle.

**Les barres et les spots gardent des adresses individuelles**, parce que les effets
animés font glisser un dégradé *à travers* les appareils. Les mettre sur la même
adresse ferait que tous afficheraient la même couleur au même instant, ce qui
supprimerait l'animation.

### Implantation des canaux

| Appareil | 0 | 1 | 2 | 3 |
|---|---|---|---|---|
| Axente FresnelLED WW | Dimmer | — | — | — |
| Chauvet ColorBand Pix IP | **Red** | **Green** | **Blue** | Dimmer |
| Showtec Spectral M800 IPX | Dimmer | **Red** | **Green** | **Blue** |

⚠️ L'ordre diffère entre les barres et les spots : le ColorBand est `R G B Dimmer`,
le Spectral `Dimmer R G B`. C'est le piège à retenir pour toute modification manuelle.

Les Axente sont patchés en **dimmer générique** QLC+ (`Generic / Generic`, mode
`1 Channel`, appelé `Generic` avant QLC+ 5.3) : aucun fichier de définition à
installer, l'engine la construit à la volée.

### Structure du projet

- **5 groupes** — `FACE - Chorale`, `FACE - Instru`, `FACE - Discours` (une entrée
  par zone, les projecteurs partageant l'adresse), `Retro - Spot` (8 appareils,
  géométrie 8 × 1), `Retro - Barres` (6 appareils, géométrie 6 × 1).
- **18 palettes** — 17 couleurs + 1 intensité à 100 %.
- **44 fonctions** — 39 scènes (34 couleurs sur 2 bus, 5 intensités) et
  **5 RGBMatrix**.

La géométrie des groupes (8 × 1 et 6 × 1) est ce qui donne leur sens aux effets : le
dégradé se déplace d'une case à l'autre dans cet ordre.

### Mapping MIDI complet (univers 2)

| Canal | Contrôle |
|---|---|
| 1 / 2 | Intensité Spot / Intensité Barre |
| 7 / 8 / 9 | Face Discours / Instru / Chorale |
| 18 / 20 / 22 | Spots : Red / Green / Blue |
| 19 / 21 / 23 | Barres : Red / Green / Blue |
| 136–141 | Remise à zéro des faders de mélange (`136 + n` pour le fader `18 + n`) |
| 144 / 145 | Boutons Vert / Rouge du bus spots |
| 168, 169, 174, 175, 176 | boutons d'effets et de couleurs |
| 181 / 182 | Stop / Blackout |

Canaux libres : **5, 6** (ex-TOP Chorale et Skye), **15, 16, 17, 24, 25**, et les
resets **142, 143**.

À vérifier au premier branchement : les notes 144 et 145 étaient assignées sur le
mauvais univers dans toutes les versions précédentes et n'ont donc jamais pu être
testées. Passez par l'assistant de profil d'entrée si elles ne répondent pas.

### Contrôle de cohérence

```bash
python3 tools/check_qxw.py "Concert Light 2026_1.qxw"
```

Croise le `.qxw` avec les définitions de projecteurs installées et signale :
chevauchements d'adresses, références à des projecteurs ou des têtes inexistants,
canaux hors plage, canaux pilotés par plusieurs faders à la fois, appareils présents
dans plusieurs groupes, groupes vides, palettes orphelines, entrées MIDI assignées
par erreur sur un univers de sortie. Code de sortie non nul s'il trouve un problème.

Il ne relève **aucun problème** sur cette configuration, contre 6 sur la version
finale des célébrations (tag `2026-Q1`) et 51 sur la toute première.

### Versionner le projet

QLC+ 5 enregistre les widgets de chaque cadre de la console dans un ordre qui change
à chaque sauvegarde, même sans rien modifier : il les parcourt par adresse mémoire.
Un filtre git les remet dans l'ordre de leur ID au moment du `git add` et du
`git diff`, pour que le diff ne montre que les vrais changements. Le fichier ouvert par
QLC+ n'est pas modifié. À activer une fois par clone (le `.gitattributes` l'applique
déjà aux `*.qxw`) :

```bash
git config filter.qxw.clean "python3 tools/normalize_qxw.py"
```

Changements qu'une sauvegarde peut encore faire apparaître sans que rien ait été
modifié dans le projet :

- `<Author>` : le nom de la session qui a enregistré ;
- `<InputOutputMap>` : un périphérique absent au moment de l'enregistrement (X-Touch
  débranchée, ordinateur hors du réseau `192.168.1.104`) est enregistré en `None`,
  et la sortie ArtNet perd son IP de sortie. Ne pas le commiter tel quel : reprendre
  ce bloc de la version précédente (`git checkout -p`), ou le reconnecter (voir
  Démarrage, étape 5).

Deux widgets qui se chevauchent passeraient l'un sur l'autre au hasard des
sauvegardes : il n'y en a aucun, à garder ainsi en déplaçant un widget.

---

## Ce qui change par rapport aux célébrations

| | `2026-Q1` (célébrations) | Courant (concerts) |
|---|---|---|
| Face | 29 dimmers de la salle sur l'univers USB | 8 Axente FresnelLED WW, 3 adresses |
| Rétro — barres | 10 ColorBand (Jardin / Cour / Fond) | 6 ColorBand |
| Rétro — spots | 1 Spectral M800 | 8 Spectral M800 |
| Univers utilisés | 0 (ArtNet) **et** 1 (DMX USB) | 0 seulement |
| Canaux DMX | 73 | 59 |

Hérité tel quel : les 5 RGBMatrix, le retour MIDI, l'interface web, les 18 palettes,
les 34 scènes couleur, les deux SoloFrames, l'horloge et le mapping X-Touch.

Retiré, faute de matériel équivalent dans la série : le groupe `FACE - Skye` et sa
scène, `TOP - Chorale` et sa scène, les 10 dimmers de réserve `Réglages` et la
Page 2 qui les pilotait.

Corrigé au passage, par rapport à `2026-Q1` : les faders de mélange des spots qui
pointaient sur un projecteur supprimé, les deux boutons dont l'entrée MIDI était sur
l'univers de sortie, les fondus de Rouge et Vert restés à 0 ms, la palette 19
renommée `Couleur - Magenta` puisque sa valeur est `#ff00ff`, et la scène résiduelle
`New Scene`. Le doublon de groupe sur `Face Salle Instrument 1` disparaît avec le
groupe `Skye`.

`RGB - Spot - Abstract` tournait sur un groupe d'une seule case en `2026-Q1`, faute
d'un seul spot patché ; avec 8 spots, l'effet prend enfin son sens.
