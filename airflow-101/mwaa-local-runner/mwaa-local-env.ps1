$AIRFLOW_VERSION = "2_7"
$DOCKER_COMPOSE_PROJECT_NAME = "aws-mwaa-local-runner-$AIRFLOW_VERSION"

function Display-Help {
    Write-Host "======================================"
    Write-Host "   MWAA Local Runner CLI"
    Write-Host "======================================"
    Write-Host "Syntax: .\mwaa-local-runner.ps1 [command]"
    Write-Host "Airflow version $AIRFLOW_VERSION"
    Write-Host "---commands---"
    Write-Host "help                   Print CLI help"
    Write-Host "build-image            Build Image Locally"
    Write-Host "reset-db               Reset local PostgresDB container."
    Write-Host "start                  Start Airflow local environment. (LocalExecutor, Using postgres DB)"
    Write-Host "stop                   Stop Airflow local environment. (LocalExecutor, Using postgres DB)"
    Write-Host "test-requirements      Install requirements on an ephemeral instance of the container."
    Write-Host "package-requirements   Download requirements WHL files into plugins folder."
    Write-Host "test-startup-script    Execute shell script on an ephemeral instance of the container."
    Write-Host "validate-prereqs       Validate pre-reqs installed (docker, docker-compose, python3, pip3)"
    Write-Host ""
}

function Validate-Prereqs {
    docker -v | Out-Null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "'docker' is not installed or not runnable without sudo. ❌"
    } else {
        Write-Host "Docker is Installed. ✔"
    }

    docker-compose -v | Out-Null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "'docker-compose' is not installed. ❌"
    } else {
        Write-Host "Docker compose is Installed. ✔"
    }

    python --version | Out-Null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Python is not installed. ❌"
    } else {
        Write-Host "Python is Installed ✔"
    }

    pip --version | Out-Null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Pip is not installed. ❌"
    } else {
        Write-Host "Pip is Installed. ✔"
    }
}

function Build-Image {
    docker build --rm --compress -t "amazon/mwaa-local:$AIRFLOW_VERSION" ./docker
}

Switch ($args[0]) {
    "validate-prereqs" {
        Validate-Prereqs
    }
    "test-requirements" {
        $BUILT_IMAGE = docker images -q "amazon/mwaa-local:$AIRFLOW_VERSION"
        if ($BUILT_IMAGE) {
            Write-Host "Container amazon/mwaa-local:$AIRFLOW_VERSION exists. Skipping build"
        } else {
            Write-Host "Container amazon/mwaa-local:$AIRFLOW_VERSION not built. Building locally."
            Build-Image
        }
        docker run -v "${PWD}/dags:/usr/local/airflow/dags" -v "${PWD}/plugins:/usr/local/airflow/plugins" -v "${PWD}/requirements:/usr/local/airflow/requirements" -it "amazon/mwaa-local:$AIRFLOW_VERSION" test-requirements
    }
    "test-startup-script" { } # No operation, fall through
    "package-requirements" { } # No operation, fall through
    "build-image" {
        Build-Image
    }
    "reset-db" { } # No operation, fall throug
    "start" { } # No operation, fall through
    "stop" { } # No operation, fall through
    "help" {
        Display-Help
    }
    Default {
        Write-Host "No command specified, displaying help"
        Display-Help
    }
}

