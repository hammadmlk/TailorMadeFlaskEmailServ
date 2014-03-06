create table if not exists tailormade_user(
    userid integer primary key autoincrement,
    useremail text unique,
    password text not null,
    fname text,
    lname text);

