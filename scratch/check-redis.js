const Redis = require('ioredis');

// Reconstruct URL from application-dev.properties logic if possible, 
// but I'll just ask the user or try to find it.
// Actually, Redisson uses 'redis://...' format. upstash uses that too.

const redis = new Redis("rediss://default:AbG9AAIjcDE1ZDE2N2UxZTFiMmU0ODU3YjFlMGFjMWEyMWIwZjAwMXAxMA@hot-sunbird-92255.upstash.io:6379");

async function check() {
    try {
        const length = await redis.llen('submission-queue');
        console.log('Queue Length:', length);
        
        const items = await redis.lrange('submission-queue', 0, -1);
        console.log('Items:', items);
        
        process.exit(0);
    } catch (err) {
        console.error(err);
        process.exit(1);
    }
}

check();
