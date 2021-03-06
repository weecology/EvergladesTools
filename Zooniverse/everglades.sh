sbatch <<EOT
#!/bin/bash
#SBATCH --job-name=EvBirdDetect   # Job name
#SBATCH --mail-type=END               # Mail events
#SBATCH --mail-user=ethanwhite@ufl.edu  # Where to send mail
#SBATCH --account=ewhite
#SBATCH --nodes=1                 # Number of MPI ran
#SBATCH --cpus-per-task=8
#SBATCH --mem=50GB
#SBATCH --time=48:00:00       #Time limit hrs:min:sec
#SBATCH --output=/blue/ewhite/everglades/EvergladesTools/Zooniverse/logs/bird_detector_%j.out   # Standard output and error log
#SBATCH --error=/blue/ewhite/everglades/EvergladesTools/Zooniverse/logs/bird_detector_%j.err
#SBATCH --partition=gpu
#SBATCH --gpus=1
ulimit -c 0
ml git
git checkout $1
source activate EvergladesTools
python create_bird_detector_annotations.py
python everglades.py
EOT
