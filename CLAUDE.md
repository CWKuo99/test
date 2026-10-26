# 理化教學互動網（Kwok's Science Lab）

國中理化的互動教學網站，以 GitHub Pages 發布於 https://cwkuo99.github.io/test/ 。
使用者是學生（學校 iPad、家裡手機）和授課老師郭家瑋。對話請用繁體中文。

## 結構

- 純靜態網站，沒有建置步驟。每個頁面都是一個獨立的 `.html`，樣式和程式寫在同一個檔案裡。
- `index.html` 是卡片式首頁。新增頁面時，同時在 `index.html` 加一張卡片，放在教學頁區塊的最後一張卡片之後、`<div class="mt-16 mb-8 ...">`（Student Projects 分隔線）之前。卡片沿用現有的樣式：`card-hover`、`rounded-2xl`、上方色塊 + SVG 圖示、標題、一句說明、「開始」字樣。每張卡片用不同的 Tailwind 主色。
- `students/`：學生作品，學生區塊的卡片也在 `index.html`。
- 外部函式庫只從 CDN 載入（Tailwind CDN、unpkg、jsdelivr），不引入 npm 或打包工具。

## 必守規則

1. **只放學生版。** 含答案、教師手冊、錯誤概念講解的教師版，一律不能進 repo（repo 是公開的）。同一個模擬若有教師版，以腳本從教師版產生學生版，只提交學生版。
2. **不放學生個資。** 不放學生作答資料、成績、照片或班級座號。學生作品的署名方式要先問老師。
3. **localStorage 一定要加前綴。** `cwkuo99.github.io` 底下的所有網站共用同一個來源（含歷史複習站 `history-review`）。每個頁面使用專屬前綴，並登記在下表。新頁面要先選一個不重複的前綴。讀寫都包在 try/catch 裡，沒有儲存功能時，頁面也要能正常運作。

   | 前綴 | 頁面 |
   | --- | --- |
   | `sci8-` | exam_review_g8.html |
   | `soundlab-` | sound_lab.html |
   | `pc-` | 另一個 repo：課程站（同一個來源，不要用這個前綴） |
   | `periodic_game_scores`（舊，未加前綴） | game_periodtable.html |
   | `sciUltraS…`（舊，兩頁共用） | students/ 的兩個遊戲 |
   | `hrv-`、`hre-` | 另一個 repo：history-review（不要用這兩個前綴） |

4. **著作權。** 題目和圖片只能用自己原創或有授權的內容。不能把參考書或課本的題目改寫後放上來（公開網站不適用授課合理使用）。
5. **科學正確性優先。** 改動物理或化學內容時，數值、單位、方向（例如波的傳播方向、粒子振動方向）都要再核對一次；有疑慮先列出來問老師，不要自行決定。
6. **手機可用。** 目標裝置是 iPad 與手機：版面在 390px 寬時不能橫向捲動，觸控目標至少 44px，文字至少 16px。有聲音的頁面要處理 iOS 靜音鍵（參考 sound_lab.html 的做法）。

## 工作流程

- 改動前先說明計畫；大改（超過一個頁面，或重寫某頁的主要邏輯）先等老師確認。
- 改完執行 `python3 scripts/check.py`，必須沒有錯誤才能 commit。
- 用 Playwright 在 390px 和 1280px 寬度截圖看過，並確認 console 沒有錯誤。
- 一個 commit 只做一件事，commit 訊息用中文寫「頁面：做了什麼」，例如 `聲音模擬實驗室：修正手機聽不到聲音`。
- 推送前先 `git fetch origin main && git rebase origin/main`。推送後約 1 分鐘，GitHub Pages 才會更新。
- 每次交付時，最後列出 2–3 個可能的邏輯盲點或邊界情況（例如極端數值、手機瀏覽器差異、學生可能的誤解）。
