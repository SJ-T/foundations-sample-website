
CREATE TABLE meetings(
    meeting_id INTEGER PRIMARY KEY AUTOINCREMENT,
    meeting_date TEXT NOT NULL,
    contact_id INTEGER NOT NULL,
    FOREIGN KEY(contact_id) REFERENCES contacts(contact_id),
    UNIQUE(meeting_date,contact_id)
);

