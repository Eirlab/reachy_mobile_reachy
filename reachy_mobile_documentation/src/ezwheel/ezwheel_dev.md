# Ezwheel

Trois principaux blocs ont été développés pour la gestion de la base mobile : le développement du package
ros `reachy_mobile_ezwheel` (contenant les packages `reachy_mobile_navigation`, `reachy_mobile_description`
, `reachy_mobile_slam` et `reachy_mobile_teleop`), le développement d'une API permettant d'exposer les fonctions de
contrôle de la base ainsi que de la classe `SimpleNavigationGoals` permettant de gérer les objectifs de navigation.

## <class> Paramètres de navigation </class>

Seuls les paramètres que nous avons modifié par rapport aux valeurs par défaut sont inscrites ci-dessous

<method> TebLocalPlannerROS </method>

- **odom_topic**: /swd_diff_drive_controller/odom

<member> Trajectory </member>

- **global_plan_overwrite_orientation**: False
- **max_global_plan_lookahead_dist**: 0.5
- **feasibility_check_no_poses**: 5

<member> Robot </member>

- **max_vel_x**: 3
- **max_vel_x_backwards**: 0.01
- **max_vel_theta**: 3
- **footprint_model**:
    - **type**: "polygon"
    - **vertices**: `[[0.12, 0.267], [0.12, -0.267], [-0.415, -0.2], [-0.415, 0.2]]`

<member> Goal Tolerance </member>

- **xy_goal_tolerance**: 0.4
- **yaw_goal_tolerance**: 0.4
- **free_goal_vel**: True

<member> Obstacle parameters </member>

- **min_obstacle_dist**: 0.15
- **obstacle_poses_affected**: 20
- **costmap_converter_rate**: 10

<member> Optimization parameters </member>

- **penalty_epsilon**: 0.01
- **weight_kinematics_forward_drive**: 1000
- **weight_kinematics_turning_radius**: 100
- **weight_optimaltime**: 10

<method> costmap_common_param_reachy </method>

- **obstacle_range**: 5.0
- **raytrace_range**: 20.0
- **footprint**: `[[0.12, 0.267], [0.12, -0.267], [-0.415, -0.2], [-0.415, 0.2]]`
- **inflation_radius**: 0.50
- **cost_scaling_factor**: 1.0
- **observation_sources**: scan
- **scan**: {sensor_frame: laser_1, data_type: LaserScan, topic: /laser_1/scan, marking: true, clearing: true}

<method> global_costmap_param </method>

- **rolling_window**: true
- **width**: 40.0
- **height**: 40.0
- **resolution**: 0.2

<method> local_costmap_param </method>

- **rolling_window**: true
- **width**: 8.0
- **height**: 8.0
- **resolution**: 0.1

## <class> SimpleNavigationGoals </class>

Cette classe a pour but de générer les différents messages nécessaire pour communiquer avec le robot en utilisant
l'action serveur **move_base**.

<method> \_\_init__ </method>

Cette fonction instancier la classe et récupère un accès au **move_base** action server. Elle initialise aussi les
différents champs des messages qui seront envoyés.

<method> go_to </method>

Crée et envoie un message sur le topic **/move_base_simple/goal** pour se déplacer sur la carte

<member> Paramètres </member>

- **x**: Position en x
- **y**: Position en y
- **theta**: Orientation
- **wait_for_result**: timeout avant d'annuler le déplacement
- **frame**: Nom de la frame dans laquelle se trouve le point
- **blocking**: Si True, la fonction bloque jusqu'à ce que le robot arrive à la position

<method> is_arrived </method>

Renvoie le **GoalStatus** de la dernière requête envoyée parmis la liste suivante : "Running", "Rejected", "Preempted"
, "Aborted", "Succeeded", "Lost" or "Undefined".

<method> cancel_all_goals </method>

Met fin à tous les déplacements en cours et tous les objectifs en attente.

## <class> API </class>

L'API est une api flask nous permettant de transmettre un ordre de navigation, d'obtenir le statut de la navigation et
de l'annuler.

<method> goal </method>

- Méthode : POST
- Route : /goal
- Données : {"x": float, "y": float, "theta": float}
- Résumé : Envoie un ordre de navigation

<method> status </method>

- Méthode : GET
- Route : /status
- Données : Aucune
- Résumé : Renvoie le statut de la navigation

<method> cancel </method>

- Méthode : POST
- Route : /cancel
- Données : Aucune
- Résumé : Annule la navigation en cours

