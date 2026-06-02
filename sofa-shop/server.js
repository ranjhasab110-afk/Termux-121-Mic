const express = require('express');
const bodyParser = require('body-parser');
const multer = require('multer');
const path = require('path');
const fs = require('fs');
const app = express();
const PORT = 3000;

// تصویریں سیو کرنے کا سیٹ آپ
const uploadDir = './uploads';
if (!fs.existsSync(uploadDir)){
    fs.mkdirSync(uploadDir);
}

const storage = multer.diskStorage({
    destination: (req, file, cb) => { cb(null, uploadDir); },
    filename: (req, file, cb) => { cb(null, Date.now() + path.extname(file.originalname)); }
});
const upload = multer({ storage: storage });

app.use(bodyParser.urlencoded({ extended: true }));
app.use('/uploads', express.static('uploads'));

// صوفہ کورز کا ڈیٹا (Database)
let products = [
    { id: 1, title: "Luxury Cotton Sofa Cover", price: "4500", image: "" }
];
let comments = [];

// 1. کسٹمرز کے لیے مین ویب سائٹ
app.get('/', (req, res) => {
    let productHTML = products.map(p => `
        <div style="border: 1px solid #333; padding: 15px; border-radius: 8px; margin-bottom: 20px; background: #252525; text-align:center;">
            ${p.image ? `<img src="/uploads/${p.image}" style="max-width:100%; height:200px; object-fit:cover; border-radius:5px;"><br>` : ''}
            <h3>${p.title}</h3>
            <p>قیمت: ${p.price} PKR</p>
            <a href="https://wa.me/923024138106?text=Hi, I want to order ${p.title} for ${p.price} PKR" target="_blank" style="background: #25d366; color: white; padding: 10px 20px; border-radius: 5px; text-decoration: none; display: inline-block; font-weight: bold;">WhatsApp پر آرڈر کریں 💬</a>
        </div>
    `).join('');

    let commentHTML = comments.map(c => `<div style="background:#222; padding:10px; margin:5px 0; border-radius:5px; border-left:4px solid #ff4757;"><strong>${c.name}:</strong> ${c.text}</div>`).join('');

    res.send(`
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Sofa Cover Premium Store</title>
        <style>
            body { font-family: sans-serif; background: #121212; color: #fff; padding: 20px; }
            .container { max-width: 600px; margin: auto; background: #1e1e1e; padding: 20px; border-radius: 10px; }
            input, textarea { width: 90%; padding: 10px; margin: 10px 0; border-radius: 5px; border: 1px solid #444; background: #222; color: #fff; }
        </style>
    </head>
    <body>
        <div class="container">
            <h2 style="text-align:center;">VIP Sofa Cover House 🛋️</h2>
            <div>${productHTML}</div>
            <h3>Customer Reviews 💬</h3>
            <div>${commentHTML}</div>
            <form action="/add-comment" method="POST">
                <input type="text" name="name" placeholder="Your Name" required>
                <textarea name="text" placeholder="Your Comment..." rows="3" required></textarea>
                <button type="submit" style="background: #ff4757; color: white; border: none; padding: 10px; width: 95%; border-radius: 5px; cursor: pointer;">Post Comment</button>
            </form>
        </div>
    </body>
    </html>
    `);
});

app.post('/add-comment', (req, res) => {
    const { name, text } = req.body;
    if (name && text) comments.push({ name, text });
    res.redirect('/');
});

// 2. بھائی کے لیے سیکرٹ ایڈمن پینل (Owner Dashboard)
app.get('/admin-panel-secret', (req, res) => {
    let adminProductHTML = products.map(p => `
        <tr style="border-bottom: 1px solid #444;">
            <td>${p.title}</td>
            <td>${p.price} PKR</td>
            <td><a href="/delete-product/${p.id}" style="color:#ff4757;">حذف کریں</a></td>
        </tr>
    `).join('');

    res.send(`
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Owner Admin Dashboard</title>
        <style>
            body { font-family: sans-serif; background: #1e1e1e; color: #fff; padding: 20px; }
            .box { max-width: 600px; margin: auto; background: #2d2d2d; padding: 20px; border-radius: 8px; }
            input { width: 95%; padding: 10px; margin: 10px 0; background: #222; color: #fff; border: 1px solid #444; }
        </style>
    </head>
    <body>
        <div class="box">
            <h2>Sofa Cover Owner Settings ⚙️</h2>
            <p>یہاں سے آپ صوفہ کور کی قیمت اور تصویر بدل سکتے ہیں۔</p>
            
            <h3>نیا صوفہ کور ایڈ کریں:</h3>
            <form action="/add-product" method="POST" enctype="multipart/form-data">
                <input type="text" name="title" placeholder="صوفہ کور کا نام" required>
                <input type="number" name="price" placeholder="قیمت (مثال: 4500)" required>
                <label>صوفہ کور کی تصویر سلیکٹ کریں:</label>
                <input type="file" name="image" accept="image/*" required>
                <button type="submit" style="background:#25d366; color:white; padding:10px; border:none; width:100%; border-radius:5px; font-weight:bold;">ویب سائٹ پر لائیو کریں</button>
            </form>

            <h3>موجودہ پروڈکٹس:</h3>
            <table style="width:100%; border-collapse: collapse;">
                <tr style="background:#444;"><th>نام</th><th>قیمت</th><th>ایکشن</th></tr>
                ${adminProductHTML}
            </table>
        </div>
    </body>
    </html>
    `);
});

// پروڈکٹ ایڈ کرنے کا ہینڈلر
app.post('/add-product', upload.single('image'), (req, res) => {
    const { title, price } = req.body;
    const filename = req.file ? req.file.filename : '';
    if (title && price) {
        products.push({
            id: Date.now(),
            title: title,
            price: price,
            image: filename
        });
    }
    res.redirect('/admin-panel-secret');
});

// پروڈکٹ ڈیلیٹ کرنے کا ہینڈلر
app.get('/delete-product/:id', (req, res) => {
    products = products.filter(p => p.id != req.params.id);
    res.redirect('/admin-panel-secret');
});

app.listen(PORT, () => {
    console.log(`Server running on http://localhost:${PORT}`);
});

