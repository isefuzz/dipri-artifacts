## Artifacts of TOSEM'23 submission: *DiPri: Distance-based Seed Prioritization for Greybox Fuzzing*

This is the guideline repository for the TOSEM submission *DiPri: Distance-based Seed Prioritization for Greybox Fuzzing*.
The structure of this repository is as follows: 

```text
.
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
git clone https://github.com/QRXqrx/dipri-artifacts.git
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
git -C ./fuzzbench checkout v1.2
# Download and copy integration materials into the 'fuzzers/' folder.
git clone https://github.com/QRXqrx/dipri-artifacts.git
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
docker pull njuqrx/dipri:v1.1
```

To build the image manually, you can run:

```shell
# Download dipri artifacts .
git clone https://github.com/isefuzz/dipri-artifacts.git
cd ./dipri-artifacts
# Download subjects.
mkdir subjects
bash ./scripts/subject/download-subjects.sh ./subjects
# Download AFL ++- DiPri.
git clone https://github.com/isefuzz/aflpp-dipri.git
# Construct the docker image.
docker build -t dipri .
```

After get the image, you can run a container and reproduce experiments inside it.
Say we have built an image manually and want to fuzz `readelf`, which is one of our experimental subjects, 
a possible sequence of instructions are as follows:

```shell
# Suppose we have built the image manually.
docker run -it --privileged dipri

# ##############################
# Inside the docker container  #
# ##############################

# Setup experimental environments .
cd /root/dipri
source ./scripts/subject/setup/config/setup-dipri-AH.sh
# Compiling targets. Please prepare folder for each fuzzer.
mkdir -p ./data/dipri-AH
bash  ./scripts/subject/inst/binutils.sh \
      ./subjects/binutil-2.40 \
      ./data/dipri-AH
# Run targets to generate raw fuzz data.
bash ./scripts/subject/fuzz/readelf.sh ./data/dipri-AH 82800 1 10
# Extract edge coverage.
python3 ./scripts/analysis/tosem/extract_data.py -f ./data
# Analyze raw data to get tables and figures .
bash ./scripts/analysis/tosem/run_rw_cov_analysis.sh ./data
```




