Conclusion
==========

Cet état de l'art avance différentes parties de la construction d'un
cobot de service, plus particulièrement ce document s'attarde sur la
navigation d'un robot, ses interactions avec les humains et le contenu
de ces interactions. Tout d'abord en abordant les problématiques de
modélisation de l'environnement en fonction de nos capteurs et en
présentant un modèle rependu : la modélisation par grille d'occupation
probabiliste. Une fois cette modélisation avancée il est démontré les
différents moyens de planifier une trajectoire dans un environnement
comme une foule. Les algorithmes délibératifs et plus particulièrement
l'algorithme *riskRRT* est présenté pour permettre de naviguer de
manière la plus fiable possible dans un environnement dynamique et
incertain.

Une fois que la navigation est mise en place, un deuxième aspect d'un
cobot de service est abordé : les interractions qu'il doit avoir avec
les humains. Ces interactions sont discutées selon deux axes, d'une part
sur le comportement que doit adopter un cobot en présenter les règles
sociales élémentaires et la théorie proxémique. D'autre part, la
question de la communication entre un robot et une machine est explorée
pour converger vers une conversation non verbale basée sur la détection
de squelette.

Finalement, toujours dans le but des interactions avec l'humain, il est
discuté des techniques de mise en places des différents jeux en
utilisant du *machine learning*. Plus particulièrement les différentes
techniques de *machines learning* sont étudiées pour converger vers des
techniques de *deep learning* permettant de mettre en place ces jeux.

Ces trois axes d'études ne représentent qu'une partie des problèmes
soulevés par la construction d'un cobot de service. Nous n'avons pas
discuté, par exemple, de la taille que le cobot final doit avoir ou sa
réaction attendue en fonction des différents problèmes qu'il va
rencontrer. Comment réagir, par exemple, si un enfant tire sur le bras
du robot fortement ?

En conclusion ce document définit et précise l'existant et les solutions
qui existent pour résoudre des problèmes typiques à la construction d'un
robot de service. Les solutions avancées dans ce document permettront de
résoudre des problèmes majeurs dans la construction de notre robot de
service, mais ne permettront pas à elles seule la construction d'un
robot de service parfait.

<script type="text/javascript" src="https://cdn.mathjax.org/mathjax/latest/MathJax.js?config=TeX-AMS-MML_HTMLorMML"> </script> <script type="text/x-mathjax-config"> MathJax.Hub.Config({ tex2jax: { inlineMath: [['$','$']], displayMath: [['$$','$$']], processEscapes: true, processEnvironments: true, skipTags: ['script', 'noscript', 'style', 'textarea', 'pre'], TeX: { equationNumbers: { autoNumber: "AMS" }, extensions: ["AMSmath.js", "AMSsymbols.js"] } } }); MathJax.Hub.Queue(function() { var all = MathJax.Hub.getAllJax(), i; for(i = 0; i < all.length; i += 1) { all[i].SourceElement().parentNode.className += ' has-jax'; } }); </script>