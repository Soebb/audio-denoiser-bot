FROM python:3.10-slim-bookworm
ARG USER=root
USER $USER
RUN python3 -m venv venv
WORKDIR /app
COPY . ./
RUN apt-get update && apt-get -y install python3-pip ffmpeg
RUN pip3 install pyrogram tgcrypto denoisers torch==2.2.0 torchaudio==2.2.0 tqdm==4.66.2
EXPOSE 5000
CMD ["python3", "bot.py"]
