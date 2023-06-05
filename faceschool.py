from flask import Flask, render_template, request, redirect, url_for, Response, jsonify
import sqlite3
import os
import cv2
from Yuz_tani import YüzTani
from datetime import datetime
from datetime import date


app = Flask(__name__)


def get_db_connection():
    conn = sqlite3.connect('veritabanı.db')
    conn.row_factory = sqlite3.Row
    return conn

# --------------------------------------------------------------------------------------


@app.route('/')
def giris_sayfasi():
    return render_template('kullanici_giris.html')


@app.route('/giris', methods=['POST'])
def giris():
    email = request.form['email']
    sifre = request.form['sifre']

    conn = sqlite3.connect('veritabanı.db')
    cursor = conn.cursor()

    query = "SELECT rol FROM kullanici WHERE email = ? AND sifre = ?"
    cursor.execute(query, (email, sifre))
    result = cursor.fetchone()

    if result is not None:
        rol = result[0]

        if rol == "Öğretmen":
            return redirect('/ogretmenana')
        elif rol == "Yönetici":
            return redirect('/yoneticiana')

    return "E-posta veya şifre hatalı!"

# öğretmen ana sayfası


@app.route('/ogretmenana', methods=['GET', 'POST'])
def ogretmen_ana():
    if request.method == 'POST':
        return render_template('ogretmen_sayfa.html', secim=request.form['secim'])
    return render_template('ogretmen_sayfa.html')


@app.route('/ogretmenislem', methods=['GET', 'POST'])
def ogretmenislem():
    istek = request.form.get('istek')
    if istek == 'ogrenciler':
        return redirect(url_for('ogrencilistele'))
    elif istek == 'yoklama':
        return redirect(url_for('ders_secimi'))
    elif istek == 'yoklamasonuc':
        return redirect(url_for('analiz'))
    else:
        return "İşlem seçilmedi"

# Yönetici ana sayfası


@app.route('/yoneticiana', methods=['GET', 'POST'])
def yoneticiana():
    if request.method == 'POST':
        return render_template('islem.html', secim=request.form['secim'])
    return render_template('islem.html')


@app.route('/yoneticiislem', methods=['GET', 'POST'])
def yoneticiislem():
    secim = request.form.get('secim')
    if secim == 'dersis':
        return redirect(url_for('dersislemleri'))
    elif secim == 'ogrenciis':
        return redirect(url_for('ogrenciisler'))
    else:
        return "İşlem seçilmedi"

# öğrenci işlemleri sayfası


@app.route('/ogrenciisler', methods=['GET', 'POST'])
def ogrenciisler():
    if request.method == 'POST':
        return render_template('ogrenci_islem.html', secim=request.form['secim'])
    return render_template('ogrenci_islem.html')


@app.route('/ogrenci_islemleri', methods=['GET', 'POST'])
def ogrenci_islemleri():
    istek = request.form.get('istek')
    if istek == 'ogrenciekle':
        return redirect(url_for('home'))
    elif istek == 'derskayit':
        return redirect(url_for('kayit_ekle'))
    elif istek == 'ogrencigor':
        return redirect(url_for('ogrenci_gor'))
    else:
        return "İşlem seçilmedi"

# ders ve bölüm işlemleri


@app.route('/dersislemleri')
def dersislemleri():
    if request.method == 'POST':
        return render_template('ders_islem.html', secim=request.form['secim'])
    return render_template('ders_islem.html')


@app.route('/dersislem', methods=['GET', 'POST'])
def dersislem():
    istek = request.form.get('istek')
    if istek == 'bolumekle':
        return redirect(url_for('bolum_ekle'))
    elif istek == 'dersekle':
        return redirect(url_for('ders_ekle'))
    else:
        return "İşlem seçilmedi"


# hangi tarihde hangi öğrenciler gelmiş

