const express = require("express");
const app = express();
const path = require("path");
const cors = require("cors");

app.use(express.json());
app.use(cors());

app.use(express.static(path.join(__dirname, "public")));

app.get("/", (req, res) => {
    res.send('Priya, kaash mein tumhe bataa sakta, mein tumhe kitna chahta hun I love you, I love you very very much Priya Mein aankhe band karta hun to tumhari yaad aati hai Aankhe kholta hun to tumhe dekhna chahta hun Tum paas nahi hoti to tumhe charo taraf mehsoos karta hun Har pal, har ghadi, har waqt — yeh aankhein sirf tumhe hi doondhti hain Kyunki tum hi ho jo meri nazar mein ho, meri rooh mein ho, mere dil mein ho Ise pyar kaho, paagalpan kaho, ya mere dil ki dhadkan — Mere liye ek hi baat hai Pyar to bahut log karte hain Lekin mere jaisa pyar koi nahi kar sakta Kyunki kisi ke paas tum jo nahi ho Mein tumhe bhool nahi sakta Priya Mein tumhe bhoolna hi nahi chahta Tum meri ho, mein tumhe zindagi bhar pyar karunga Marte dam tak pyar karunga — aur uske baad bhi')
});

app.listen(3000, () => {
    console.log("Server is running on port 3000");
});