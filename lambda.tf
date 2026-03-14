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