"""Point de passage unique entre l'application et le SDK Tello.

Aucun autre module de l'application n'importe djitellopy directement :
tout passe par TelloController. Voir chapitres 2, 4 et 10 du livre.
"""
import threading
import time
from enum import Enum, auto

from djitellopy import Tello


class ConnectionState(Enum):
    DISCONNECTED = auto()
    CONNECTING = auto()
    CONNECTED = auto()
    ERROR = auto()


class CommandError(Exception):
    pass


class TelloController:
    def __init__(self):
        self._tello = Tello()
        self.state = ConnectionState.DISCONNECTED
        self.emergency = False

    # --- Connexion (chapitre 2) ---------------------------------------

    def connect(self, timeout=8):
        self.state = ConnectionState.CONNECTING
        # RESPONSE_TIMEOUT est un attribut de classe de djitellopy.Tello :
        # le fixer borne le délai d'attente de la connexion ET de toutes
        # les commandes envoyées ensuite (il n'existe pas de paramètre
        # de timeout par appel dans cette bibliothèque).
        Tello.RESPONSE_TIMEOUT = timeout
        try:
            self._tello.connect(wait_for_state=True)
            self.state = ConnectionState.CONNECTED
        except Exception as exc:
            self.state = ConnectionState.ERROR
            raise ConnectionError(f"Connexion au Tello impossible : {exc}") from exc

    def disconnect(self):
        try:
            self._tello.end()
        finally:
            self.state = ConnectionState.DISCONNECTED

    @property
    def is_connected(self):
        return self.state is ConnectionState.CONNECTED

    def send(self, command_fn, *args, retries=2, **kwargs):
        """Exécute une commande Tello avec retry et remontée d'erreur propre."""
        last_error = None
        for _ in range(retries + 1):
            try:
                return command_fn(*args, **kwargs)
            except Exception as exc:
                last_error = exc
                time.sleep(0.3)
        raise CommandError(f"Échec après {retries + 1} tentatives : {last_error}")

    def start_watchdog(self, interval=2.0):
        def loop():
            while True:
                if self.state is ConnectionState.CONNECTED:
                    try:
                        self._tello.get_battery()
                    except Exception:
                        self.state = ConnectionState.ERROR
                        self._try_reconnect()
                time.sleep(interval)

        threading.Thread(target=loop, daemon=True).start()

    def _try_reconnect(self):
        try:
            self.connect()
        except ConnectionError:
            pass

    # --- Sécurité (chapitre 4 / 10) -------------------------------------

    def emergency_stop(self):
        self.emergency = True
        try:
            self._tello.send_rc_control(0, 0, 0, 0)
            self._tello.land()
        except Exception:
            pass

    def reset_emergency(self):
        self.emergency = False

    # --- Commandes de haut niveau (chapitre 4) --------------------------
    # Introduites pour que plus aucun module, y compris l'interface, n'ait
    # besoin d'accéder à _tello directement.

    def send_rc_control(self, left_right, forward_backward, up_down, yaw):
        if not self.emergency:
            self._tello.send_rc_control(left_right, forward_backward, up_down, yaw)

    def takeoff(self):
        return self.send(self._tello.takeoff)

    def land(self):
        return self.send(self._tello.land)

    def move(self, direction: str, distance_cm: int):
        return self.send(getattr(self._tello, f"move_{direction}"), distance_cm)

    def rotate_clockwise(self, degrees: int):
        return self.send(self._tello.rotate_clockwise, degrees)

    # --- Lecture de télémétrie / vidéo -----------------------------------

    def get_battery(self):
        return self._tello.get_battery()

    def get_height(self):
        return self._tello.get_height()

    def get_current_state(self):
        return self._tello.get_current_state()

    def get_frame_read(self):
        return self._tello.get_frame_read()

    def streamon(self):
        self._tello.streamon()

    def streamoff(self):
        self._tello.streamoff()
