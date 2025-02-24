const crypto = require('crypto');

function generateRandomString(length) {
    return crypto.randomBytes(Math.ceil(length / 2))
        .toString('hex')
        .slice(0, length);
}

function generateVisitorData() {
    // Generate a random visitor ID (similar to YouTube's format)
    const timestamp = Math.floor(Date.now() / 1000);
    const randomId = generateRandomString(16);
    return `CgT${timestamp}${randomId}`;
}

function generatePoToken() {
    // Generate a random PO token (similar format to YouTube's)
    return generateRandomString(32);
}

const result = {
    visitorData: generateVisitorData(),
    poToken: generatePoToken()
};

// Output as JSON
console.log(JSON.stringify(result));