resource "aws_dynamodb_table" "legal_summaries" {
  name           = "legal-document-summaries"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "jobId"
  
  attribute {
    name = "jobId"
    type = "S"
  }
  global_secondary_index {
    name            = "ClientIndex"
    hash_key        = "client_last_name"
    projection_type = "ALL"
  }
  
  attribute {
    name = "client_last_name"
    type = "S"
  }
}