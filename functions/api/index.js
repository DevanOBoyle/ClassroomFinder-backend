// const credentials = require("../../utils/connection.js");
const dotenv = require("dotenv");
const express = require("express");
const cors = require("cors");
const { Client } = require("pg");

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
    const client = new Client({
      connectionString: process.env.CONNECTIONSTRING,
    });

    await client.connect();

    client.query(`select * from buildings`, (error, response) => {
      if (!error) {
        res.status(200).send({ status: 200, buildings: response.rows });
      } else {
        console.log("Error occured while querying building data");
      }
      client.end;
    });
  } catch (err) {
    res.status(500).send({ status: 500, error: "Unable to grab building data" });
    functions.logger.log(`Unable to retrieve building data`);
  }
});

query_classes("fall2022");
query_classes("winter2023");
query_classes("spring2023");

function query_classes(quarter) {
  app.get(`/${quarter}`, async (req, res) => {
    try {
      const client = new Client({
        connectionString: process.env.CONNECTIONSTRING,
      });
  
      await client.connect();
  
      client.query(`select * from classes_${quarter}`, (error, response) => {
        if (!error) {
          res.status(200).send({ status: 200, classes: response.rows });
        } else {
          console.log(`Error occured while querying ${quarter} data`);
        }
        client.end;
      });
    } catch (err) {
      res.status(500).send({ status: 500, error: `Unable to grab ${quarter} data` });
      functions.logger.log(`Unable to class ${quarter} data`);
    }
  });
}

const port = process.env.PORT || 5000;
app.listen(port, () => console.log(`Listening on port ${port}`));
