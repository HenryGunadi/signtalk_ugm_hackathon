"use client";
import React, { useEffect, useReducer, useRef, use } from "react";

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

const Meeting = ({ params }: { params: Promise<{ id: string }> }) => {
    const wsRef = useRef<WebSocket | null>(null);
    const { id } = use(params);
    const configuration = {
        iceServers: [
            {
                urls: ["stun:stun1.l.google.com:19302", "stun:stun2.l.google.com:19302"],
            },
        ],
        iceCandidatePoolSize: 10,
    };
    let pc: RTCPeerConnection;
    let localStream;
    let startButton;
    let hangupButton;
    let muteAudButton;
    let remoteVideo;
    let localVideo;

    useEffect(() => {
        try {
            console.log("Creating a meeting ...");

            if (wsRef.current && wsRef.current.readyState <= 1) {
                console.log("WebSocket is already open or connecting...");
                return;
            }

            const ws: WebSocket = new WebSocket("ws://localhost:8000");
            wsRef.current = ws;

            ws.binaryType = "arraybuffer";

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

                switch (message.type) {
                    case "pong":
                        console.log("Pong received from server");
                        break;
                    case "offer":
                        handleOffer();
                        break;
                    case "answer":
                        handleAnswer();
                        break;
                    case "candidate":
                        handleCandidate();
                        break;
                    default:
                        console.log("unhandled data type : ", message);
                        break;
                }
            });

            ws.addEventListener("close", () => {
                console.log("WebSocket closed");
            });

            ws.addEventListener("error", (err) => {
                console.error("WebSocket error", err);
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

    const handleOffer = (offer: any, ws: WebSocket) => {
        if (pc) {
            // peer connection has already been established
            console.error("existing peerconnection");
            return;
        }
        try {
            pc = new RTCPeerConnection(configuration);

            pc.onicecandidate = (e: RTCPeerConnectionIceEvent) => {
                const message: ICECandidate = {
                    type: "candidate",
                    candidate: null,
                    sdpMid: null,
                    sdpMlineIndex: null,
                };

                // if there candidate exists
                if (e.candidate) {
                    message.candidate = e.candidate.candidate;
                    message.sdpMid = e.candidate.sdpMid;
                    message.sdpMlineIndex = e.candidate.sdpMLineIndex;
                }

                // send ICE to other peers via ws server
                ws.send(JSON.stringify(message));
            };
        } catch (e) {
            console.error("Error handling offer : ", e);
        }
    };

    const handleAnswer = () => {};

    const handleCandidate = () => {};

    return <div className=" text-white">Meeting Room: #{id}</div>;
};

export default Meeting;
