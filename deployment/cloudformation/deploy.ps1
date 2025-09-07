# CloudFormation Deployment Script for Fraud Detection System (PowerShell)

param(
    [Parameter(Position=0)]
    [ValidateSet('deploy', 'delete', 'outputs', 'validate', 'help')]
    [string]$Action = 'help',
    
    [string]$StackName = 'fraud-detection-system',
    [string]$Region = 'us-east-1',
    [string]$TemplateFile = 'fraud-detection-stack.yaml',
    [string]$ParametersFile = 'parameters.env'
)

# Functions
function Write-Info {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor Green
}

function Write-Warn {
    param([string]$Message)
    Write-Host "[WARN] $Message" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

function Test-AWSCli {
    if (!(Get-Command aws -ErrorAction SilentlyContinue)) {
        Write-Error "AWS CLI not found. Please install AWS CLI first."
        exit 1
    }
    
    try {
        aws sts get-caller-identity | Out-Null
        Write-Info "AWS CLI configured correctly"
    }
    catch {
        Write-Error "AWS credentials not configured. Please run 'aws configure'."
        exit 1
    }
}

function Test-Template {
    Write-Info "Validating CloudFormation template..."
    try {
        aws cloudformation validate-template --template-body "file://$TemplateFile" --region $Region | Out-Null
        Write-Info "Template validation successful"
    }
    catch {
        Write-Error "Template validation failed"
        exit 1
    }
}

function ConvertTo-CloudFormationParameters {
    if (!(Test-Path $ParametersFile)) {
        Write-Error "Parameters file $ParametersFile not found"
        exit 1
    }
    
    $parameters = @()
    Get-Content $ParametersFile | ForEach-Object {
        $line = $_.Trim()
        if ($line -and !$line.StartsWith('#')) {
            $key, $value = $line.Split('=', 2)
            if ($key -and $value) {
                $parameters += "ParameterKey=$key,ParameterValue=$value"
            }
        }
    }
    
    return $parameters
}

function Test-StackExists {
    try {
        aws cloudformation describe-stacks --stack-name $StackName --region $Region | Out-Null
        return $true
    }
    catch {
        return $false
    }
}

function Deploy-Stack {
    param([string]$Action)
    
    $parameters = ConvertTo-CloudFormationParameters
    Write-Info "Starting CloudFormation $Action..."
    
    $paramArgs = @()
    if ($parameters.Count -gt 0) {
        $paramArgs += '--parameters'
        $paramArgs += $parameters
    }
    
    $commonArgs = @(
        '--stack-name', $StackName,
        '--template-body', "file://$TemplateFile",
        '--capabilities', 'CAPABILITY_NAMED_IAM',
        '--region', $Region
    )
    
    if ($Action -eq 'create') {
        $args = @('cloudformation', 'create-stack') + $commonArgs + $paramArgs + @(
            '--tags', 'Key=Project,Value=FraudDetection', 'Key=ManagedBy,Value=CloudFormation'
        )
    }
    else {
        $args = @('cloudformation', 'update-stack') + $commonArgs + $paramArgs
    }
    
    try {
        & aws @args
    }
    catch {
        Write-Error "Stack $Action failed"
        exit 1
    }
}

function Wait-ForStack {
    param([string]$Action)
    
    Write-Info "Waiting for stack $Action to complete..."
    
    try {
        if ($Action -eq 'create') {
            aws cloudformation wait stack-create-complete --stack-name $StackName --region $Region
        }
        else {
            aws cloudformation wait stack-update-complete --stack-name $StackName --region $Region
        }
        Write-Info "Stack $Action completed successfully"
    }
    catch {
        Write-Error "Stack $Action failed"
        exit 1
    }
}

function Get-StackOutputs {
    Write-Info "Getting stack outputs..."
    try {
        aws cloudformation describe-stacks --stack-name $StackName --region $Region --query 'Stacks[0].Outputs[*].[OutputKey,OutputValue]' --output table
    }
    catch {
        Write-Error "Failed to get stack outputs"
        exit 1
    }
}

function Remove-Stack {
    Write-Warn "This will delete the entire stack and all resources!"
    $confirmation = Read-Host "Are you sure you want to continue? (y/N)"
    
    if ($confirmation -eq 'y' -or $confirmation -eq 'Y') {
        Write-Info "Deleting stack..."
        try {
            aws cloudformation delete-stack --stack-name $StackName --region $Region
            
            Write-Info "Waiting for stack deletion to complete..."
            aws cloudformation wait stack-delete-complete --stack-name $StackName --region $Region
            
            Write-Info "Stack deleted successfully"
        }
        catch {
            Write-Error "Stack deletion failed"
            exit 1
        }
    }
    else {
        Write-Info "Stack deletion cancelled"
    }
}

function Show-Help {
    Write-Host @"
Usage: .\deploy.ps1 [ACTION]

Actions:
  deploy    Deploy the CloudFormation stack (create or update)
  delete    Delete the CloudFormation stack
  outputs   Show stack outputs
  validate  Validate the CloudFormation template
  help      Show this help message

Parameters:
  -StackName       CloudFormation stack name (default: fraud-detection-system)
  -Region          AWS region (default: us-east-1)
  -TemplateFile    CloudFormation template file (default: fraud-detection-stack.yaml)
  -ParametersFile  Parameters file (default: parameters.env)

Examples:
  .\deploy.ps1 deploy
  .\deploy.ps1 deploy -StackName my-fraud-stack -Region us-west-2
  .\deploy.ps1 outputs
  .\deploy.ps1 delete
"@
}

# Main execution
switch ($Action) {
    'deploy' {
        Test-AWSCli
        Test-Template
        
        if (Test-StackExists) {
            Write-Info "Stack exists, updating..."
            Deploy-Stack 'update'
            Wait-ForStack 'update'
        }
        else {
            Write-Info "Stack does not exist, creating..."
            Deploy-Stack 'create'
            Wait-ForStack 'create'
        }
        
        Get-StackOutputs
    }
    'delete' {
        Test-AWSCli
        Remove-Stack
    }
    'outputs' {
        Test-AWSCli
        Get-StackOutputs
    }
    'validate' {
        Test-AWSCli
        Test-Template
    }
    'help' {
        Show-Help
    }
    default {
        Write-Error "Unknown action: $Action"
        Show-Help
        exit 1
    }
}