@app.route('/analiz', methods=['GET', 'POST'])
def analiz():
    if request.method == 'POST':
        ders = request.form.get('ders')
        tarih = request.form.get('tarih')

        conn = sqlite3.connect('veritabanı.db')
        cursor = conn.cursor()

        if ders and tarih:
            cursor.execute(
                '''SELECT ad, tarih, saat FROM yoklama WHERE ders_ad = ? AND tarih = ?''', (ders, tarih))
        elif ders:
            cursor.execute(
                '''SELECT ad, tarih, saat FROM yoklama WHERE ders_ad = ?''', (ders,))
        elif tarih:
            cursor.execute(
                '''SELECT ad, tarih, saat FROM yoklama WHERE tarih = ?''', (tarih,))
        else:
            cursor.execute('''SELECT ad, tarih, saat FROM yoklama''')

        veriler = cursor.fetchall()
        conn.close()

        if veriler:
            ogrenci_sayisi = len(veriler)
            return render_template('sonuc.html', ders=ders, tarih=tarih, ogrenci_sayisi=ogrenci_sayisi, veriler=veriler)
        else:
            hata_mesaji = 'Yoklama listesinde öğrenci bulunamadı'
            conn = sqlite3.connect('veritabanı.db')
            cursor = conn.cursor()
            cursor.execute('''SELECT DISTINCT ders_ad FROM yoklama''')
            dersler = cursor.fetchall()

            cursor.execute('''SELECT DISTINCT tarih FROM yoklama''')
            tarihler = cursor.fetchall()

            conn.close()

            return render_template('analiz.html', dersler=dersler, tarihler=tarihler, hata_mesaji=hata_mesaji)

    conn = sqlite3.connect('veritabanı.db')
    cursor = conn.cursor()
    cursor.execute('''SELECT DISTINCT ders_ad FROM yoklama''')
    dersler = cursor.fetchall()

    cursor.execute('''SELECT DISTINCT tarih FROM yoklama''')
    tarihler = cursor.fetchall()

    conn.close()

    return render_template('analiz.html', dersler=dersler, tarihler=tarihler, hata_mesaji=None)

# Bölüm ekleme sayfası


@app.route('/bolumekle', methods=['GET', 'POST'])
def bolum_ekle():
    if request.method == 'POST':
        bolum_yerleske = request.form['yerleske']
        bolum_ad = request.form['bolum_ad']
        bolum_kod = request.form['bolum_kod']
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO bolum (yerleske, bolum_ad, bolum_kod) VALUES (?, ?, ?)',
                       (bolum_yerleske, bolum_ad, bolum_kod))
        conn.commit()
        conn.close()

    return render_template('bolum_ekle.html')


# Ders ekleme sayfası

@app.route('/dersekle', methods=['GET', 'POST'])
def ders_ekle():
    if request.method == 'POST':
        ders_ad = request.form['ders_ad']
        ders_kod = request.form['ders_kod']
        bolum_ad = request.form['bolum_ad']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM bolum WHERE bolum_ad = ?', (bolum_ad,))
        bolum = cursor.fetchone()

        if bolum:
            bolum_id = bolum['id']
            cursor.execute(
                'INSERT INTO ders (ders_ad, ders_kod, bolum_id) VALUES (?, ?, ?)', (ders_ad, ders_kod, bolum_id))
            conn.commit()
            conn.close()
        conn.close()

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT bolum_ad FROM bolum')
    bolumler = cursor.fetchall()
    conn.close()

    return render_template('ders_ekle.html', bolumler=bolumler)


# öğrenci ekleme sayfası
app.config['UPLOAD_FOLDER'] = 'images'


@app.route('/ogrencikayit')
def home():
    # Bölüm adlarını veritabanından al
    db_connection = sqlite3.connect('veritabanı.db')
    cursor = db_connection.cursor()
    select_query = "SELECT bolum_ad FROM bolum"
    cursor.execute(select_query)
    bolumler = cursor.fetchall()
    db_connection.close()

    return render_template('ogrenci_ekle.html', bolumler=bolumler)


