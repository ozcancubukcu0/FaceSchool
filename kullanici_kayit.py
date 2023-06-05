import PySimpleGUI as sg
import sqlite3
arayüz = [
    [sg.Text("TC Kimlik no :  "), sg.Input(key='tc')],
    [sg.Text("Ad :                  "), sg.Input(key="ad")],
    [sg.Text("Soyad :            "), sg.Input(key="soyad")],
    [sg.Text("Bölüm :            "), sg.Input(key="bolum")],
    [sg.Text("E-Posta :         "), sg.Input(key='email',
                                             default_text='@beykent.edu.tr')],
    [sg.Text("Şifre :              "), sg.Input(key='sifre')],
    [sg.Text("Kullanıcı Rol"), sg.Radio('Yönetici', 'rol', key='yonetici'),
     sg.Radio('Öğretmen', 'rol', key='ogretmen')],
    [sg.Button('Kaydet')]
]

window = sg.Window("Kullanıcı Kayıt", arayüz, size=(500, 200))

while True:
    event, values = window.read()
    if event == sg.WINDOW_CLOSED:
        break
    elif event == "Kaydet":
        tc = values["tc"]
        email = values["email"]
        sifre = values["sifre"]
        ad = values["ad"]
        soyad = values["soyad"]
        bolum = values["bolum"]
        if values["yonetici"]:
            rol = "Yönetici"
        else:
            rol = "Öğretmen"

        if len(tc) != 11:
            sg.popup("Hatalı TC girişi")
        elif sifre != tc:
            sg.popup("Hatalı şifre girişi", title="Başarısız")
        else:
            db_connection = sqlite3.connect('veritabanı.db')
            cursor = db_connection.cursor()

            insert_query = "INSERT INTO kullanici (tc, ad, soyad,bolum,email,sifre,rol) VALUES (?, ?, ?, ?, ?, ?, ?)"
            cursor.execute(insert_query, (tc, ad, soyad,
                           bolum, email, sifre, rol))

            db_connection.commit()
            db_connection.close()

        window["tc"].update("")
        window["email"].update("")
        window["sifre"].update("")
        window["ad"].update("")
        window["soyad"].update("")
        window["bolum"].update("")
        window["yonetici"].update(False)
        window["ogretmen"].update(False)

window.close()
