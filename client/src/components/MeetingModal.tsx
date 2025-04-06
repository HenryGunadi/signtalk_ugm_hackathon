'use client';
import React, {ReactNode} from 'react';
import {Dialog, DialogContent} from './ui/dialog';
import {cn} from '@/lib/utils';
import {Button} from './ui/button';
import Image from 'next/image';
import {DialogTitle} from '@radix-ui/react-dialog';
import {Input} from './ui/input';

interface MeetingModalProps {
	isOpen: boolean;
	onClose: () => void;
	title: string;
	className?: string;
	children?: ReactNode;
	handleClick?: () => void;
	buttonText?: string;
	instantMeeting?: boolean;
	image?: string;
	buttonClassName?: string;
	buttonIcon?: string;
	handleInput?: (e: React.ChangeEvent<HTMLInputElement>) => void;
	meetingID?: string;
}

const MeetingModal = ({
	isOpen,
	onClose,
	title,
	className,
	children,
	handleClick,
	buttonText,
	instantMeeting,
	image,
	buttonClassName,
	buttonIcon,
	handleInput,
	meetingID,
}: MeetingModalProps) => {
	return (
		<Dialog open={isOpen} onOpenChange={onClose}>
			<DialogContent className="flex w-full max-w-[520px] flex-col gap-6 border-none bg-black px-6 py-9 text-white">
				<DialogTitle>Hello</DialogTitle>

				<div className="flex flex-col gap-6">
					{image && (
						<div className="flex justify-center">
							<Image src={image} alt="checked" width={72} height={72} />
						</div>
					)}
					<h1 className={cn('text-3xl font-bold leading-[42px]', className)}>{title}</h1>
					{children}

					{buttonText?.toLowerCase() == 'join' && (
						<Input type="text" placeholder="Enter meeting ID" onChange={handleInput} value={meetingID} />
					)}

					<Button
						className={'bg-gray-700 focus-visible:ring-0 focus-visible:ring-offset-0 cursor-pointer'}
						onClick={() => {
							console.log('clicked');
							if (handleClick) {
								handleClick();
							}
						}}
					>
						{buttonIcon && <Image src={buttonIcon} alt="button icon" width={13} height={13} />} &nbsp;
						{buttonText || 'Schedule Meeting'}
					</Button>
				</div>
			</DialogContent>
		</Dialog>
	);
};

export default MeetingModal;
