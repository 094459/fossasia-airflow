param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("start","stop","build")]
    [string]$action
)

function Build-Container {
    # Example Docker build command
    docker build --rm --compress -t amazon/mwaa-local:2_7 ./docker
    Write-Host "Docker build completed."
}

function Start-Container {
    # Example Docker run command
    docker-compose -p aws-mwaa-local-runner-2_7 -f ./docker/docker-compose-local.yml up
    Write-Host "Docker container started."
}

function Stop-Container {
    # Example Docker stop command
    ddocker-compose -p aws-mwaa-local-runner-2_7 -f ./docker/docker-compose-local.yml down
    Write-Host "Docker container stopped and removed."
}

Switch ($action) {
    "build-image" {
        Build-Container
    }
    "start" {
        Start-Container
    }
    "stop" {
        Stop-Container
    }
}

