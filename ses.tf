#ses domain identity
# 1. Create the "Box" (Rule Set)
resource "aws_ses_receipt_rule_set" "main" {
  rule_set_name = "primary-ruleset"
}

# 2. Tell AWS: "This is the box I am currently using"
resource "aws_ses_active_receipt_rule_set" "main" {
  rule_set_name = aws_ses_receipt_rule_set.main.rule_set_name
}
resource "aws_ses_domain_identity" "legal_domain"{
    domain = "vijayalakshmi-kurra-porfolio.website"
}
# receipt rule
resource "aws_ses_receipt_rule" "storage_email" {
  name = "store-to-s3"
  rule_set_name = aws_ses_active_receipt_rule_set.main.rule_set_name
  recipients = [
    "legal@vijayalakshmi-kurra-porfolio.website",
    "intake@vijayalakshmi-kurra-porfolio.website",
    "claims@vijayalakshmi-kurra-porfolio.website"
  ]
  enabled = true
  scan_enabled = true

  s3_action {
    bucket_name = aws_s3_bucket.legal_uploads.id
    position = 1
  }
}