"use strict";

const bodyParser = require("body-parser");
const expressSanitizer = require("express-sanitizer");
const methodOverride = require("method-override");
const express = require("express");
const request = require("request");
const cors = require("cors");
const pythonShell = require("python-shell");

const app = express();

// APP CONFIG
app.use(bodyParser.urlencoded({extended: true}));
app.use(expressSanitizer());
app.use(methodOverride("_method"));
app.use(cors());

app.use(express.static("dist"));

app.get("/", function (req, res) {
    res.render("index");
});

app.get("/api", function (req, res) {
    try {
    console.log(req.query);
    let article = req.sanitize(req.query.inputUrl);

    let options = {
        mode: 'text',
        pythonPath: '/home/ian/.virtualenvs/biasearch/bin/python',
        scriptPath: '/home/ian/BiaSearchApi/app',
        args: article
    };

    pythonShell.run('exp_get_matches.py', options, function (err, results) {
        if (err) console.log("PYTHON ERROR OCCURRED FETCHING ARTICLES");
        // if (err) throw err;

        // results is an array consisting of messages collected during execution
        let result_articles = [];
        let curr_article;
        if (results) {
            for (let i = 0; i < results.length; i++) {
                curr_article = {};
                curr_article.title = results[i];
                curr_article.url = results[++i];
                curr_article.imageUrl = results[++i];
                curr_article.source = results[++i];
                result_articles.push(curr_article);
            }

            let result_json = {"articles": result_articles};

            console.log(result_articles);

            res.setHeader('Content-Type', 'application/json');
            res.send(result_json);
        } else {
            res.send("ERROR FETCHING ARTICLES. PLEASE TRY AGAIN.")
        }
    });

    } catch (err) {
        res.send("ERROR FETCHING ARTICLES. PLEASE TRY AGAIN.")
    }

});

app.listen(3000, () => console.log("server has started!"));
