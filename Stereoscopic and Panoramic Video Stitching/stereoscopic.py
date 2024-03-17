import cv2
import numpy as np
import imutils
import os


class VideoStitcher:
    def __init__(self, video_out_width=800, display=True, auto_load_homo=True,
                 homo_matrix_filename="homography.npy",
                 camera_matrix_filename="camera_matrix.npy",
                 distortion_coefficients_filename="distortion_coefficients.npy"):
        self.video_out_width = video_out_width
        self.display = display
        self.homo_matrix_filename = homo_matrix_filename
        self.camera_matrix_filename = camera_matrix_filename
        self.distortion_coefficients_filename = distortion_coefficients_filename

        self.saved_homo_matrix = None
        self.camera_matrix = None
        self.dist_coefficients = None

        if auto_load_homo:
            self.load_homography()
            self.load_camera_calibration()

    def load_camera_calibration(self):
        if os.path.exists(self.camera_matrix_filename) and os.path.exists(self.distortion_coefficients_filename):
            self.camera_matrix = np.load(self.camera_matrix_filename)
            self.dist_coefficients = np.load(self.distortion_coefficients_filename)
            print("[INFO]: Camera calibration matrices loaded.")
        else:
            print("[ERROR]: Camera calibration files do not exist.")

    def load_homography(self):
        if os.path.exists(self.homo_matrix_filename):
            self.saved_homo_matrix = np.load(self.homo_matrix_filename)
            print(f"[INFO]: Homography matrix loaded from {self.homo_matrix_filename}")
        else:
            print("[INFO]: Homography matrix file does not exist")

    def detect_and_extract(self, image):
        # Convert the image to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        # Use ORB to detect and extract features
        orb = cv2.ORB_create()
        # Find the keypoints and descriptors with ORB
        keypoints, descriptors = orb.detectAndCompute(gray, None)
        return keypoints, descriptors

    def match_keypoints(self, kpsA, kpsB, featuresA, featuresB, ratio=0.75, reprojThresh=4.0):
        matcher = cv2.DescriptorMatcher_create("BruteForce")
        rawMatches = matcher.knnMatch(featuresA, featuresB, k=2)
        matches = []

        for m in rawMatches:
            if len(m) == 2 and m[0].distance < m[1].distance * ratio:
                matches.append((m[0].trainIdx, m[0].queryIdx))

        if len(matches) >= 4:
            ptsA = np.float32([kpsA[i].pt for (_, i) in matches])
            ptsB = np.float32([kpsB[i].pt for (i, _) in matches])
            (H, status) = cv2.findHomography(ptsA, ptsB, cv2.RANSAC, reprojThresh)
            return (matches, H, status)
        return None

    def stitch(self, images, ratio=0.75, reproj_thresh=4.0):
        (imageB, imageA) = images

        # Eğer daha önce kaydedilmiş bir homografi matrisi yoksa, özellik noktalarını eşleştir ve homografi matrisini hesapla
        if self.saved_homo_matrix is None:
            (kpsA, featuresA) = self.detect_and_extract(imageA)
            (kpsB, featuresB) = self.detect_and_extract(imageB)
            M = self.match_keypoints(kpsA, kpsB, featuresA, featuresB, ratio, reproj_thresh)

            if M is None:
                return None  # Yeterli eşleşme bulunamazsa, None dön
            self.saved_homo_matrix = M[1]  # Homografi matrisini kaydet
            self.save_homography()

        # Perspektif dönüşümü uygula ve sağ taraftaki görüntüyü yerleştir
        result_width = imageA.shape[1] + imageB.shape[1]
        result_height = max(imageA.shape[0], imageB.shape[0])
        result = cv2.warpPerspective(imageA, self.saved_homo_matrix, (result_width, result_height))
        result[0:imageB.shape[0], 0:imageB.shape[1]] = imageB

        # Sonuç görüntüsünü döndür
        return result

    def save_homography(self):
        if self.saved_homo_matrix is not None:
            np.save(self.homo_matrix_filename, self.saved_homo_matrix)
            print(f"[INFO]: Homography matrix saved to {self.homo_matrix_filename}")

    def run(self):
        left_video = cv2.VideoCapture(0)
        right_video = cv2.VideoCapture(1)

        print('[INFO]: Video stitching starting...')

        while True:
            ret1, left_frame = left_video.read()
            ret2, right_frame = right_video.read()

            if not ret1 or not ret2:
                print("[INFO]: No frame is detected. Ending video stitching...")
                break

            left_undistorted = cv2.undistort(left_frame, self.camera_matrix, self.dist_coefficients, None,
                                             self.camera_matrix)
            right_undistorted = cv2.undistort(right_frame, self.camera_matrix, self.dist_coefficients, None,
                                              self.camera_matrix)

            left_resized = imutils.resize(left_undistorted, width=self.video_out_width)
            right_resized = imutils.resize(right_undistorted, width=self.video_out_width)

            stitched = self.stitch([left_resized, right_resized])

            if stitched is None:
                print("[INFO]: Homography could not be computed!")
                break

            if self.display:
                cv2.imshow("Stitched Output", stitched)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

        print("[INFO]: Cleaning up...")
        cv2.destroyAllWindows()
        left_video.release()
        right_video.release()


# Usage
stitcher = VideoStitcher(display=True)
stitcher.run()
