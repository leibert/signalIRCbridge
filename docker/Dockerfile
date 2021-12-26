# FROM oraclelinux:8
FROM ubuntu:jammy

# ARG JAVA_VER=8
# ARG JAVA_RELEASE=JDK

# RUN bash -c ' \
#     set -euxo pipefail && \
#     apt-get update && \
#     pkg="openjdk-$JAVA_VERSION"; \
#     if [ "$JAVA_RELEASE" = "JDK" ]; then \
#         pkg="$pkg-jdk-headless"; \
#     else \
#         pkg="$pkg-jre-headless"; \
#     fi; \
#     apt-get install -y --no-install-recommends "$pkg" && \
#     apt-get clean && \
#     rm -fr /var/lib/apt/lists \
#     '


# COPY profile.d/java.sh /etc/profile.d/


VOLUME [ "/config" ]


VOLUME /config

# RUN apt-get update && \
#     DEBIAN_FRONTEND=noninteractive \
#     apt-get -y install default-jre-headless && \
#     apt-get clean && \
#     rm -rf /var/lib/apt/lists/*

RUN apt-get update
RUN apt-get -y install openjdk-17-jre-headless
RUN apt-get -y install dbus
# Setup JAVA_HOME -- useful for docker commandline
# ENV JAVA_HOME /usr/lib/jvm/java-8-openjdk-amd64/
# RUN export JAVA_HOME

ENV JAVA_HOME=/usr/

# export VERSION=<latest version, format "x.y.z">
# wget https://github.com/AsamK/signal-cli/releases/download/v"${VERSION}"/signal-cli-"${VERSION}".tar.gz
ADD signal-cli-0.10.0.tar.gz /opt

# RUN tar xf /home/signal-cli-0.10.0.tar.gz -C /opt
RUN ln -sf /opt/signal-cli-0.10.0/bin/signal-cli /usr/local/bin/

COPY run.sh /
COPY data/org.asamk.Signal.conf /etc/dbus-1/system.d/
COPY data/org.asamk.Signal.service /usr/share/dbus-1/system-services/
COPY data/signal-cli.service /etc/systemd/system/
RUN sed -i -e "s|%dir%|<INSERT_INSTALL_PATH>|" /etc/systemd/system/signal-cli.service

RUN dbus-uuidgen > /var/lib/dbus/machine-id
RUN mkdir -p /var/run/dbus
# RUN dbus-daemon --config-file=/usr/share/dbus-1/system.conf --print-address
# RUN dockerd
# RUN systemctl daemon-reload
# RUN systemctl enable signal-cli.service
# RUN systemctl reload dbus.service



# ENTRYPOINT ["/signal-cli-0.6.5/bin/signal-cli", "--config", "/config"]
# CMD ["/bin/bash"]
ENTRYPOINT [ "/run.sh" ]
