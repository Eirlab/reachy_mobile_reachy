# État de l'art

## Résumé

Parmi les différents cobots existant, les cobots de service sont ceux évoluant le plus proche des humains. Les
utilisations de ces derniers sont variées (guidage dans un aéroport, aide à la personne ...) et la construction d'un
cobot de service implique de relever plusieurs défis.

Dans le cas d'un cobot de service mobile, il est nécessaire de faire en sorte que ce robot puisse se déplacer dans un
environnement dynamique et incertain avec une certaine fiabilité. Pour cela une modélisation du monde, comme celle par
grille d'occupation probabiliste, est utilisée pour permettre au cobot de traduire ce que ses capteurs perçoivent et sa
position dans l'environnement. De plus une stratégie d'élaboration de trajectoires prenant en compte l'incertitude sur
l'environnement et le dynamisme de ce dernier est nécessaire. Pour ce défi, les méthodes délibératives et plus
particulièrement l'algorithme \textit{riskRRT} permettent de fournir une solutions.

En plus de la navigation, un cobot de service a pour rôle d'interagir avec les humains. Pour cela il est nécessaire
d'étudier et de proposer une implémentation des règles sociales par la théorie proxémique. Au-delà du respect des règles
sociales, il est nécessaire de mettre en place un moyen de communication entre le cobot et les humains. Plusieurs
techniques peuvent être utilisées comme la reconnaissance vocale, la détection de gestes ou l'\textit{eye-contact}.
L'intégration de ces règles et de cette communication est une phase clé permettant de passer d'un robot ayant la
capacité de naviguer dans une foule à un robot interagissant convenablement avec cette foule.

Finalement, lorsqu'un robot de service est capable de naviguer dans une foule et d'interagir correctement avec des
humains, il reste à fournir du contenu lors de ces interactions pour que le cobot ait une réelle utilité. Ces
interactions peuvent avoir différentes formes comme guider les utilisateurs vers des points d'intérêts, faire visiter un
espace ou dans notre cas jouer à des jeux simples. Dans le cadre des jeux, nous pouvons citer un jeu de plateau, le
tictactoe qui nécessite de détecter des formes sur un plateau pour jouer et établir une stratégie de jeux. Ou le
chifoumi qui nécessite de détecter la forme de la main pour savoir qui entre le robot et l'humain a gagné. Ces deux
détections sont résolues en utilisant du \textit{deep learning} permettant de s'adapter à une grande variété de
situations.

Introduction
============

Depuis la révolution industrielle, les automates puis la robotique
tendent à aider l'humain dans les différentes tâches qu'il doit
réaliser, principalement dans les tâches de production en usine.
Cependant, nombre de robots possèdent sont performants lorsqu'ils sont
isolés (parfois en cage) et que l'humain n'est là que pour contrôler
globalement l'ensemble des procédés. Imaginer un robot évoluant
librement dans un magasin sans gêner, ni physiquement, ni
psychologiquement, les usagers soulève des problématiques.

Depuis 1996, J. E. Colgate, W. Wannasuphoprasit et M. A. Peshkin ont
proposé une définition de la notion de cobotique, cette notion a été
subdivisée avec le temps en trois grands domaines de la cobotique. D'une
part la cobotique industrielle permettant de répondre aux tâches
difficiles et pénibles ou à très faible valeur ajoutée. Le cobot asiste
en direct les gestes de l'opérateur en démultipliant ses capacités pour
manipuler en sécurité des pièces chaudes, lourdes, encombrantes, petites
\... La cobotique médicale, parfaitement illustrée par le cobot [Da
Vinci](https://fr.wikipedia.org/wiki/Da_Vinci_(chirurgie)) qui permet
d'assister un chirurgien lors d'une opération. Finalement la cobotique
qui va nous intéresser pendant ce projet, la cobotique dites conviviale,
elle consiste à utiliser des robots, le plus souvent humanoïdes (par
exemple le robot [NAO](https://fr.wikipedia.org/wiki/NAO_(robotique))),
pour établir des communications et rendre des services. Cette
utilisation prend son sens dans la robotique de service, où le robot
humanoïde est par exemple appelé à guider, interagir et rendre des
services[^1].

C'est dans ce cadre de la cobotique de service que s'inscrit notre
projet, en effet, notre client souhaite disposer d'un robot de service
dans le cadre des 100 ans de l'ENSEIRB-MATMECA. L'objectif de ce robot
est de fournir du contenu utile aux visiteurs comme leur indiquer la
localisation des salles, des toilettes, proposer des jeux interactifs,
etc. Pour se faire nous avons à notre disposition deux robots
indépendants, d'une part un [robot de navigation
EZ-WHEEL](https://ez-wheel.com/fr/kit-de-developpement-pour-agvamr) et
un [robot semi-humanoïde REACHY](https://www.pollen-robotics.com/).
L'objectif de ce projet est d'intégrer les deux robots ensemble sur
l'environnement ROS. Cette intégration couvre plusieurs domaines puisque
nous devons à la fois réaliser l'intégration mécatronique, réaliser les
algorithmes de navigation adéquats à ce nouveau robot et prévoir des
interactions avec les visiteurs pour que ce robot soit une réelle valeur
ajoutée à l'événement et non une curiosité à la limite de la vallée de
l'étrange. Cela nous amène donc à la problématique générale de ce
projet, comment concevoir un cobot destiné aux interactions humaines
lors d'événements ?

Le contexte de ce projet soulève d'abord une problématique de foule, en
effet le robot devra évoluer dans un environnement densément peuplé, il
devra même faire plus qu'une simple navigation dans cet environnement,
il devra être capable de détecter les humains et interagir avec eux de
manière adéquate. Dans cet optique, nous allons orienter notre état de
l'art selon trois axes, premièrement les questions de navigation dans un
environnement dynamique et incertain sont traitées. Nous rajouterons
ensuite le fait qu'un humain n'est pas un simple objet en mouvement,
mais qu'il obéit à certaines règles sociales. Pour que notre robot soit
suffisamment accepté il est nécessaire d'étudier ces règles sociales
pour, *in fine*, en faire un modèle et l'intégrer au robot. Finalement
notre robot est amené à interagir avec les gens et à réaliser des jeux
avec lui. Que ce soit pour l'interaction ou pour les jeux il est
nécessaire qu'il possède la capacité de voir et de comprendre la
sémantique derrière la vision, nous traitons donc des différents
algorithmes qui seront utilisées.

[^1]: Exemple d'un robot de service à l'aéroport de Genève :
    <https://www.youtube.com/watch?v=Jdc_AmLVlVI>
