import type {NextConfig} from 'next';

const nextConfig: NextConfig = {
	// other options...
	experimental: {
		// 👇 Add your ngrok domain here
		allowedDevOrigins: ['holy-hyena-nicely.ngrok-free.app'],
	},
};

export default nextConfig;
