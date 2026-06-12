# ROS_FINAL_ODEVI_
# Bookstore Service Robot - QR Doğrulamalı Çoklu Görev Navigasyonu

Bu proje, ROS1 Noetic ve TurtleBot3 Waffle Pi kullanılarak Gazebo ortamında çalışan bir servis robotu uygulamasıdır. Robot, AWS RoboMaker Bookstore World ortamında haritalama yapar, kaydedilmiş harita üzerinde AMCL ile lokalize olur, `mission.yaml` dosyasında tanımlanan görev noktalarına sırayla gider ve her noktada kamera ile QR kod okuyarak doğru noktaya ulaştığını doğrular.

## Proje Senaryosu

Servis robotu bir kitabevi/kütüphane ortamında ziyaretçileri belirlenen noktalara yönlendirmekle görevlidir.

Robotun görevleri:

1. Gazebo ortamında SLAM ile harita çıkarmak.
2. Haritayı `map.yaml` ve `map.pgm` olarak kaydetmek.
3. Kaydedilen harita ile AMCL + move_base navigasyonu başlatmak.
4. RViz üzerinden initial pose verilerek robotu lokalize etmek.
5. `mission.yaml` dosyasında tanımlanan görev noktalarına sırayla gitmek.
6. Her görev noktasında QR kod okuyarak doğrulama yapmak.
7. Görev sonunda SUCCESS, SKIPPED veya FAIL durumlarını raporlamak.

## Kullanılan Sistem

* Ubuntu 20.04
* ROS1 Noetic
* Gazebo Classic
* TurtleBot3 Waffle Pi
* AWS RoboMaker Bookstore World
* Python 3
* OpenCV QRCodeDetector
* move_base action server
* AMCL localization

## Paket Yapısı

```text
bookstore_service_robot/
├── launch/
│   ├── simulation.launch
│   ├── slam.launch
│   ├── navigation.launch
│   ├── qr_markers.launch
│   ├── qr_reader.launch
│   ├── waypoint_navigator.launch
│   └── task_manager.launch
├── src/
│   ├── qr_reader.py
│   ├── waypoint_navigator.py
│   ├── task_manager.py
│   ├── create_qr_codes.py
│   └── create_qr_models.py
├── config/
│   └── mission.yaml
├── maps/
│   ├── map.yaml
│   └── map.pgm
├── models/
│   ├── qr_information_desk/
│   ├── qr_science_section/
│   ├── qr_novel_section/
│   ├── qr_checkout_area/
│   └── qr_markers/
├── CMakeLists.txt
├── package.xml
└── README.md
```

## Kurulum Adımları

Önce ROS workspace içine girilir:

```bash
cd ~/rbtg_ws/src
```

AWS RoboMaker Bookstore World paketi eklenir:

```bash
git clone -b ros1 https://github.com/aws-robotics/aws-robomaker-bookstore-world.git
```

Gerekli Python paketleri kurulur:

```bash
sudo apt update
sudo apt install python3-qrcode python3-pil python3-yaml
```

ROS bağımlılıkları kurulur:

```bash
sudo apt install ros-noetic-map-server ros-noetic-navigation ros-noetic-gmapping ros-noetic-cv-bridge ros-noetic-image-transport
```

Workspace derlenir:

```bash
cd ~/rbtg_ws
catkin_make
source devel/setup.bash
```

TurtleBot3 modeli ayarlanır:

```bash
export TURTLEBOT3_MODEL=waffle_pi
```

Kalıcı olması için `~/.bashrc` dosyasına şu satır eklenebilir:

```bash
export TURTLEBOT3_MODEL=waffle_pi
source /home/hikmetunverdi/rbtg_ws/devel/setup.bash
```

QR modellerinin Gazebo tarafından bulunabilmesi için şu satır da `~/.bashrc` içine eklenebilir:

```bash
export GAZEBO_MODEL_PATH=$GAZEBO_MODEL_PATH:/home/hikmetunverdi/rbtg_ws/src/bookstore_service_robot/models
```

Sonra terminal yenilenir:

```bash
source ~/.bashrc
```

## QR Kodların Oluşturulması

QR görselleri şu komutla oluşturulur:

```bash
python3 ~/rbtg_ws/src/bookstore_service_robot/src/create_qr_codes.py
```

QR Gazebo model klasörleri şu komutla oluşturulur:

```bash
python3 ~/rbtg_ws/src/bookstore_service_robot/src/create_qr_models.py
```

Oluşan QR içerikleri:

