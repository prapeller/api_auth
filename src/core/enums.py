from enum import Enum


class OrderEnum(str, Enum):
    asc = 'asc'
    desc = 'desc'


class EnvEnum(str, Enum):
    local = 'local'
    docker_compose_local = 'docker-compose-local'
    prod = 'prod'

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.value


class ResponseDetailEnum(str, Enum):
    ok = 'ok'
    unauthorized = 'Unauthorized for this action.'
    invalid_credentials = 'Invalid credentials were provided.'


class RolesNamesEnum(str, Enum):
    superuser = 'superuser'
    staff = 'staff'
    guest = 'guest'
    registered = 'registered'
    premium = 'premium'

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.value


class TokenTypesEnum(str, Enum):
    access = 'access'
    refresh = 'refresh'

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.value


class PermissionsNamesEnum(str, Enum):
    # permission for superuser
    all_of_all = 'all_of_all'

    # users
    all_of_users = 'all_of_users'
    create_users = 'create_users'
    read_users = 'read_users'
    update_users = 'update_users'
    delete_users = 'delete_users'

    # content
    all_of_content = 'all_of_content'
    create_content = 'create_content'
    read_content_all = 'read_content_all'
    read_content_free = 'read_content_free'
    read_content_premium = 'read_content_premium'
    update_content = 'update_content'
    delete_content = 'delete_content'

    # ratings
    all_of_ratings = 'all_of_ratings'
    create_ratings = 'create_ratings'
    read_ratings = 'read_ratings'
    update_ratings = 'update_ratings'
    delete_ratings = 'delete_ratings'

    # comments
    all_of_comments = 'all_of_comments'
    create_comments = 'create_comments'
    read_comments_all = 'read_comments_all'
    read_comments_my = 'read_comments_my'
    update_comments_all = 'update_comments_all'
    update_comments_my = 'update_comments_my'
    delete_comments = 'delete_comments'

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.value


class SessionOrderByEnum(str, Enum):
    created_at = 'created_at'
    updated_at = 'updated_at'
    useragent = 'useragent'
    ip = 'ip'

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.value


class MethodsEnum(str, Enum):
    get = 'get'
    post = 'post'
    put = 'put'
    delete = 'delete'
