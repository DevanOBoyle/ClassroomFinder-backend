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

// query_classes("fall2022");
// query_classes("winter2023");
// query_classes("spring2023");

app.get("/rooms", async (req, res) => {
  try {
    const client = new Client({
      connectionString: process.env.CONNECTIONSTRING,
    });

    await client.connect();

    client.query(`select * from rooms R join buildings B on R.building_number = B.number`, (error, response) => {
      if (!error) {
        res.status(200).send({ status: 200, buildings: response.rows });
      } else {
        console.log("Error occured while querying room data");
      }
      client.end;
    });
  } catch (err) {
    res.status(500).send({ status: 500, error: "Unable to grab room data" });
    functions.logger.log(`Unable to retrieve room data`);
  }
});

app.get("/classes/:term", async (req, res) => {
  try {
    const client = new Client({
      connectionString: process.env.CONNECTIONSTRING,
    });

    await client.connect();

    client.query(`select * from classes_${req.params.term} C 
    join instructors_${req.params.term} I on C.number = I.class_number 
    join meetings_${req.params.term} M on C.number = M.class_number`, (error, response) => {
      if (!error) {
        res.status(200).send({ status: 200, classes: response.rows });
      } else {
        console.log(`Error occured while querying ${req.params.term} data`);
      }
      client.end;
    });
  } catch (err) {
    res.status(500).send({ status: 500, error: `Unable to grab ${req.params.term} data` });
    functions.logger.log(`Unable to class ${req.params.term} data`);
  }
});

const port = process.env.PORT || 5000;
app.listen(port, () => console.log(`Listening on port ${port}`));
