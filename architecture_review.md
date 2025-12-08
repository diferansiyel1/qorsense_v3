diff --git a/ARCHITECTURE_REVIEW.md b/ARCHITECTURE_REVIEW.md
new file mode 100644
index 0000000000000000000000000000000000000000..d5e2cb55117d27eb2ad956d38c83d8535624ca58
--- /dev/null
+++ b/ARCHITECTURE_REVIEW.md
@@ -0,0 +1,115 @@
+# Mimari İnceleme Raporu
+
+## Bölüm 1: Yönetici Özeti
+- Proje; FastAPI tabanlı bir sensör analitik ajanı, Vite/React gösterge paneli ve Tauri/Electron masaüstü sarmalayıcılarını birleştiriyor, ancak arayüz ve üretim sertleştirmesi henüz minimal seviyede.
+- Çekirdek analitik mantık (sağlık puanlama, metrikler) mevcut; fakat konfigürasyon, kalıcılık, güvenlik, test ve CI/CD gibi platform konuları büyük ölçüde eksik olduğundan işletimsel ve güvenilirlik riskleri yaratıyor.
+- Acil öncelikler: ağ yüzeylerini güvenli ve parametrik hâle getirmek, veri akışları için doğrulama ve hata yönetimi eklemek, otomatik test ve linting kurmak, ajanı sürümlenebilir API'lere ve yapılandırılmış durum yönetimine ayrıştırmak.
+
+## Bölüm 2: Mevcut Mimarinin Güçlü Yanları
+- **Sorumluluk ayrımı**: Analitik hesaplamalar `agent/analytics` altında metrik yardımcıları ve puanlama ile yalıtılmış; birim testi ve yeniden kullanımı teşvik ediyor.【F:agent/analytics/metrics.py†L1-L73】【F:agent/analytics/scoring.py†L1-L83】
+- **CORS ve WebSocket destekli FastAPI tabanı**: HTTP uç noktaları ve akış tabanlı analitik kanalları sağlıyor; neredeyse gerçek zamanlı gösterge panelleri için uygun.【F:agent/main.py†L1-L156】
+- **Hafif React ön yüzü**: React Router ve axios soyutlaması kullanıyor; sayfaların ve API istemcilerinin genişletilmesi kolay.【F:app/src/main.tsx†L1-L12】【F:app/src/lib/api.ts†L1-L3】
+- **Masaüstü paketleme kancaları**: Tauri kurulumu başlangıçta paketlenmiş ajan ikili dosyasını çalıştırıyor, çevrimdışı kullanıma hazır dağıtım sağlıyor.【F:src-tauri/src/main.rs†L1-L20】
+
+## Bölüm 3: Kritik Zayıflıklar ve Riskler
+- **Akış verileri için kalıcılık veya geri basınç yok**: Sensör verileri kalıcılık politikası, sıkıştırma veya dayanıklılık olmadan bellek içi deque yapılarında tutuluyor; yeniden başlatmada veri kaybı ve `maxlen` kaldırıldığında/artsınca sınırsız bellek riski var.【F:agent/main.py†L18-L48】
+- **Girdi doğrulaması ve hata yönetimi eksik**: API uç noktaları sensör kimliklerine ve sorgu parametrelerine güveniyor; genel istisnalar döndürülüyor. WebSocket döngüleri hataları yutuyor, kapanış kodu yok; sessiz hatalar ve kaynak sızıntısı oluşabilir.【F:agent/main.py†L24-L130】【F:agent/main.py†L132-L199】
+- **Sert kodlanmış konfigürasyon ve gizli bilgiler**: Temel URL'ler ve host/port kodda sabit; ortam temelli dağıtımı engelliyor ve ikili paketlerde istenmeyen açığa çıkma riski yaratıyor.【F:agent/core/config.py†L1-L9】【F:app/src/lib/api.ts†L1-L3】
+- **Asgari güvenlik duruşu**: CORS tüm origin'lere açık; kimlik doğrulama, hız sınırlama, TLS sonlandırma yok; localhost dışı dağıtımda OWASP A01/A05/A07 riskleri oluşuyor.【F:agent/main.py†L9-L27】
+- **Test ve CI eksiklikleri**: Birim/entegrasyon testi, linting ve pipeline yapılandırması yok; analitik fonksiyonlar ve WebSocket davranışı doğrulanmadığından regresyon riski yüksek.
+- **Bağımlılık hijyeni sorunları**: `requirements.txt` sürüm sabitlemesi olmayan ve format hatası (birleşik `scipy`) içeren şekilde; kurulum hataları ve tedarik zinciri sapması riski var.【F:agent/requirements.txt†L1-L7】
+- **Ön yüz UX ve durum eksikleri**: Gösterge paneli yalnızca `/health` çağrısı yapıyor; hata yüzeyi, yeniden bağlanma mantığı, tipli sensör depoları yok; gözlemlenebilirlik ve dayanıklılık sınırlı.【F:app/src/pages/Dashboard.tsx†L1-L18】【F:app/src/lib/store.ts†L1-L3】
+
+## Bölüm 4: Dosya ve Modül Bazlı İnceleme
+- **agent/main.py**: Tek dosyada yönlendirme, simülasyon, durum ve analitik karışmış. Payload'lar için Pydantic model yok; uç noktalar sensör varlık kontrolünü yineliyor; WebSocket'ler kapanmıyor veya iptal ele almıyor; CSV dışa aktarım büyük veri için akış/paginasyon olmadan ad-hoc yazılmış.【F:agent/main.py†L18-L199】
+- **agent/analytics/metrics.py**: Metrik fonksiyonları net ancak tüm yollar için NaN ele alma yok (ör. SNR, std'e küçük epsilon ekliyor). Girdi/çıktı type hint'leri eksik; `calculate_all_metrics` dönüş şeması için docstring yok. Her istekte polyfit/logspace tekrarları önbelleksiz; performans maliyeti yaratabilir.【F:agent/analytics/metrics.py†L1-L73】
+- **agent/analytics/scoring.py**: Sert kodlu ağırlıklar/threshold'lar ayar yapmayı zorlaştırıyor; `generate_recommendations` threshold mantığını yineliyor; yerelleştirme ve önem dereceleri yok. Boş dizilere karşı koruma sınırlı (kısmen çağıran kontrol ediyor).【F:agent/analytics/scoring.py†L1-L83】【F:agent/analytics/scoring.py†L84-L123】
+- **agent/core/config.py**: BaseSettings kullanıyor fakat `.env` yükleme yönergesi ve şema doğrulaması (port aralığı vb.) yok; varsayılanlar yalnızca localhost'u açığa çıkarıyor.【F:agent/core/config.py†L1-L9】
+- **agent/core/logging.py**: Log rotasyonu ayarlı ancak yol göreli ve dizin oluşturma garanti değil; log seviye konfigürasyonu veya bağlamsal izleme (istek ID'leri) bulunmuyor.【F:agent/core/logging.py†L1-L4】
+- **agent/requirements.txt**: Sürüm sabitlemesi yok ve biçim hatası bağımlılık kurulumunu kırabilir; tekrarlanabilir inşa sağlanamıyor.【F:agent/requirements.txt†L1-L7】
+- **app/src/lib/api.ts**: Axios örneği localhost'a sabit; kimlik doğrulama/yeniden deneme için interceptor yok; zaman aşımı ayarı ve tüketicilere hata normalizasyonu eksik.【F:app/src/lib/api.ts†L1-L3】
+- **app/src/pages/Dashboard.tsx**: `any` kullanımı, yükleniyor/hata arayüzü yok ve yenileme tam sayfa yeniden yüklemeye bağlı; canlı veri veya sağlık bozulması göstergesi içermiyor.【F:app/src/pages/Dashboard.tsx†L1-L18】
+- **app/src/lib/store.ts**: Zustand store `any[]` sensör tutuyor; metrikler veya bağlantı durumu için slice yok; kalıcılık ve yeniden render'ı azaltacak selector'lar eksik.【F:app/src/lib/store.ts†L1-L3】
+- **app/src/components/ui/button.tsx**: Basit sarmalayıcı; erişilebilirlik (aria) props'ları, disabled/loading durumları ve tasarım token'ları eksik; sınıf birleştirme yardımcısı minimal.【F:app/src/components/ui/button.tsx†L1-L6】
+- **src-tauri/src/main.rs**: Ajan ikilisini sağlık kontrolü veya zarif kapanış olmadan çalıştırıyor; kaynak eksikse panic riski var; komut yürütme için IPC/güvenlik konfigürasyonu yok.【F:src-tauri/src/main.rs†L1-L20】
+
+## Bölüm 5: Eksik Bileşenler
+- API ve WebSocket için kimlik doğrulama/yetkilendirme katmanı (JWT/oturum).
+- Sensör verisi ve analitik geçmişi için kalıcı depolama soyutlaması (SQLite/PostgreSQL).
+- Sensör payload'ları, metrikler ve skor yanıtları için yapılandırılmış alan modelleri (Pydantic şemaları).
+- Konfigürasyon yönetimi (.env, gizli bilgi yönetimi, ön yüz/arka yüz/masaüstü için tiplenmiş ayarlar).
+- Linting, tip kontrolü, test ve güvenlik taraması içeren CI/CD pipeline'ı.
+- Ön yüzde gerçek zamanlı veri görselleştirme, hata sınırları ve tipli API istemcisi.
+- Gözlemlenebilirlik yığını: yapılandırılmış loglama, metrikler (Prometheus), izleme ve sağlık prob'ları.
+- Yeniden üretilebilir paketleme betikleri (Dockerfile, sürüm sabitlenmiş lockfile'lar) ve bağımlılık denetimi.
+
+## Bölüm 6: Refaktör Önerileri (Öncelikli)
+1) **Ajanı modülerleştirin**: FastAPI uygulamasını yönlendiricilere (`/health`, `/sensors`, `/analytics`), servislere (simülasyon, kalıcılık) ve şema modüllerine bölün; depolama ve analitik yapılandırması için bağımlılık enjeksiyonu ekleyin.
+2) **Pydantic şemaları ve doğrulama ekleyin**: Sensör verisi, metrikler ve skorlar için istek/yanıt modelleri tanımlayın; sorgu parametrelerini ve WebSocket payload'larını doğrulayın; yapılandırılmış hata yanıtları döndürün.
+3) **Kalıcılık ve geri basınç ekleyin**: Sensör depolamasını depo (repository) desenine göre soyutlayın (SQLite/Timescale); tutma politikaları ve dışa aktarımlar için paginasyon/akış desteği ekleyin.
+4) **Konfigürasyonu sertleştirin**: `.env` ve Pydantic ayarları kullanın; izinli origin listesini, zaman aşımlarını ve auth token'larını zorunlu kılın; axios `baseURL` değerini `import.meta.env` üzerinden parametrik yapın.
+5) **Gözlemlenebilirlik ve hata yönetimini iyileştirin**: Loglama ve istek ID'leri için middleware ekleyin; WebSocket'leri kodlarla kapatın; istisnaları merkezi yönetin; kuyruk boyutu ve işlem gecikmesi metriklerini toplayın.
+6) **Ön yüz iyileştirmeleri**: Zod/TypeScript arayüzleriyle tipli API istemcisi oluşturun, yükleniyor/hata durumları ekleyin, canlı akış görselleştirmesi ve otomatik yeniden bağlanma sağlayın; `any` kullanımını kaldırın ve sayfa yeniden yüklemesine bağlı olmayan yenileme ekleyin.
+7) **Bağımlılık ve build hijyeni**: `requirements.txt`/`package.json` içinde sürüm sabitleyin, biçim hatalarını düzeltin ve lockfile'lar ekleyin; Dockerfile ve CI iş akışları (lint, test, SAST) oluşturun.
+8) **Güvenlik kontrolleri**: Kimlik doğrulama (API anahtarları/JWT), hız sınırlama ve TLS sonlandırma rehberi ekleyin; CORS'u sınırlandırın ve Tauri'de komut çalıştırmayı korumaya alın.
+
+## Bölüm 7: Güvenlik ve Güvenilirlik İyileştirmeleri
+- CORS izin listesini zorlayın ve HTTP/WebSocket için API token'ı gerektirin; anonim trafiği reddeden middleware ekleyin ve OWASP A05/A10 riskleri için hız sınırlama (örn. slowapi) uygulayın.
+- Sensör kimliklerini ve payload şemalarını doğrulayın; deque boyutlarını sınırlandırın, büyük CSV dışa aktarımları akış ile sınırlandırın ve satır sayısını kısıtlayın.【F:agent/main.py†L18-L123】
+- Üretimde HTTPS/TLS sonlandırma rehberi sağlayın; temel URL'leri ortamdan alın ve güvenilmeyen ortamlarda otomatik süreç başlatmayı devre dışı bırakın.
+- Yapılandırılmış loglama, korelasyon ID'leri ve hata izleme ekleyin; log dizini oluşturma ve rotasyonu platform genelinde güvenceye alın.【F:agent/core/logging.py†L1-L4】
+- Bağımlılık sabitlemesi ve zafiyet taraması (pip-audit, npm audit) uygulayarak tedarik zinciri risklerini azaltın.【F:agent/requirements.txt†L1-L7】
+
+## Bölüm 8: Performans ve Ölçeklenebilirlik İyileştirmeleri
+- İstek başına ağır hesaplamaları (örn. DFA polyfit) önbelleğe alın veya artımlı hale getirin; yüksek frekanslı akışlar için analitik işlemlerini arka plan işçilerine/iş havuzuna taşıyın.【F:agent/analytics/metrics.py†L38-L73】
+- Yapılandırılabilir örnekleme aralıklarıyla asenkron veri üreticileri ve geri basınç (kuyruk sınırı, sınırlı kanal) ekleyin; WebSocket güncellemelerini toplu göndererek istemci yükünü azaltın.【F:agent/main.py†L90-L156】
+- `/data` ve `/metrics` için paginasyon ve filtreleme ekleyin; kalıcılık eklendiğinde veritabanı indeksleri kullanın.
+- Ön yüz: yenilemeleri debounce edin, WebSocket yeniden bağlanmasını üssel backoff ile sağlayın, büyük veri setleri için sanallaştırılmış zaman çizelgeleri kullanın.
+
+## Bölüm 9: Önerilen Klasör Yapısı (İdeal Mimari)
+```
+agent/
+  app/
+    main.py
+    api/
+      __init__.py
+      health.py
+      sensors.py
+      analytics.py
+    schemas/
+      sensor.py
+      metrics.py
+      scoring.py
+    services/
+      streaming.py
+      storage.py
+      analytics.py
+    core/
+      config.py
+      logging.py
+      security.py
+    tests/
+      test_metrics.py
+      test_scoring.py
+      test_routes.py
+  requirements.txt
+app/
+  src/
+    api/client.ts
+    components/
+    pages/
+    store/
+    hooks/
+    types/
+    styles/
+  .env.example
+ci/
+  github/
+    workflows/ci.yml
+Dockerfile
+```
+
+## Bölüm 10: Sonraki Adım Teknik Yol Haritası
+- **1: Temelleri sabitleyin—bağımlılık sabitlemesi ve biçim düzeltmesi yapın, .env tabanlı konfigürasyon ekleyin, Pydantic şemaları tanımlayın ve FastAPI'yi yönlendiricilere ayırıp merkezi hata yönetimi ekleyin; analitik fonksiyonlar için temel birim testleri yazın.
+- **2: Kalıcılık katmanını (SQLite/Postgres) depo deseniyle ekleyin, kimlik doğrulama ve kısıtlı CORS uygulayın, yapılandırılmış loglama/metric entegrasyonu yapın; Dashboard'u tipli API istemcisi, yükleniyor/hata durumları ve sağlık/metrik görünümüyle güçlendirin.
+- **3: WebSocket yeniden bağlanma ve canlı grafikler ekleyin, geri basınç kontrollü arka plan analitik işçilerini devreye alın, CI/CD pipeline'ı (lint, test, güvenlik taraması) kurun, Docker/Tauri/Electron ile güvenli paketleme ve gözlemlenebilirlik yığını (Prometheus/Grafana veya OpenTelemetry) entegre edin.
