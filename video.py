import cv2
from ultralytics import YOLO
import numpy as np
import os

def process_video(input_video_path, output_video_path, model_path, conf=0.1):
    # Load the model
    model = YOLO(model_path)

    # Define colors for each category (in BGR format)
    colors = {
        'Tweezers': (0, 255, 0),   # Green
        'Needle_driver': (0, 0, 255)  # Red
    }

    # Open the video file
    cap = cv2.VideoCapture(input_video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # Define the codec and create VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_video_path, fourcc, fps, (width, height))

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Perform segmentation on the frame
        results = model(frame, conf=conf)

        # Process results
        for result in results:
            masks = result.masks
            boxes = result.boxes

            if masks is not None:
                for i in range(len(masks)):
                    mask = masks.data[i].cpu().numpy().astype(bool)
                    class_id = int(boxes[i].cls)
                    confidence = boxes[i].conf
                    category = model.names[class_id]

                    # Resize the mask to match the frame dimensions
                    resized_mask = cv2.resize(mask.astype(np.uint8), (width, height), interpolation=cv2.INTER_NEAREST)
                    resized_mask = resized_mask.astype(bool)

                    # Create a color mask with the same shape as the frame
                    color_mask = np.zeros_like(frame)
                    color_mask[resized_mask] = colors.get(category, (255, 255, 255))

                    # Combine the color mask with the original frame
                    frame = cv2.addWeighted(frame, 1, color_mask, 0.5, 0)

                    # Get the bounding box coordinates for placing the label
                    box = boxes[i].xyxy.cpu().numpy()[0]
                    x1, y1, x2, y2 = map(int, box)

                    # Draw the bounding box on the frame
                    cv2.rectangle(frame, (x1, y1), (x2, y2), colors.get(category, (255, 255, 255)), 2)

                    # Prepare label with category and confidence score
                    label = f"{category} {confidence.item():.2f}"

                    # Draw the label with confidence score on the frame
                    cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, colors.get(category, (255, 255, 255)), 2)

        # Write the processed frame to the output video
        out.write(frame)

    # Release resources
    cap.release()
    out.release()
    cv2.destroyAllWindows()

def main():
    # Define paths
    output_dir = 'output_videos/' #change with your desired video saving directory
    os.makedirs(output_dir, exist_ok=True)

    input_video_path = 'shorter_test_video.mp4' #replace with the video path from your environment
    output_video_path = os.path.join(output_dir, 'test2_output_video_20_epochs_fine_tune_backgrounds.mp4')
    model_path = 'yolov8_20_epochs_fine_tune.pt' #load model

    # Process video
    process_video(input_video_path, output_video_path, model_path)

if __name__ == "__main__":
    main()
