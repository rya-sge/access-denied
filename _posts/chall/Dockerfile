FROM python:3.13-slim as challenge

RUN apt-get update && \
    apt-get install -y curl git build-essential && \
    rm -rf /var/lib/apt/lists/*

ENV FOUNDRY_DIR=/opt/foundry
ENV PATH=${FOUNDRY_DIR}/bin/:${PATH}
RUN curl -L https://foundry.paradigm.xyz | bash && \
    foundryup

COPY contracts /home/ctf/challenge/contracts/
COPY challenge.py /home/ctf/challenge/

WORKDIR /home/ctf/challenge

RUN git clone --branch v5.1.0 https://github.com/OpenZeppelin/openzeppelin-contracts contracts/dependencies/openzeppelin-contracts/
RUN git clone --branch v1.9.5 https://github.com/foundry-rs/forge-std.git contracts/dependencies/forge-std/
RUN git clone --branch rpc_allowlist https://github.com/bbjubjub2494/helloweb3.git

RUN pip install ./helloweb3