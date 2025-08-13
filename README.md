-----

## 主要功能

  * **反檢測**：
      * 使用 `selenium` 搭配 Chrome 選項，隱藏 `webdriver` 痕跡。
      * 模擬隨機且不規律的滑鼠點擊、延遲與暫停，模仿人類的思考和操作習慣。
      * 在連勝或連敗時，自適應地調整休息時間，避免規律的行為模式。
  * **遊戲自動化**：
      * **導航**：自動導航到 Shuffle.com 首頁，並找到掃雷遊戲。
      * **登錄處理**：檢測登錄狀態，如果未登錄會引導使用者手動完成 Google 登錄。
      * **貨幣切換**：自動將遊戲貨幣切換為美金（USD）。
      * **下注**：設定並執行下注動作。
      * **遊戲邏輯**：
          * 採用**隨機策略**選擇要點擊的格子。
          * 根據目前的**連勝/連敗**狀態，調整每次遊戲選擇的格子數量，模擬玩家的心理變化（連勝時保守，連敗時激進）。
          * 在點擊數個格子後，**隨機決定是否兌現**，避免每次都點擊固定數量的格子。
  * **會話管理**：
      * 可以設定最大遊戲回合數、每回合的下注金額。
      * 提供\*\*停損（Stop-Loss）**和**停利（Stop-Win）\*\*機制，當連敗或連勝達到預設次數時，會自動結束遊戲。
      * 在遊戲過程中會隨機進行長暫停，模擬使用者分心或離開的情況。
  * **日誌記錄**：詳細記錄每個步驟的執行狀態，方便追蹤與除錯。

    # 已知錯誤: 修改美金餘額換算必須在手動調整
    # Cookie記得要處理掉

-----

## 程式碼架構

程式碼被封裝在一個名為 `IntelligentMinesweeperBot` 的類別中，其核心方法包括：

  * `__init__`：初始化瀏覽器、反檢測參數和日誌。
  * `setup_driver`：設定並啟動一個具備反檢測功能的 Chrome 瀏覽器。
  * `human_like_delay`：核心的反檢測方法，用於模擬人類的延遲。
  * `Maps_to_game`、`switch_to_usd_currency`、`Maps_to_mines`：負責網頁導航。
  * `handle_login`：處理登錄邏輯。
  * `set_bet_amount`、`place_bet`：處理下注。
  * `get_smart_tile_selection`：**智能選擇**格子數量的核心邏輯。
  * `click_tile`：點擊格子並模擬人類行為。
  * `cash_out`：執行兌現。
  * `play_intelligent_round`：執行一輪完整的遊戲流程。
  * `run_intelligent_session`：管理整個遊戲會話，包含停損停利邏輯。
  * `close`：關閉瀏覽器。

-----

## 安裝與使用

### 前置條件

在運行程式碼之前，請確保已安裝 Python 3 和必要的套件。

### 安裝步驟

1.  **安裝 Python 套件**
    使用 `pip` 安裝 `selenium`：

    ```bash
    pip install selenium
    ```

2.  **安裝 Chrome 瀏覽器**
    請確保您的電腦上已安裝 Google Chrome。

3.  **下載 ChromeDriver**

      * 瀏覽 [ChromeDriver 官方下載頁面](https://googlechromelabs.github.io/chrome-for-testing/)。
      * 找到與您電腦上 **Chrome 瀏覽器版本**相對應的 ChromeDriver。
      * 將下載的檔案解壓縮，並將 `chromedriver` 可執行檔的路徑記下來。

4.  **修改程式碼 (可選)**

      * 如果您想指定 ChromeDriver 的路徑，可以在 `main` 函數中，將 `IntelligentMinesweeperBot` 實例化時傳入路徑。
      * 例如：`bot = IntelligentMinesweeperBot(chromedriver_path='/path/to/chromedriver')`
      * 如果 ChromeDriver 已經在系統的 PATH 中，則無需傳入路徑。

5.  **運行程式碼**

      * 執行 `shuffle.py` 檔案：

    <!-- end list -->

    ```bash
    python shuffle.py
    ```

      * 當程式運行到登錄步驟時，會提示您手動在彈出的瀏覽器視窗中完成 Google 登錄，登錄完成後在終端機中按 `Enter` 繼續。
