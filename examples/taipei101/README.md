# 台北 101・信義街區互動 demo

[開啟完整 demo](https://bigtongue5566.github.io/demos/taipei101/index.html) · [Skill 介紹](https://bigtongue5566.github.io/?skill=blender-landmark-generator) · [建模 skill](https://github.com/bigtongue5566/blender-landmark-generator)

以 Google Earth 俯視與不同方向的 3D 斜視、Google Maps 松智路街景及官方資料作觀察參考，建立原創 Blender 外觀沙盤。主塔尖端 508 公尺，保留八段竹節、圓形飾盤及相連購物中心。周邊包括世貿一館、國際會議中心、國貿大樓、君悅飯店與市政府。

世貿一館使用中央拱形覆蓋屋頂、七層退台、綠色屋面及南側入口；可切到「世貿」近看。屋頂、退台與入口逐棟比對，並保留 [觀察與近似說明](DESIGN.md)。本作品是外觀示範，寬深、周邊高度和立面細節為近似，不含室內或地下空間。

## 操作

左鍵或中鍵拖曳旋轉，滾輪縮放，右鍵平移；手機可拖曳及雙指縮放。提供全景、主塔、世貿、俯視，日間、夕陽及夜景。夜間會開啟窗燈、塔身飾帶、街燈及廣場燈光；亮燈位置與色彩為示意。

場景設定包含白模、植栽、周邊建築、地標名稱、自動環繞，以及畫面 PNG、GLB 和離線 HTML 下載。完整頁面及模型不依賴執行期 CDN 或 Google API 金鑰。

## 重建

需要 Blender 5.2+、Node.js 20+ 與 npm。在本目錄執行：

```powershell
npm ci
& 'C:/Program Files/Blender Foundation/Blender 5.2/blender.exe' --background --python scripts/taipei101.py -- --render
npm run build
npm run check
& 'C:/Program Files/Blender Foundation/Blender 5.2/blender.exe' --background dist/Taipei101.blend --python scripts/review_model.py
npm start
```

可修改隨附的 `Taipei101.blend`，或由 Python 腳本重新產生。建模腳本保留原場景，另建 `TAIPEI 101 · Xinyi District`，只匯出該場景。網站交付檔案位於本儲存庫 `docs/demos/taipei101/`。

檢查涵蓋 GLB、HTML 內嵌一致性、塔頂 508 公尺、夜間發光材質，以及一館中央屋頂覆蓋、弧度與退台的實際三角形取樣。`review_model.py` 重新開啟 Blender 原檔並渲染南側、西側與俯視；檔案驗證不能代替外觀比對。

## 來源與授權

Google 影像僅作觀察，未擷取原始 3D 網格或嵌入照片。預覽為本模型自行渲染。[來源與授權](RIGHTS.md) 記錄影像日期、外觀限制和 Three.js 授權聲明。
