// api/lectures.js
// This file should be placed in an 'api' directory at the root of your Vercel project.

module.exports = async (req, res) => {
    // Set CORS headers to allow requests from your frontend
    // In production, replace '*' with your specific Vercel domain (e.g., 'https://your-app.vercel.app')
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

    // Handle preflight OPTIONS request (required for CORS)
    if (req.method === 'OPTIONS') {
        return res.status(200).end();
    }

    const { uid } = req.query;

    if (!uid) {
        return res.status(400).json({ error: 'UID is required' });
    }

    try {
        const unacademyApiUrl = `https://unacademy.com/api/v3/collection/${uid}/items?limit=600`;
        
        // Use a timeout for the fetch request to prevent hanging
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 10000); // 10 seconds timeout

        const response = await fetch(unacademyApiUrl, { signal: controller.signal });
        clearTimeout(timeoutId); // Clear the timeout if fetch completes in time

        if (!response.ok) {
            // Attempt to parse error details from Unacademy's response
            let errorDetails = response.statusText;
            try {
                const errorJson = await response.json();
                if (errorJson && errorJson.message) {
                    errorDetails = errorJson.message;
                } else if (errorJson && typeof errorJson === 'string') {
                    errorDetails = errorJson;
                }
            } catch (e) {
                // If response is not JSON, just use statusText
            }
            console.error(`Unacademy API error for UID ${uid}: ${response.status} - ${errorDetails}`);
            return res.status(response.status).json({
                error: `Failed to fetch from Unacademy API`,
                details: errorDetails,
                statusCode: response.status
            });
        }

        const data = await response.json();
        res.status(200).json(data);
    } catch (error) {
        console.error('Proxy server error:', error);
        if (error.name === 'AbortError') {
            res.status(504).json({ error: 'Request to Unacademy API timed out', details: error.message });
        } else {
            res.status(500).json({ error: 'Internal server error while fetching lectures', details: error.message });
        }
    }
};
