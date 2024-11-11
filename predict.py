import cv2
from ultralytics import YOLO
import numpy as np


def predict_on_image(image_path, model_path, output_path, conf=0.1):
    # Load the model
    model = YOLO(model_path)

    # Define colors for each category (in BGR format)
    colors = {
        'Tweezers': (0, 255, 0),
        'Needle_driver': (0, 0, 255)
    }

    # Load the image
    image = cv2.imread(image_path)
    if image is None:
        print(f"Error: Could not load image at {image_path}")
        return

    # Perform segmentation on the image
    results = model(image, conf=conf)

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

                # Resize the mask to match the image dimensions
                resized_mask = cv2.resize(mask.astype(np.uint8), (image.shape[1], image.shape[0]),
                                          interpolation=cv2.INTER_NEAREST)
                resized_mask = resized_mask.astype(bool)

                # Create a color mask with the same shape as the image
                color_mask = np.zeros_like(image)
                color_mask[resized_mask] = colors.get(category, (255, 255, 255))

                # Blend the color mask onto the image
                image = cv2.addWeighted(image, 1, color_mask, 0.5, 0)

                # Get the bounding box coordinates
                box = boxes[i].xyxy.cpu().numpy()[0]
                x1, y1, x2, y2 = map(int, box)

                # Draw the bounding box on the image
                cv2.rectangle(image, (x1, y1), (x2, y2), colors.get(category, (255, 255, 255)), 2)

                # Prepare label with category and confidence score
                label = f"{category} {confidence.item():.2f}"

                # Draw the label on the image
                cv2.putText(image, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                            colors.get(category, (255, 255, 255)), 2)

    # Save the processed image
    cv2.imwrite(output_path, image)
    print(f"Processed image saved at {output_path}")


def main():
    # Define paths
    image_path = 'my_path/input_image.jpg'  # Replace with the path to your input image
    model_path = 'yolov8_20_epochs_fine_tune.pt'  # Replace with the path to your YOLO model
    output_path = 'my_path/output_image.jpg'  # Replace with the desired output path for the processed image

    # Call the prediction function
    predict_on_image(image_path, model_path, output_path,conf=0.5)


if __name__ == "__main__":
    main()
