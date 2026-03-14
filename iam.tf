# the ID BADGE
resource "aws_iam_role" "lambda_role" {
  name = "legal_lambda_role"
  # this allows the Lambda service to use this role
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = { Service = "lambda.amazonaws.com"}

    }]
    
  })
}
# permissions
resource "aws_iam_role_policy" "lambda_all_permissions" {
  name   = "lambda_all_permissions"
  role   = aws_iam_role.lambda_role.id
  
  depends_on = [
    aws_s3_bucket.legal_uploads,
    aws_iam_role.lambda_role
  ]

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "S3Read"
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:GetObjectVersion"
        ]
        Resource = "${aws_s3_bucket.legal_uploads.arn}/*"
      },
      {
        Sid    = "Textract"
        Effect = "Allow"
        Action = [
          "textract:StartDocumentTextDetection",
          "textract:GetDocumentTextDetection",
          "textract:DetectDocumentText"
        ]
        Resource = "*"
      },
      {
        Sid    = "Bedrock"
        Effect = "Allow"
        Action = [
          "bedrock:InvokeModel"
        ]
        Resource = "*"
      },
      {
         Sid    = "BedrockList"
         Effect = "Allow"
         Action = [
           "bedrock:ListFoundationModels"
        ]
         Resource = "*"
      },
      {
        Sid    = "DynamoDBAccess"
        Effect = "Allow"
        Action = [
           "dynamodb:PutItem",
           "dynamodb:GetItem",
           "dynamodb:Query",
           "dynamodb:UpdateItem",
         ]
         Resource = "arn:aws:dynamodb:us-east-1:272183979798:table/legal-document-summaries"
       },
      {
        Sid    = "AWSMarketplaceAccess"
        Effect = "Allow"
        Action = [
          "aws-marketplace:ViewSubscriptions",
          "aws-marketplace:Subscribe"
       ]
       Resource = "*"
}
    ]
  })
}
resource "aws_iam_role_policy_attachment" "lambda_logs" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}
# 1. Define the policy for Textract
resource "aws_iam_role_policy" "lambda_textract_policy" {
  name = "legal_lambda_textract_policy"
  role = aws_iam_role.lambda_role.id # Ensure this matches your role name

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = [
          "textract:StartDocumentTextDetection",
          "textract:GetDocumentTextDetection",
          "textract:DetectDocumentText"
        ]
        Resource = "*"
      },
      {
        Effect   = "Allow"
        Action   = [
          "s3:GetObject"
        ]
        # This allows Textract to read the file from your bucket
        Resource = "${aws_s3_bucket.legal_uploads.arn}/*"
      },
      {
        Effect   = "Allow"
        Action   = "bedrock:InvokeModel"
        Resource = "*" 
      },
      {
        Sid    = "InvokeLambda"
        Effect = "Allow"
        Action = [
           "lambda:InvokeFunction"
         ]
        Resource = "arn:aws:lambda:us-east-1:272183979798:function/extract_legal_data"
      },
      {
  "Effect": "Allow",
  "Action": [
    "s3:ListBucket"
  ],
  "Resource": "${aws_s3_bucket.legal_uploads.arn}" # Note: No /* here!
}
    ]
  })
}
resource "aws_iam_role_policy" "lambda_b_bedrock" {
  name = "LambdaBedrockAccess"
  role = aws_iam_role.lambda_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = "bedrock:InvokeModel"
      Resource = "*" # Or restrict to specific model ARNs
    }]
  })
}
resource "aws_iam_role_policy" "lambda_bedrock_s3_policy" {
  name = "lambda_bedrock_s3_policy"
  role = aws_iam_role.lambda_role.id  # Change this to your second Lambda's role name

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "S3ReadForBedrock"
        Effect = "Allow"
        Action = [
          "s3:GetObject"
        ]
        Resource = "${aws_s3_bucket.legal_uploads.arn}/*"
      },
      {
        Sid    = "TextractRead"
        Effect = "Allow"
        Action = [
          "textract:GetDocumentTextDetection"
        ]
        Resource = "*"
      },
      {
        Sid    = "BedrockInvoke"
        Effect = "Allow"
        Action = [
          "bedrock:InvokeModel"
        ]
        Resource = "*"
      }
    ]
  })
}
# IAM Permission for Lambda 2 to invoke Lambda 3
resource "aws_iam_role_policy" "lambda_invoke_extractor" {
  name = "lambda_invoke_extractor"
  role = aws_iam_role.lambda_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "InvokeLambda3"
        Effect = "Allow"
        Action = [
          "lambda:InvokeFunction"
        ]
        Resource = "arn:aws:lambda:us-east-1:272183979798:function:legal_data_extractor"
      }
    ]
  })
}


