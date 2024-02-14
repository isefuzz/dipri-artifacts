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

### Cross-language implementation of DiPri

We have implemented DiPri in both C/C++ and Java respectively on top of AFL++ (version 4.06) and Zest 
(version 2.0-SNAPSHOT). We put the source code of these two implementations in two separate repositories.
The links to the two implementations are as follows:

- AFL++-dipri (C/C++ implementation): https://github.com/QRXqrx/aflpp-dipri
- Zest-dipri (Java implementation): https://github.com/YangDingNY/zest-dipri

