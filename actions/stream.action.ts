'use server';

import { StreamVideoClient } from "@stream-io/video-react-sdk";

const apiKey = process.env.NEXT_PUBLIC_STREAM_API_KEY;
const apiSecret = process.env.STREAM_SECRET_KEY;

export const tokenProvider = async () => {
    if (!apiKey) throw new Error('Stream API key secret is missing');
  if (!apiSecret) throw new Error('Stream API secret is missing');

  const client = new StreamVideoClient( apiKey);
}