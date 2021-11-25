db.createUser({
    user: 'root',
    pwd: 'toor',
    roles: [
        {
            role: 'readWrite',
            db: 'logshipping',
        },
    ],
});

db = new Mongo().getDB("logshipping");

db.createCollection('lsdb', { capped: false });

db.lsdb.insert([
    {
        _id: "lsdb",
        driver: "FreeTDS",
        server: "SQLMASTERc",
        port: "1433",
        ls_database: "LSDB",
        user: "SA",
        password: "Root05211840000048",
        trusted_conn: "no"
    }
]);