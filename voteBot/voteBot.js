const puppeteer = require('puppeteer-extra');
const StealthPlugin = require('puppeteer-extra-plugin-stealth');
puppeteer.use(StealthPlugin());

// List of realistic user agents
const userAgents = [
	'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
	'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
	'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36',
	'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.3 Safari/605.1.15',
	'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
	'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/109.0',
	'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/109.0'
];

// Helper function to get a random element from an array
const getRandomElement = (arr) => arr[Math.floor(Math.random() * arr.length)];

// Helper function for random delays
const getRandomDelay = (min, max) => Math.floor(Math.random() * (max - min + 1)) + min;

// Helper function for short "human-like" pauses
const shortPause = async () => {
	await new Promise(resolve => setTimeout(resolve, getRandomDelay(150, 600)));
};

// --- Main Function ---
(async () => {
	// Read configuration from environment variables
	const pollURL = process.env.POLLURL;
	const answerId = process.env.ANSWERID;
	const proxyUrl = process.env.PROXY_URL; // Optional proxy
	const minDelaySeconds = parseInt(process.env.MIN_DELAY || '5', 10); // Default 5 seconds
	const maxDelaySeconds = parseInt(process.env.MAX_DELAY || '20', 10); // Default 20 seconds

	if (!pollURL || !answerId) {
		console.error('Error: POLLURL and ANSWERID environment variables must be set.');
		process.exit(1);
	}

	console.log(`Starting Vote Bot for URL: ${pollURL}`);
	console.log(`Target Answer ID: ${answerId}`);
	console.log(`Delay between votes: ${minDelaySeconds} - ${maxDelaySeconds} seconds`);
	if (proxyUrl) {
		console.log(`Using Proxy: ${proxyUrl}`);
	}

	const launchOptions = {
		headless: true, // Consider 'new' for future Puppeteer versions, or false for debugging
		args: [
			'--no-sandbox',
			'--disable-setuid-sandbox',
			'--disable-infobars',
			'--window-position=0,0',
			'--ignore-certifcate-errors',
			'--ignore-certifcate-errors-spki-list',
			`--user-agent=${getRandomElement(userAgents)}` // Initial UA, will be overridden per page
		]
	};

	if (proxyUrl) {
		launchOptions.args.push(`--proxy-server=${proxyUrl}`);
	}

	let browser;
	try {
		browser = await puppeteer.launch(launchOptions);
		console.log('Browser launched.');

		let voteCount = 0;

		// Graceful shutdown handler
		process.on('SIGINT', async () => {
			console.log('\nCaught interrupt signal (Ctrl+C). Shutting down gracefully...');
			if (browser) {
				await browser.close();
				console.log('Browser closed.');
			}
			process.exit(0);
		});

		// Main voting loop
		while (true) {
			// let context = null; // Remove context variable
			let page = null; // Use page variable directly
			try {
				// context = await browser.createIncognitoBrowserContext(); // Remove this line
				// const page = await context.newPage(); // Remove this line
				page = await browser.newPage(); // Create a new page directly
				// console.log('\nNew incognito context and page created.'); // Update log message
				console.log('\nNew page created.'); // Updated log message

				// Randomize User Agent for this session
				const userAgent = getRandomElement(userAgents);
				await page.setUserAgent(userAgent);
				console.log(`Using User Agent: ${userAgent.substring(0, 50)}...`);

				// Randomize Viewport
				const width = getRandomDelay(1280, 1920);
				const height = getRandomDelay(720, 1080);
				await page.setViewport({ width, height });
				console.log(`Using Viewport: ${width}x${height}`);

				console.log(`Navigating to poll page: ${pollURL}`);
				await page.goto(pollURL, { waitUntil: 'networkidle2', timeout: 60000 }); // Increased timeout
				console.log('Page loaded.');

				await shortPause(); // Pause before interacting

				console.log(`Looking for answer element: #${answerId}`);
				await page.waitForSelector('#' + answerId, { timeout: 30000 }); // Increased timeout
				await shortPause(); // Pause after finding, before clicking
				await page.click('input#' + answerId);
				console.log('Answer chosen.');

				await shortPause(); // Pause before looking for vote button

				const voteButtonSelector = '#poll > div > div > div > div > main > form > div.css-vote.pds-vote > div > a';
				console.log(`Looking for vote button: ${voteButtonSelector}`);
				await page.waitForSelector(voteButtonSelector, { timeout: 30000 }); // Increased timeout
				await shortPause(); // Pause after finding, before clicking
				await page.click(voteButtonSelector);
				voteCount++;
				console.log(`Voted successfully! (Total votes this session: ${voteCount})`);

			} catch (error) {
				console.error('Error during voting attempt:', error.message);
				// Optional: Add more specific error handling if needed
			} finally {
				// if (context) { // Remove context check
				if (page) { // Check if page exists
					try {
						// await context.close(); // Remove context close
						await page.close(); // Close the page
						// console.log('Incognito context closed.'); // Update log message
						console.log('Page closed.'); // Updated log message
					} catch (closeError) {
						// console.error('Error closing context:', closeError.message); // Update log message
						console.error('Error closing page:', closeError.message); // Updated log message
					}
				}
			}

			// Randomized delay before next vote
			const delayMs = getRandomDelay(minDelaySeconds * 1000, maxDelaySeconds * 1000);
			const delaySec = (delayMs / 1000).toFixed(1);
			console.log(`Waiting for ${delaySec} seconds before next attempt...`);
			await new Promise(resolve => setTimeout(resolve, delayMs));
		}

	} catch (launchError) {
		console.error('Failed to launch browser:', launchError);
		process.exit(1);
	} finally {
		// This part might only be reached if the loop breaks unexpectedly,
		// SIGINT handler is the primary intended exit path.
		if (browser) {
			await browser.close();
			console.log('Browser closed during final cleanup.');
		}
	}
})();