```text
LOCATION=INFORMATION_DESK
LOCATION=SCIENCE_SECTION
LOCATION=NOVEL_SECTION
LOCATION=CHECKOUT_AREA
```

## Haritalama ve Harita Kaydı

### Terminal 1 - Simülasyon

```bash
cd ~/rbtg_ws
source devel/setup.bash
export TURTLEBOT3_MODEL=waffle_pi
roslaunch bookstore_service_robot simulation.launch
```

### Terminal 2 - SLAM

```bash
cd ~/rbtg_ws
source devel/setup.bash
export TURTLEBOT3_MODEL=waffle_pi
roslaunch bookstore_service_robot slam.launch
```

### Terminal 3 - Teleop

```bash
cd ~/rbtg_ws
source devel/setup.bash
export TURTLEBOT3_MODEL=waffle_pi
roslaunch turtlebot3_teleop turtlebot3_teleop_key.launch
```

Robot klavye ile gezdirilerek ortam haritası çıkarılır. Harita yeterince oluşunca yeni terminalde kaydedilir:

```bash
cd ~/rbtg_ws
source devel/setup.bash
rosrun map_server map_saver -f ~/rbtg_ws/src/bookstore_service_robot/maps/map
```

Bu işlem sonunda şu dosyalar oluşur:

```text
maps/map.yaml
maps/map.pgm
```

## Haritadan Navigasyon

### Terminal 1 - Simülasyon

```bash
cd ~/rbtg_ws
source devel/setup.bash
export TURTLEBOT3_MODEL=waffle_pi
roslaunch bookstore_service_robot simulation.launch
```

### Terminal 2 - QR Tabelaları

```bash
cd ~/rbtg_ws
source devel/setup.bash
roslaunch bookstore_service_robot qr_markers.launch
```

Eğer QR modelleri zaten eklenmişse ve `entity already exists` uyarısı alınırsa, bu QR modellerinin Gazebo ortamında zaten bulunduğu anlamına gelir.

### Terminal 3 - Navigation

```bash
cd ~/rbtg_ws
source devel/setup.bash
export TURTLEBOT3_MODEL=waffle_pi
roslaunch bookstore_service_robot navigation.launch
```

RViz açıldıktan sonra `2D Pose Estimate` aracı ile robotun harita üzerindeki başlangıç konumu verilir. Bu işlem AMCL lokalizasyonu için gereklidir.

## QR Okuyucu

QR okuyucu node şu komutla başlatılır:

```bash
cd ~/rbtg_ws
source devel/setup.bash
roslaunch bookstore_service_robot qr_reader.launch
```

QR çıktısını izlemek için:

```bash
rostopic echo /qr_code_data
```

Beklenen örnek çıktı:

```text
data: "LOCATION=INFORMATION_DESK"
```

## Görev Yöneticisi / Çoklu Waypoint

Robotun görev noktalarına sırayla gitmesi ve QR doğrulama yapması için görev yöneticisi başlatılır:

```bash
cd ~/rbtg_ws
source devel/setup.bash
roslaunch bookstore_service_robot task_manager.launch
```

Alternatif olarak:

```bash
roslaunch bookstore_service_robot waypoint_navigator.launch
```

Görev yöneticisi şu akışta çalışır:

1. `mission.yaml` dosyasından görev noktalarını okur.
2. İlk hedefi `move_base` action server'a gönderir.
3. Robot hedefe ulaşınca QR doğrulama başlatılır.
4. QR içeriği beklenen değerle eşleşirse görev noktası `SUCCESS` olur.
5. QR okunamazsa veya yanlış okunursa yeniden deneme yapılır.
6. Başarısız QR doğrulamada nokta `SKIPPED` olarak işaretlenir.
7. Navigasyon başarısız olursa nokta `FAIL` olarak işaretlenir.
8. Sonraki görev noktasına geçilir.
9. Görev sonunda rapor yazdırılır.

Örnek görev raporu:

```text
----- GOREV RAPORU -----
INFORMATION_DESK: SUCCESS
SCIENCE_SECTION: SUCCESS
NOVEL_SECTION: SUCCESS
CHECKOUT_AREA: SUCCESS
Gorev tamamlandi.
```

## Görev Noktaları

Görev noktaları `config/mission.yaml` dosyasında tutulur. Koordinatlar kod içine gömülmemiştir.

Örnek yapı:

