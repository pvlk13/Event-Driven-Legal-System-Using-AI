# 1. Create the SNS Topic
resource "aws_sns_topic" "textract_notifications" {
  name = "AmazonTextract-LegalSummaries"
}

# 2. Allow Textract to publish to this topic
resource "aws_sns_topic_policy" "default" {
  arn = aws_sns_topic.textract_notifications.arn

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "AllowTextractToPublish"
        Effect = "Allow"
        Principal = {
          Service = "textract.amazonaws.com"
        }
        Action   = "sns:Publish"
        Resource = aws_sns_topic.textract_notifications.name
      }
    ]
  })
}
# Link SNS to Lambda
resource "aws_sns_topic_subscription" "textract_to_lambda" {
  topic_arn = aws_sns_topic.textract_notifications.arn
  protocol  = "lambda"
  endpoint  = aws_lambda_function.results_processor.arn # Your new Lambda B
}

# Give SNS permission to invoke the Lambda
resource "aws_lambda_permission" "allow_sns_invoke" {
  statement_id  = "AllowExecutionFromSNS"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.results_processor.function_name
  principal     = "sns.amazonaws.com"
  source_arn    = aws_sns_topic.textract_notifications.arn
}