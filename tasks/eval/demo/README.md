# PLLaVA Demo API Engine

## Install relative project

```sh
pip install gradio_client tqdm
cd ~/pllava
pip install -e .
```

## Process 1 (screen or tmux): deploy demo

Example with `screen`:

```sh
screen -S demo
conda activate pllava
cd ~/pllava
bash scripts/eval.sh |& tee log_demo.log
```

Exit screen with Ctrl+A, Ctrl+D.

## Process 2 (Python): use with

Just instantiate the client class GradioClientPllava

```python
from pllava.tasks.eval.demo.gradio_client_pllava.py import GradioClientPllava


pllava = GradioClientPllava()
video_path_mp4 = '/home/ubuntu/pllava/DATAS/VCGBench/Videos/Benchmarking/v__B7rGFDRIww.mp4'
result = pllava.do_one(video_path_mp4)
````
