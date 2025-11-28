-- Add attendance status to event_attendees table
ALTER TABLE event_attendees 
ADD COLUMN attendance_status ENUM('pending', 'going', 'maybe', 'not_going') 
DEFAULT 'pending' 
AFTER role;

