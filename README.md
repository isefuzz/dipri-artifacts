## Artifacts of TOSEM'23 submission: *DiPri: Distance-based Seed Prioritization for Greybox Fuzzing*

This is the guideline repository for the TOSEM submission *DiPri: Distance-based Seed Prioritization for Greybox Fuzzing*.
The structure of this repository is as follows: 

```text
.
├── configs                 # Configuration files for FuzzBench and Magma.
├── Dockerfile              # Docker reproduction for manually built targets.
├── LICENSE.md              # The open-source license.
├── README.md               # This file.
├── fuzzbench-integration   # Integrating AFL++-dipri into FuzzBench
├── magma-integration       # Integrating AFL++-dipri into Magma
└── scripts                 # Scripts to generate and analyze data.
```

**Status**: According to the requirements of [TOSEM CFP](https://dl.acm.org/journal/tosem/replicated-computational-results), 
there are three ACM badges for artifacts, namely _available, functional, and reusable_. Our artifacts aim to apply for
all three badges. Note that we elaborate on the **INSTALL** and **REQUIREMENTS** parts of CFP in the section 3, i.e., 
the reproduction with the `Dockfile`.

**Papers**: This paper is a submission of the pre-registered model of [FUZZING Workshop](https://fuzzingworkshop.github.io/).
Please check [FUZZING'23 registered paper](https://dl.acm.org/doi/10.1145/3605157.3605172).

### 1 Cross-language implementation of DiPri

We have implemented DiPri in both C/C++ and Java respectively on top of AFL++ (version 4.06) and Zest 
(version 2.0-SNAPSHOT). We put the source code of these two implementations in two separate repositories.
The links to the two implementations are as follows:

- AFL++-dipri (C/C++ implementation): https://github.com/isefuzz/aflpp-dipri
- Zest-dipri (Java implementation): https://github.com/isefuzz/zest-dipri

### 2 Reproduction of Experiments on FuzzBench and Magma

This repository includes scripts for integrating AFL++-dipri (under `AH` and `VH` configurations) into standard 
benchmarks [FuzzBench](https://github.com/google/fuzzbench) and [Magma](https://github.com/HexHive/magma). 
To reproduce our experiments, one should clone FuzzBench and Magma, copy the integration scripts into the project 
folders, and build and run experiments following their official instructions. Exemplified shell instructions are as 
follows:

For FuzzBench integration:
```shell
# Download FuzzBench and checkout to the commit ID we use.
git clone https://github.com/google/fuzzbench.git
git -C ./ fuzzbench checkout 7c70037a73d2cc66627c6109d53d20b3594f85c9
# Download and copy integration materials into the 'fuzzers/' folder.
git clone https://github.com/isefuzz/dipri-artifacts.git
cp -r ./dipri-artifacts/fuzzbench-integration/* ./fuzzbench/fuzzers/
# Try building fuzzers with some targets after building FuzzBench.
cd ./fuzzbench
source .venv/bin/activate
make -j8 build-aflplusplus_406_dipri_ah-bloaty_fuzz_target
```

For Magma integration:
```shell
# Download Magma and checkout to the version we use.
git clone https://github.com/HexHive/magma.git
git -C ./magma checkout v1.2
# Download and copy integration materials into the 'fuzzers/' folder.
git clone https://github.com/isefuzz/dipri-artifacts.git
cp -r ./dipri-artifacts/magma-integration/* ./magma/fuzzers/
# Enter './tools/captain/' and try building fuzzers with Magma targets
cd ./tools/captain
FUZZER=aflplusplus_dipri_ah TARGET=libpng./build.sh
```

### 3 Docker-based Reproduction of Experiments on Manually Built Targets. 

We provide docker environments for the reproduction of our experiments on fuzz targets real-world 
projects. We first describe the software and hardware requirements and then give out exemplified shell 
instructions.

#### 3.1 Software and Hardware Requirements

The functionalities of DiPri can be implemented by standard libraries, so the software requirements of
DiPri prototypes are same with its host fuzzers, i.e., AFL++ and Zest. Besides, the requirements of 
running our scripts are put in `scripts/requirements.txt`. The contents are as follows:

```text
matplotlib==3.7.2
numpy==1.25.2
pandas==2.0.3
scikit_learn==1.3.0
tqdm==4.66.1
venn==0.1.3
```

In our evaluation, we use three machines, i.e., two cloud servers and one workstation, to run our experiments.
Here we summarized the hardware requirements as follows:

| Infrastructure | Requirement  |
|----------------|--------------|
| OS             | Ubuntu 22.04 |
| # of Cores     | \>= 16       |
| Memory         | \>= 32GB     |

#### 3.2 Installation of Docker-based Reproduction

The user may either download a ready-to-use image to conduct the docker-based reproduction or
build the image manually with the Dockerfile and scripts provided in this repository.

To download the off-the-shell image, you can run:

```shell
docker pull isefuzz/dipri-aflpp:v1.0  # Image for C/C++ targets.
docker pull isefuzz/dipri-zest:v1.0   # Image for Java targets. 
```

After get the image, you can run a container and reproduce experiments inside it.
Say we have built an image manually and want to fuzz `mjs`, which is one of our experimental subjects, 
a possible sequence of instructions are as follows:

```shell
## Pull image and enter the docker container.
docker pull isefuzz/dipri-aflpp:v1.0
docker run -it --privileged isefuzz/dipri-aflpp:v1.0

## Run experiment inside the docker container.
# Prepare environment.
cd /root/isefuzz/dipri
source ./scripts/subject/setup/config/setup-dipri-AH.sh
# Instrument mjs and check whether instrumented mjs is existed.
mkdir -p ./data/dipri-AH
bash ./scripts/subject/inst/mjs.sh ./subjects/mjs-2.20.0 ./data/dipri-AH/
ls -al ./data/dipri-AH/mjs/mjs
# Make some fuzz for 5 minutes (300s) and 3 repeatitions and check outs.
bash ./scripts/subject/fuzz/mjs.sh ./data/dipri-AH 300 1 3
ls -al ./data/dipri-AH/mjs/outs

## Analyze raw data inside the docker container with the out-of-box raw data.
cd /root/isefuzz/dipri
bash ./scripts/analysis/tosem/run_rw_cov_analysis.sh ./dipri-aflpp-data
# Check generated tables (.csv) and figures (fig_*).
ls -al ./dipri-aflpp-data/_results/
```




