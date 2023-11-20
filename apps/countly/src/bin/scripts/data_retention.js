var async = require('async'),
    crypto = require('crypto'),
    plugins = require('../../plugins/pluginManager.js');

var Promise = require("bluebird");

Promise.all([plugins.dbConnection("countly"), plugins.dbConnection("countly_drill")]).spread(function(db, db_drill) {

    var W9_ID = "5d68e5012257c30a2f409e0e";
    var EXPIRE_AFTER = 365 * 24 * 60 * 60; //1 year in seconds
    var INDEX_NAME = "cd_1";

    var collections = [];
    collections.push("drill_events" + crypto.createHash('sha1').update("[CLY]_session" + W9_ID).digest('hex'));
    collections.push("drill_events" + crypto.createHash('sha1').update("[CLY]_crash" + W9_ID).digest('hex'));
    collections.push("drill_events" + crypto.createHash('sha1').update("[CLY]_view" + W9_ID).digest('hex'));
    collections.push("drill_events" + crypto.createHash('sha1').update("[CLY]_action" + W9_ID).digest('hex'));
    collections.push("drill_events" + crypto.createHash('sha1').update("[CLY]_push_action" + W9_ID).digest('hex'));
    collections.push("drill_events" + crypto.createHash('sha1').update("[CLY]_star_rating" + W9_ID).digest('hex'));
    collections.push("drill_events" + crypto.createHash('sha1').update("[CLY]_nps" + W9_ID).digest('hex'));
    collections.push("drill_events" + crypto.createHash('sha1').update("[CLY]_survey" + W9_ID).digest('hex'));
    db.collection("events").findOne({'_id': db.ObjectID(W9_ID)}, {list: 1}, function(err, eventData) {
        if (eventData && eventData.list) {
            for (var i = 0; i < eventData.list.length; i++) {
                collections.push("drill_events" + crypto.createHash('sha1').update(eventData.list[i] + W9_ID).digest('hex'));
            }
        }
        function eventIterator(collection, done) {
            console.log("processing", collection);
            db_drill.collection(collection).indexes(function(err, indexes) {
                if (!err && indexes) {
                    var hasIndex = false;
                    var dropIndex = false;
                    for (var i = 0; i < indexes.length; i++) {
                        if (indexes[i].name == INDEX_NAME) {
                            if (indexes[i].expireAfterSeconds == EXPIRE_AFTER) {
                                //print("skipping", c)
                                hasIndex = true;
                            }
                            //has index but incorrect expire time, need to be reindexed
                            else {
                                dropIndex = true;
                            }
                            break;
                        }
                    }
                    if (dropIndex) {
                        console.log("dropping index", collection);
                        db_drill.collection(collection).dropIndex(INDEX_NAME, function() {
                            console.log("creating index", collection);
                            db_drill.collection(collection).createIndex({"cd": 1}, {expireAfterSeconds: EXPIRE_AFTER, "background": true}, function() {
                                done();
                            });
                        });
                    }
                    else if (!hasIndex) {
                        console.log("creating index", collection);
                        db_drill.collection(collection).createIndex({"cd": 1}, {expireAfterSeconds: EXPIRE_AFTER, "background": true}, function() {
                            done();
                        });
                    }
                    else {
                        done();
                    }
                }
                else {
                    done();
                }
            });
        }
        async.eachSeries(collections, eventIterator, function() {
            db.close();
            db_drill.close();
        });
    });
});