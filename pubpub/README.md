Use instructions

1. set `PUBPUB_USERNAME` (email), `PUBPUB_PASSWORD`, and `PUBPUB_BASE_URL` (eg. https://metagov.pubpub.org) environment variables or in .env file
2. make sure user is an administrator to gain access to protected API endpoints

*NOTE* The CryptoJS library used by the PubPub API has implemented an outdated version of SHA-3. Since the API requires the password to be hashed client side before logging in, the Python hash function must match. This can be found in the pycryptodome Keccak 512 bit hash function.