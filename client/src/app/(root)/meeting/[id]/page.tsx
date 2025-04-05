"use client";
// import { role } from "@stream-io/video-react-sdk";
import { off } from "process";
import React, { useEffect, useReducer, useRef, use, useState } from "react";
import { FiVideo, FiVideoOff, FiMic, FiMicOff } from "react-icons/fi";
import { UUID } from "crypto";

type SendMessage = {
    type: string;
    message: string | null;
};

type ICECandidate = {
    type: string;
    candidate: string | null;
    sdpMid: string | null;
    sdpMlineIndex: number | null;
};

// === TESTING ONLY ===
const role: string | null = sessionStorage.getItem("role");
const user_id: string | null = sessionStorage.getItem("user_id");

const Meeting = ({ params }: { params: Promise<{ id: string }> }) => {
    const pc = useRef<RTCPeerConnection | null>(null);
    const localStream = useRef<MediaStream | null>(null);
    const startButton = useRef<HTMLButtonElement | null>(null);
    const hangupButton = useRef<HTMLButtonElement | null>(null);
    const muteAudButton = useRef<HTMLButtonElement | null>(null);
    const localVideo = useRef<HTMLVideoElement | null>(null);
    const remoteVideo = useRef<HTMLVideoElement | null>(null);
    const wsRef = useRef<WebSocket | null>(null);
    const [audiostate, setAudio] = useState(false);
    const { id } = use(params);

    const configuration = {
        iceServers: [
            {
                urls: ["stun:stun1.l.google.com:19302", "stun:stun2.l.google.com:19302"],
            },
        ],
        iceCandidatePoolSize: 10,
    };

    useEffect(() => {
        try {
            console.log("Creating a meeting ...");

            if (wsRef.current && wsRef.current.readyState <= 1) {
                console.log("WebSocket is already open or connecting...");
                return;
            }

            const ws: WebSocket = new WebSocket("ws://192.168.100.8:8000");
            wsRef.current = ws;
            ws.binaryType = "arraybuffer";

            // create or join room
            if (role == "create") {
                const createRoom = {
                    type: "create",
                    id: user_id!, // TESTING ONLY, later fetch from db
                };

                wsRef.current.send(JSON.stringify(createRoom));
            } else if (role == "join") {
                const joinRoom = {
                    type: "join",
                    id: crypto.randomUUID(),
                };

                wsRef.current.send(JSON.stringify(joinRoom));
            }

            ws.addEventListener("open", () => {
                const sendMsg: SendMessage = {
                    type: "connect",
                    message: "Hello server",
                };

                ws.send(JSON.stringify(sendMsg));

                const pingInterval = setInterval(() => {
                    if (ws.readyState === WebSocket.OPEN) {
                        ws.send(JSON.stringify({ type: "ping", message: null }));
                    } else {
                        clearInterval(pingInterval);
                        console.log("Ping stopped: socket closed");
                    }
                }, 5000);
            });

            ws.addEventListener("message", (event: MessageEvent) => {
                const message = JSON.parse(event.data);
                console.log(message);

                if (message.type == "pong") {
                    console.log("Pong received from server");
                }

                if (!localStream.current) {
                    console.log("not ready yet");
                    return;
                }

                switch (message.type) {
                    case "offer":
                        handleOffer(message, ws);
                        break;
                    case "answer":
                        handleAnswer(message);
                        break;
                    case "candidate":
                        handleCandidate(message);
                        break;
                    case "ready":
                        if (pc.current) {
                            console.log("already in call, ignoring");
                            return;
                        }
                        makeCall(ws);
                        break;
                    case "bye":
                        if (pc.current) {
                            hangup();
                        }
                }
            });

            ws.addEventListener("close", () => {
                console.log("WebSocket closed");
                // do something here
            });

            ws.addEventListener("error", (err) => {
                console.error("WebSocket error", err);
                // do something here
            });
        } catch (e) {
            console.error(`Meeting error : ${e}`);
        } finally {
            return () => {
                if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
                    wsRef.current.close();
                }
            };
        }
    }, []);

    const handleOffer = async (offer: any, ws: WebSocket) => {
        if (pc.current) {
            // peer connection has already been established
            console.error("existing peerconnection");
            return;
        }

        try {
            pc.current = new RTCPeerConnection(configuration);

            pc.current.onicecandidate = (e: RTCPeerConnectionIceEvent) => {
                const message: ICECandidate = {
                    type: "candidate",
                    candidate: null,
                    sdpMid: null,
                    sdpMlineIndex: null,
                };

                // if candidate exists
                if (e.candidate) {
                    message.candidate = e.candidate.candidate;
                    message.sdpMid = e.candidate.sdpMid;
                    message.sdpMlineIndex = e.candidate.sdpMLineIndex;
                }

                // send ICE to other peers via ws server
                ws.send(JSON.stringify(message));
            };

            pc.current.ontrack = (e) => (remoteVideo.current ? (remoteVideo.current.srcObject = e.streams[0]) : console.log("remoteVideo.current is null"));

            if (localStream.current) {
                localStream.current.getTracks().forEach((track: MediaStreamTrack) => pc.current!.addTrack(track, localStream.current!));
            } else {
                console.log("localstream is null");
            }

            await pc.current.setRemoteDescription(offer);

            const answer = await pc.current.createAnswer();
            ws.send(JSON.stringify({ type: "answer", sdp: answer.sdp }));

            await pc.current.setLocalDescription(answer);
        } catch (e) {
            console.error("Error handling offer : ", e);
        }
    };

    const handleAnswer = async (answer: RTCSessionDescriptionInit) => {
        if (!pc.current) {
            console.error("no peerconnection");
            return;
        }

        try {
            // set remote descx from the remote's answer
            await pc.current.setRemoteDescription(answer);
        } catch (e) {
            console.error("Error handling answer : ", e);
        }
    };

    const handleCandidate = async (candidate: RTCIceCandidate) => {
        try {
            if (!pc.current) {
                console.log("no peerconnection");
                return;
            }

            if (!candidate) {
                await pc.current.addIceCandidate(null);
            } else {
                await pc.current.addIceCandidate(candidate);
            }
        } catch (e) {
            console.error("Error handling candidate : ", e);
        }
    };

    async function makeCall(ws: WebSocket) {
        try {
            pc.current = new RTCPeerConnection(configuration);
            pc.current.onicecandidate = (e: RTCPeerConnectionIceEvent) => {
                const message: ICECandidate = {
                    type: "candidate",
                    candidate: null,
                    sdpMid: null,
                    sdpMlineIndex: null,
                };

                if (e.candidate) {
                    message.candidate = e.candidate.candidate;
                    message.sdpMid = e.candidate.sdpMid;
                    message.sdpMlineIndex = e.candidate.sdpMLineIndex;
                }

                ws.send(JSON.stringify(message));
            };

            // media stream track
            pc.current.ontrack = (e) => (remoteVideo.current ? (remoteVideo.current.srcObject = e.streams[0]) : console.log("remoteVideo.current is null"));

            if (localStream.current) {
                localStream.current.getTracks().forEach((track: MediaStreamTrack) => pc.current!.addTrack(track, localStream.current!));
            } else {
                console.log("localstream is null");
            }

            // if user is the creator of the room
            if (role == "create") {
                return;
            }

            // Offerer would make the offer
            const offer = await pc.current.createOffer();
            ws.send(JSON.stringify({ type: "offer", sdp: offer.sdp, user_id: user_id! }));
            await pc.current.setLocalDescription(offer);
        } catch (e) {
            console.error("Error making call: ", e);
        }
    }

    async function hangup() {
        if (pc.current) {
            pc.current.close();
            pc.current = null;
        }

        localStream.current && localStream.current.getTracks().forEach((track) => track.stop());
        localStream.current = null;
        startButton.current!.disabled = false;
        hangupButton.current!.disabled = true;
        muteAudButton.current!.disabled = true;
    }

    const startB = async () => {
        try {
            localStream.current = await navigator.mediaDevices.getUserMedia({
                video: true,
                audio: { echoCancellation: true },
            });

            localVideo.current!.srcObject = localStream.current;
        } catch (err) {
            console.error("Error starting a call : ", err);
        }

        startButton.current!.disabled = true;
        hangupButton.current!.disabled = false;
        muteAudButton.current!.disabled = false;
        wsRef.current!.send(JSON.stringify({ type: "ready" }));
    };

    const hangB = async () => {
        hangup();
        wsRef.current!.send(JSON.stringify({ type: "bye" }));
    };

    function muteAudio() {
        if (audiostate) {
            localVideo.current!.muted = true;
            setAudio(false);
        } else {
            localVideo.current!.muted = false;
            setAudio(true);
        }
    }

    useEffect(() => {
        if (hangupButton.current && muteAudButton.current) {
            hangupButton.current.disabled = true;
            muteAudButton.current.disabled = true;
        }
    }, []);

    return (
        <main className="w-screen h-screen flex justify-center">
            <div className="w-1/3 h-1/2 bg-white rounded-md mt-24 flex flex-col justify-between">
                <div className="border-2 border-red-600">
                    <video ref={localVideo} className="" autoPlay playsInline src=" "></video>
                    <video ref={remoteVideo} className="" autoPlay playsInline src=" "></video>
                </div>

                <div className="border-1 flex justify-center gap-12">
                    <button className="" ref={startButton} onClick={startB}>
                        <FiVideo className="w-6 h-6 cursor-pointer" />
                    </button>
                    <button className="" ref={hangupButton} onClick={hangB}>
                        <FiVideoOff className="w-6 h-6 cursor-pointer" />
                    </button>
                    <button className="" ref={muteAudButton} onClick={muteAudio}>
                        {audiostate ? <FiMic className="w-6 h-6 cursor-pointer" /> : <FiMicOff className="w-6 h-12 cursor-pointer" />}
                    </button>
                </div>
            </div>
        </main>
    );
};

export default Meeting;
