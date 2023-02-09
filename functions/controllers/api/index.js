const credentials = require("../../utils/connection.js");
const express = require("express");
const cors = require("cors");
const { Client } = require("pg");
const dotenv = require("dotenv");

const app = express();
app.disable("x-powered-by");
app.use(express.json());

const corsOptions = {
  optionsSuccessStatus: 200,
};

app.use(cors(corsOptions));

dotenv.config();

app.get("/buildings", async (req, res) => {
  try {
    // TO DO: Get query headers from postgreSQL
    const client = new Client({
      user: process.env.PGUSER,
      host: process.env.PGHOST,
      database: process.env.PGDATABASE,
      password: process.env.PGPASSWORD,
      port: process.env.PGPORT,
    });

    await client.connect();
    console.log("connected");
    const doc = await client.query(`SELECT * from buildings`, (error, result));
    /*
    const dummy_data = [
      { name: "Engineering 2" },
      { name: "Baskin Engineering" },
      { name: "Bio Room" },
      { name: "Mchenry Library" },
      { name: "Science and Engineering Library" },
      { name: "Stevenson" },
      { name: "Thimaan Lecture Hall" },
    ];
    */
    res.status(200).send({ status: 200, buildings: doc });
    await client.end();
  } catch (err) {
    res.status(500).send({ status: 500, error: "Unable to grab building data" });
    functions.logger.log(`Unable to retrieve building data`);
  }
});

const port = process.env.PORT || 5000;
app.listen(port, () => console.log(`Listening on port ${port}`));
