const express = require("express");

const buildings = express();
buildings.disable("x-powered-by");
buildings.use(express.json());

// API CALLS HERE

const service = functions.https.onRequest(buildings);

module.exports = { buildings, service };
