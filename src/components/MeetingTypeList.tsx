'use client'
import React, { useState } from 'react'
import HomeCard from '../components/HomeCard';
import { useRouter } from 'next/navigation';
import MeetingModal from './MeetingModal';
import Image from 'next/image';
const MeetingTypeList = () => {
  const router = useRouter(); // Make sure to call useRouter() with parentheses
  const [meetingState, setMeetingState] = useState<'isScheduleMeeting' | 'isJoiningMeeting' | 'isInstantMeeting' | undefined>(undefined);

  const createMeeting = () => {
    // Your logic for creating a meeting here
    console.log("Creating meeting...");
  };

  return (
    <section className='grid grid-cols-1 gap-5 md:grid-cols-2 xl:grid-cols-4'>
      <HomeCard
        img="/icons/add-meeting.svg"
        title="New Meeting"
        description="Start an instant meeting"
        handleClick={() => {
          setMeetingState('isInstantMeeting');
        }}
      />
      <HomeCard
        img="/icons/join-meeting.svg"
        title="Join Meeting"
        description="via invitation link"
        className="bg-blue-700"
        handleClick={() => {
          setMeetingState('isJoiningMeeting');
        }}
      />
      <HomeCard
        img="/icons/schedule.svg"
        title="Schedule Meeting"
        description="Plan your meeting"
        className="bg-purple-600"
        handleClick={() => {setMeetingState('isScheduleMeeting');}}
      />
      <HomeCard
        img="/icons/recordings.svg"
        title="View Recordings"
        description="Meeting Recordings"
        className="bg-yellow-600"
        // handleClick={() => router.push('/recordings')}
      />
      <MeetingModal
        isOpen={meetingState === 'isScheduleMeeting'} // This condition should trigger the modal
        onClose={() => setMeetingState(undefined)}
        title="Create Meeting"
        handleClick={createMeeting}
      />
        <MeetingModal
        isOpen={meetingState === 'isJoiningMeeting'} // This condition should trigger the modal
        onClose={() => setMeetingState(undefined)}
        title="Create Meeting"
        handleClick={createMeeting}
      />
        <MeetingModal
        isOpen={meetingState === 'isInstantMeeting'} // This condition should trigger the modal
        onClose={() => setMeetingState(undefined)}
        title="Create Meeting"
        handleClick={createMeeting}
      />
    </section>
  );
}

export default MeetingTypeList;
