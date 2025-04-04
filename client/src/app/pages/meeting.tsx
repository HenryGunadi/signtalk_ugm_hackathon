import React, { useEffect, useReducer, useRef } from "react";

type SendMessage = {
    type: string;
    message: string | null;
};

const Meeting = ({ params }: { params: { id: string } }) => {
    const wsRef = useRef<WebSocket | null>(null);

    useEffect(() => {
        try {
            console.log("Creating a meeting ...");

            if (wsRef.current && wsRef.current.readyState <= 1) {
                console.log("WebSocket is already open or connecting...");
                return;
            }

            const ws = new WebSocket("ws://localhost:8000");
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

                if (message.type === "pong") {
                    console.log("Pong received from server");
                }

                console.log("Message from server:", message);
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

    const configuration = {
        iceServers: [
            {
                urls: ["stun:stun1.l.google.com:19302", "stun:stun2.l.google.com:19302"],
            },
        ],
        iceCandidatePoolSize: 10,
    };

    let pc;
    let localStream;
    let startButton;
    let hangupButton;
    let muteAudButton;
    let remoteVideo;
    let localVideo;

    return <div className=" text-white">Meeting Room: #{params.id}</div>;
};

export default Meeting;
