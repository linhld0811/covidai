#!/bin/bash

conda_dir="/home/voice/anaconda3"
export PATH="/home/voice/anaconda3/bin:$PATH"
export PATH="${conda_dir}/bin:$PATH:~/.local/bin/"
# >>> conda initialize >>>
# !! Contents within this block are managed by 'conda init' !!
__conda_setup="$('${conda_dir}/bin/conda' 'shell.bash' 'hook' 2> /dev/null)"
if [ $? -eq 0 ]; then
    eval "$__conda_setup"
else
    if [ -f "${conda_dir}/etc/profile.d/conda.sh" ]; then
        . "${conda_dir}/etc/profile.d/conda.sh"
    else
        export PATH="${conda_dir}/bin:$PATH"
    fi
fi
unset __conda_setup
# <<< conda initialize <<<
