\documentclass{article}
\usepackage{hyperref}

\begin{document}

\title{Final Project: Computer Vision for Surgical Instruments}
\author{}
\date{}
\maketitle

\section*{Project Overview}
This project involves an image segmentation system for surgical instruments using synthetic data generation and domain adaptation techniques.

\section*{Installation}
To install the required dependencies, run the following command:
\begin{verbatim}
pip install -r requirements.txt
\end{verbatim}

\section*{Videos}
The videos related to the project can be accessed at:  
\href{https://technionmail-my.sharepoint.com/:f:/r/personal/guy_shoef_campus_technion_ac_il/Documents/Final_project_cv_videos?csf=1&web=1&e=v6pDIJ}{Videos Link}

\section*{Synthetic Data}
The synthetic data is located in the directory \texttt{synthetic\_images\_examples}, which includes:
\begin{itemize}
    \item Original images
    \item Segmentation masks
    \item Images with masks overlaid
\end{itemize}

\section*{Data Generation}
The following directories and scripts are used for generating synthetic data:
\begin{itemize}
    \item \texttt{render\_on\_hdri}
    \begin{itemize}
        \item \texttt{synthetic\_data\_generator.py}: Generates synthetic data based on paths specified in \texttt{config.json}.
    \end{itemize}
    \item \texttt{render\_and\_paste}
    \begin{itemize}
        \item \texttt{render\_tools.py}: Creates a single tool with a glove occluding it.
        \item \texttt{render\_tools\_combined.py}: Generates images with two tools and gloves in each frame.
        \item \texttt{paste\_on\_random\_background.py}: Pastes tools onto images from paths specified in \texttt{config.json}.
    \end{itemize}
\end{itemize}

\end{document}











# Final-project-CV
Image segmentation system for surgical instruments using synthetic data generation and domain adaptation techniques.

In order to download the requirements file write in you environment:

pip install -r requirements.txt

Vidoes link:
https://technionmail-my.sharepoint.com/:f:/r/personal/guy_shoef_campus_technion_ac_il/Documents/Final_project_cv_videos?csf=1&web=1&e=v6pDIJ

Synthetic images are in the directory synthetic_images_examples and includes the original images, the segmentation masks and the images with the masks on them.

In render_on_hdri there is synthetic_data_generator.py and the config with the data paths is config.json. because we used more scripts to create data we added them in render_and_paste: render_tools.py is a script that we used to create single tool with a glove that occludes it. render_tools_combined.py we used to create 2 tools and 2 gloves at each frame. finally paste_on_random_background.py is to paste the tools on images from path in config.json  

