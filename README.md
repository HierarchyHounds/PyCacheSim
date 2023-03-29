# PyCacheSim

A simple memory cache simulator using a two-level cache hierarchy with L1 and L2 caches. The simulator supports various cache configurations, replacement policies, and inclusion properties.

## Usage

```sh
python main.py <BLOCKSIZE> <L1_SIZE> <L1_ASSOC> <L2_SIZE> <L2_ASSOC> <REPLACEMENT_POLICY> <INCLUSION_PROPERTY> <TRACE_FILE>
```

`BLOCKSIZE`: Positive integer. Block size in bytes. (Same block size for all caches in the memory hierarchy.)
`L1_SIZE`: Positive integer. L1 cache size in bytes.
`L1_ASSOC`: Positive integer. L1 set-associativity (1 is direct-mapped).
`L2_SIZE`: Positive integer. L2 cache size in bytes. L2_SIZE = 0 signifies that there is no L2 cache.
`L2_ASSOC`: Positive integer. L2 set-associativity (1 is direct-mapped).
`REPLACEMENT_POLICY`: Positive integer. 0 for LRU, 1 for FIFO.
`INCLUSION_PROPERTY`: Positive integer. 0 for non-inclusive, 1 for inclusive.
`TRACE_FILE`: Character string. Full name of trace file, including any extensions.

Example trace files and expected outputs are located under `assets` directory.

## LICENSE

This project is published under [Apache 2.0 license](https://www.apache.org/licenses/LICENSE-2.0).
