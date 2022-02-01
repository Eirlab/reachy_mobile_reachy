# Ezwheel

Notre projet se base sur le SWD Starter Kit
d'[EZWheel](https://www.ez-wheel.com/storage/upload/pdf/leaflet-starter-kit-swd-fr-08122021.pdf), l'objectif de ce robot
est de permettre au robot Reachy de se déplacer dans une foule.

Le robot est livré avec odométrie, l'asservissement en vitesse, le SLAM ainsi qu'une intégration sur ROS. Notre objectif
sur ce robot est d'y intégrer la stack de navigation classique en ROS 1.

La navigation consiste à déplacer le robot d'un endroit à une destination spécifiée dans un environnement donné. Pour ce
faire, une carte contenant les informations géométriques des meubles, des objets et des murs de l'environnement est
nécessaires. La carte a été créée avec les informations de distance obtenues par le capteur Lidar et les informations de
position du robot via les algorithmes de SLAM.

La navigation permet au robot de se déplacer de la position actuelle à la position cible désignée sur la carte en
utilisant la carte, l'encodeur du robot et le capteur de distance.

## Lancement de la navigation

Sur la base ez-wheel d'EirLab la stack de navigation démarre automatiquement au démarrage du robot.

Sur une autre base il faudra se connecter au même WiFi que la base, créer un `catkin_ws` et
copier [notre dépôt](https://github.com/Eirlab/reachy_mobile_ezwheel) dans le dossier `src` de l'environnement. Compiler
avec `catkin_make` puis le sourcer et lancer `roslaunch reachy_mobile_navigation reachy_mobile_navigation.launch` sur
votre PC.

## Estimation de la position initiale

Une fois lancé il faut réaliser l'estimation de la position initiale à l'aide de rviz, si vous êtes sur la base ez-wheel
d'EirLab lancez simplement dans un terminal `rviz` puis chargez la [configuration](images/default.rviz)

Vous pouvez ensuite utiliser l'outils 2D Pose Estimate pour estimer sa position initiale

![Pose estimate](images/2d_pose_button.png)

## Donner un objectif de navigation

Pour donner un objectif de navigation au robot vous pouvez, en utilisant Rviz, utiliser l'outil 2D Nav Goal pour définir
la position cible.

![Nav goal](images/2d_nav_goal_button.png)

Sinon, sans utiliser rviz vous pouvez utiliser l'API fournie par le robot pour donner un objectif de navigation en
effectuant une requête POST sur l'URL `http://<IP_ROBOT>:5000/goal` avec les paramètres `x`, `y` et `theta` qui
définissent la position cible. Pour plus d'informations sur l'[API](ezwheel_dev.md)

## Lancement du SLAM

Si vous souhaiter réaliser un SLAM sur la carte, vous pouvez lancer le SLAM en lançant la commande `roslaunch reachy_mobile_slam reachy_mobile_slam.launch`

Pour enregistrer la map lancez simplement `rosrun map_server map_saver -f /path/to/maps/map`

## Lancement de la téléoperation

Si vous souhaitez téléopérer le robot, vous pouvez lancer le téléoperation en lançant la commande `roslaunch reachy_mobile_teleop reachy_mobile_teleop.launch`