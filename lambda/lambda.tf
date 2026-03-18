# the packaging 
data "archive_file" "lambda_zip" {
  type = "zip"
  source_file = "${path.module}/lambda_function.py" # Adding path.module makes it more stable
  output_path = "${path.module}/lambda_function.zip"
}
data "archive_file" "lambda2_zip" {
  type = "zip"
  source_file = "${path.module}/lambda_function2.py" # Adding path.module makes it more stable
  output_path = "${path.module}/results_processor.zip"  
}
# Lambda 3 - Data Extractor
data "archive_file" "lambda_extractor_zip" {
  type        = "zip"
  source_file = "${path.module}/lambda_function3.py"
  output_path = "${path.module}/lambda_extractor.zip"
}
# Lambda Step function
data "archive_file" "start_sf_zip" {
  type        = "zip"
  source_file = "${path.module}/lambda_step.py"
  output_path = "${path.module}/start_step_function.zip"
}
# Package send_retainer_email Lambda
data "archive_file" "send_email_zip" {
  type        = "zip"
  source_file = "${path.module}/send_retainer_email.py"
  output_path = "${path.module}/send_retainer_email.zip"
}

resource "aws_lambda_function" "start_step_function" {
  filename         = data.archive_file.start_sf_zip.output_path
  function_name    = "start-step-function"
  role             = aws_iam_role.lambda_role.arn
  handler          = "lambda_step.lambda_handler"
  runtime          = "python3.9"
  source_code_hash = data.archive_file.start_sf_zip.output_base64sha256

  environment {
    variables = {
      STATE_MACHINE_ARN = aws_sfn_state_machine.retainer_workflow.arn
    }
  }
}

# the Function
resource "aws_lambda_function" "legal_processor" {
    filename = data.archive_file.lambda_zip.output_path
    function_name = "legal_pdf_processor"
    role = aws_iam_role.lambda_role.arn
    handler       = "lambda_function.lambda_handler"
    runtime       = "python3.9"
    source_code_hash = data.archive_file.lambda_zip.output_base64sha256
  
}
resource "aws_lambda_function" "results_processor" {
    filename = data.archive_file.lambda2_zip.output_path
    function_name = "results_processor"
    role = aws_iam_role.lambda_role.arn
    handler       = "lambda_function2.lambda_handler"
    runtime       = "python3.9"
    source_code_hash = data.archive_file.lambda2_zip.output_base64sha256
  
}

 # permission for s3 to invoke lambda
 resource "aws_lambda_permission" "allow_s3" {
    statement_id = "AllowExecutionFromS3Bucket"
    action = "lambda:InvokeFunction"
    function_name = aws_lambda_function.legal_processor.function_name
    principal = "s3.amazonaws.com"
    source_arn = aws_s3_bucket.legal_uploads.arn
   
 }
 resource "aws_lambda_function" "legal_data_extractor" {
  filename         = data.archive_file.lambda_extractor_zip.output_path
  function_name    = "legal_data_extractor"
  role             = aws_iam_role.lambda_role.arn
  handler          = "lambda_function3.lambda_handler"
  runtime          = "python3.9"
  source_code_hash = data.archive_file.lambda_extractor_zip.output_base64sha256
  timeout          = 60
}
# Query Lambda
data "archive_file" "lambda_query_zip" {
  type        = "zip"
  source_file = "${path.module}/lambda_query.py"
  output_path = "${path.module}/lambda_query.zip"
}

resource "aws_lambda_function" "query_function" {
  filename         = data.archive_file.lambda_query_zip.output_path
  function_name    = "legal-query-function"
  role             = aws_iam_role.lambda_role.arn
  handler          = "lambda_query.lambda_handler"
  runtime          = "python3.9"
  source_code_hash = data.archive_file.lambda_query_zip.output_base64sha256
  timeout          = 30
}

# API Gateway
resource "aws_apigatewayv2_api" "legal_api" {
  name          = "legal-case-api"
  protocol_type = "HTTP"
  
  cors_configuration {
    allow_origins = ["*"]
    allow_methods = ["GET", "POST", "OPTIONS"]
    allow_headers = ["*"]
  }
}

# Lambda Integration
resource "aws_apigatewayv2_integration" "lambda" {
  api_id             = aws_apigatewayv2_api.legal_api.id
  integration_type   = "AWS_PROXY"
  integration_method = "POST"
  integration_uri    = aws_lambda_function.query_function.arn
  payload_format_version = "2.0"
}

# Route
resource "aws_apigatewayv2_route" "get_case" {
  api_id    = aws_apigatewayv2_api.legal_api.id
  route_key = "GET /cases/{jobId}"
  target    = "integrations/${aws_apigatewayv2_integration.lambda.id}"
}

# Stage
resource "aws_apigatewayv2_stage" "default" {
  api_id      = aws_apigatewayv2_api.legal_api.id
  name        = "$default"
  auto_deploy = true
}

# Lambda Permission
resource "aws_lambda_permission" "api_gateway" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.query_function.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.legal_api.execution_arn}/*/*"
}
# DynamoDB streams
resource "aws_lambda_event_source_mapping" "ddb_trigger" {
  event_source_arn  = aws_dynamodb_table.legal_summaries.stream_arn
  function_name     = aws_lambda_function.start_step_function.arn
  starting_position = "LATEST"
}

# Arn for stepfunction

resource "aws_sfn_state_machine" "retainer_workflow" {
  name     = "retainer-workflow"
  role_arn = aws_iam_role.step_function_role.arn
  definition = file("step_function_definition.json")
}

resource "aws_lambda_function" "send_retainer_email" {
  filename         = data.archive_file.send_email_zip.output_path
  function_name    = "send_retainer_email"
  role             = aws_iam_role.lambda_role.arn
  handler          = "send_retainer_email.lambda_handler"
  runtime          = "python3.9"
  source_code_hash = data.archive_file.send_email_zip.output_base64sha256
  timeout          = 60

  environment {
    variables = {
      TABLE_NAME            = aws_dynamodb_table.legal_summaries.name
      SENDER_EMAIL          = "legal@vijayalakshmi-kurra-porfolio.website"
      OFFICE_CALENDLY_LINK  = "https://calendly.com/office-consultation"
      VIRTUAL_CALENDLY_LINK = "https://calendly.com/virtual-consultation"
    }
  }
}
# Output API endpoint
output "api_endpoint" {
  value = aws_apigatewayv2_api.legal_api.api_endpoint
  description = "API Gateway endpoint URL"
}

