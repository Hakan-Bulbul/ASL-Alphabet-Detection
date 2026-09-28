import cv2 #opencv kütüphanesi
import customtkinter as ctk #arayüz
from PIL import Image, ImageTk #pillow kütüphanesi
from ultralytics import YOLO #yolo modeli
from collections import deque, Counter #kuyruk
import time #zaman
import os #dosya yolları kontrolü için
import sys

#Model Yolu
#MODEL_PATH = "C:/Users/hakan/PycharmProjects2/PythonProject6/runs/detect/train/weights/best.pt"

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

MODEL_PATH = resource_path("best.pt")

class ASLMasterApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("ASL Parmak Alfabesi") #pencere başlığı
        self.geometry("1920x1080") #pencere boyutu
        try:
            self.iconbitmap(resource_path("icon.ico")) #ikon görseli
        except:
            pass

        self.model = YOLO(MODEL_PATH) #eğitilmiş model belleğe yüklenir
        self.alphabet = [ #sistemin tanıyacağı sınıflar
            "A", "B", "C", "D", "E", "F",
            "G", "H", "I", "J", "K", "L",
            "M", "N", "O", "P", "Q", "R",
            "S", "T", "U", "V", "W", "X",
            "Y", "Z", "SPACE", "DEL"
        ]
        self.current_word = "" #oluşturulan kelime
        self.last_added_letter = "" #son eklenen harf
        self.last_add_time = time.time() #harfin eklenme zamanı
        self.is_paused = False #duraklatma kontrolü

        # Ana Konteyner
        self.container = ctk.CTkFrame(self)
        self.container.pack(fill="both", expand=True)

        self.show_main_menu() #açılışta ana menü gösterilir

    def clear_screen(self): #ekran temizleme
        for widget in self.container.winfo_children():
            widget.destroy()

    def show_main_menu(self): #ana ekran oluşturulur
        self.clear_screen()

        self.font_box = ctk.CTkLabel(self.container, text="ASL Parmak Alfabesi",width=500, height=60, font=("Arial", 24, "bold"),fg_color="#1f538d", text_color="white", corner_radius=10) #üst başlık
        self.font_box.place(relx=0.5, rely=0.15, anchor="center")

        btn_yazdir = ctk.CTkButton(self.container, text="KELİME YAZDIRMA",width=220, height=70,font=("Arial", 20, "bold"),fg_color="#2c3e50", hover_color="#211d01", text_color="white", command=self.start_word_building_mode) #kelime yazdırma butonu
        btn_yazdir.place(relx=0.35, rely=0.65, anchor="center") #düzen

        btn_egitim = ctk.CTkButton(self.container, text="EĞİTİM",width=220, height=70,font=("Arial", 20, "bold"),fg_color="#07bc25", hover_color="#047c16", text_color="white", command=self.show_education_menu) #eğitim butonu
        btn_egitim.place(relx=0.65, rely=0.65, anchor="center") #düzen

        #sol bilgilendirme kutusu
        self.left_info_box = ctk.CTkFrame(
            self.container,
            width=260,
            height=350,
            corner_radius=15,
            fg_color="#1f2a38"
        )

        self.left_info_box.place(relx=0.1, rely=0.4, anchor="center")
        self.left_info_box.pack_propagate(False)

        self.left_info_title = ctk.CTkLabel( #sol bilgilendirme kutusu başlık
            self.left_info_box,
            text="Nedir?",
            font=("Arial", 22, "bold"),
            text_color="white"
        )

        self.left_info_title.pack(pady=(20, 15))

        self.left_info_text = ctk.CTkLabel( #sol bilgilendirme kutusu yazı
            self.left_info_box,
            text=
            "• İşitme engelli bireyler genellikle işaret dili ile iletişim kurarlar.\n\n"
            "• İşaret dili; el hareketleri, yüz ifadeleri ve beden diliyle oluşturulan bir dildir.\n\n"
            "• İşaret dilleri, harfleri tek tek göstermek için kullanılan bir parmak alfabesini bünyesinde barındırır.\n\n"
            "• Kelimeler, harf harf ifade edilmek istendiğinde parmak alfabesi kullanılır.",
            justify="left",
            font=("Arial", 14),
            text_color="white",
            wraplength=220
        )

        self.left_info_text.pack(padx=15, pady=10)

        #sağ bilgilendirme kutusu
        self.right_info_box = ctk.CTkFrame(
            self.container,
            width=260,
            height=350,
            corner_radius=15,
            fg_color="#1f2a38"
        )

        self.right_info_box.place(relx=0.9, rely=0.4, anchor="center")
        self.right_info_box.pack_propagate(False)

        self.right_info_title = ctk.CTkLabel( #sağ bilgilendirme kutusu başlık
            self.right_info_box,
            text="Önemi",
            font=("Arial", 22, "bold"),
            text_color="white"
        )

        self.right_info_title.pack(pady=(20, 15))

        self.right_info_text = ctk.CTkLabel( #sağ bilgilendirme kutusu yazı
            self.right_info_box,
            text=
            "• İşitme engelli bireyler, toplumda sık sık kendilerini ifade etme veya anlaşılma sorunu yaşarlar.\n\n"
            "• Parmak alfabesini bizlerin biliyor olması, kelime bazında onları anlayabilmemizi sağlar.\n\n"
            "• Bizler ile onlar arasındaki iletişim köprüsünü kurmamıza olanak tanır. \n\n"
            "• Anlatmak İsteyen Anlaşılmak İster",
            justify="left",
            font=("Arial", 14),
            text_color="white",
            wraplength=220
        )

        self.right_info_text.pack(padx=15, pady=10)

    def setup_camera_ui(self, title_text): #kamera ekranı oluşturulur
        self.cap = cv2.VideoCapture(0) #bilgisayar kamerası açılır
        self.history = deque(maxlen=15) #son 15 tahmin harf saklanır
        self.is_paused = False

        self.info_label = ctk.CTkLabel(self.container, text=title_text, font=("Arial", 22)) #ekran başlığı
        self.info_label.pack(pady=10)

        self.word_display = ctk.CTkLabel(self.container, text="Durum: Hazır", font=("Arial", 25, "bold"), text_color="#3498db") #yazılan kelimeyi gösterir
        self.word_display.pack(pady=5)

        #ANA İÇERİK FRAME
        self.content_frame = ctk.CTkFrame(self.container, fg_color="transparent") #kamera ve görsel alanı
        self.content_frame.pack(fill="both", expand=True, pady=10)

        #KAMERA GÖRÜNTÜSÜ
        self.video_label = ctk.CTkLabel(self.content_frame, text="")
        self.video_label.place(relx=0.5, rely=0.5, anchor="center")

        #HARF GÖRSEL KUTUSU -> SAĞ TARAF
        self.image_frame = ctk.CTkFrame(
            self.content_frame,
            width=400,
            height=400,
            corner_radius=15
        )

        self.image_frame.place(relx=0.88, rely=0.5, anchor="center") #eğitim modu -> örnek harf görseli
        self.image_frame.pack_propagate(False)

        self.sign_image_label = ctk.CTkLabel(self.image_frame, text="")
        self.sign_image_label.pack(expand=True)

        # --- KELİME YAZDIRMA MODU BUTONLARI ---
        if self.mode == "WORD_BUILDER":

            self.ctrl_frame = ctk.CTkFrame(self.container, fg_color="transparent")
            self.ctrl_frame.pack(pady=10)

            self.btn_pause = ctk.CTkButton( #duraklat butonu
                self.ctrl_frame,
                text="DURAKLAT",
                font=("Arial", 14),
                fg_color="#e67e22",
                hover_color="#d35400",
                command=self.toggle_pause
            )
            self.btn_pause.grid(row=0, column=0, padx=10)

            self.btn_start = ctk.CTkButton( #başlat butonu
                self.ctrl_frame,
                text="BAŞLAT",
                font=("Arial", 14),
                fg_color="#27ae60",
                hover_color="#2ecc71",
                command=self.toggle_resume
            )
            self.btn_start.grid(row=0, column=1, padx=10)

            self.btn_manual_del = ctk.CTkButton( #manuel silme butonu
                self.container,
                text="SON HARFİ SİL (MANUEL)",
                font=("Arial", 14),
                fg_color="#c0392b",
                hover_color="#a93226",
                command=self.manual_delete
            )
            self.btn_manual_del.pack(pady=5)

            btn_finish = ctk.CTkButton( #ana menüye dön butonu
                self.container,
                text="ANA MENÜYE DÖN",
                font=("Arial", 14),
                fg_color="#7c0584",
                hover_color="#6a046d",
                command=self.stop_camera
            )
            btn_finish.pack(pady=10)

        # --- EĞİTİM MODU BUTONU ---
        elif self.mode == "EDUCATION":

            btn_back = ctk.CTkButton( #geriye dön butonu
                self.container,
                text="GERİYE DÖN",
                font=("Arial", 14),
                width=200,
                height=45,
                fg_color="#0a07bf",
                hover_color="#0913e2",
                command=self.back_to_education_menu
            )

            btn_back.pack(pady=15)

        self.update_frame() #kamera döngüsü oluşturulur

    def manual_delete(self): #son karakter silinir
        self.current_word = self.current_word[:-1]
        self.word_display.configure(text=f"Kelime: {self.current_word}")

    def toggle_pause(self): #analiz durdurulur
        self.is_paused = True
        self.word_display.configure(text="Durum: DURAKLATILDI", text_color="#e74c3c")

    def toggle_resume(self): #analiz devam ettirilir
        self.is_paused = False
        self.word_display.configure(text="Durum: ÇALIŞIYOR", text_color="#2ecc71")

    def update_frame(self): #ana kamera döngüsü
        ret, frame = self.cap.read() #kameradan görüntü alınır
        if ret:
            results = self.model(frame, verbose=False)
            annotated_frame = results[0].plot()

            if not self.is_paused: #görüntü duraklatılana kadar çalışır
                if len(results[0].boxes) > 0:
                    cls_id = int(results[0].boxes.cls[0])
                    current_prediction = self.model.names[cls_id]
                    self.history.append(current_prediction)

                    most_common = Counter(self.history).most_common(1)[0][0]

                    if self.mode == "WORD_BUILDER":#kelime yazdırma modu - kamera
                        self.handle_word_logic(most_common)

                    elif self.mode == "EDUCATION": #eğitim modu - kamera
                        if most_common.upper() == self.target_letter.upper():
                            self.stop_camera()
                            self.show_success_screen()
                            return
            #
            """#ekrandaki kamera görüntüsü tahmin oranları olmadan gözükür (kaliteli)
            display_frame = getattr(self, 'last_annotated_frame', frame)
            img_rgb = cv2.cvtColor(display_frame, cv2.COLOR_BGR2RGB)
            img_pil = Image.fromarray(img_rgb)
            ctk_img = ctk.CTkImage(light_image=img_pil,dark_image=img_pil,size=(640, 480))
            self.video_label.configure(image=ctk_img)
            self.video_label.image = ctk_img  # Referansı koru"""
            #

            #ekrandaki kamera görüntüsü tahmin oranlarıyla gözükür
            img = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(img)
            img_tk = ImageTk.PhotoImage(image=img)
            self.video_label.img_tk = img_tk
            self.video_label.configure(image=img_tk)
            #
            self.after(10, self.update_frame)

    def start_word_building_mode(self): #kelime yazdırma modu başlatılır
        self.clear_screen()
        self.current_word = ""
        self.mode = "WORD_BUILDER"
        self.setup_camera_ui("Kelime Yazma Modu")

    def handle_word_logic(self, detected_letter):
        if detected_letter == self.last_added_letter:
            if time.time() - self.last_add_time > 2.0: #el hareketi 2 saniye kaldığında kelimeye eklenir
                if detected_letter.lower() == "del":#del(silme) karakteri -> son harfi siler
                    self.current_word = self.current_word[:-1]
                elif detected_letter.lower() == "space": #space(boşluk) karakteri -> boşluk bırakır
                    self.current_word += " "
                elif detected_letter.lower() == "nothing":
                    pass
                else:
                    self.current_word += detected_letter
                self.word_display.configure(text=f"Kelime: {self.current_word}", text_color="#3498db")
                self.last_add_time = time.time()
        else:
            self.last_added_letter = detected_letter
            self.last_add_time = time.time()

    def show_education_menu(self): #eğitim modu - harf seçim ekranı
        self.clear_screen()
        label = ctk.CTkLabel(self.container, text="Eğitim: Bir Harf Seçin", font=("Arial", 20))
        label.pack(pady=20)
        grid_frame = ctk.CTkFrame(self.container)
        grid_frame.pack(pady=10, padx=10)
        for i, char in enumerate(self.alphabet):
            btn = ctk.CTkButton(grid_frame, text=char, width=70, height=70,command=lambda c=char: self.start_education_task(c))
            btn.grid(row=i // 6, column=i % 6, padx=5, pady=5)
        btn_back = ctk.CTkButton(self.container, text="ANA MENÜYE DÖN", font=("Arial",14), fg_color="#7c0584", hover_color="#6a046d", command=self.show_main_menu)
        btn_back.pack(pady=20)

    def load_sign_image(self, letter): #eğitim modu - örnek harf görselleri
        try:
            image_path = resource_path(os.path.join("harf_isaretleri", f"{letter}.jpg"))

            if os.path.exists(image_path):
                img = Image.open(image_path)

                # Görsel boyutu
                img = img.resize((220, 300))

                ctk_img = ctk.CTkImage(
                    light_image=img,
                    dark_image=img,
                    size=(220, 300)
                )

                self.sign_image_label.configure(image=ctk_img, text="")
                self.sign_image_label.image = ctk_img

            else:
                self.sign_image_label.configure(
                    text=f"{letter} Görsel Bulunamadı",
                    image=None
                )

        except Exception as e:
            self.sign_image_label.configure(
                text=f"Hata:\n{e}",
                image=None
            )

    def start_education_task(self, char): #eğitim modu - eğitim başlatılır (seçilen harf hedef seçilir)
        self.clear_screen()
        self.target_letter = char
        self.mode = "EDUCATION"

        self.setup_camera_ui(f"Hedef Harf: {char}")
        self.load_sign_image(char) #harf görseli yüklenir

    def show_success_screen(self): #"tebrikler yazısı"
        self.clear_screen()
        success_label = ctk.CTkLabel(self.container, text=f"TEBRİKLER!\n'{self.target_letter}' Harfini Doğru Yaptınız",text_color="#27ae60", font=("Arial", 30, "bold"))
        success_label.place(relx=0.5, rely=0.5, anchor="center")
        self.after(2000, self.show_education_menu) #"tebrikler" yazısının görünme süresi

    def back_to_education_menu(self): #eğitim modunda geriye dönme
        if hasattr(self, 'cap') and self.cap.isOpened():
            self.cap.release()

        self.show_education_menu()

    def stop_camera(self): #kamera kapatılır
        if hasattr(self, 'cap') and self.cap.isOpened():
            self.cap.release()
        self.show_main_menu()

if __name__ == "__main__":
    app = ASLMasterApp()
    app.mainloop()