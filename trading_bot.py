import time
from pocketoptionapi.stable_api import PocketOption
import logging
import pandas as pd
from datetime import datetime

class TradingBot:
    def __init__(self, ssid, demo=True):
        # تنظیم لاگینگ
        logging.basicConfig(level=logging.INFO, 
                          format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)
        
        # اتصال به API
        self.api = PocketOption(ssid, demo)
        self.connected = self.api.connect()
        if not self.connected:
            raise Exception("خطا در اتصال به API")
        
        # تنظیمات پیش‌فرض
        self.asset = "EURUSD_otc"  # جفت ارز
        self.amount = 1  # مقدار سرمایه‌گذاری
        self.duration = 1  # مدت زمان معامله (دقیقه)
        
        time.sleep(2)  # صبر برای اتصال کامل
        
        # چک کردن موجودی
        self.initial_balance = self.api.get_balance()
        self.logger.info(f"موجودی اولیه: ${self.initial_balance}")

    def analyze_market(self):
        """تحلیل ساده بازار با استفاده از میانگین متحرک"""
        try:
            # دریافت کندل‌های قیمت
            candles = self.api.get_candles(self.asset, 60, count=20)
            df = pd.DataFrame(candles)
            
            if df.empty:
                return None
                
            # محاسبه میانگین متحرک
            sma_5 = df['close'].rolling(window=5).mean().iloc[-1]
            sma_20 = df['close'].rolling(window=20).mean().iloc[-1]
            
            current_price = df['close'].iloc[-1]
            
            # استراتژی ساده معامله
            if sma_5 > sma_20:
                return "call"  # سیگنال خرید
            elif sma_5 < sma_20:
                return "put"   # سیگنال فروش
                
            return None
            
        except Exception as e:
            self.logger.error(f"خطا در تحلیل بازار: {e}")
            return None

    def place_trade(self, direction):
        """انجام معامله"""
        try:
            result = self.api.buy(
                amount=self.amount,
                asset=self.asset,
                direction=direction,
                duration=self.duration
            )
            
            if result[0]:  # اگر معامله موفق بود
                self.logger.info(f"معامله باز شد - جهت: {direction}")
                
                # بررسی نتیجه معامله
                time.sleep(self.duration * 60 + 2)  # انتظار برای بسته شدن معامله
                profit, status = self.api.check_win(result[1])
                
                self.logger.info(f"نتیجه معامله: {status} - سود/ضرر: ${profit if profit else 0}")
                return profit
            else:
                self.logger.error("خطا در باز کردن معامله")
                return None
                
        except Exception as e:
            self.logger.error(f"خطا در انجام معامله: {e}")
            return None

    def run(self, max_trades=5):
        """اجرای ربات"""
        trade_count = 0
        total_profit = 0
        
        self.logger.info("شروع معاملات خودکار...")
        
        try:
            while trade_count < max_trades:
                self.logger.info(f"\nمعامله {trade_count + 1}/{max_trades}")
                
                # تحلیل بازار
                signal = self.analyze_market()
                
                if signal:
                    # انجام معامله
                    profit = self.place_trade(signal)
                    if profit:
                        total_profit += profit
                    
                    trade_count += 1
                
                time.sleep(5)  # تاخیر بین معاملات
                
            # نمایش نتایج
            final_balance = self.api.get_balance()
            self.logger.info("\n=== نتایج معاملات ===")
            self.logger.info(f"تعداد معاملات: {trade_count}")
            self.logger.info(f"سود/ضرر کل: ${total_profit:.2f}")
            self.logger.info(f"موجودی نهایی: ${final_balance:.2f}")
            
        except KeyboardInterrupt:
            self.logger.info("\nربات متوقف شد.")
        except Exception as e:
            self.logger.error(f"خطای سیستمی: {e}")
        finally:
            self.api.disconnect()

if __name__ == "__main__":
    # تنظیمات اتصال
    SSID = """42["auth",{"session":"YOUR_SESSION_HERE","isDemo":1,"uid":YOUR_UID_HERE,"platform":2}]"""
    
    # ایجاد و اجرای ربات
    bot = TradingBot(SSID, demo=True)
    bot.run(max_trades=5)