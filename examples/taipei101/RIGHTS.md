# 台北 101・信義街區：素材來源與授權

模型、程序化幾何、材質及網頁預覽由本次 demo 製作產生；未使用 Google Earth 原始 3D tiles、抽取網格或街景貼圖。公開成品及製作原始碼置於本網站儲存庫，依網站的 [MIT 授權](https://github.com/bigtongue5566/bigtongue5566.github.io/blob/main/LICENSE) 提供。建模 skill 儲存庫本身未宣告授權；本站的授權不延伸到該獨立儲存庫。

## 外觀觀察來源

- [Google Earth](https://earth.google.com/web/search/Taipei+101)：塔身、街廓與屋頂；世貿一館另查看俯視、南側及其他方向斜視。可見影像日期 2018/11；一館近景顯示 2018/11/11。
- [Google Maps 松智路街景](https://www.google.com/maps/@?api=1&map_action=pano&pano=DJx8RfyhF9l9h6cosRiC3g&viewpoint=25.0323288,121.5653816&heading=319&pitch=21&fov=75)：可見拍攝日期 2025/01，提供竹節、格線及飾盤觀察。
- [李祖原聯合建築師事務所](https://www.cylee.com/project/Taipei-101?lang=tw) 與 [Council on Vertical Urbanism](https://www.skyscrapercenter.com/building/taipei-101/117)：508 公尺高度資料。
- [台北世貿中心](https://www.twtc.com.tw/about)：一館七層及外觀／室內照片，確認中央展場有覆蓋屋頂；館方照片拍攝日期未知。

以上外部影像權利屬原來源，僅供觀察，沒有包含在網站素材或來源套件中。查閱日期 2026-10-10，詳細方向與遮蔽限制見 [DESIGN.md](DESIGN.md)。

## 軟體與限制

- Three.js 0.180.0：MIT；完整聲明保留於 [THIRD_PARTY_NOTICES.txt](THIRD_PARTY_NOTICES.txt)，也嵌入示範 HTML。
- esbuild 0.25.10：MIT；作為建置依賴，版本鎖定於 package-lock.json。
- 不需 Google API 金鑰；沒有第三方字型、付費素材、攝影貼圖或影片。

這是外觀沙盤，非測繪或官方模型。未使用 Earth 尺規量測；平面尺寸、周邊高度、窗帶與不可見細部為視覺估算。夜間燈光位置和色彩為示意，不代表實際燈光排程。
