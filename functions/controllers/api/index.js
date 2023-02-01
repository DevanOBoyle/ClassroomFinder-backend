const client = require("../../utils/connection.js");
const express = require("express");
const cors = require("cors");

const app = express();
app.disable("x-powered-by");
app.use(express.json());

const corsOptions = {
  optionsSuccessStatus: 200,
};

app.use(cors(corsOptions));

// API CALLS HERE

client.connect();

app.get("/buildings", async (req, res) => {
  try {
    // TO DO: Get query headers from postgreSQL
    /*
    const buildings = await client.query("Get building data", (err, result));
    const buildingDocs = [];
    buildings.forEach((doc) => {
      data = doc.data();
      buildingDocs.push({
        //TO DO
        name: data.name,
      });
    });
    
    res.status(200).send({ status: 200, buildings: buildingDocs });
    */
    res.status(200).send({ status: 200, buildings: "Hello" });
  } catch (err) {
    res.status(500).send({ status: 500, error: "Unable to grab building data" });
    functions.logger.log(`Unable to retrieve building data`);
  }
  //client.end;
});

const port = process.env.PORT || 3000;
app.listen(port, () => console.log(`Listening on port ${port}`));
