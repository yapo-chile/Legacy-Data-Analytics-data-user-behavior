# scrapper-pi pipeline 

# Description

Scrapper-pi is a pipeline that would be extracting data from PortalInmobiliario website.
We would be looking for inmo info:
- Dealers

## Pipeline Implementation Details

|   Field           | Description                                         |
|-------------------|-----------------------------------------------------|
| Input Source      | Portal Inmobiliario website (Ads)                   |
| Output Source     | ods.pi_inmo;                                        |
| Schedule          | Every friday                                        |
| Rundeck Access    |                                                     |
| Associated Report | *soon*                                              |
|-------------------|-----------------------------------------------------|

### Build
```
make docker-build
```

### Run micro services
```
docker run -v /local-path/secrets/pulse:/app/pulse-secret \
           -v /local-path/secrets/db-secret:/app/db-secret \
           containers.mpi-internal.com/yapo/scrapper-pi:[TAG]
```

### Run micro services with parameters

```
docker run -v /local-path/secrets/pulse:/app/pulse-secret \
           -v /local-path/secrets/db-secret:/app/db-secret \
           containers.mpi-internal.com/yapo/scrapper-pi:[TAG]
```

### Adding Rundeck token to Travis

If we need to import a job into Rundeck, we can use the Rundeck API
sending an HTTTP POST request with the access token of an account.
To add said token to Travis (allowing travis to send the request),
first, we enter the user profile:
```
<rundeck domain>:4440/user/profile
```
And copy or create a new user token.

Then enter the project settings page in Travis
```
htttp://<travis server>/<registry>/<project>/settings
```
And add the environment variable RUNDECK_TOKEN, with value equal
to the copied token

### General changes

- Rename [project-name](https://github.mpi-internal.com/Yapo/data-pipeline-base/tree/master/project-name) folder for you develop name. For example **bounce-rate**.
- Rename [APPNAME](https://github.mpi-internal.com/Yapo/data-pipeline-base/blob/d330a8c59c6dff28339d44df57d575abfe145d2c/project-name/scripts/commands/vars.mk#L19) environment variable with new nombre of micro services. For each one the repositories from data, we can use the following prefixs.

| Repository    | Prefix docker image |
| ------------- |-------------|
| [data-content](https://github.mpi-internal.com/Yapo/data-content)      | data-content-**pipelineName** |
| [data-pulse](https://github.mpi-internal.com/Yapo/data-pulse)      | data-pulse-**pipelineName**      |
| [data-user-behavior](https://github.mpi-internal.com/Yapo/data-user-behavior) | data-user-behavior-**pipelineName**      |

