const express = require('express');
const axios = require('axios');
const Redis = require('redis');

const client = Redis.createClient();
const DEFAULT_EXPIRATION = 1440;
const PORT = 5000;

const app = express();

app.get("/cache_photos", async (req, res) => {
    const albumId = req.query.albumId;
    const key = `=${albumId}`;
    const photos = await memoise(key, async () => {
        const {data} = await axios.get(
            "https://jsonplaceholder.typicode.com/photos",
            {params: {albumId}}
        )
        return data;
    })

    res.json(photos);
})

app.get("/photos", async (req, res) => {
    const albumId = req.query.albumId;
    const {data} = await axios.get(
        "https://jsonplaceholder.typicode.com/photos",
        {params: {albumId}}
    )
    res.json(data);
});


function memoise(key, req) {
    return new Promise((resolve, reject) => {
        client.get(key, async (err, jobs) => {
            if (err)
                throw err;
            if (jobs)
                return resolve(JSON.parse(jobs));
            const freshData = await req();
            client.setex(key, DEFAULT_EXPIRATION, JSON.stringify(freshData));
            resolve(freshData);
        })
    })
}

app.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
});