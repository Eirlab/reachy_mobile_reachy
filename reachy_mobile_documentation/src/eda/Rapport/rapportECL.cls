\LoadClass[a4paper,12pt]{article} % Classe du document

% Configuration de la page

\usepackage{sectsty}
\usepackage{xcolor}
\usepackage{lipsum} 

% On définit les deux couleurs utilisées
\definecolor{couleur_section}{RGB}{0,0,160}%Partie
\definecolor{couleur_subsection}{RGB}{0,128,255}

% On personnalise chacun des titres à l'aide des commandes "sectionfont", "subsectionfont", etc.
\sectionfont{\color{couleur_section}}
\subsectionfont{\color{couleur_subsection}}
\subsubsectionfont{\itshape}
% -------------------- Informations sur le rapport ----------------------

\newcommand{\UE}[1]{\renewcommand{\UE}{#1}}
\newcommand{\DateduRapport}[1]{\renewcommand{\DateduRapport}{#1}}
\newcommand{\sujet}[1]{\renewcommand{\sujet}{#1}}
\newcommand{\titre}[1]{\renewcommand{\titre}{#1}}
\newcommand{\client}[1]{\renewcommand{\client}{#1}}
\newcommand{\encadrant}[1]{\renewcommand{\encadrant}{#1}}
\newcommand{\professeur}[1]{\renewcommand{\professeur}{#1}}
\newcommand{\eleves}[1]{\renewcommand{\eleves}{#1}}
\newcommand{\resume}[1]{\renewcommand{\resume}{#1}}

\newcommand{\fairemarges}{
  \makenomenclature
  \pagestyle{fancy}
  \cfoot{}
  \fancyheadoffset{1cm}
  \lhead{État de l'art projet robotique} %Affichage de l'image au top de la page
  \rhead{\nouppercase{\leftmark}}
  \chead{Reachy Mobile}
  \rfoot{\thepage}
}

\newcommand{\fairepagedegarde}{
  \begin{titlepage}
    \ThisLRCornerWallPaper{0.6}{logos/logo_background.png}
    \centering %Centraliser le contenu
    \includegraphics[width=0.8\textwidth]{logos/logo.png}\par\vspace{0.5 cm} %Insertion du logo
    {\scshape\Large \UE \\ \sujet \\ Troisième Année Option Robotique\par} %sous-titre
    \vspace{0.5cm}%Espace de 1cm
    \rule{\linewidth}{0.2 mm} \\[0.4 cm]
    {\huge\bfseries \titre \par} \
    \rule{\linewidth}{0.2 mm} \\[0.5 cm]
    \vspace{0.5cm}%Espace de 0.5cm
    \begin{minipage}{0.5\textwidth} %Minipage pour faire deux colonnes
      \begin{flushleft} \large %Envoyer à gauche
        \emph{\textbf{Élèves :}} \\ %Pour le titre au dessus des noms à gauche
        \eleves %Remplacer pour chacun
      \end{flushleft}
    \end{minipage}
    ~
    \begin{minipage}{0.45\textwidth}
      \begin{flushright} \large
        \emph{\textbf{Client :}} \\
        \client \\
        \vspace{0.5cm}
        \emph{\textbf{Encadrant :}} \\
        \encadrant \\
        \vspace{0.5cm}
        \emph{\textbf{Professeur :}} \\
        \professeur
      \end{flushright}
    \end{minipage}\\[1cm]
    % \begin{minipage}{1 \textwidth}
    %   \begin{flushleft}
    %         \resume
    %   \end{flushleft}
    % \end{minipage}\\[0.5cm]
    \vfill
    {\large \DateduRapport\par} %Affichage de la date
  \end{titlepage}
}

\newcommand{\tabledematieres}{

  \tableofcontents
  \newpage

}

\newcommand{\insererfigure}[4]{
  \begin{figure}[ht]
    \centering
    \includegraphics[height=#2]{#1}
    \caption{#3}
    \label{fig: #4}
  \end{figure}
}
