echo "Add your CI code here, below is example"

cat > app.js <<EOF
const http = require('http');
const port = 8080;

const server = http.createServer((req, res) => {
    res.writeHead(200, { 'Content-Type': 'text/plain' });
    res.write('Hello World!');
    res.end();
});

server.listen(port, () => {
    console.log(\`Example app listening on port \${port}\`);
});
EOF

node app.js

## Sample One: Express

# npm install express --save
# cat > app.js <<EOF
# const express = require('express')
# const app = express()
# const port = 8080

# app.get('/', (req, res) => {
#   res.send('Hello World!')
# })

# app.listen(port, () => {
#   console.log(\`Example app listening on port \${port}\`)
# })
# EOF
# node app.js



## Sample Two: docusaurus

# #1 Create framework
# npx create-docusaurus@latest classic

# #2 Install packages
# cd classic && yarn install

# #3 Running for test
# npm run start -- --host 0.0.0.0  --port 8080