# PoseNet

## Qu'est ce que PoseNet ❓

PoseNet est un système de detection de pose en temps réel permettant la detection d'humains dans une image ou une vidéo. 
Une image RGB est donnée en entrée d'un réseau de neurone convolutionnel. En sortie du réseau, PoseNet fournit l'objet pose contenant la liste de 17 points clés du corps. 
PoseNet est en mesure de detecter plusieurs personnes en simultané.

## Pourquoi PoseNet

La detection de pose est utilisée dans de nombreux domaines, notamment pour les interactions avec les utilisateurs.
PoseNet a été le système retenu pour ce projet car il fonctionne sur un Edge TPU conçu par Google. 
Reachy est équipé du Coral USB Accelerator qui est un accessoire qui ajoute le Edge TPU.

## PoseNet avec Reachy

PoseNet permet à un utilisateur d'intéragir avec Reachy. 
Lorsque une personne lève une des deux main, les antennes de reachy se mettent en mouvement pour indiquer qu'il a bien vu l'utilisateur
Si l'utilisateur garde sa main levée suffisament longtemps (3 secondes environ), reachy devient content et le Tic-tac-toe se lance
Dans le cas contraire, Reachy baisse ses antennes pour signifier qu'il est triste.
