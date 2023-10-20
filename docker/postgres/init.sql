create schema if not exists content;

create table if not exists content.genre
(
    id          serial primary key,
    uuid        uuid unique              not null,
    created_at  timestamp with time zone not null,
    updated_at  timestamp with time zone,

    name        varchar                  not null,
    description text
);

create table if not exists content.film
(
    id           serial primary key,
    uuid         uuid unique              not null,
    created_at   timestamp with time zone not null,
    updated_at   timestamp with time zone,

    title        varchar                  not null,
    description  text,
    release_date date,
    file_path    varchar,
    "type"       varchar                  not null,
    imdb_rating  numeric
);

create table if not exists content.person
(
    id         serial primary key,
    uuid       uuid unique              not null,
    created_at timestamp with time zone not null,
    updated_at timestamp with time zone,

    full_name  varchar                  not null
);

create table if not exists content.film_genre
(
    id         serial primary key,
    uuid       uuid unique              not null,
    created_at timestamp with time zone not null,

    film_uuid  uuid references content.film (uuid) on delete cascade,
    genre_uuid uuid references content.genre (uuid) on delete cascade
);

create table if not exists content.film_person
(
    id          serial primary key,
    uuid        uuid unique              not null,
    created_at  timestamp with time zone not null,

    film_uuid   uuid references content.film (uuid) on delete cascade,
    person_uuid uuid references content.person (uuid) on delete cascade,
    role        varchar                  not null
);

create index if not exists idx_film_title on content.film (title);
create index if not exists idx_film_type on content.film ("type");
create index if not exists idx_film_release_date on content.film (release_date);
create index if not exists idx_genre_uuid on content.genre (uuid);
create index if not exists idx_film_uuid on content.film (uuid);
create index if not exists idx_person_uuid on content.person (uuid);

alter table content.film_genre
    add constraint unique_film_genre unique (film_uuid, genre_uuid);
alter table content.film_person
    add constraint unique_film_person_role unique (film_uuid, person_uuid, role);