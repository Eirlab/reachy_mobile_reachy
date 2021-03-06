# Reachy

Le Reachy possède quatre principaux blocs de fonctionnalités : le contrôleur général permettant d'orchestrer toutes les
actions que le robot effectue et dans quel ordre (détection de squelette, lancement du jeu, navigation etc), le jeu de
tictactoe, la détection de squelette par PoseNet ainsi qu'une API permettant de contrôler le robot de l'extérieur.

## <class> Contrôleur général </class>

Le contrôleur général permet d'orchestrer les actions de Reachy il est appelé lorsque l'on effectue une requête POST sur
le point de terminaison `/play` de l'API ci-dessous ou lorsqu'on effectue la commande `python3 reachy.py` depuis le
dossier `reachy_mobile_reachy`.

Le contrôleur prend en paramètres 3 booléens (posenet, navigation et tictactoe) qui détermine si on veut activer ou non
les fonctionnalités correspondantes. Si navigation est activée, un thread est lancé permettant de se déplacer de point en
point sur la carte. Si posenet est activé alors le tictactoe ne sera lancé que si le robot détecte un squelette levant
la main.

Ce fichier permet de définir le comportement général du robot, mais les interactions avec les utilisateurs (sons,
mouvements de la tête, mouvements des antennes) sont disséminées dans les différents blocs.

## <class> API </class>

L'API permet de contrôler le robot à distance, elle se lance automatiquement au démarrage du robot ou via un terminal
depuis le répertoire `reachy_mobile_reachy/API` : `python3 run_api.py`

Il suffit ensuite de se rendre en `<IP_ROBOT>:8000` pour accéder à l'API.

Le front de l'API est défini dans le dossier `API/templates` et se base principalement sur de l'html en utilisant
bootstrap.

Le back de l'API est défini dans `API/api.py` et est constitué d'une API Flask dont les points de terminaisons sont
ci-dessous.

<method> index </method>
- Méthode : GET
- Route : /
- Données : Aucune
- Résumé : Retourne la page d'accueil du site

<method> error_404 </method>
- Méthode : GET
- Route : /error_404
- Données : Aucune
- Résumé : Retourne la page d'erreur 404

<method> error_500 </method>
- Méthode : GET
- Route : /error_500
- Données : Aucune
- Résumé : Retourne la page d'erreur 500

<method> reachy </method>
- Méthode : GET
- Route : /reachy
- Données : Aucune
- Résumé : Retourne la page du reachy

<method> ezwheel </method>
- Méthode : GET
- Route : /ezwheel
- Données : Aucune
- Résumé : Retourne la page du ezwheel

<method> reachy_on </method>
- Méthode : POST
- Route : /reachy/on
- Données : Aucune
- Résumé : Rend rigide le bras droit du robot

<method> reachy_off </method>
- Méthode : POST
- Route : /reachy/off
- Données : Aucune
- Résumé : Rend mou le bras droit du robot

<method> play </method>
- Méthode : POST
- Route : /reachy/play
- Données : {"posenet":bool, "tictactoe":bool, "navigation":bool}
- Résumé : Lance le programme général avec les différentes fonctionnalités

<method> stop </method>
- Méthode : POST
- Route : /reachy/stop
- Données : Aucune
- Résumé : Arrête le programme général

<method> head_on </method>
- Méthode : POST
- Route : /reachy/head/on
- Données : Aucune
- Résumé : Rend rigide la tête du robot

<method> head_off </method>
- Méthode : POST
- Route : /reachy/head/off
- Données : Aucune
- Résumé : Rend mou la tête du robot

<method> head_lookat </method>
- Méthode : POST
- Route : /reachy/head/lookat
- Données : {"x":float, "y":float, "z":float, "duration":float}
- Résumé : Fait regarder la tête du robot vers un point

<method> head_happy </method>
- Méthode : POST
- Route : /reachy/head/happy
- Données : Aucune
- Résumé : Rend le robot heureux

<method> head_sad </method>
- Méthode : POST
- Route : /reachy/head/sad
- Données : Aucune
- Résumé : Rend le robot triste

<method> camera_left </method>
- Méthode : GET
- Route : /reachy/camera/left
- Données : Aucune
- Résumé : Retourne l'image de la caméra gauche

<method> camera_right </method>
- Méthode : GET
- Route : /reachy/camera/right
- Données : Aucune
- Résumé : Retourne l'image de la caméra droite

<method> camera_left_autofocus </method>
- Méthode : POST
- Route : /reachy/camera/left/autofocus
- Données : Aucune
- Résumé : La caméra gauche fait l'autofocus

<method> camera_right_autofocus </method>
- Méthode : POST
- Route : /reachy/camera/right/autofocus
- Données : Aucune
- Résumé : La caméra droite fait l'autofocus

<method> detection </method>
- Méthode : POST
- Route : /reachy/detection
- Données : Aucune
- Résumé : Renvoie la liste des images analysées par le réseau de neuronne du TicTacToe

<method> detection_get </method>
- Méthode : GET
- Route : /reachy/detection/<filename>
- Données : Aucune
- Résumé : Renvoie l'image analysée par le réseau de neuronne du TicTacToe en fonction de son nom

<method> ezwheel_goal </method>
- Méthode : POST
- Route : /ezwheel/goal
- Données : {"x":float, "y":float, "theta":float}
- Résumé : Envoie un ordre de navigation vers un point

<method> ezwheeel_status </method>
- Méthode : GET
- Route : /ezwheel/status
- Données : Aucune
- Résumé : Retourne l'état de la navigation

<method> ezwheel_cancel </method>
- Méthode : POST
- Route : /ezwheel/cancel
- Données : Aucune
- Résumé : Annule l'ordre de navigation

