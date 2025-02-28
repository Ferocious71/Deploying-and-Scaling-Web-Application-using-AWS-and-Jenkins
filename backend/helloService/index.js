const express = require('express');
require('dotenv').config();
const mongoose = require('mongoose');
const cors = require('cors');

const app = express();
app.use(cors());
app.use(express.json());

const PORT = process.env.PORT || 5001;  // Use environment variable
const MONGO_URI = process.env.MONGO_URI;

// Connect to MongoDB
mongoose.connect(MONGO_URI, {
    useNewUrlParser: true,
    useUnifiedTopology: true,
})
.then(() => console.log(`✅ MongoDB Connected to HelloService`))
.catch(err => console.error(`❌ MongoDB Connection Error:`, err));

// Routes
app.get('/', (req, res) => {
    res.send({ msg: 'Hello from Hello Service' });
});

app.listen(PORT, () => {
    console.log(`✅ Hello Service is running on port ${PORT}`);
});
