const jwt = require('jsonwebtoken');

const payload = {
    "sub": "dev-user",
    "name": "Developer",
    "aud": "local-dev",
    "iss": "http://localhost:3000/",
    "localhost/agent": "dhruv@example.com"
};

const token = jwt.sign(payload, 'dev-only-secret', { expiresIn: '1h', algorithm: 'HS256' });
console.log("JWT Token:", token);
