# MSC Nastran Op2 Reader - Masaüstü Uygulaması

MSC Nastran tarafından oluşturulan **op2** dosyalarındaki tüm sonuçları görüntülemek için geliştirilmiş PyQt5 tabanlı masaüstü uygulaması.

## 📋 Özellikler

- ✅ Op2 dosyası açma ve okuma
- ✅ Tüm loadcase/subcase desteği
- ✅ Tüm result type'larını görüntüleme:
  - Displacement (Deplasman)
  - Stress (Gerilim)
  - Strain (Şekil Değiştirme)
  - Force (Kuvvet)
  - Diğer tüm sonuçlar
- ✅ **Node ID veya Element ID ile filtreleme**
- ✅ Sayısal sonuçları tablo formatında gösterme
- ✅ Kullanıcı dostu arayüz

## 🚀 Kurulum

### 1. Gereksinimler
- Python 3.7+
- pip

### 2. Bağımlılıkları Yükle

```bash
cd op2_reader
pip install -r requirements.txt
```

Eğer hata alırsan şu şekilde kurabilirsin:

```bash
pip install pyNastran PyQt5 numpy pandas
```

## 💻 Çalıştırma

```bash
python main.py
```

## 📖 Kullanım Kılavuzu

### 1. Dosya Aç
- "Dosya Aç" butonuna tıkla
- MSC Nastran op2 dosyasını seç
- Dosya otomatik olarak yüklenecek

### 2. Loadcase Seç
- Sol panelde "Loadcase Seç" açılır menüsünden bir loadcase seç
- O loadcase'e ait tüm result type'ları listelenir

### 3. Result Type Seçimi
- Solda listelenen result type'lardan birini seç (Displacement, Stress, vb.)
- Sağ tarafta ilk 100 sonuç görüntülenecek

### 4. Node veya Element Arama
Sağ üst panelden:
- **Tür**: "Node ID" veya "Element ID" seç
- **ID**: Aranacak ID numarasını gir
- **Ara** butonuna tıkla

Sonuçlar yeni bir tab'da açılacak ve o ID'ye ait tüm parametreler gösterilecek.

## 📊 Örnek Sonuç Formatı

Bir Node ID araması sırasında göreceğin çıktı:

```
DISPLACEMENT Sonuçları
Parametre    | Değer
T1          | 0.00123
T2          | -0.00456
T3          | 0.00789
R1          | 0.00001
R2          | 0.00002
R3          | 0.00003
```

## 🔧 Teknik Detaylar

### Op2 Handler (op2_handler.py)
- pyNastran kütüphanesini kullanarak op2 dosyasını parse eder
- Tüm loadcase ve result type'larını otomatik olarak algılar
- Node/Element bazlı veri filtreleme

### Ana Uygulama (main.py)
- PyQt5 tabanlı GUI
- Dosya açma dialogu
- Sekmeli sonuç görüntüleme
- Arka planda dosya yükleme (threading)

## ⚠️ Notlar

- İlk açılış sırasında büyük op2 dosyaları biraz zaman alabilir
- Uygulama ilk 100 sonucu genel görünümde gösterir
- Node/Element araması yapıldığında tam sonuçlar görüntülenir

## 🐛 Sorun Giderme

### "ModuleNotFoundError: No module named 'pyNastran'"
```bash
pip install pyNastran
```

### "ModuleNotFoundError: No module named 'PyQt5'"
```bash
pip install PyQt5
```

### Dosya açılmıyor
- Dosyanın geçerli bir op2 dosyası olduğundan emin ol
- Dosya yolu boşluk içermiyorsa daha iyi olur

## 📝 Yapılacaklar / Geliştirmeler

- [ ] 3D görselleştirme (isteğe bağlı)
- [ ] Export to CSV/Excel
- [ ] Arşiv dosya desteği
- [ ] İleri filtreleme seçenekleri
