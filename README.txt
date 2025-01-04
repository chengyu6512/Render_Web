資料庫設定：
app.py中的程式碼 app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:123456@localhost:5432/my_hotel'
請根據自己的資料庫名稱密碼進行更改

開始執行：
執行檔案 app.py 後，終端會提供一個網址訪問伺服器URL，伺服器會根據 URL 路由匹配對應的 Flask 路由函數，並執行該函數來處理請求。

訪問首頁"/"，執行index()函數，db.session.query() 讀取所有訂房 (Booking) 和訪客 (Guest) 資料，並透過 join() 方法關聯兩張表格，獲取每筆資料，並將它們整理成一個 Python 字典列表 booking_data，render_template()將資料傳遞給 index.html，動態生成 HTML 頁面，顯示在瀏覽器上，在index.html頁面上，{% for booking in bookings %}會顯示目前所有的訂房資料，該頁面有兩個按鈕，Book a Room 按鈕，固定在頁面底部，連接 /booking 路由，進入訂房頁面；Clear All Bookings 按鈕，觸發 /clear_bookings POST 請求，清除所有資料(包含資料庫)。

訪問訂房頁面"/booking"，執行booking()函數，GET 請求為首次加載頁面時，呈現空白的 BookingForm 表單，POST 請求為當使用者提交表單時，執行 if form.validate_on_submit()，進行表單驗證。若驗證成功，將訪客資訊存入 Guest 資料表，並通過 db.session.flush() 獲取訪客 ID，使用訪客 ID 和表單資料，創建一條新的 Booking 記錄，然後執行 db.session.commit() 將資料提交至資料庫，提交成功後，使用 redirect(url_for('index')) 導回首頁。

按下 Clear All Bookings 按鈕時，發送 POST 請求到 /clear_bookings，該函數刪除所有 Booking 和 Guest 資料，並提交刪除，清空緩存和資料庫會話，最後重新導回首頁。