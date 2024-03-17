import cv2
import numpy as np

class CameraStitcher:
    def __init__(self, camera_index1=0, camera_index2=1, calibration_file1="kamera_kalibrasyon_verileri.npz",
                 calibration_file2="kamera_kalibrasyon_verileri_2.npz"):
        self.camera_index1 = camera_index1
        self.camera_index2 = camera_index2
        self.calibration_file1 = calibration_file1
        self.calibration_file2 = calibration_file2
        self.load_calibration_data()  # Load calibration data
        self.stitcher = cv2.Stitcher_create()  # Create Stitcher object
        self.cap1 = cv2.VideoCapture(self.camera_index1)
        self.cap2 = cv2.VideoCapture(self.camera_index2)

    def load_calibration_data(self):
        calibration_data1 = np.load(self.calibration_file1)
        self.camera_matrix1 = calibration_data1["kamera_matrisi"]  # Calibration matrix for Camera 1
        self.dist_coefficients1 = calibration_data1["dist_katsayilari"]  # Distortion coefficients for Camera 1

        calibration_data2 = np.load(self.calibration_file2)
        self.camera_matrix2 = calibration_data2["kamera_matrisi"]  # Calibration matrix for Camera 2
        self.dist_coefficients2 = calibration_data2["dist_katsayilari"]  # Distortion coefficients for Camera 2

    def stitch_frames(self):
        ret1, frame1 = self.cap1.read()
        ret2, frame2 = self.cap2.read()

        if ret1 and ret2:
            # Pre-process the images
            preprocessed_frame1 = self.preprocess_frame(frame1)
            preprocessed_frame2 = self.preprocess_frame(frame2)

            # Perform stitching
            status, stitched_frame = self.stitcher.stitch((preprocessed_frame1, preprocessed_frame2))

            if status == cv2.Stitcher_OK:
                return stitched_frame
            else:
                print("Stitching failed.")
                return None
        else:
            print("Could not retrieve images from cameras.")
            return None

    def preprocess_frame(self, frame):
        # Apply CLAHE to enhance contrast directly to each channel
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced_frame = cv2.merge([clahe.apply(frame[:, :, i]) for i in range(frame.shape[-1])])

        return enhanced_frame


# Create the CameraStitcher object
camera_stitcher = CameraStitcher()

cv2.namedWindow("Stitched Frame", cv2.WINDOW_NORMAL)  # Allow window resizing
cv2.resizeWindow("Stitched Frame", 1280, 720)  # Set the window size

# Infinite loop to capture, correct, and stitch images from cameras
while True:
    stitched_frame = camera_stitcher.stitch_frames()

    if stitched_frame is not None:
        # Display the stitched frame
        cv2.imshow("Stitched Frame", stitched_frame)

    # Check for key presses
    key = cv2.waitKey(1)
    if key == ord("q"):  # Exit on 'q' press
        break

# Close the window
cv2.destroyAllWindows()
