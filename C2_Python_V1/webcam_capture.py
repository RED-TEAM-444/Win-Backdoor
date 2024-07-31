import cv2
import os

def capture_webcam(output_file, camera_index=0, max_attempts=10):
    cap = None

    # Try to open the specified camera index first
    print(f"Trying to open camera at index {camera_index}")
    cap = cv2.VideoCapture(camera_index)
    if not cap.isOpened():
        print(f"Failed to open camera at index {camera_index}. Trying other indices.")

        # Try other camera indices if the specified index fails
        for i in range(max_attempts):
            if i == camera_index:
                continue
            print(f"Trying to open camera at index {i}")
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                print(f"Successfully opened camera at index {i}")
                break
            cap.release()
        else:
            print("No available cameras found.")
            return False

    ret, frame = cap.read()
    if ret:
        output_path = os.path.join("recordings", output_file)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)  # Ensure directory exists
        cv2.imwrite(output_path, frame)
        cap.release()
        print(f"Image saved at {output_path}")
        return output_path
    else:
        print("Failed to capture image from webcam")
        cap.release()
        return False
