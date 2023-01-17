const express = require('express')
const app = express()
const port = 8000

app.get('/ping/', (req, res) => {
    res.send('pong')
})

app.get('/to_json/', (req, res) => {
    if (req.query.token !== 'hardcoded_token') {
        res.send('{description: "unauthorized"}', 403);
        return;
    }
    let data = {
        param1: req.query.param1,
        param2: req.query.param2,
        param3: req.query.param3
    }
    res.send(data);;
});

app.get('/plain/', (req, res) => {
    if (req.query.token !== 'hardcoded_token') {
        res.send('{description: "unauthorized"}', 403);
        return;
    }
    let param1 = req.query.param1;
    let param2 = req.query.param2;
    let param3 = req.query.param3;
    res.send(`param1=${param1}, param2=${param2}, param3=${param3}`);
});

app.listen(port, () => {
  console.log(`app listening on port ${port}`)
})