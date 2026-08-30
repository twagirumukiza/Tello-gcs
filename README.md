# Tello Ground Control Station

Code source complet du livre **« Programmer un drone Tello »** (Innocent Twagirumukiza) — une station de contrôle au sol pour drone DJI Tello : pilotage manuel, télémétrie, vidéo, vision par ordinateur, missions automatisées, sécurité, assistant IA, historique et packaging.

Ce dépôt correspond à la version corrigée du manuscrit (bugs d'encapsulation, bug d'unité sur l'altitude, action `photo` manquante, dépendances de packaging, etc. — voir la section *Corrections* plus bas).

## Installation

```bash
python -m venv .venv
source .venv/bin/activate      # ou .venv\Scripts\activate sous Windows
pip install -r requirements.txt
```

Configuration testée : Tello standard, Windows 11, Python 3.10, `djitellopy` 2.5.

Pour l'assistant IA (chapitre 11), définis ta clé API :

```bash
export ANTHROPIC_API_KEY="sk-..."
```

## Lancer l'application

```bash
python main.py
```

**⚠ Avant le premier vol** : fais ce test dans un espace dégagé, sans personnes ni obstacles à proximité. Garde le drone à portée de vue. Le code de ce dépôt est fourni à titre pédagogique, sans garantie, et ne remplace pas la réglementation locale applicable aux drones.

## Structure du projet et correspondance avec le livre

| Fichier | Chapitre |
|---|---|
| `tello_link/controller.py`, `tello_link/connection.py` | 2 — Connexion et moteur de communication |
| `ui/main_window.py` (squelette) | 3 — Interface du cockpit |
| `tello_link/input.py`, `tello_link/gamepad.py`, `ui/main_window.py` (pilotage) | 4 — Pilotage manuel |
| `tello_link/telemetry.py`, `ui/telemetry_panel.py` | 5 — Télémétrie temps réel |
| `tello_link/video.py`, `ui/video_panel.py` | 6 — Vidéo & HUD |
| `vision/pipeline.py` | 7 — Reconnaissance visuelle & suivi d'objets |
| `vision/follow.py` | 8 — Reconnaissance faciale & suivi automatique |
| `missions/model.py`, `missions/engine.py`, `missions/builder.py`, `missions/patterns.py` | 9 — Vol autonome & plan de vol |
| `safety/monitor.py`, `safety/position.py` | 10 — Sécurité et position estimée |
| `ai/assistant.py`, `ai/validation.py` | 11 — Assistant IA |
| `storage/database.py`, `storage/recorder.py`, `storage/export.py`, `monitoring/alerts.py` | 12 — Journal de bord & analyse des données de vol |
| `tests/`, `config.py` | 13 — Finalisation et packaging |

## Tests

```bash
pytest tests/
```

## Packaging en exécutable Windows

```bash
pip freeze > requirements.txt
pyinstaller --name "TelloGCS" --windowed --onefile ^
  --hidden-import cv2 --hidden-import djitellopy ^
  --hidden-import pygame --hidden-import anthropic ^
  main.py
```

## Corrections apportées par rapport au manuscrit initial

- `TelloController.connect()` applique réellement le `timeout` demandé.
- Le pilotage clavier gère désormais plusieurs touches maintenues simultanément sans se réinitialiser au relâchement de l'une d'elles.
- Plus aucun module hors de `TelloController` n'accède à `djitellopy` directement (sauf le chapitre 8, laissé tel quel intentionnellement — voir la note dans `ui/main_window.py`).
- La détection de ligne au sol (`VisionPipeline._detect_line`) est bien branchée dans `process()`.
- Le moteur de missions gère l'action `photo`, lève une erreur explicite sur un type d'action inconnu, et `wait()` est interruptible.
- Le contrôle d'altitude de `SafetyMonitor` compare des centimètres avec des centimètres (bug d'unité corrigé).
- `FlightRecorder.max_battery_used` est réellement calculé via `record_battery()`.
- `requirements.txt` inclut toutes les dépendances utilisées (`pygame`, `anthropic`, `pytest`), pas seulement celles du chapitre 1.
- Le parsing JSON des réponses de l'assistant IA est protégé par un `try/except` explicite.

## Licence

Code fourni à titre pédagogique dans le cadre du livre. Voir la mention légale de l'ouvrage.
