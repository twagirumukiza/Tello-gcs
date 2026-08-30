"""Moteur d'exécution séquentiel de missions, avec pause/reprise/annulation.

Voir chapitre 9 du livre. Version corrigée : action "photo" implémentée,
type d'action inconnu lève une erreur explicite, wait() est interruptible.
"""
import threading
import time


class MissionExecutionError(Exception):
    pass


class MissionEngine:
    def __init__(self, controller, photo_callback=None):
        self.controller = controller
        self.photo_callback = photo_callback  # fourni par le module vidéo si besoin
        self._pause_event = threading.Event()
        self._pause_event.set()  # non en pause par défaut
        self._cancel_requested = False
        self.current_step = 0
        self.log: list[str] = []

    def run(self, mission):
        self._cancel_requested = False
        self.current_step = 0
        for i, action in enumerate(mission.actions):
            self.current_step = i
            self._pause_event.wait()  # bloque ici si en pause
            if self._cancel_requested or self.controller.emergency:
                self.log.append(f"Mission annulée à l'étape {i}")
                return
            try:
                self._execute(action)
            except MissionExecutionError as exc:
                # Erreur fondamentale (type inconnu, photo sans callback...) :
                # on arrête la mission plutôt que de continuer à l'aveugle.
                self.log.append(f"Mission arrêtée : {exc}")
                return

    def _execute(self, action):
        handlers = {
            "takeoff": lambda p: self.controller.takeoff(),
            "land": lambda p: self.controller.land(),
            "move": lambda p: self.controller.move(p["direction"], p["distance"]),
            "rotate": lambda p: self.controller.rotate_clockwise(p["degrees"]),
            "wait": lambda p: self._interruptible_wait(p["seconds"]),
            "photo": lambda p: self._take_photo(),
        }
        handler = handlers.get(action.type)
        if handler is None:
            raise MissionExecutionError(f"Type d'action inconnu : {action.type!r}")
        try:
            handler(action.params)
            self.log.append(f"OK : {action.type} {action.params}")
        except MissionExecutionError:
            raise  # erreur fondamentale : on la laisse remonter jusqu'à run()
        except Exception as exc:
            # Erreur ponctuelle (ex : commande refusée par le drone) : on la
            # journalise et on continue avec l'étape suivante.
            self.log.append(f"Erreur sur {action.type} : {exc}")

    def _interruptible_wait(self, seconds: float, step: float = 0.1):
        """Attend par petits pas plutôt qu'en un seul sleep, pour qu'une
        annulation ou un arrêt d'urgence soit pris en compte sans délai."""
        elapsed = 0.0
        while elapsed < seconds:
            if self._cancel_requested or self.controller.emergency:
                return
            time.sleep(step)
            elapsed += step

    def _take_photo(self):
        if self.photo_callback is None:
            raise MissionExecutionError("Aucun photo_callback fourni au moteur de missions")
        self.photo_callback()

    def pause(self):
        self._pause_event.clear()

    def resume(self):
        self._pause_event.set()

    def cancel(self):
        self._cancel_requested = True
        self._pause_event.set()  # débloque une éventuelle pause en cours
