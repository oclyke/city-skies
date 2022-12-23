# github actions / workflows runners

this project relies on github actions to automate certain maintenance tasks including:
* continuous integration
  * linting / code style enforcement
* continuous deployment
  * building firmware images for supported targets

when possible these actions are run on github's cloud runners. this is done for
simplicity. tasks which can run on the github runners are things like linting and other
simple checks. building the firmware for targets is more complicated and so self-hosted
runners are the solution.

specifically the issue being solved by using self-hosted runners is that there is a
large amount of overhead required to build the firmware including installation of the
esp-idf, updates to all the submodules (for esp-idf, micropython, and precious-time),
and building the mpy-cross compiler. it is inefficient to perform these steps for each
of the supported targets. github workflows support job dependencies and matrices which
together enable a reasonable workflow:
* set up build environment once in one job
* build each target in a matrix job which depends on the setup job

unfortunately the use of two jobs here introduces a problem: the build jobs are very
unlikely to run (or perhaps explicitly barred from running) on the same machine as the
setup job. this means the required tools are not available.

self-hosted runners are the solution. by specifying one particular runner dedicated to
these tasks the workspace is persisted across jobs.

# setting up a self-hosted runner
this is very easy to do thanks to githubs self-hosted runner application. follow the 
[instructions for adding a self-hosted runner](https://docs.github.com/en/actions/hosting-your-own-runners/adding-self-hosted-runners).

the ```bin/runners``` directory is gitignored so that it can be used to contain the runner
application locally.

generally the process looks something like:
* create a subdirectory under ```bin/runners``` for the runner instance (you can create multiple instances)
* download the latest github self-hosted runner tools (a collection of scripts) into that directory
* on the repository settings use **actions** -> **runners** -> **add a new runner** to
  generate a command which is used to configure the runner
* follow the prompts to configure additional details
* start the runner ```./run.sh```

for this use case there should be exactly one self-hosted runner available to ensure that
the build steps happen on the same machine which the setup steps were run. the runner must
be active when jobs are queued in order to pick them up.