```yaml
locations:
  - INFORMATION_DESK
  - SCIENCE_SECTION
  - NOVEL_SECTION
  - CHECKOUT_AREA

INFORMATION_DESK:
  goal:
    x: -5.1
    y: -3.45
    yaw: -1.018
  qr_expected: "LOCATION=INFORMATION_DESK"

SCIENCE_SECTION:
  goal:
    x: -1.6
    y: -1.5
    yaw: 1.604
  qr_expected: "LOCATION=SCIENCE_SECTION"

NOVEL_SECTION:
  goal:
    x: 0.05
    y: 1.8
    yaw: 0.0
  qr_expected: "LOCATION=NOVEL_SECTION"

CHECKOUT_AREA:
  goal:
    x: -6.9
    y: -5.75
    yaw: 1.551
  qr_expected: "LOCATION=CHECKOUT_AREA"
```

Buradaki `yaw` değerleri radyandır.

Robotun anlık `x`, `y`, `yaw` değerini bulmak için:

```bash
rosrun tf tf_echo map base_footprint
```

Çıktıda:

```text
Translation: [x, y, z]
RPY (radian): [roll, pitch, yaw]
```

kısmındaki `x`, `y` ve `yaw` değerleri `mission.yaml` içine yazılır.

## Kullanılan Topic Yapıları

### `/cmd_vel`

Robotun hız komutlarını aldığı topic.

Mesaj tipi:

```text
geometry_msgs/Twist
```

Kullanım amacı:

```text
Teleop, move_base veya manuel komutlar robot hareketini bu topic üzerinden sağlar.
```

### `/scan`

Lidar verisinin yayınlandığı topic.

Mesaj tipi:

```text
sensor_msgs/LaserScan
```

Kullanım amacı:

```text
SLAM, obstacle avoidance ve costmap üretimi için kullanılır.
```

### `/odom`

Robotun odometry bilgisinin yayınlandığı topic.

Mesaj tipi:

```text
nav_msgs/Odometry
```

Kullanım amacı:

```text
Robotun kısa süreli konum ve hız tahmini için kullanılır.
```

### `/map`

Kaydedilmiş veya SLAM tarafından üretilen haritanın yayınlandığı topic.

Mesaj tipi:

```text
nav_msgs/OccupancyGrid
```

Kullanım amacı:

```text
RViz, AMCL ve move_base tarafından kullanılır.
```

### `/amcl_pose`

AMCL tarafından hesaplanan robot konumu.

Mesaj tipi:

```text
geometry_msgs/PoseWithCovarianceStamped
```

Kullanım amacı:

```text
Robotun harita üzerindeki tahmini konumunu verir.
```

### `/camera/rgb/image_raw`

TurtleBot3 Waffle Pi kamera görüntüsü.

Mesaj tipi:

```text
sensor_msgs/Image
```

Kullanım amacı:

```text
QR kod okuma işlemi bu görüntü üzerinden yapılır.
```

### `/qr_code_data`

QR okuyucu node tarafından yayınlanan QR içeriği.

Mesaj tipi:

```text
std_msgs/String
```

Örnek çıktı:

```text
LOCATION=INFORMATION_DESK
```

### `/move_base/status`

move_base action server durum bilgisini yayınlar.

Mesaj tipi:

```text
actionlib_msgs/GoalStatusArray
```

Kullanım amacı:

```text
Hedefin aktif, başarılı veya başarısız durumunu takip etmek için kullanılır.
```

### `/move_base/result`

move_base sonucunu yayınlar.

Mesaj tipi:

```text
move_base_msgs/MoveBaseActionResult
```

Kullanım amacı:

```text
Hedefe ulaşılıp ulaşılmadığını kontrol etmek için kullanılır.
```

### `/tf` ve `/tf_static`

Robot frame dönüşümlerinin yayınlandığı topiclerdir.

Kullanım amacı:

```text
map, odom, base_footprint, base_link, base_scan ve kamera frame'leri arasındaki dönüşümleri sağlar.
```

## Kullanılan Service Yapıları

### `/gazebo/spawn_sdf_model`

QR tabelalarını Gazebo ortamına eklemek için kullanılır.

Service tipi:

```text
gazebo_msgs/SpawnModel
```

Kullanıldığı yer:

```text
qr_markers.launch
```

### `/gazebo/spawn_urdf_model`

TurtleBot3 robot modelini Gazebo ortamına eklemek için kullanılır.

Service tipi:

```text
gazebo_msgs/SpawnModel
```

Kullanıldığı yer:

```text
simulation.launch
```

### `/gazebo/delete_model`

Gazebo içindeki bir modeli silmek için kullanılır.

Service tipi:

```text
gazebo_msgs/DeleteModel
```

