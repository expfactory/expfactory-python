# Here is how to generate the entire expfactory.github.io

from expfactory.views import generate_experiment_web

output_folder = "/home/vanessa/Desktop/site" # does not have to exist
generate_experiment_web(output_folder)
