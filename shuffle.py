import time
import random
import math
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import logging
from itertools import combinations


class IntelligentMinesweeperBot:
    def __init__(self, chromedriver_path=None, headless=False):
        """
        智能掃雷機器人 - 防檢測版本

        Args:
            chromedriver_path: ChromeDriver路徑
            headless: 是否以無頭模式運行
        """
        self.setup_logging()
        self.driver = self.setup_driver(chromedriver_path, headless)
        self.wait = WebDriverWait(self.driver, 10)
        self.actions = ActionChains(self.driver)

        # 防檢測參數
        self.last_action_time = time.time()
        self.action_delays = []
        self.win_streak = 0
        self.loss_streak = 0
        self.total_rounds = 0

    def setup_logging(self):
        """設置日誌記錄"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

    def setup_driver(self, chromedriver_path, headless):
        """設置反檢測Chrome瀏覽器驅動"""
        options = webdriver.ChromeOptions()
        if headless:
            options.add_argument('--headless')

        # 反檢測設置
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-plugins')
        options.add_argument('--disable-images')
        options.add_argument(
            '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)

        if chromedriver_path:
            service = Service(chromedriver_path)
            driver = webdriver.Chrome(service=service, options=options)
        else:
            driver = webdriver.Chrome(options=options)

        # 隱藏webdriver痕跡
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        driver.execute_cdp_cmd('Network.setUserAgentOverride', {
            "userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })

        return driver

    def human_like_delay(self, min_delay=0.5, max_delay=3.0, action_type="normal"):
        """
        人類行為模擬延遲

        Args:
            min_delay: 最小延遲
            max_delay: 最大延遲
            action_type: 動作類型 (thinking, clicking, typing, reading)
        """
        delay_ranges = {
            "thinking": (1.0, 4.0),
            "clicking": (0.3, 1.2),
            "typing": (0.1, 0.5),
            "reading": (2.0, 5.0),
            "normal": (min_delay, max_delay)
        }

        min_d, max_d = delay_ranges.get(action_type, (min_delay, max_delay))

        # 加入一些隨機性，模擬人類不規律的行為
        base_delay = random.uniform(min_d, max_d)

        # 偶爾加入更長的暫停，模擬思考
        if random.random() < 0.15:
            base_delay += random.uniform(1.0, 3.0)

        time.sleep(base_delay)
        self.action_delays.append(base_delay)

    def navigate_to_game(self):
        """導航到遊戲頁面"""
        try:
            self.logger.info("正在導航到Shuffle首頁...")
            self.driver.get("https://shuffle.com/zh")
            self.driver.set_window_size(1936, 1048)
            self.human_like_delay(action_type="reading")
            return True
        except Exception as e:
            self.logger.error(f"導航失敗: {e}")
            return False

    def switch_to_usd_currency(self):
        """切換到美金貨幣"""
        try:
            self.logger.info("開始切換貨幣到美金...")

            # 點擊餘額按鈕
            balance_button = self.wait.until(
                EC.element_to_be_clickable((By.ID, "balance-button"))
            )
            balance_button.click()
            self.human_like_delay(action_type="clicking")

            # 查找並點擊美金選項 (通常是USD相關的按鈕)
            try:
                # 嘗試查找美金餘額項目 (可能需要根據實際頁面調整)
                usd_balance = self.driver.find_element(
                    By.CSS_SELECTOR,
                    ".BalanceItem_root__yVdDK:nth-child(6)"  # 根據提供的選擇器
                )
                usd_balance.click()
                self.human_like_delay(action_type="clicking")
                self.logger.info("已選擇美金餘額")

            except NoSuchElementException:
                self.logger.warning("找不到美金餘額選項，嘗試查找切換開關...")

                # 查找貨幣切換開關
                currency_switch = self.driver.find_element(
                    By.CSS_SELECTOR,
                    ".Switch_checked___kgCm"
                )
                currency_switch.click()
                self.human_like_delay(action_type="clicking")

            # 保存設置
            try:
                save_button = self.wait.until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, ".PrimaryButton_buttonHeightMedium__mnZqo"))
                )
                save_button.click()
                self.human_like_delay(action_type="clicking")
                self.logger.info("已保存貨幣設置")

            except TimeoutException:
                self.logger.info("沒有找到保存按鈕，可能已自動保存")

            return True

        except Exception as e:
            self.logger.error(f"切換貨幣失敗: {e}")
            return False

    def navigate_to_mines(self):
        """導航到掃雷遊戲"""
        try:
            self.logger.info("正在導航到掃雷遊戲...")

            # 查找並點擊掃雷遊戲卡片
            mines_game = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR,
                                            "section:nth-child(1) .TallGameCard_root__HJ_sr:nth-child(2) .GameCardBorder_root__z0Mcd"))
            )
            mines_game.click()
            self.human_like_delay(action_type="clicking")

            # 等待遊戲頁面加載
            self.human_like_delay(action_type="reading")
            return True

        except Exception as e:
            self.logger.error(f"導航到掃雷遊戲失敗: {e}")
            return False

    def handle_login(self, email=None, password=None):
        """處理登錄流程"""
        try:
            # 檢查是否需要登錄
            login_button = self.driver.find_elements(By.CSS_SELECTOR, ".ButtonVariants_tertiary__LojiE")

            if login_button:
                self.logger.info("檢測到需要登錄...")
                login_button[0].click()
                self.human_like_delay(action_type="clicking")

                # 選擇Google登錄
                google_login_btn = self.wait.until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, ".ButtonVariants_secondary__3TEjO:nth-child(1)"))
                )
                google_login_btn.click()
                self.logger.info("已點擊Google登錄，請手動完成認證...")

                # 等待用戶手動完成登錄
                input("請在瀏覽器中完成登錄，然後按Enter繼續...")

        except NoSuchElementException:
            self.logger.info("已經登錄或不需要登錄")
        except Exception as e:
            self.logger.error(f"登錄處理失敗: {e}")

    def set_bet_amount(self, amount=0.1):
        """
        設置下注金額 (美金)

        Args:
            amount: 下注金額，默認0.1美金
        """
        try:
            bet_input = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, ".Input_root__lWEbp"))
            )

            # 模擬人類輸入行為
            bet_input.click()
            self.human_like_delay(action_type="clicking")

            # 清除並輸入新金額
            bet_input.clear()
            self.human_like_delay(action_type="typing")

            # 模擬逐字輸入
            amount_str = str(amount)
            for char in amount_str:
                bet_input.send_keys(char)
                time.sleep(random.uniform(0.05, 0.2))

            self.logger.info(f"設置下注金額: ${amount}")
            self.human_like_delay(action_type="thinking")

        except Exception as e:
            self.logger.error(f"設置下注金額失敗: {e}")

    def place_bet(self):
        """下注"""
        try:
            bet_button = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, ".GamesBetBtnContainer_root__uTUbr"))
            )
            bet_button.click()
            self.logger.info("已下注")
            self.human_like_delay(action_type="thinking")
            return True

        except Exception as e:
            self.logger.error(f"下注失敗: {e}")
            return False

    def generate_random_tile_selection(self, total_tiles=25, min_tiles=3, max_tiles=6):
        """
        生成隨機的格子選擇策略 (C25取3-6)

        Args:
            total_tiles: 總格子數
            min_tiles: 最少選擇格子數
            max_tiles: 最多選擇格子數

        Returns:
            list: 選中的格子位置列表
        """
        # 隨機決定這輪要選幾個格子
        num_tiles = random.randint(min_tiles, max_tiles)

        # 從25個位置中隨機選擇
        all_positions = list(range(1, total_tiles + 1))
        selected_positions = random.sample(all_positions, num_tiles)
        selected_positions.sort()  # 排序以便按順序點擊

        self.logger.info(f"本輪策略: 選擇 {num_tiles} 個格子，位置: {selected_positions}")
        return selected_positions

    def get_smart_tile_selection(self, total_tiles=25):
        """
        智能格子選擇策略 - 基於統計學和心理學

        Returns:
            list: 推薦的格子位置
        """
        # 根據勝負情況調整策略
        if self.win_streak >= 3:
            # 連勝時保守一點
            return self.generate_random_tile_selection(total_tiles, 3, 4)
        elif self.loss_streak >= 2:
            # 連敗時稍微激進一點
            return self.generate_random_tile_selection(total_tiles, 4, 6)
        else:
            # 正常情況
            return self.generate_random_tile_selection(total_tiles, 3, 5)

    def click_tile(self, tile_index):
        """
        點擊指定的格子，加入人類行為模擬

        Args:
            tile_index: 格子索引（1-25）
        """
        try:
            tiles = self.driver.find_elements(
                By.CSS_SELECTOR,
                ".MinesGameTileWrapper_root__JPw_y .MinesGameTileElement_root__6PJj3:nth-child(2)"
            )

            if tile_index <= len(tiles):
                tile = tiles[tile_index - 1]

                # 模擬人類的滑鼠移動和思考
                self.actions.move_to_element(tile).perform()
                self.human_like_delay(action_type="thinking")

                # 點擊
                tile.click()
                self.logger.info(f"點擊格子: {tile_index}")

                # 點擊後的停頓
                self.human_like_delay(action_type="clicking")
                return True
            return False

        except Exception as e:
            self.logger.error(f"點擊格子失敗: {e}")
            return False

    def check_game_result(self):
        """
        檢查遊戲結果

        Returns:
            str: 'win', 'lose', 'continue', 'unknown'
        """
        try:
            # 檢查是否有兌現按鈕（表示可以兌現，遊戲還在進行）
            cash_out_buttons = self.driver.find_elements(
                By.CSS_SELECTOR,
                ".MinesGameManualBet_button__nA9rb:nth-child(1)"
            )

            if cash_out_buttons and cash_out_buttons[0].is_displayed():
                return 'continue'

            # 檢查是否觸雷或遊戲結束的其他指示
            # 這裡可能需要根據實際的遊戲UI來調整

            return 'unknown'

        except Exception as e:
            self.logger.error(f"檢查遊戲結果失敗: {e}")
            return 'unknown'

    def cash_out(self):
        """智能兌現"""
        try:
            cash_out_button = self.driver.find_element(
                By.CSS_SELECTOR,
                ".MinesGameManualBet_button__nA9rb:nth-child(1)"
            )

            # 模擬思考時間
            self.human_like_delay(action_type="thinking")
            cash_out_button.click()

            self.logger.info("已兌現")
            self.win_streak += 1
            self.loss_streak = 0
            self.human_like_delay(action_type="clicking")
            return True

        except NoSuchElementException:
            self.logger.info("沒有找到兌現按鈕")
            return False
        except Exception as e:
            self.logger.error(f"兌現失敗: {e}")
            return False

    def play_intelligent_round(self, bet_amount=0.1):
        """執行一輪智能遊戲"""
        try:
            self.total_rounds += 1
            self.logger.info(f"=== 第{self.total_rounds}輪遊戲開始 ===")

            # 設置下注金額
            self.set_bet_amount(bet_amount)

            # 下注
            if not self.place_bet():
                return False

            # 獲取本輪的選擇策略
            selected_positions = self.get_smart_tile_selection()

            # 隨機決定兌現點（在選擇的格子中）
            cash_out_point = random.randint(2, len(selected_positions))
            self.logger.info(f"計劃在第{cash_out_point}個格子後兌現")

            # 依次點擊選中的格子
            for i, position in enumerate(selected_positions, 1):
                self.logger.info(f"點擊第{i}個格子，位置: {position}")

                if not self.click_tile(position):
                    break

                # 檢查遊戲狀態
                result = self.check_game_result()
                if result == 'lose':
                    self.logger.info("觸雷了！")
                    self.loss_streak += 1
                    self.win_streak = 0
                    break
                elif result == 'win':
                    self.logger.info("獲勝！")
                    self.win_streak += 1
                    self.loss_streak = 0
                    break

                # 決定是否兌現
                if i >= cash_out_point and random.random() < 0.7:
                    self.logger.info(f"達到兌現點，準備兌現...")
                    if self.cash_out():
                        break

                # 隨機暫停，模擬思考
                if random.random() < 0.3:
                    self.human_like_delay(action_type="thinking")

            # 輪次結束後的等待
            self.human_like_delay(action_type="reading")

        except Exception as e:
            self.logger.error(f"遊戲回合失敗: {e}")

    def adaptive_session_management(self):
        """自適應會話管理"""
        # 根據連勝連敗情況調整行為
        if self.win_streak >= 5:
            self.logger.info("連勝過多，暫停較長時間避免檢測...")
            self.human_like_delay(10, 30)
        elif self.loss_streak >= 3:
            self.logger.info("連敗較多，短暫休息...")
            self.human_like_delay(5, 15)

        # 隨機長暫停，模擬人類行為
        if random.random() < 0.1:
            self.logger.info("隨機長暫停，模擬查看其他頁面...")
            self.human_like_delay(15, 45)

    def run_intelligent_session(self, max_rounds=20, bet_amount=0.1, stop_loss=None, stop_win=None):
        """
        運行智能遊戲會話

        Args:
            max_rounds: 最大遊戲回合數
            bet_amount: 每回合下注金額（美金）
            stop_loss: 停損點
            stop_win: 停利點
        """
        self.logger.info(f"開始智能遊戲會話，最多{max_rounds}輪")

        for round_num in range(1, max_rounds + 1):
            try:
                # 執行一輪遊戲
                self.play_intelligent_round(bet_amount)

                # 自適應會話管理
                self.adaptive_session_management()

                # 檢查停損停利條件
                if stop_loss and self.loss_streak >= stop_loss:
                    self.logger.info(f"達到停損條件（連敗{self.loss_streak}），結束會話")
                    break

                if stop_win and self.win_streak >= stop_win:
                    self.logger.info(f"達到停利條件（連勝{self.win_streak}），結束會話")
                    break

                # 隨機決定是否提前結束會話
                if round_num > 5 and random.random() < 0.05:
                    self.logger.info("隨機決定結束會話，模擬人類行為")
                    break

            except KeyboardInterrupt:
                self.logger.info("用戶中斷會話")
                break
            except Exception as e:
                self.logger.error(f"第{round_num}輪異常: {e}")
                continue

        self.logger.info(
            f"會話結束 - 總輪數: {self.total_rounds}, 當前連勝: {self.win_streak}, 當前連敗: {self.loss_streak}")

    def close(self):
        """關閉瀏覽器"""
        if self.driver:
            self.driver.quit()
            self.logger.info("瀏覽器已關閉")


def main():
    """主函數"""
    bot = IntelligentMinesweeperBot(headless=False)

    try:
        # 1. 導航到首頁
        if not bot.navigate_to_game():
            return

        # 2. 處理登錄
        bot.handle_login()

        # 等待登錄完成
        input("登錄完成後，按Enter繼續...")

        # 3. 切換到美金
        if bot.switch_to_usd_currency():
            bot.logger.info("貨幣切換完成")

        # 4. 導航到掃雷遊戲
        if not bot.navigate_to_mines():
            return

        # 5. 運行智能遊戲會話
        bot.run_intelligent_session(
            max_rounds=15,  # 最多15輪
            bet_amount=0.1,  # 每輪下注0.1美金
            stop_loss=4,  # 連敗4次停損
            stop_win=8  # 連勝8次停利
        )

    except KeyboardInterrupt:
        bot.logger.info("用戶中斷程序")
    except Exception as e:
        bot.logger.error(f"程序異常: {e}")
    finally:
        bot.close()


if __name__ == "__main__":
    main()