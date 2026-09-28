import torch #torch ana kütüphanesi
from ultralytics import YOLO #YOLO modeli

def main():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu") #gpu/cpu seçimi
    print("Kullanılan cihaz:", device)

    model = YOLO("yolo11n.pt") #yolo11 modeli

    #EĞİTİM
    results = model.train(
        data="dataset_yolo/dataset.yaml", #veri seti(train,validation,class isimleri,class sayıları)
        epochs=30, #tur sayısı
        imgsz=320, #görüntü boyutu
        batch=64, #eş zamanlı işlenecek görüntü sayısı
        device=device, #cihaz seçimi

        workers=0,

        # AUGMENTATION
        hsv_h=0.015, #renk tonu değişimi
        hsv_s=0.7, #renk doygunluğu değişimi
        hsv_v=0.4, #parlaklık değişimi
        degrees=10, #rastgele döndürme
        translate=0.1, #görüntü %10 oranında sağa-sola/yukarı-aşağı kaydırılır
        scale=0.5, #yakınlaştırma/uzaklaştırma
        shear=2.0, #eğme(yamultma/yamuklaştırma)
        fliplr=0.5, #görüntü yatay çevrilir
        mosaic=1.0, #4 resim birleştirilerek yeni görüntü oluşturulur
        mixup=0.2, #iki resim karıştırılır

        #OPTIMIZATION
        lr0=0.01, #learning rate(öğrenme oranı)
        momentum=0.937, #gradient güncellemelerini hızlandırır
        weight_decay=0.0005, #overfitting azaltılır
        patience=10, #early stopping sınırı
        verbose=True, #eğitim detayları terminalde gösterilir
        plots=True #eğitim sonunda grafikler oluşturulur
    )

    #VALIDATION
    metrics = model.val() #eğitim sonunda model test edilir

    print("\n===== METRİKLER =====")
    print(metrics)

    model.export(format="onnx") #model oluşturma (çıktı model)

if __name__ == "__main__":
    main()