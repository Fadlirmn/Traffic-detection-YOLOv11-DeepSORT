import os
from datetime import datetime, timedelta
import telebot
import threading

class TelegramBot:
    def __init__(self, token: str, min_vehicles: int = 10):
        self.bot = telebot.TeleBot(token)
        self.active_groups = set()
        self.min_vehicles = min_vehicles
        self.last_vehicle_count = 0
        self.last_detection_time = None
        self.latest_frame_path = None
        self.current_frame = None
        self.last_status = "Belum ada data"
        self.thread = None
        self.last_notification_time = None
        self.notification_cooldown = timedelta(minutes=5)  # Cooldown 5 menit
        self.consecutive_high_traffic = 0
        self.setup_handlers()

    def setup_handlers(self):
        @self.bot.message_handler(commands=['start'])
        def start(message):
            if message.chat.type in ['group', 'supergroup']:
                self.active_groups.add(message.chat.id)
                self.bot.reply_to(message, "🚦 Traffic Monitoring Bot activated!")

        @self.bot.message_handler(commands=['stop'])
        def stop(message):
            self.active_groups.discard(message.chat.id)
            self.bot.reply_to(message, "❌ Monitoring stopped.")

        @self.bot.message_handler(commands=['status'])
        def status(message):
            status = (
                f"✅ Active\n🚗 Threshold: {self.min_vehicles}"
                if message.chat.id in self.active_groups else
                "❌ Inactive"
            )
            self.bot.reply_to(message, status)

        @self.bot.message_handler(commands=['current'])
        def send_current(message):
            if self.current_frame is not None and self.last_detection_time:
                caption = (f"📊 Status terakhir:\n"
                        f"{self.last_status}\n"
                        f"🚗 Jumlah kendaraan: {self.last_vehicle_count}\n"
                        f"⏰ Waktu: {self.last_detection_time.strftime('%H:%M:%S')}")
                try:
                    import cv2
                    import tempfile
                    _, buffer = cv2.imencode(".jpg", self.current_frame)
                    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
                        tmp.write(buffer.tobytes())
                        tmp_path = tmp.name
                    with open(tmp_path, "rb") as photo:
                        self.bot.send_photo(message.chat.id, photo, caption=caption)
                    os.remove(tmp_path)
                except Exception as e:
                    self.bot.reply_to(message, f"⚠️ Gagal kirim gambar: {e}")
            else:
                self.bot.reply_to(message, "❌ Belum ada frame terbaru.")


        @self.bot.message_handler(commands=['help'])
        def help(message):
            self.bot.reply_to(message,
                "/start\n/stop\n/status\n/current\n/latest\n/help")

    def update_status(self, vehicle_count: int, frame=None, congestion: dict = None):
        self.last_vehicle_count = vehicle_count
        self.last_detection_time = datetime.now()
        if frame is not None:
            self.current_frame = frame.copy()  # simpan frame hasil deteksi terbaru

        if congestion:
            self.last_status = f"Traffic: {congestion['level']} (Index={congestion['index']:.1f})"
        else:
            self.last_status = f"Traffic update, kendaraan: {vehicle_count}"

        if vehicle_count >= self.min_vehicles:
            self.consecutive_high_traffic += 1
        else:
            self.consecutive_high_traffic = 0


    def should_send_notification(self):
        current_time = datetime.now()
        
        # Cek apakah sudah melewati cooldown
        if self.last_notification_time and \
           current_time - self.last_notification_time < self.notification_cooldown:
            return False
            
        # Kirim notifikasi jika traffic tinggi selama beberapa deteksi berturut-turut
        if self.consecutive_high_traffic >= 3:  # Minimal 3 deteksi berturut-turut
            return True
            
        return False

    def send_notification(self, image_path: str = None, vehicle_count: int = 0):
        self.update_status(vehicle_count, image_path)
        
        if not self.should_send_notification():
            return
            
        caption = (
            f"🚨 Kemacetan Terdeteksi\n"
            f"🚗 Jumlah kendaraan: {vehicle_count}\n"
            f"🕒 Waktu: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        
        for group_id in self.active_groups:
            try:
                if image_path and os.path.exists(image_path):
                    with open(image_path, 'rb') as photo:
                        self.bot.send_photo(group_id, photo, caption=caption)
                else:
                    self.bot.send_message(group_id, caption)
                self.last_notification_time = datetime.now()
                self.consecutive_high_traffic = 0
            except Exception as e:
                print(f"[Telegram Error] {e}")

    def send_photo(self, caption, image_path, vehicle_count=0):
        # Tambahkan jumlah kendaraan ke caption jika belum ada
        for group_id in self.active_groups:
            try:
                with open(image_path, 'rb') as img:
                    self.bot.send_photo(chat_id=group_id, photo=img, caption=caption)
            except Exception as e:
                print(f"[ERROR]  Failed to send photo: {e}")

    def send_text(self, msg: str):
        for group_id in self.active_groups:
            try:
                self.bot.send_message(group_id, msg)
            except Exception as e:
                print(f"[Telegram Error] {e}")

    def start_polling(self):
        self.thread = threading.Thread(target=self.bot.polling, kwargs={'none_stop': True})
        self.thread.start()
