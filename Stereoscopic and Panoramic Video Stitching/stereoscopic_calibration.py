import numpy as np
import cv2
import glob

# Satranç tahtası için taş sayısı
chessboard_size = (9, 6)

# Dünya koordinatları için 3D noktalar
objp = np.zeros((chessboard_size[0] * chessboard_size[1], 3), np.float32)
objp[:, :2] = np.mgrid[0:chessboard_size[0], 0:chessboard_size[1]].T.reshape(-1, 2)

# Depolama dizileri
obj_points = [] # 3D dünya noktaları
img_points = [] # 2D görüntü noktaları

# Kalibrasyon görüntülerini yükle
images = glob.glob('res*.jpg')

for fname in images:
    img = cv2.imread(fname)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Satranç tahtasındaki köşeleri bul
    ret, corners = cv2.findChessboardCorners(gray, chessboard_size, None)

    # Köşeler bulunduysa, depolama dizilerine ekle
    if ret == True:
        obj_points.append(objp)
        img_points.append(corners)

        # Köşeleri çiz
        img = cv2.drawChessboardCorners(img, chessboard_size, corners, ret)
        cv2.imshow('img', img)
        cv2.waitKey(500)

cv2.destroyAllWindows()

# Kamera kalibrasyonunu yap
ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(obj_points, img_points, gray.shape[::-1], None, None)

# Kalibrasyon sonucunu kaydet
np.save("camera_matrix.npy", mtx)
np.save("distortion_coefficients.npy", dist)

print("Kamera matrisi:")
print(mtx)
print("\nDüzeltme katsayıları:")
print(dist)