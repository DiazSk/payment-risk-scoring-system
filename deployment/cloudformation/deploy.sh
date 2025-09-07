#!/bin/bash
# CloudFormation Deployment Script for Fraud Detection System

set -e

# Configuration
STACK_NAME="fraud-detection-system"
TEMPLATE_FILE="fraud-detection-stack.yaml"
PARAMETERS_FILE="parameters.env"
REGION="us-east-1"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check AWS CLI
check_aws_cli() {
    if ! command -v aws &> /dev/null; then
        log_error "AWS CLI not found. Please install AWS CLI first."
        exit 1
    fi
    
    if ! aws sts get-caller-identity &> /dev/null; then
        log_error "AWS credentials not configured. Please run 'aws configure'."
        exit 1
    fi
    
    log_info "AWS CLI configured correctly"
}

# Validate CloudFormation template
validate_template() {
    log_info "Validating CloudFormation template..."
    if aws cloudformation validate-template --template-body file://$TEMPLATE_FILE --region $REGION; then
        log_info "Template validation successful"
    else
        log_error "Template validation failed"
        exit 1
    fi
}

# Convert parameters file to CloudFormation parameter format
convert_parameters() {
    if [ ! -f "$PARAMETERS_FILE" ]; then
        log_error "Parameters file $PARAMETERS_FILE not found"
        exit 1
    fi
    
    # Read parameters and convert to JSON format
    local params=""
    while IFS='=' read -r key value; do
        # Skip empty lines and comments
        [[ $key =~ ^[[:space:]]*# ]] && continue
        [[ -z $key ]] && continue
        
        if [ -z "$params" ]; then
            params="\"ParameterKey=$key,ParameterValue=$value\""
        else
            params="$params \"ParameterKey=$key,ParameterValue=$value\""
        fi
    done < "$PARAMETERS_FILE"
    
    echo $params
}

# Check if stack exists
stack_exists() {
    aws cloudformation describe-stacks --stack-name $STACK_NAME --region $REGION &> /dev/null
}

# Deploy stack
deploy_stack() {
    local action="$1"
    local params=$(convert_parameters)
    
    log_info "Starting CloudFormation $action..."
    
    # Create parameter array
    local param_args=""
    if [ ! -z "$params" ]; then
        param_args="--parameters $params"
    fi
    
    if [ "$action" = "create" ]; then
        aws cloudformation create-stack \
            --stack-name $STACK_NAME \
            --template-body file://$TEMPLATE_FILE \
            $param_args \
            --capabilities CAPABILITY_NAMED_IAM \
            --region $REGION \
            --tags Key=Project,Value=FraudDetection Key=ManagedBy,Value=CloudFormation
    else
        aws cloudformation update-stack \
            --stack-name $STACK_NAME \
            --template-body file://$TEMPLATE_FILE \
            $param_args \
            --capabilities CAPABILITY_NAMED_IAM \
            --region $REGION
    fi
}

# Wait for stack operation to complete
wait_for_stack() {
    local action="$1"
    log_info "Waiting for stack $action to complete..."
    
    if [ "$action" = "create" ]; then
        aws cloudformation wait stack-create-complete --stack-name $STACK_NAME --region $REGION
    else
        aws cloudformation wait stack-update-complete --stack-name $STACK_NAME --region $REGION
    fi
    
    if [ $? -eq 0 ]; then
        log_info "Stack $action completed successfully"
    else
        log_error "Stack $action failed"
        exit 1
    fi
}

# Get stack outputs
get_outputs() {
    log_info "Getting stack outputs..."
    aws cloudformation describe-stacks \
        --stack-name $STACK_NAME \
        --region $REGION \
        --query 'Stacks[0].Outputs[*].[OutputKey,OutputValue]' \
        --output table
}

# Delete stack
delete_stack() {
    log_warn "This will delete the entire stack and all resources!"
    read -p "Are you sure you want to continue? (y/N): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        log_info "Deleting stack..."
        aws cloudformation delete-stack --stack-name $STACK_NAME --region $REGION
        
        log_info "Waiting for stack deletion to complete..."
        aws cloudformation wait stack-delete-complete --stack-name $STACK_NAME --region $REGION
        
        if [ $? -eq 0 ]; then
            log_info "Stack deleted successfully"
        else
            log_error "Stack deletion failed"
            exit 1
        fi
    else
        log_info "Stack deletion cancelled"
    fi
}

# Show help
show_help() {
    echo "Usage: $0 [OPTION]"
    echo ""
    echo "Options:"
    echo "  deploy    Deploy the CloudFormation stack (create or update)"
    echo "  delete    Delete the CloudFormation stack"
    echo "  outputs   Show stack outputs"
    echo "  validate  Validate the CloudFormation template"
    echo "  help      Show this help message"
    echo ""
    echo "Environment Variables:"
    echo "  STACK_NAME       CloudFormation stack name (default: fraud-detection-system)"
    echo "  REGION          AWS region (default: us-east-1)"
    echo "  TEMPLATE_FILE   CloudFormation template file (default: fraud-detection-stack.yaml)"
    echo "  PARAMETERS_FILE Parameters file (default: parameters.env)"
}

# Main execution
main() {
    case "${1:-}" in
        deploy)
            check_aws_cli
            validate_template
            
            if stack_exists; then
                log_info "Stack exists, updating..."
                deploy_stack "update"
                wait_for_stack "update"
            else
                log_info "Stack does not exist, creating..."
                deploy_stack "create"
                wait_for_stack "create"
            fi
            
            get_outputs
            ;;
        delete)
            check_aws_cli
            delete_stack
            ;;
        outputs)
            check_aws_cli
            get_outputs
            ;;
        validate)
            check_aws_cli
            validate_template
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            log_error "Unknown option: ${1:-}"
            show_help
            exit 1
            ;;
    esac
}

# Execute main function
main "$@"