Örnek kullanım:

```bash
rosservice call /gazebo/delete_model "model_name: 'qr_information_desk'"
```

### `/static_map`

map_server tarafından sağlanan harita servisidir.

Service tipi:

```text
nav_msgs/GetMap
```

Kullanım amacı:

```text
Kaydedilmiş haritanın navigation sistemine verilmesi.
```

### `/move_base/make_plan`

move_base tarafından yol planı oluşturmak için kullanılabilen servistir.

Service tipi:

```text
nav_msgs/GetPlan
```

Kullanım amacı:

```text
Başlangıç ve hedef arasında global plan oluşturulabilir.
```

## Kullanılan Action Yapısı

### `/move_base`

Robotun hedef noktalara gitmesi için kullanılan action server'dır.

Action tipi:

```text
move_base_msgs/MoveBaseAction
```

Görev yöneticisi her hedef için `MoveBaseGoal` oluşturur ve `/move_base` action server'a gönderir.

Goal içeriği:

```text
target_pose.header.frame_id = "map"
target_pose.pose.position.x
target_pose.pose.position.y
target_pose.pose.orientation
```

Başarı durumu:

```text
GoalStatus.SUCCEEDED
```

Başarılı durumda görev yöneticisi QR doğrulama aşamasına geçer. Hedefe ulaşılamazsa görev noktası `FAIL` olarak işaretlenir.

## Hata Yönetimi

Bu projede şu hata yönetimleri uygulanmıştır:

### Navigasyon Hatası

Robot hedefe ulaşamazsa:

1. Hedef için yeniden deneme yapılır.
2. Yeniden deneme başarısız olursa görev noktası `FAIL` olur.
3. Robot bir sonraki görev noktasına geçer.

### QR Okuma Hatası

QR okunamazsa veya yanlış QR okunursa:

1. QR okuma tekrar denenir.
2. Belirlenen deneme sayısı sonunda doğrulama başarısızsa görev noktası `SKIPPED` olur.
3. Robot bir sonraki görev noktasına geçer.

### Timeout

Her hedef için süre sınırı uygulanır.

Örnek parametreler:

```text
goal_timeout: 90 saniye
qr_timeout: 8 saniye
qr_retry_count: 2
move_retry_count: 1
```

## Final Çalıştırma Sırası

Tüm sistemi test etmek için komut sırası:

### Temiz Başlangıç

```bash
killall -9 gzserver gzclient roslaunch rosmaster roscore
```

### Terminal 1

```bash
cd ~/rbtg_ws
source devel/setup.bash
export TURTLEBOT3_MODEL=waffle_pi
roslaunch bookstore_service_robot simulation.launch
```

### Terminal 2

```bash
cd ~/rbtg_ws
source devel/setup.bash
roslaunch bookstore_service_robot qr_markers.launch
```

### Terminal 3

```bash
cd ~/rbtg_ws
source devel/setup.bash
export TURTLEBOT3_MODEL=waffle_pi
roslaunch bookstore_service_robot navigation.launch
```

RViz üzerinden `2D Pose Estimate` verilir.

### Terminal 4

```bash
cd ~/rbtg_ws
source devel/setup.bash
roslaunch bookstore_service_robot qr_reader.launch
```

### Terminal 5

```bash
cd ~/rbtg_ws
source devel/setup.bash
roslaunch bookstore_service_robot waypoint_navigator.launch
```

## Demo Videosunda Gösterilecekler

Demo videosunda şu aşamalar gösterilebilir:

1. Gazebo Bookstore ortamının açılması.
2. TurtleBot3 robotunun ortamda görünmesi.
3. SLAM ile harita çıkarma ve harita kaydı.
4. Kaydedilmiş harita ile navigation başlatma.
5. RViz üzerinden initial pose verilmesi.
6. Robotun görev noktalarına sırayla gitmesi.
7. Her görev noktasında QR doğrulaması.
8. Görev raporunun terminalde gösterilmesi.

## Sonuç

Bu proje ile ROS1 Noetic üzerinde TurtleBot3 Waffle Pi kullanılarak Gazebo ortamında QR doğrulamalı çoklu görev navigasyonu gerçekleştirilmiştir. Robot, harita üzerinden AMCL ile lokalize olmakta, move_base ile görev noktalarına gitmekte, kamera görüntüsünden QR kod okumakta ve görev sonunda sonuç raporu üretmektedir.

Demo linki: https://drive.google.com/drive/folders/1nnkY4ANMgyMFOfeLdY4rPvx88oylYdZs?usp=drive_link
