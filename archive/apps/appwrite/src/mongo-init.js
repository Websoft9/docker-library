// Switch to the admin database used during Appwrite MongoDB bootstrap.
const adminDb = db.getSiblingDB('admin');

const username = process.env.MONGO_INITDB_USERNAME;
const password = process.env.MONGO_INITDB_PASSWORD;
const database = process.env.MONGO_INITDB_DATABASE;

adminDb.createUser({
  user: username,
  pwd: password,
  roles: [{ role: 'readWrite', db: database }]
});