# Öğrenci ekleme
@app.route('/add_student', methods=['POST'])
def ogrenci_ekle():
    ad = request.form['ad']
    soyad = request.form['soyad']
    numara = request.form['numara']
    bolum = request.form['bolum']
    tc = request.form['tc']

    foto = request.files.get('foto')

    db_connection = sqlite3.connect('veritabanı.db')
    cursor = db_connection.cursor()

    # Fotoğrafın veritabanında zaten var olup olmadığını kontrol et
    select_query = "SELECT foto FROM ogrenciler WHERE ad = ? AND soyad = ? AND numara = ?"
    cursor.execute(select_query, (ad, soyad, numara))
    existing_student = cursor.fetchone()

    if existing_student:
        return "Öğrenci zaten kayıtlı, öğrenci kaydedilmedi."

    # Fotoğrafın yolu kaydet
    foto_path = os.path.join(app.config['UPLOAD_FOLDER'], foto.filename)
    foto.save(foto_path)

    insert_query = "INSERT INTO ogrenciler (tc, ad, soyad, numara, bolum, foto) VALUES (?, ?, ?, ?, ?,?)"
    cursor.execute(insert_query, (tc, ad, soyad, numara, bolum, foto_path))

    db_connection.commit()
    db_connection.close()

    message = f' {ad} {soyad} {numara} Öğrenci {bolum} bölümüne başarıyla eklendi.'
    return render_template('ogrenci_ekle.html', message=message)


# yüz tanıma
yzt = YüzTani()
yzt.resim_yukleme("images/")

kamera_aktif = False
kamera = None
yzt = None
selected_ders = ""


def ogrenci_kaydet(ad, soyad, ders_ad):
    tarih = datetime.now().strftime('%Y-%m-%d')
    saat = datetime.now().strftime('%H:%M:%S')

    try:
        conn = sqlite3.connect('veritabanı.db')
        cursor = conn.cursor()

        # Kişinin daha önce kaydedilip kaydedilmediğini kontrol et
        cursor.execute(
            "SELECT * FROM yoklama WHERE ad = ? AND soyad = ? AND ders_ad = ?",
            (ad, soyad, ders_ad))
        existing_row = cursor.fetchone()

        if existing_row is None:
            cursor.execute(
                "INSERT INTO yoklama (ad, soyad, ders_ad, tarih, saat) VALUES (?, ?, ?, ?, ?)",
                (ad, soyad, ders_ad, tarih, saat))
            conn.commit()
            print("Öğrenci kaydedildi.")

        cursor.close()
        conn.close()
    except sqlite3.Error as error:
        print("Veritabanı hatası:", error)


def generate_frames():
    global cap
    cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read()

        yüz_location, face_names = yzt.yüzleri_algıla(frame)
        for yüz_loc, name in zip(yüz_location, face_names):
            y1, x2, y2, x1 = yüz_loc[0], yüz_loc[1], yüz_loc[2], yüz_loc[3]

            if name != "Tanimsiz":
                cv2.putText(frame, name, (x1, y1 - 10),
                            cv2.FONT_HERSHEY_DUPLEX, 1, (0, 200, 0), 2)
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 200, 0), 4)
                # Yüzü tanınan öğrenciyi yoklama tablosuna kaydetme
                ogrenci_kaydet(name, "", selected_ders)
            else:
                cv2.putText(frame, name, (x1, y1 - 10),
                            cv2.FONT_HERSHEY_DUPLEX, 1, (0, 0, 200), 2)
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 200), 4)

        ret, jpeg = cv2.imencode('.jpg', frame)
        frame = jpeg.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')


@app.route('/ders_secimi', methods=['GET', 'POST'])
def ders_secimi():
    global selected_ders

    if request.method == 'POST':
        selected_ders = request.form['ders']
        return redirect('/yoklama_al')
    else:
        return render_template('index.html', dersler=get_dersler(), selected_ders=selected_ders)


@app.route('/yoklama_al')
def yoklama_al():
    global kamera_aktif, kamera, yzt, selected_ders
    kamera_aktif = True
    kamera = cv2.VideoCapture(0)
    yzt = YüzTani()
    yzt.resim_yukleme("images/")
    return render_template('yoklama_al.html', selected_ders=selected_ders)


@app.route('/kamera_kapat', methods=['POST'])
def kamera_kapat():
    global kamera_aktif, kamera

    kamera_aktif = False
    kamera.release()

    return redirect('/ogretmenana')


