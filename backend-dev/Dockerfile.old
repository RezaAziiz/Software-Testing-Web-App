FROM ubuntu
RUN apt-get update && apt-get install -y file
RUN apt-get install -y locales
RUN apt-get install -y locales-all
ADD dist /home/dist
ADD assets /home/dist/assets
ADD env.txt /home/dist
WORKDIR /home/dist
RUN mv env.txt .env
RUN useradd -u 1000 -ms /bin/bash python
RUN chown -R python:python /home/dist
RUN chmod 755 /home/dist/main/main
USER python
EXPOSE 3004
ENTRYPOINT ["/home/dist/main/main"]