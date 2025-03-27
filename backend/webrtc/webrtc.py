from aiortc import RTCPeerConnection, MediaStreamTrack
import asyncio
import cv2

class CustomVideoTrack(MediaStreamTrack):
    kind = "video"

    async def recv(self):
        frame = await self.next_frame()
        # frames can be manipulated to use the ai model
        return frame

class VideoStreamTrack(MediaStreamTrack):
    # Your implementation here to capture video frames
    pass

async def connect(peer_connection: RTCPeerConnection):
    offer = await peer_connection.createOffer()
    await peer_connection.setLocalDescription(offer)

    
    

async def main():
    peer_connection = RTCPeerConnection()
    video_track = VideoStreamTrack()
    peer_connection.addTrack(video_track)

    @peer_connection.on("track")
    def on_track(track):
        print("Received track:", track.kind)
        if track.kind == "video":
            pass
        elif track.kind == "audio":
            pass

    @peer_connection.on("icecandidate")
    def on_icecandidate(candidate):
        print("New ICE candidate : ", candidate)


    

if __name__ == "__main__":
    main()
