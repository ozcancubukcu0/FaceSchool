import face_recognition
import cv2
import os
import glob
import numpy as np


class YüzTani:
    def __init__(self):
        self.yüz_kodlama = []
        self.yüz_adi = []

        self.cerceveboyut = 0.25

    def resim_yukleme(self, resim_yolu):
        """
        Load encoding images from path
        :param images_path:
        :return:
        """
        resim_yolu = glob.glob(os.path.join(resim_yolu, "*.*"))

        print("Bulunan {} resim taranıyor".format(len(resim_yolu)))

        for resim in resim_yolu:
            img = cv2.imread(resim)
            rgb_resim = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

            basename = os.path.basename(resim)
            (dosyaadi, ext) = os.path.splitext(basename)

            resim_kodlama = face_recognition.face_encodings(rgb_resim)[0]

            self.yüz_kodlama.append(resim_kodlama)
            self.yüz_adi.append(dosyaadi)
        print("Yüklenen Görüntüleri Kodlama")

    def yüzleri_algıla(self, frame):
        kucuk_cerceve = cv2.resize(
            frame, (0, 0), fx=self.cerceveboyut, fy=self.cerceveboyut)

        rgb_kucuk_cerceve = cv2.cvtColor(kucuk_cerceve, cv2.COLOR_BGR2RGB)
        yüz_location = face_recognition.face_locations(rgb_kucuk_cerceve)
        yüz_encoding = face_recognition.face_encodings(
            rgb_kucuk_cerceve, yüz_location)

        face_names = []
        for yüz_encod in yüz_encoding:

            matches = face_recognition.compare_faces(
                self.yüz_kodlama, yüz_encod)
            name = "Tanimsiz"

            yüz_mesafe = face_recognition.face_distance(
                self.yüz_kodlama, yüz_encod)
            matches_index = np.argmin(yüz_mesafe)
            if matches[matches_index]:
                name = self.yüz_adi[matches_index]
            face_names.append(name)

        yüz_location = np.array(yüz_location)
        yüz_location = yüz_location / self.cerceveboyut
        return yüz_location.astype(int), face_names
