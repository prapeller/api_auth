create table "user"
(
    id         serial primary key,
    uuid       uuid unique              default uuid_generate_v4() not null,
    created_at timestamp with time zone default now()              not null,
    updated_at timestamp with time zone,
    email      varchar(50) unique,
    name       varchar(50),
    password   varchar(100),
    is_active  boolean                                             not null
);
