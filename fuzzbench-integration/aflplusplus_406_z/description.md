# aflplusplus-Z: AFL++ using sequential seed selection

In aflplusplus, the term "seed selection" is analogous to the term "seed prioritization" generally used in academia.

AFL++-Z fuzzer instance that has the following config active for all benchmarks:
  - PCGUARD instrumentation 
  - cmplog feature
  - dict2file feature
  - "fast" power schedule
  - persistent mode + shared memory test cases
  - sequential seed selection (the `-Z` option)

Repository: [https://github.com/AFLplusplus/AFLplusplus/](https://github.com/AFLplusplus/AFLplusplus/)

[builder.Dockerfile](builder.Dockerfile)
[fuzzer.py](fuzzer.py)
[runner.Dockerfile](runner.Dockerfile)

AFL++-v4.06 using out-of-queued seed prioritization by enabling the `-Z` option.
