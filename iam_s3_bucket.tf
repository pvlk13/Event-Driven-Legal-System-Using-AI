resource "aws_iam_role_policy" "lambda_s3_put_delete" {
  name = "lambda_s3_put_delete"
  role = aws_iam_role.lambda_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "S3PutDelete"
        Effect = "Allow"
        Action = [
          "s3:PutObject",
          "s3:DeleteObject",
          "s3:GetObject"
        ]
        Resource = "${aws_s3_bucket.legal_uploads.arn}/*"
      }
    ]
  })
}