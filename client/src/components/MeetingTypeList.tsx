"use client";
import React, { useEffect, useRef, useState } from "react";
import HomeCard from "./Homecard";
import { useRouter } from "next/navigation";
import MeetingModal from "./MeetingModal";
import Image from "next/image";
import { json } from "stream/consumers";
import { send } from "process";
import axios from "axios";
import { name } from "@stream-io/video-react-sdk";

const secretKey = process.env.NEXT_PUBLIC_SECRET_KEY;

const MeetingTypeList = () => {
    const router = useRouter(); // Make sure to call useRouter() with parentheses
    const [meetingState, setMeetingState] = useState<"isScheduleMeeting" | "isJoiningMeeting" | "isInstantMeeting" | undefined>(undefined);
    const createMeeting = async (): Promise<void> => {
        // send http req post to server to make a meeting
        try {
            const data = {
                name: "testingaja",
            };

            const response = await axios.post("http://localhost:8080/create_room", data, {
                headers: {
                    "Content-Type": "application/json",
                    Authorization: "Bearer YOUR_TOKEN_HERE", // FIX IT LATER!
                    "Custom-Header": "HelloFromClient",
                },
                withCredentials: true,
            });

            router.push(`/meeting/${response.data.room_id}`);
        } catch (e) {
            console.error(`Error creating a meeting room : ${e}`);
            return;
        }
    };

    return (
        <section className="grid grid-cols-1 gap-5 md:grid-cols-2 xl:grid-cols-4">
            <HomeCard
                img="/icons/add-meeting.svg"
                title="New Meeting"
                description="Start an instant meeting"
                handleClick={() => {
                    setMeetingState("isInstantMeeting");
                }}
            />
            <HomeCard
                img="/icons/join-meeting.svg"
                title="Join Meeting"
                description="via invitation link"
                className="bg-blue-700"
                handleClick={() => {
                    setMeetingState("isJoiningMeeting");
                }}
            />
            <HomeCard
                img="/icons/schedule.svg"
                title="Schedule Meeting"
                description="Plan your meeting"
                className="bg-purple-600"
                handleClick={() => {
                    setMeetingState("isScheduleMeeting");
                }}
            />
            <HomeCard
                img="/icons/recordings.svg"
                title="View Recordings"
                description="Meeting Recordings"
                className="bg-yellow-600"
                // handleClick={() => router.push('/recordings')}
            />
            <MeetingModal
                isOpen={meetingState === "isScheduleMeeting"} // This condition should trigger the modal
                onClose={() => setMeetingState(undefined)}
                title="Create Meeting"
                handleClick={() => {
                    router.push("/");
                }}
            />
            <MeetingModal
                isOpen={meetingState === "isJoiningMeeting"} // This condition should trigger the modal
                onClose={() => setMeetingState(undefined)}
                title="Create Meeting"
                // handleClick={() =>}
            />
            <MeetingModal
                isOpen={meetingState === "isInstantMeeting"} // This condition should trigger the modal
                onClose={() => setMeetingState(undefined)}
                title="Create Meeting"
                // handleClick={createMeeting}
            />
        </section>
    );
};

export default MeetingTypeList;
