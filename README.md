# The Experiment Factory Python

[![Circle CI](https://circleci.com/gh/expfactory/expfactory-python.svg?style=svg)](https://circleci.com/gh/expfactory/expfactory-python)

The Experiment Factory Python is a module for managing reproducible experiments. The previous version focused on a template approach for [experiments](https://github.com/expfactory/expfactory-experiments), [surveys](https://github.com/expfactory/expfactory-surveys), and [games](https://github.com/expfactory/expfactory-games), and this version is agnostic to the underlying driver of the experiments, and provides reproducible, instantly deployable "container" experiments. What does that mean?

 - You obtain (or build from scratch) one container, a battery of experiments.
 - The container is a Singularity container, meaning that it's a file that can be easily moved, and shared.
 - You run the container with (optionally) some subset and ordering of your battery.
 
The means that the minimum requirement of an experiment is:

 - an `index.html` file and `config.json` in the root of the folder.
 - (optional) documentation about any special variables that can be set in the Singularity build recipe environment section for it (more on this later).
 - an associated repository to clone from, (optionally) registered in the library.

- Please see our [documentation](http://expfactory.readthedocs.org/en/latest/getting-started.html) for more complete details.
- Jump in and [try out our experiments](http://expfactory.github.io/table.html)
- Express interest in Experiments as a Service (EaS) as [expfactory.org](http://www.expfactory.org)

The Experiment Factory code is licensed under the MIT open source license, which is a highly permissive license that places few limits upon reuse. This ensures that the code will be usable by the greatest number of researchers, in both academia and industry. 



## Quick start

You don't actually need to install the Software on your local machine, it will be installed into a container where your experiments live.

You do, however, need to install [Singularity](https://singularityware.github.io) on your local machine. This is a container technology akin to Docker, but it has support on most HPC clusters and works on old kernels, and Docker does not.


### Write your recipe
A Singularity Recipe is a file that details how you want your container to build. In our case, we want to give instructions about which experiments to install. First, copy an example recipe:


```
wget https://raw.githubusercontent.com/vsoch/expfactory-python/development/examples/Singularity
```

This will place the build recipe `Singularity` in your present working directory, and by fault we will install two experiments, adaptive-n-back and tower-of-london. The experiments each have their own repository maintained at [https://www.github.com/expfactory-experiments](https://www.github.com/expfactory-experiments).

If you look inside the recipe, you will see an "app" section for each experiment. All it does is clone the repository content:

```
git clone https://github.com/expfactory-experiments/adaptive-n-back
mv adaptive-n-back/* .
```

We are installing each experiment as a [Standard Container Integration Format (SCI-F)](https://containers-ftw.github.io/SCI-F/) app. The high level idea is that it gives easy accessibility to multiple different internal modules in our container. In our case, an internal module is an experiment. Note that here we might add different environment variables for an experiment, or specify a custom database, but since we are just developing and testing now, let's keep it simple! Let's build the image, and we are going to create a development (tester) image called a "sandbox" first:


```
sudo singularity build --sandbox expfactory Singularity
```

Let's break down the above. We are asking the singularity command line software to `build` an image, specifically a `--sandbox` (folder) kind for development, **from** the recipe file `Singularity`.

Once building is done, we can see what experiments are installed:


```
singularity apps expfactory
adaptive-n-back
tower-of-london
```

You can also ask for help:

```
singularity help expfactory
```

In the future I will likely make an automatic "recipe generator" that uses the config.jsons to help, for now it's just a game of copy pasting :)

 singularity instance.start expfactory.img web1

