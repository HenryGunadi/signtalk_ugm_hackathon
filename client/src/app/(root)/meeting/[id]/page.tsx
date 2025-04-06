'use client';
// import { role } from "@stream-io/video-react-sdk";
import {off} from 'process';
import React, {useEffect, useReducer, useRef, use, useState} from 'react';
import {FiVideo, FiVideoOff, FiMic, FiMicOff} from 'react-icons/fi';
import {UUID} from 'crypto';

type SendMessage = {
	type: string;
	message: string | null;
};

type ICECandidate = {
	type: string;
	candidate: string | null;
	sdpMid: string | null;
	sdpMlineIndex: number | null;
	user_id: string;
};

type OfferAnswerMessage = {
	type: string;
	sdp: RTCSessionDescriptionInit;
	user_id: string;
};

type Connection = {
	user_id: string;
	pc: RTCPeerConnection;
};

// === TESTING ONLY ===
const role: string | null = localStorage.getItem('role');
const storedId = localStorage.getItem('user_id');
const user_id: number | null = storedId ? parseInt(storedId) : null;

const Meeting = ({params}: {params: Promise<{id: string}>}) => {
	const pcs = useRef<Set<Connection>>(new Set());
	const localStream = useRef<MediaStream | null>(null);
	const startButton = useRef<HTMLButtonElement | null>(null);
	const hangupButton = useRef<HTMLButtonElement | null>(null);
	const muteAudButton = useRef<HTMLButtonElement | null>(null);
	const localVideo = useRef<HTMLVideoElement | null>(null);
	const remoteVideo = useRef<HTMLVideoElement | null>(null);
	const wsRef = useRef<WebSocket | null>(null);
	const [audiostate, setAudio] = useState(false);
	const {id} = use(params);

	const configuration = {
		iceServers: [
			{
				urls: ['stun:stun1.l.google.com:19302', 'stun:stun2.l.google.com:19302'],
			},
		],
		iceCandidatePoolSize: 10,
	};

	useEffect(() => {
		try {
			if (role == 'create') {
				console.log('Creating a meeting ...');
			} else {
				console.log('Joining the meeting ...');
			}

			if (wsRef.current && wsRef.current.readyState <= 1) {
				console.log('WebSocket is already open or connecting...');
				return;
			}

			// change wss to ws if not using ngrok uri
			// const ws: WebSocket = new WebSocket('wss://192.168.100.9:8000');
			const ws = new WebSocket(`${window.location.origin.replace('http', 'ws')}/ws`);

			wsRef.current = ws;
			ws.binaryType = 'arraybuffer';
			const room_id: number = parseInt(id);

			ws.addEventListener('open', async () => {
				console.log(`User ID : ${user_id} connected!`);

				// create or join room
				if (role == 'create') {
					const createRoom = {
						type: 'create',
						id: user_id, // TESTING ONLY, later fetch from db
						room_id: room_id,
					};

					if (wsRef.current) {
						wsRef.current.send(JSON.stringify(createRoom));
					}
				} else if (role == 'join') {
					console.log('ROOM ID IN JOIN CIENT : ', room_id);

					const joinRoom = {
						type: 'join',
						id: user_id,
						room_id: room_id,
					};

					if (wsRef.current) {
						wsRef.current.send(JSON.stringify(joinRoom));
					}
				}

				const sendMsg: SendMessage = {
					type: 'connect',
					message: 'Hello server',
				};

				ws.send(JSON.stringify(sendMsg));

				// ping pong intervals
				const pingInterval = setInterval(() => {
					if (ws.readyState === WebSocket.OPEN) {
						ws.send(JSON.stringify({type: 'ping', message: null}));
					} else {
						clearInterval(pingInterval);
						console.log('Ping stopped: socket closed');
					}
				}, 5000);

				// immediately get local stream
				try {
					console.log('localVideo ref:', localVideo.current);

					localStream.current = await navigator.mediaDevices.getUserMedia({
						video: true,
						audio: {echoCancellation: true},
					});

					if (localVideo.current) {
						localVideo.current.srcObject = localStream.current;
					}
				} catch (err) {
					alert('Permission to use camera/mic was denied or failed.');
					console.error("User's devices crashed or blocked: ", err);
					console.error("User's devices crashed or blocked : ", err);
				}

				startButton.current!.disabled = true;
				hangupButton.current!.disabled = false;
				muteAudButton.current!.disabled = false;

				wsRef.current!.send(JSON.stringify({type: 'ready'}));
			});

			ws.addEventListener('message', (event: MessageEvent) => {
				const message = JSON.parse(event.data);
				console.log(message);

				if (message.type == 'pong') {
					console.log('Pong received from server');
				}

				if (!localStream.current) {
					console.log('not ready yet');
					return;
				}

				switch (message.type) {
					case 'offer':
						handleOffer(message, ws); // <-- receive offer
						break;
					case 'answer':
						handleAnswer(message);
						break;
					case 'candidate':
						handleCandidate(message);
						break;
					case 'ready': // <-- someone has joined and ready to be offered
						offerCallConnection(ws, message.user_id);
						break;
					case 'bye':
						hangup();
				}
			});

			ws.addEventListener('close', () => {
				console.log('WebSocket closed');
				// do something here
			});

			ws.addEventListener('error', (err) => {
				console.error('WebSocket error', err);
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

	function searchConnection(message: OfferAnswerMessage | ICECandidate | {user_id: string}): Connection | null {
		for (const connection of pcs.current) {
			if (connection.user_id == message.user_id) {
				return connection;
			}
		}

		return null;
	}

	const handleOffer = async (offer: OfferAnswerMessage, ws: WebSocket) => {
		try {
			const connection = searchConnection(offer);
			if (!connection) return;

			const pc: RTCPeerConnection = new RTCPeerConnection(configuration);
			pcs.current.add({user_id: offer.user_id, pc: pc});

			pc.onicecandidate = (e: RTCPeerConnectionIceEvent) => {
				const message: ICECandidate = {
					type: 'candidate',
					candidate: null,
					sdpMid: null,
					sdpMlineIndex: null,
					user_id: offer.user_id,
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

			pc.ontrack = (e) =>
				remoteVideo.current ? (remoteVideo.current.srcObject = e.streams[0]) : console.log('remoteVideo.current is null');

			if (localStream.current) {
				localStream.current.getTracks().forEach((track: MediaStreamTrack) => pc.addTrack(track, localStream.current!));
			} else {
				console.log('localstream is null');
			}

			await pc.setRemoteDescription(offer.sdp);

			const answer = await pc.createAnswer();
			ws.send(JSON.stringify({type: 'answer', sdp: answer.sdp}));

			await pc.setLocalDescription(answer);
		} catch (e) {
			console.error('Error handling offer : ', e);
		}
	};

	const handleAnswer = async (answer: OfferAnswerMessage) => {
		try {
			const connection = searchConnection(answer);

			if (connection) {
				await connection.pc.setRemoteDescription(answer.sdp);
			}
		} catch (e) {
			console.error('Error handling answer : ', e);
		}
	};

	const handleCandidate = async (candidate: ICECandidate) => {
		try {
			const connection = searchConnection(candidate);

			if (connection) {
				if (!candidate.candidate) {
					await connection.pc.addIceCandidate(null);
				} else {
					const iceCandidateInit: RTCIceCandidateInit = {
						candidate: candidate.candidate,
						sdpMid: candidate.sdpMid,
						sdpMLineIndex: candidate.sdpMlineIndex,
					};

					await connection.pc.addIceCandidate(iceCandidateInit);
				}
			}
		} catch (e) {
			console.error('Error handling candidate : ', e);
		}
	};

	async function offerCallConnection(ws: WebSocket, user_id: string) {
		try {
			const connection = searchConnection({user_id: user_id});

			// connection already exists
			if (connection) {
				return;
			}

			const pc = new RTCPeerConnection(configuration);
			const newConnection: Connection = {
				user_id: user_id,
				pc: pc,
			};

			pcs.current.add(newConnection);

			pc.onicecandidate = (e: RTCPeerConnectionIceEvent) => {
				const message: ICECandidate = {
					type: 'candidate',
					candidate: null,
					sdpMid: null,
					sdpMlineIndex: null,
					user_id: user_id,
				};

				if (e.candidate) {
					message.candidate = e.candidate.candidate;
					message.sdpMid = e.candidate.sdpMid;
					message.sdpMlineIndex = e.candidate.sdpMLineIndex;
				}

				ws.send(JSON.stringify(message));
			};

			// media stream track
			pc.ontrack = (e) =>
				remoteVideo.current ? (remoteVideo.current.srcObject = e.streams[0]) : console.log('remoteVideo.current is null');

			if (localStream.current) {
				localStream.current.getTracks().forEach((track: MediaStreamTrack) => pc.addTrack(track, localStream.current!));
			} else {
				console.log('localstream is null');
			}

			const offer = await pc.createOffer();
			ws.send(JSON.stringify({type: 'offer', sdp: offer.sdp, user_id: user_id!}));
			await pc.setLocalDescription(offer);
		} catch (e) {
			console.error('Error making call: ', e);
		}
	}

	async function hangup() {
		for (const connection of pcs.current) {
			connection.pc.close();
		}
		pcs.current.clear();

		localStream.current && localStream.current.getTracks().forEach((track) => track.stop());
		localStream.current = null;
		startButton.current!.disabled = false;
		hangupButton.current!.disabled = true;
		muteAudButton.current!.disabled = true;
	}

	// const startB = async () => {};

	const hangB = async () => {
		hangup();
		wsRef.current!.send(JSON.stringify({type: 'bye'}));
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
					<button className="" ref={startButton}>
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