@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/shutdown', methods=['POST'])
def shutdown():
    global cap
    cap.release()
    return 'Shutting down...'


def get_dersler():
    conn = sqlite3.connect('veritabanı.db')
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT ders_ad FROM ders")
    dersler = [row[0] for row in cursor.fetchall()]
    cursor.close()
    conn.close()
    return dersler


# öğrencileri derslere kayıt etme
def get_db_connection():
    conn = sqlite3.connect('veritabanı.db')
    conn.row_factory = sqlite3.Row
    return conn

# Öğrencileri derslere kayıt etme


@app.route('/derslerekayit', methods=['GET', 'POST'])
def kayit_ekle():
    if request.method == 'POST':
        ogrenci_id = request.form['ogrenci']
        ders_id = request.form['ders']

        # Veritabanına öğrenciyi ve dersi kaydet
        conn = get_db_connection()
        cursor = conn.cursor()

        # Öğrenci adı, soyadı, numarası, ders adı ve ders kodunu sorgudan al
        cursor.execute("""
            INSERT INTO kayitlar (ogrenci_id, ders_id, ad, soyad, numara,ders_ad, ders_kod)
            SELECT ogrenciler.id, ders.id, ogrenciler.ad, ogrenciler.soyad, ogrenciler.numara, ders.ders_ad, ders.ders_kod
            FROM ogrenciler, ders
            WHERE ogrenciler.id = ? AND ders.id = ?
        """, (ogrenci_id, ders_id))

        conn.commit()
        conn.close()

    # Öğrencileri ve dersleri veritabanından al
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, ad, soyad, numara FROM ogrenciler")
    ogrenciler = cursor.fetchall()
    cursor.execute("SELECT id, ders_ad, ders_kod FROM ders")
    dersler = cursor.fetchall()
    conn.close()

    return render_template('kayit_ekle.html', ogrenciler=ogrenciler, dersler=dersler)


# hangi derslerde hangi öğrencilerin kayıt olduğunu görme
@app.route('/ogrencilerigor', methods=['GET', 'POST'])
def ogrenci_gor():
    if request.method == 'POST':
        secilen_ders = request.form.get('ders_ad')

        # Veritabanından seçilen ders ile ilişkili kayıtlı öğrencileri çekme
        db_connection = sqlite3.connect('veritabanı.db')
        cursor = db_connection.cursor()
        cursor.execute(
            "SELECT ad, soyad, numara FROM kayitlar WHERE ders_ad = ?", (secilen_ders,))
        ogrenciler = cursor.fetchall()
        cursor.close()
        return render_template('ogrencileri_gor.html', ogrenciler=ogrenciler, secilen_ders=secilen_ders)
    else:
        # Tüm ders adlarını veritabanından çekme
        db_connection = sqlite3.connect('veritabanı.db')
        cursor = db_connection.cursor()
        cursor.execute("SELECT DISTINCT ders_ad FROM kayitlar")
        dersler = cursor.fetchall()
        cursor.close()
        return render_template('ogrencileri_gor.html', dersler=dersler)


@app.route('/ogrencilistele', methods=['GET', 'POST'])
def ogrencilistele():
    if request.method == 'POST':
        secilen_ders = request.form.get('ders_ad')

        # Veritabanından seçilen ders ile ilişkili kayıtlı öğrencileri çekme
        db_connection = sqlite3.connect('veritabanı.db')
        cursor = db_connection.cursor()
        cursor.execute(
            "SELECT ad, soyad, numara FROM kayitlar WHERE ders_ad = ?", (secilen_ders,))
        ogrenciler = cursor.fetchall()
        cursor.close()
        return render_template('ogrencilerilistele.html', ogrenciler=ogrenciler, secilen_ders=secilen_ders)
    else:
        # Tüm ders adlarını veritabanından çekme
        db_connection = sqlite3.connect('veritabanı.db')
        cursor = db_connection.cursor()
        cursor.execute("SELECT DISTINCT ders_ad FROM kayitlar")
        dersler = cursor.fetchall()
        cursor.close()
        return render_template('ogrencilerilistele.html', dersler=dersler)


if __name__ == '__main__':
    app.run()
