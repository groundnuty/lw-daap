FROM python:2.7-slim
MAINTAINER Aeonium <info@aeonium.eu>

RUN apt-get update && \
    apt-get -qy install --fix-missing --no-install-recommends curl && \
    curl -sL https://deb.nodesource.com/setup | bash -

RUN apt-get update && \
    apt-get -qy upgrade --fix-missing --no-install-recommends && \
    apt-get -qy install --fix-missing --no-install-recommends \
        apache2 \
        gcc \
        git \
        libapache2-mod-wsgi \
        libffi-dev \
        libjpeg-dev \
        libmysqlclient-dev \
        libssl-dev \
        libxslt-dev \
        mysql-client \
        nodejs \
        sudo \
        uwsgi \
        uwsgi-plugin-python && \
    apt-get clean autoclean && \
    apt-get autoremove -y && \
    rm -rf /var/lib/{apt,dpkg}/ && \
    (find /usr/share/doc -depth -type f ! -name copyright -delete || true) && \
    (find /usr/share/doc -empty -delete || true) && \
    rm -rf /usr/share/man/* /usr/share/groff/* /usr/share/info/*

RUN pip install --upgrade pip virtualenv
RUN npm update && \
    npm install --silent -g bower less clean-css uglify-js requirejs


COPY lwosf_vhost.conf /etc/apache2/sites-available/lwosf.conf
RUN update-rc.d -f  apache2 remove && \
    a2enmod rewrite && \
    a2dissite *default* && \
    a2ensite lwosf && \
    truncate -s 0 /etc/apache2/ports.conf

RUN ln -s /usr/lib/python2.7/plat-*/_sysconfigdata_nd.py /usr/lib/python2.7/

RUN useradd --home-dir /home/lwosf --create-home --shell /bin/bash --uid 1000 lwosf

COPY ./lw-daap/ /home/lwosf/code/
COPY ./setup_app.sh /home/lwosf/code/

WORKDIR /home/lwosf/
RUN virtualenv venv &&\
    . venv/bin/activate && \
    cd  /home/lwosf/code && \
    pip install -r requirements.txt --exists-action i && \
    pip install -e .

RUN chown -R lwosf:lwosf /home/lwosf && \
    echo "lwosf ALL=NOPASSWD: "$(which apachectl) >> /etc/sudoers

VOLUME /home/lwosf
VOLUME /tmp

USER lwosf
#ENTRYPOINT ["/home//code/setup_app.sh"]
#CMD ["sudo apachectl -e info -DFOREGROUND"]
CMD ["bash"

