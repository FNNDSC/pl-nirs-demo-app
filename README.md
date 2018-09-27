# pl-nirs-demo-app
An app to demo nirs mcx simulations.

## Run

### Requirements
- a compatible nvidia gpu
  - compatible meaning, at least compute-capability 3.0, see list of [here](https://developer.nvidia.com/cuda-gpus)
  - nvidia driver installed
- docker
- [nvidia-docker](https://github.com/NVIDIA/nvidia-docker)
- to configure the simulations, experience with [mcx](http://mcx.space/), Monte Carlo eXtreme, is needed.
- understanding of [chrisapp](https://github.com/FNNDSC/chrisapp) would be useful, but not necessary


### Arguments

1. incoming: input directory for files.
2. outgoing: output directory for files.
3. head: NIfTI file containing head to simulate.
4. mcx_config: json file containing options for how to run mcx, and vectors for srcpos, srcdir, detpos, and detdir.


#### Example json for mcx_config

```json
{
    "mcx" : {
        "gpuid": "11",
        "prop": [
            [0, 0, 1, 1],
            [0.014600,  8.28, 0.9, 1.37],
            [0.019500, 11.11, 0.9, 1.37]
        ]
    },
    "srcpos": [85, 122, 53],
    "srcdir": [-0.7818184, -0.62350625, 0],
    "detpos": [117.669, 196.430,  53],
    "detdir": [-0.29373407, -0.9558872, 0]
}
```

### How to run example

Using the example config and head, here is an example of how to run 
this plugin using nvidia-docker.

```bash
mkdir -p out && nvidia-docker run -v example:/incoming -v out:/outgoing   \
             jdtatz/pl-nirs-demo-app nirs_demo_app.py /incoming /outgoing \
             --head=example_head.nii.gz --mcx_config=example_config.json
```
