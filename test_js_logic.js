const data = {
    "date": "2026-01-17T03:28:18.401682+00:00",
    "timestamp": 1768620498.401711
};

// Mock browser environment logic
function formatDate(data) {
    let dateStr = 'Unknown';
    try {
        if (data.timestamp) {
            dateStr = new Date(data.timestamp * 1000).toLocaleString(); // Uses system locale (likely UTC in sandbox)
        } else if (data.date) {
            dateStr = new Date(data.date).toLocaleString();
        }
    } catch (e) {
        dateStr = data.date || 'Unknown';
    }
    return dateStr;
}

console.log("Mocked Output (System Locale):", formatDate(data));

// To simulate Peru, we can set TZ env var if running in bash, but here inside node we can test specific locales if available.
// However, node in sandbox might be limited.
// Let's try to verify if the Date object correctly identifies the UTC input.

const d = new Date(data.timestamp * 1000);
console.log("ISO String:", d.toISOString());
console.log("UTC String:", d.toUTCString());
