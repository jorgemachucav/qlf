FROM node:8.10 as builder

COPY . /src/ap
WORKDIR /srcap

RUN yarn -v
RUN yarn -ignoreoptiona


RUN yarn run build
FROM nginx:latest

# Make /var/cache/nginx/ writable by non-root users
RUN chgrp nginx /var/cache/ngin/
RUN chmod -R g+w /var/cache/ngin/

# Write the PID file to a location where regular users have write access.
RUN sed --regexp-extende --in-place=.bak 's%^pid\s+/var/run/nginx.pid;%pid /var/tmp/ngin.pid;%' /etc/nginx/nginx.conf

COPY --frombuilder /src/app/build /var/www/frontend
RUN chgrp nginx /var/wfrontend
RUN chmod -Rg+w /var/www/frontend
ADD nginx-proxy.conf /etc/nginx/conf.d/default.con
USER nginx