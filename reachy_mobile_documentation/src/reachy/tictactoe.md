# Tictactoe

## Qu'est-ce que le jeu du Tic-tac-toe ❓

![tictactoe](images/tictactoe.png)   
Pollen Robotics, l'entreprise créatrice de robot Reachy, a crée un programme capable de souligner l'interactivité de
Reachy à la fois avec les humains et lors de la saisie et du déplacement d'objets : le Tic-tac-toe.   
Le tic-tac-toe, aussi appelé « morpion » (par analogie au jeu de morpion) et « oxo » en Belgique, est un jeu de
réflexion se pratiquant à deux joueurs au tour par tour dont le but est de créer un alignement de même symbole. Le jeu
se joue généralement avec papier et crayon.   
Deux joueurs s'affrontent. Ils doivent remplir chacun leur tour une case de la grille avec le symbole qui leur est
attribué : O ou X. Le gagnant est celui qui arrive à aligner trois symboles identiques, horizontalement, verticalement
ou en diagonale.

## Jouer avec Reachy

La démonstration est complètement autonome : le robot ne commencera une partie que lorsque quelqu'un se mettra devant
lui et lèvera la main. À la fin de la partie c'est à vous de remettre les pièces dans le filet. Les pièces qui
permettent de jouer au tictactoe (cubes et cylindres) se trouvent dans des paniers se situant sur les cotés de la
grille. Dès lors que reachy vous tendra le bras et ouvrira sa pince en faisant un bruit, il vous faudra lui fournir sa
pièce (cylindre) à l'endroit indiqué.

Ensuite, si quelque chose d'étrange se produit au cours d'une partie (comme quelqu'un qui triche ou que la détection est
mauvaise et donc que l'état actuel de la grille n'est pas connu) le robot baissera une de ses antennes et baleyera
toutes les pièces du plateau. Il attendra ensuite le début d'une nouvelle partie, lorsque le plateau sera à nouveau
nettoyé. Vous pouvez utiliser ce comportement pour réinitialiser le jeu quand vous le souhaitez.

Lorsque le plateau est prêt, le jeu commence. S'il vous montre, c'est à votre tour de commencer en plaçant une de vos
pièces (cubes) sur la grille. Une fois que vous avez joué, Reachy va analyser le plateau en baissant la tête, il lui
faut un peu de temps pour tout détecter, mais une fois que c'est bon, il va prendre sa pièce et jouer à son tour. Et
ainsi de suite jusqu'à ce que quelqu'un gagne.

Lorsqu'une partie est terminée, le robot se remet en mode navigation, il vous faudra relever la main pour jouer une nouvelle partie de tictactoe. Ainsi, à la fin d'une partie, nettoyez le plateau en rangeant les pièces dans les filets et une nouvelle partie pourra être rejouée.








