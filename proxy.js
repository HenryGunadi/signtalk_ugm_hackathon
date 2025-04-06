// proxy.js
const http = require('http');
const httpProxy = require('http-proxy');
const url = require('url');

const proxy = httpProxy.createProxyServer({});
const server = http.createServer((req, res) => {
	const parsedUrl = url.parse(req.url);

	if (parsedUrl.pathname.startsWith('/api')) {
		req.url = req.url.replace('/api', ''); // 👈 Strip "/api"
		proxy.web(req, res, {target: 'http://localhost:8080'});
	} else if (parsedUrl.pathname.startsWith('/ws')) {
		proxy.web(req, res, {target: 'http://localhost:8000', ws: true});
	} else {
		proxy.web(req, res, {target: 'http://localhost:3000'});
	}
});

server.on('upgrade', (req, socket, head) => {
	const parsedUrl = url.parse(req.url);

	if (parsedUrl.pathname.startsWith('/ws')) {
		proxy.ws(req, socket, head, {target: 'http://localhost:8000'});
	}
});

server.listen(8081, () => {
	console.log('Unified Proxy running at http://localhost:8081');
});
