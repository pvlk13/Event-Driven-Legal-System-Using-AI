resource "aws_s3_bucket" "legal_uploads" {
    bucket = "legal-intake-uploads-${random_id.id.hex}"  
}
resource "random_id" "id" {
  byte_length = 4
}
# the trigger
resource "aws_s3_bucket_notification" "bucket_notification" {
    bucket = aws_s3_bucket.legal_uploads.id
    lambda_function {
      lambda_function_arn = aws_lambda_function.legal_processor.arn
      events = ["s3:ObjectCreated:*"]
      filter_prefix       = ""
      filter_suffix       = ".eml"  # Only trigger on .eml files
    }
    depends_on = [ aws_lambda_permission.allow_s3 ]
}
resource "aws_s3_bucket_policy" "legal_uploads_policy" {
     bucket = aws_s3_bucket.legal_uploads.id

     policy = jsonencode({
       Version = "2012-10-17"
       Statement = [
         {
           Sid    = "AllowSESPuts"
           Effect = "Allow"
           Principal = {
             Service = "ses.amazonaws.com"
           }
           Action   = "s3:PutObject"
           Resource = "${aws_s3_bucket.legal_uploads.arn}/*"
           Condition = {
             StringEquals = {
               "aws:Referer" = data.aws_caller_identity.current.account_id
             }
           }
         },
         {
           Sid    = "AllowTextractS3Access"
           Effect = "Allow"
           Principal = {
             Service = "textract.amazonaws.com"
           }
           Action   = "s3:GetObject"
           Resource = "${aws_s3_bucket.legal_uploads.arn}/*"
         },
         {
           Sid    = "AllowLambdaS3Access"
           Effect = "Allow"
           Principal = {
             AWS = aws_iam_role.lambda_role.arn
           }
           Action = [
             "s3:GetObject",
             "s3:GetObjectVersion"
           ]
           Resource = "${aws_s3_bucket.legal_uploads.arn}/*"
         }
       ]
     })
   }
# Add this to get your account ID automatically
data "aws_caller_identity" "current" {}