const express = require('express');
const app = express();
const PORT = process.env.PORT || 3000;

app.get('/', (req, res) => {
    res.send('<h1>Tax Master V3 Online!</h1><p>Deploy realizado com sucesso no Railway.</p>');
});

app.get('/health', (req, res) => {
    res.json({ status: 'OK' });
});

app.listen(PORT, '0.0.0.0', () => {
    console.log(`Server running on port ${PORT}`);
});
