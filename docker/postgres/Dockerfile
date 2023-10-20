FROM postgres:13.9

COPY api_auth/scripts/postgres /usr/local/bin/temp
RUN chmod +x /usr/local/bin/temp/* && \
    mv /usr/local/bin/temp/* /usr/local/bin &&  \
    rmdir /usr/local/bin/temp