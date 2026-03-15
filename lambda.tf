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

# Output API endpoint
output "api_endpoint" {
  value = aws_apigatewayv2_api.legal_api.api_endpoint
  description = "API Gateway endpoint URL"
}