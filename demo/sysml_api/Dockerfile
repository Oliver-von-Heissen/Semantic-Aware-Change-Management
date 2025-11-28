FROM sbtscala/scala-sbt:eclipse-temurin-jammy-11.0.22_7_1.9.9_3.4.0

# Base updates and services
RUN apt-get update && apt-get install -y git curl

# Clone the project
WORKDIR /opt
RUN git clone https://github.com/Systems-Modeling/SysML-v2-API-Services.git
WORKDIR /opt/SysML-v2-API-Services
RUN git checkout develop

# Reconfigure JDBC to use compose postgresql
RUN sed -i 's@jdbc:postgresql://localhost:5432@jdbc:postgresql://database:5432@' conf/META-INF/persistence.xml
## Play framework complains about the secret key length...
RUN sed s/key=.whatever./key=\"longersecretnowarnings\"/ -i conf/application.conf
# Allow the Docker service hosts
RUN printf '\nplay.filters.hosts { allowed = ["sysml-api", "localhost", "127.0.0.1", ".local"] }\n' >> conf/application.conf

# Build the sysml api server
RUN sbt clean stage

# Start sysml api server
EXPOSE 9000
CMD ["./target/universal/stage/bin/sysml-v2-api-services", "-Dplay.server.pidfile.path=/dev/null"]
