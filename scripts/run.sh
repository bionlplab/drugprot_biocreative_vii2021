#! /bin/bash -l

#SBATCH --job-name=drugprot
#SBATCH --partition=scu-cpu
##SBATCH --partition=cryo-gpu
##SBATCH --gres=gpu:rtx6000:4

# Resources h_rt: runtime limit
#SBATCH --time=2-00:00:00
#SBATCH --mem=256G
#SBATCH --nodes=1
#SBATCH --cpus-per-task=16
#SBATCH --ntasks-per-node=1
#SBATCH --requeue

# Notification
#SBATCH --mail-type=ALL
#SBATCH --mail-user=yip4002@med.cornell.edu

# JOB
#SBATCH --output="slurm-%x-%A.out.txt"
#SBATCH --error="slurm-%x-%A.err.txt"
export PYTHONPATH=.

top_dir=$HOME
cd $top_dir/drugprot_bcvii || exit
. $top_dir/venvs/wcm/bin/activate

python create_drugprot_bert2.py "$1" "$2"
