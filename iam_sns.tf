

# 3. Add basic logging permissions so you can see your summaries
resource "aws_iam_role_policy_attachment" "lambda_log" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role" "textract_service_role" {
  name = "TextractServiceRole"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "textract.amazonaws.com"
      }
    }]
  })
}

resource "aws_iam_role_policy" "textract_sns_publish" {
  name = "TextractSNSPublish"
  role = aws_iam_role.textract_service_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = "sns:Publish"
      Resource = aws_sns_topic.textract_notifications.arn
    }]
  })
}