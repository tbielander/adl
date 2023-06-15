# adl
A wrapper for Alma[^1] REST API


## How to use `adl`

Presumably the easiest way to use the `adl` library is within a docker container built from a project folder exhibiting the same folder structure as the GitLab project at hand. To that end the following folders and files are needed:

```
adl_project
|   dataloader.py
|   Dockerfile
|   docker-compose.yml
|   requirements.txt
|
├───adl
└───todo
    └───your_subproject
```

Perhaps some remarks on the more pivotal components are in order:

- `adl`: subfolder containing the `adl` library; the `adl` wrapper does not cover all Alma REST APIs but it can readily be expanded by adding new API templates to the `api.py` file and corresponding `Request` subclasses to the `api_request.py` file
- `todo/your_subproject`: path to the subfolder of your upcoming project where you put your project-specific input table as tsv (and further files as needed, e. g. XML templates of item objects) and where the log and backup files will automatically be saved; while the name of the `todo` folder is not supposed to be changed, the names of the top folder as well as of `your_project` may be chosen at will, the latter serving as a parameter of your `dataloader` file 
- `dataloader.py`: script file containing the project-specific parameters and your implementation of the core `step` function (see remarks below)

The `step` function in the `dataloader` file is the centerpiece of your `adl` project. When starting the docker container, the function will be recursively called, thereby governing the task-specific data loading process. Your `step` function defines the sequence of Alma REST API calls as well as the data to be logged row-wise in your customized log table. It does so by modifying  the `Condition` `c` object representing the process state at a time. See the simple example `dataloader` file for illustration of bibliographic items generation via POST requests.

In order to use `adl` with docker compose on a linux computer you can take the following steps:

1. cd into your `adl_project` top folder (above the `todo` folder)
2. Build the docker container passing user, group and working directory of the host:

```
docker compose build --build-arg USER_ID=$(id -u) --build-arg GROUP_ID=$(id -g) --build-arg GROUP=$(id -gn) --build-arg WD=$(pwd | rev | cut -d\/ -f1 | rev)
```

3. Run the container:

```
WD=$(pwd | rev | cut -d\/ -f1 | rev) docker compose up -d
``` 

Consult container logs for debugging (assuming that `adl_project` is the name of your top project folder):

```
docker logs adl_project -ft
```

If the dataloader script finishes successfully, the logfile with timestamp appears in the automatically generated log subfolder of your subproject folder.

4. Stop and remove the container:

```
docker compose down
```

[^1]: [Alma](https://exlibrisgroup.com/products/alma-library-services-platform/) is a library services platform developed by Ex Libris Ltd.
