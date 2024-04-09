# Submit prediction jobs
#!/bin/bash
#SBATCH --job-name=AirplanePrediction   # Job name
#SBATCH --mail-type=END               # Mail events
#SBATCH --mail-user=benweinstein2010@gmail.com  # Where to send mail
#SBATCH --account=ewhite
#SBATCH --nodes=1                 # Number of MPI ran
#SBATCH --cpus-per-task=1
#SBATCH --mem=50GB
#SBATCH --time=48:00:00       #Time limit hrs:min:sec
#SBATCH --output=/home/b.weinstein/logs/Airplane_prediction_%j.out   # Standard output and error log
#SBATCH --error=/home/b.weinstein/logs/Airplane_prediction_%j.err
#SBATCH --partition=gpu
#SBATCH --gpus=1

source activate EvergladesTools
python scripts/predict.py --model_path /blue/ewhite/everglades/Zooniverse/20220910_182547/species_model.pl --image_path $1 --output_path /blue/ewhite/everglades/Airplane/annotations