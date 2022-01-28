FROM ubuntu:trusty

RUN apt-get update; apt-get clean

# Add a user for running applications.
RUN useradd apps
RUN mkdir -p /home/apps && chown apps:apps /home/apps

# Install x11vnc.
RUN apt-get install -y x11vnc

# Install xvfb.
RUN apt-get install -y xvfb

# Install fluxbox.
RUN apt-get install -y fluxbox

# Install wget.
RUN apt-get install -y wget

# Install wmctrl.
RUN apt-get install -y wmctrl

# Set the Chrome repo.
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list

# Install Chrome.
RUN apt-get update && apt-get -y install google-chrome-stable

# Install Python dependencies.
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

# set argument vars in docker-run command
ARG AWS_ACCESS_KEY=AKIAXVPB73N52U6CFCN2
ARG AWS_ACCESS_SECRET=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
ARG DB_CLIENT_ID=cTxUnhZHOeZwUTndgNXuDgYB
ARG DB_CLIENT_SECRET=osshzLeZYEZ_,Uf+_Ww4tyCHKPpPidlxhofNej6RX1cGjdCQ8NhJfmtiKeC,3w1JYYfLW9YrOrMXGZx5WgMbD4hlKok8AalPXCCdp,CWTrrXLL5qKl2-lmOIM-EmZUtD
ARG AWS_KEYSPACE=aidboto

ENV ACCESS_KEY =$AWS_ACCESS_KEY
ENV ACCESS_SECRET =$AWS_ACCESS_SECRET
ENV KEYSPACE =$AWS_KEYSPACE
ENV CLIENT_ID =$DB_CLIENT_ID
ENV CLIENT_SECRET =$DB_CLIENT_SECRET

COPY . /app/
WORKDIR /app
#EXPOSE 5000
#RUN pip install -r requirements.txt
#CMD python app.py
# start web server
CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app", "--workers=5"]