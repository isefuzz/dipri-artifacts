FROM ubuntu:20.04

# For AFL++

ENV DEBIAN_FRONTEND=noninteractive

ENV LLVM_VERSION=14

ENV LLVM_CONFIG=/usr/bin/llvm-config-14

ENV GCC_VERSION=11

RUN apt-get update && apt-get full-upgrade -y && \
    apt-get install -y --no-install-recommends wget ca-certificates apt-utils && \
    rm -rf /var/lib/apt/lists/*

RUN apt-get update && apt-get full-upgrade -y && \
    apt-get install -y --no-install-recommends wget ca-certificates apt-utils gnupg && \
    rm -rf /var/lib/apt/lists/* && \
    wget -O - https://apt.llvm.org/llvm-snapshot.gpg.key | apt-key add -

#RUN echo "deb [signed-by=/etc/apt/keyrings/llvm-snapshot.gpg.key] http://apt.llvm.org/jammy/ llvm-toolchain-jammy-${LLVM_VERSION} main" > /etc/apt/sources.list.d/llvm.list && \
#    wget -qO /etc/apt/keyrings/llvm-snapshot.gpg.key https://apt.llvm.org/llvm-snapshot.gpg.key


RUN echo "deb  http://apt.llvm.org/focal/ llvm-toolchain-focal-${LLVM_VERSION} main" >> /etc/apt/sources.list && \
   wget -O - https://apt.llvm.org/llvm-snapshot.gpg.key | apt-key add -

RUN apt-get update
RUN apt-get install -y apt-file
RUN apt-file update
RUN apt-get install -y software-properties-common
RUN add-apt-repository -y ppa:ubuntu-toolchain-r/test



RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y \
    build-essential \
    python3-dev \
    automake \
    wget \
    make \
    cmake \
    git \
    tar \
    texinfo \
    pip \
    flex \
    bison \
    libglib2.0-dev \
    libpixman-1-dev \
    python3-setuptools \
    cargo \
    software-properties-common \
    libgtk-3-dev \
    apt-transport-https gnupg dialog \
    gnuplot-nox libpixman-1-dev \
    gcc-${GCC_VERSION} g++-${GCC_VERSION} gcc-${GCC_VERSION}-plugin-dev gdb lcov \
    clang-${LLVM_VERSION} clang-tools-${LLVM_VERSION} libc++1-${LLVM_VERSION} \
    libc++-${LLVM_VERSION}-dev libc++abi1-${LLVM_VERSION} libc++abi-${LLVM_VERSION}-dev \
    libclang1-${LLVM_VERSION} libclang-${LLVM_VERSION}-dev \
    libclang-common-${LLVM_VERSION}-dev libclang-rt-${LLVM_VERSION}-dev libclang-cpp${LLVM_VERSION} \
    libclang-cpp${LLVM_VERSION}-dev liblld-${LLVM_VERSION} \
    liblld-${LLVM_VERSION}-dev liblldb-${LLVM_VERSION} liblldb-${LLVM_VERSION}-dev \
    libllvm${LLVM_VERSION} libomp-${LLVM_VERSION}-dev libomp5-${LLVM_VERSION} \
    lld-${LLVM_VERSION} lldb-${LLVM_VERSION} llvm-${LLVM_VERSION} \
    llvm-${LLVM_VERSION}-dev llvm-${LLVM_VERSION}-runtime llvm-${LLVM_VERSION}-tools \
    $([ "$(dpkg --print-architecture)" = "amd64" ] && echo gcc-${GCC_VERSION}-multilib gcc-multilib) \
    $([ "$(dpkg --print-architecture)" = "arm64" ] && echo libcapstone-dev) && \
    rm -rf /var/lib/apt/lists/*


# For DiPri

RUN mkdir -p /root/isefuzz/dipri && \
    mkdir /root/isefuzz/dipri/aflpp-dipri && \
    mkdir /root/isefuzz/dipri/subjects && \
    mkdir /root/isefuzz/dipri/scripts && \
    cd /root/isefuzz/dipri

COPY subjects/*.tar.gz    /root/isefuzz/dipri/subjects/

COPY scripts /root/isefuzz/dipri/scripts/

COPY aflpp-dipri /root/isefuzz/dipri/aflpp-dipri/

RUN pip install -r /root/isefuzz/dipri/scripts/requirements.txt && \
    /bin/bash /root/isefuzz/dipri/scripts/subject/decompress-subjects.sh /root/isefuzz/dipri/subjects && \
    cd /root/isefuzz/dipri/aflpp-dipri && \
    make source-only && \
    make install

ENV CC=/root/isefuzz/dipri/aflpp-dipri/afl-clang-fast
ENV CXX=/root/isefuzz/dipri/aflpp-dipri/afl-clang-fast++

RUN cd /root/isefuzz/dipri/subjects/binutils-2.40 && \
    /bin/bash /root/isefuzz/dipri/subjects/binutils-2.40/configure && \
    make && \
    make install
