# Final-project-CV
Image segmentation system for surgical instruments using synthetic data generation and domain adaptation techniques.

## To install the required dependencies, run the following command:
pip install -r requirements.txt 

## Vidoes link:
https://technionmail-my.sharepoint.com/:f:/r/personal/guy_shoef_campus_technion_ac_il/Documents/Final_project_cv_videos?csf=1&web=1&e=v6pDIJ

## Synthetic images:
Synthetic images are in the directory synthetic_images_examples and includes the original images, the segmentation masks and the images with the masks on them.

## data generators:
In render_on_hdri there is synthetic_data_generator.py and the config with the data paths is config.json. because we used more scripts to create data we added them in render_and_paste: render_tools.py is a script that we used to create single tool with a glove that occludes it. render_tools_combined.py we used to create 2 tools and 2 gloves at each frame. finally paste_on_random_background.py is to paste the tools on images from path in config.json

## additional files:
predict.py - prediction of model on an image
video.py - prediction of the model on a video

## Model before domain adaptation and after weights link:
[Download models weights](https://www.dropbox.com/scl/fo/yvzc8eorsxjang8xxlidy/AIQHsWte6Eq1uU5w92-t4R0?rlkey=jorn72d4pw208stuyp8v4k3cx&st=pyimjh77&dl=0)

