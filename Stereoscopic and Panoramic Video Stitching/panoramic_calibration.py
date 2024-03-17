import cv2
import numpy as np
import glob

class CameraCalibration:
    def __init__(self, satir_sayisi, sutun_sayisi, tahta_boyutu):
        self.satir_sayisi = satir_sayisi
        self.sutun_sayisi = sutun_sayisi
        self.tahta_boyutu = tahta_boyutu
        self.dunyadan_koordinatlar = np.zeros((satir_sayisi * sutun_sayisi, 3), np.float32)
        self.dunyadan_koordinatlar[:, :2] = np.mgrid[0:sutun_sayisi, 0:satir_sayisi].T.reshape(-1, 2)
        self.dunyadan_koordinatlar *= tahta_boyutu

    def calibrate_camera(self, resim_dosyalari):
        dunyadan_koordinatlar_listesi = []
        goruntu_koordinatlar_listesi = []

        for dosya_adı in resim_dosyalari:
            goruntu = cv2.imread(dosya_adı)
            gri_goruntu = cv2.cvtColor(goruntu, cv2.COLOR_BGR2GRAY)

            # Satranç tahtası köşelerini bul
            ret, koseler = cv2.findChessboardCorners(gri_goruntu, (self.sutun_sayisi, self.satir_sayisi), None)

            # Eğer köşeler bulunursa
            if ret:
                dunyadan_koordinatlar_listesi.append(self.dunyadan_koordinatlar)
                cv2.cornerSubPix(gri_goruntu, koseler, (11, 11), (-1, -1), (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001))
                goruntu_koordinatlar_listesi.append(koseler)

                # Köşeleri çiz
                img = cv2.drawChessboardCorners(goruntu, (self.sutun_sayisi, self.satir_sayisi), koseler, ret)
                cv2.imshow('Detected Corners', img)
                cv2.waitKey(500)  # Köşelerin gösterilme süresi (ms)

        cv2.destroyAllWindows()

        # Kamera kalibrasyonunu yap
        ret, kamera_matrisi, dist_katsayilari, rotasyonlar, translasyonlar = cv2.calibrateCamera(dunyadan_koordinatlar_listesi, goruntu_koordinatlar_listesi, gri_goruntu.shape[::-1], None, None)
        return ret, kamera_matrisi, dist_katsayilari

    def save_calibration_data(self, dosya_adı, ret, kamera_matrisi, dist_katsayilari):
        np.savez(dosya_adı, ret=ret, kamera_matrisi=kamera_matrisi, dist_katsayilari=dist_katsayilari)

# Satranç tahtası için satır ve sütun sayısı
satir_sayisi = 6
sutun_sayisi = 9
tahta_boyutu = 0.015  # Satranç tahtası mesafesi

# Resim dosyalarını oku
resim_dosyalari = glob.glob('*.jpg')

# Kamera kalibrasyonunu yap
calibration = CameraCalibration(satir_sayisi, sutun_sayisi, tahta_boyutu)
ret1, kamera_matrisi1, dist_katsayilari1 = calibration.calibrate_camera(resim_dosyalari)

# İkinci kamera için aynı işlemleri yap
ret2, kamera_matrisi2, dist_katsayilari2 = calibration.calibrate_camera(resim_dosyalari)

# Verileri dosyaya yaz
calibration.save_calibration_data("kamera_kalibrasyon_verileri.npz", ret1, kamera_matrisi1, dist_katsayilari1)
calibration.save_calibration_data("kamera_kalibrasyon_verileri_2.npz", ret2, kamera_matrisi2, dist_katsayilari2)

print("Kamera 1 Kalibrasyon Sonucu:")
print("Başarı:", ret1)
print("Kamera Matrisi:")
print(kamera_matrisi1)
print("Distorsiyon Katsayıları:")
print(dist_katsayilari1)
print("\nKamera 2 Kalibrasyon Sonucu:")
print("Başarı:", ret2)
print("Kamera Matrisi:")
print(kamera_matrisi2)
print("Distorsiyon Katsayıları:")
print(dist_katsayilari2)